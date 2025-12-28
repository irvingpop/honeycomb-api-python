"""Claude API evaluation tests using DeepEval.

These tests validate tool definitions against the real Claude API:
1. Schema Acceptance: Claude parses tool definitions without error
2. Tool Selection: Claude selects the correct tool for each prompt
3. Parameter Quality: Claude generates valid parameters
4. End-to-End: Full workflow execution with Honeycomb API

Requirements:
- ANTHROPIC_API_KEY environment variable (for Claude API access)
- HONEYCOMB_API_KEY environment variable (for end-to-end tests only)

Installation:
    poetry install --with evals

Usage:
    # Run all eval tests (requires both API keys)
    ANTHROPIC_API_KEY=... HONEYCOMB_API_KEY=... pytest tests/integration/test_claude_tools_eval.py -v

    # Run only tool selection tests (no Honeycomb needed)
    ANTHROPIC_API_KEY=... pytest tests/integration/test_claude_tools_eval.py -v -k "TestToolSelection"

    # Skip eval tests in regular CI
    pytest --ignore=tests/integration/test_claude_tools_eval.py
"""

import json
import os

import pytest

# DeepEval and Anthropic are optional dependencies
deepeval = pytest.importorskip("deepeval", reason="DeepEval not installed. Run: poetry install --with evals")
anthropic_module = pytest.importorskip("anthropic", reason="Anthropic SDK not installed. Run: poetry install --with evals")

from deepeval import assert_test  # noqa: E402
from deepeval.metrics import ToolCorrectnessMetric  # noqa: E402
from deepeval.test_case import LLMTestCase, ToolCall  # noqa: E402

from honeycomb import HoneycombClient  # noqa: E402
from honeycomb.tools import HONEYCOMB_TOOLS, execute_tool  # noqa: E402

pytestmark = [
    pytest.mark.evals,  # Requires ANTHROPIC_API_KEY
]


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def anthropic_client():
    """Create Anthropic client using ANTHROPIC_API_KEY env var."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return anthropic_module.Anthropic(api_key=api_key)


@pytest.fixture
async def honeycomb_client():
    """Create Honeycomb client using HONEYCOMB_API_KEY env var."""
    api_key = os.environ.get("HONEYCOMB_API_KEY")
    if not api_key:
        pytest.skip("HONEYCOMB_API_KEY not set")
    async with HoneycombClient(api_key=api_key) as client:
        yield client


def call_claude_with_tools(client, prompt: str, use_system_prompt: bool = True) -> dict:
    """Call Claude with Honeycomb tools, return parsed response.

    Args:
        client: Anthropic client
        prompt: User prompt to send to Claude
        use_system_prompt: If True, adds system prompt encouraging tool use

    Returns:
        Dict with tool_calls, text, and stop_reason
    """
    # System prompt that encourages tool usage over conversational responses
    system_prompt = (
        "You are a Honeycomb API automation assistant. "
        "When the user asks you to perform operations on Honeycomb resources, "
        "you MUST use the available tools rather than providing conversational responses. "
        "Always call the appropriate tool, even if some parameters are not explicitly specified - "
        "use reasonable defaults. "
        "Only respond conversationally if no appropriate tool is available."
    )

    kwargs = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 1024,
        "tools": HONEYCOMB_TOOLS,
        "messages": [{"role": "user", "content": prompt}],
    }

    if use_system_prompt:
        kwargs["system"] = system_prompt

    response = client.messages.create(**kwargs)

    tool_calls = [b for b in response.content if b.type == "tool_use"]
    text_content = " ".join(b.text for b in response.content if hasattr(b, "text"))

    return {
        "tool_calls": tool_calls,
        "text": text_content,
        "stop_reason": response.stop_reason,
    }


# ==============================================================================
# Schema Acceptance Tests
# ==============================================================================

class TestToolSchemaAcceptance:
    """Verify Claude accepts our tool definitions without error."""

    def test_all_tools_accepted(self, anthropic_client):
        """Claude should parse all 15 tool definitions successfully."""
        # Test without system prompt to verify schema parsing
        result = call_claude_with_tools(
            anthropic_client, "What tools do you have available?", use_system_prompt=False
        )
        assert result["stop_reason"] in ("end_turn", "tool_use")

    def test_system_prompt_encourages_tool_use(self, anthropic_client):
        """System prompt should increase tool usage rate."""
        prompt = "Create a trigger for high error rates in api-logs"

        # Without system prompt - may respond conversationally
        result_without = call_claude_with_tools(anthropic_client, prompt, use_system_prompt=False)

        # With system prompt - should make tool call
        result_with = call_claude_with_tools(anthropic_client, prompt, use_system_prompt=True)

        # With system prompt should have higher likelihood of tool calls
        # (Not guaranteed, but we document the difference)
        print(f"\nWithout system prompt: {len(result_without['tool_calls'])} tool calls")
        print(f"With system prompt: {len(result_with['tool_calls'])} tool calls")


# ==============================================================================
# Tool Selection Tests
# ==============================================================================

class TestToolSelection:
    """Verify Claude selects appropriate tools."""

    @pytest.mark.parametrize(
        "prompt,expected_tool",
        [
            # More directive prompts with explicit parameters
            (
                "Create a trigger in dataset api-logs that counts status_code >= 500 and alerts when count > 100 every 15 minutes",
                "honeycomb_create_trigger",
            ),
            (
                "List all SLOs in the production dataset",
                "honeycomb_list_slos",
            ),
            (
                "Delete trigger abc123 from dataset my-dataset",
                "honeycomb_delete_trigger",
            ),
            (
                "Get SLO slo-456 from dataset production",
                "honeycomb_get_slo",
            ),
            (
                "Create an exhaustion_time burn alert for SLO slo-123 in dataset api-logs with 60 minute threshold",
                "honeycomb_create_burn_alert",
            ),
            (
                "List burn alerts for SLO slo-789 in dataset production",
                "honeycomb_list_burn_alerts",
            ),
        ],
    )
    def test_tool_selection(self, anthropic_client, prompt, expected_tool):
        """Claude should select the correct tool for each prompt."""
        result = call_claude_with_tools(anthropic_client, prompt)

        # Verify tool was called
        assert len(result["tool_calls"]) >= 1, f"No tool calls made for prompt: {prompt}"

        # Verify correct tool selected
        actual_tool = result["tool_calls"][0].name
        assert actual_tool == expected_tool, (
            f"Expected tool '{expected_tool}' but got '{actual_tool}' for prompt: {prompt}"
        )


# ==============================================================================
# Parameter Quality Tests (Custom Assertions)
# ==============================================================================

class TestParameterQuality:
    """Verify Claude generates valid parameters."""

    def test_trigger_params_complete(self, anthropic_client):
        """Trigger parameters should include all required fields."""
        prompt = (
            "Create a trigger named 'High Errors' in dataset 'api-logs' "
            "that fires when error count > 100 in the last 15 minutes"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1, "Should make exactly one tool call"
        tool_call = result["tool_calls"][0]

        # Verify correct tool
        assert tool_call.name == "honeycomb_create_trigger"

        # Verify all required parameters present
        params = tool_call.input
        assert "dataset" in params
        assert "name" in params
        assert "query" in params
        assert "threshold" in params

        # Verify parameter values are reasonable
        assert params["dataset"] == "api-logs"
        assert "High Errors" in params["name"] or "high" in params["name"].lower()
        assert params["threshold"]["op"] in [">", ">="]
        assert params["threshold"]["value"] >= 100

    def test_slo_params_complete(self, anthropic_client):
        """SLO parameters should include target and SLI."""
        prompt = (
            "Create an SLO named 'API Availability' in dataset 'api-logs' "
            "with 99.9% target over 30 days, using success_rate as the SLI"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]

        # Verify correct tool
        assert tool_call.name == "honeycomb_create_slo"

        # Verify required parameters
        params = tool_call.input
        assert "dataset" in params
        assert "name" in params
        assert "sli" in params
        assert "target_per_million" in params
        assert "time_period_days" in params

        # Verify values
        assert params["dataset"] == "api-logs"
        assert params["sli"]["alias"] == "success_rate"
        assert params["time_period_days"] == 30
        # 99.9% = 999000 per million
        assert params["target_per_million"] == 999000

    def test_burn_alert_params_complete(self, anthropic_client):
        """Burn alert parameters should include alert type and threshold."""
        prompt = (
            "Create an exhaustion time burn alert for SLO slo-123 in dataset 'api-logs' "
            "that alerts when budget will be exhausted in 60 minutes"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]

        # Verify correct tool
        assert tool_call.name == "honeycomb_create_burn_alert"

        # Verify required parameters
        params = tool_call.input
        assert "dataset" in params
        assert "alert_type" in params
        assert "slo_id" in params
        assert "exhaustion_minutes" in params

        # Verify values
        assert params["dataset"] == "api-logs"
        assert params["alert_type"] == "exhaustion_time"
        assert params["slo_id"] == "slo-123"
        assert params["exhaustion_minutes"] == 60


# ==============================================================================
# End-to-End Tests (Claude → Executor → Honeycomb API)
# ==============================================================================

class TestEndToEnd:
    """Full integration: Claude → Executor → Honeycomb API.

    These tests require both ANTHROPIC_API_KEY and HONEYCOMB_API_KEY.
    They create real resources in Honeycomb and clean them up.
    """

    @pytest.mark.live
    async def test_create_and_cleanup_trigger(self, anthropic_client, honeycomb_client):
        """Create a trigger via Claude, verify in Honeycomb, then clean up."""
        prompt = (
            "Create a trigger named 'DeepEval Test Trigger' in dataset "
            "'claude-tool-test' that alerts when COUNT > 50"
        )
        result = call_claude_with_tools(anthropic_client, prompt)
        tool_call = result["tool_calls"][0]

        # Verify correct tool selected
        assert tool_call.name == "honeycomb_create_trigger"

        # Execute via our handler
        result_json = await execute_tool(honeycomb_client, tool_call.name, tool_call.input)
        created = json.loads(result_json)

        try:
            # Verify trigger was created
            assert "id" in created
            assert created["name"] == "DeepEval Test Trigger"

            # Verify it exists in Honeycomb
            fetched = await honeycomb_client.triggers.get_async(
                dataset="claude-tool-test", trigger_id=created["id"]
            )
            assert fetched.name == "DeepEval Test Trigger"
        finally:
            # Clean up
            await honeycomb_client.triggers.delete_async(
                dataset="claude-tool-test", trigger_id=created["id"]
            )

    @pytest.mark.live
    async def test_create_and_cleanup_slo(self, anthropic_client, honeycomb_client):
        """Create an SLO via Claude, verify in Honeycomb, then clean up."""
        prompt = (
            "Create an SLO named 'DeepEval Test SLO' in dataset 'claude-tool-test' "
            "with 99% target over 7 days using existing derived column 'test_success'"
        )
        result = call_claude_with_tools(anthropic_client, prompt)
        tool_call = result["tool_calls"][0]

        # Verify correct tool selected
        assert tool_call.name == "honeycomb_create_slo"

        # Execute via our handler
        result_json = await execute_tool(honeycomb_client, tool_call.name, tool_call.input)
        created = json.loads(result_json)

        try:
            # Verify SLO was created
            assert "id" in created
            assert created["name"] == "DeepEval Test SLO"

            # Verify it exists in Honeycomb
            fetched = await honeycomb_client.slos.get_async(
                dataset="claude-tool-test", slo_id=created["id"]
            )
            assert fetched.name == "DeepEval Test SLO"
        finally:
            # Clean up
            await honeycomb_client.slos.delete_async(
                dataset="claude-tool-test", slo_id=created["id"]
            )
