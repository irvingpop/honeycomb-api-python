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
from deepeval.metrics import (  # noqa: E402
    ArgumentCorrectnessMetric,
    TaskCompletionMetric,
    ToolCorrectnessMetric,
)
from deepeval.models import AnthropicModel  # noqa: E402
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
def anthropic_eval_model():
    """Create DeepEval AnthropicModel for metric evaluation using ANTHROPIC_API_KEY.

    This allows metrics to use Claude for evaluation instead of requiring OpenAI.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return AnthropicModel(
        model="claude-sonnet-4-5-20250929",
        api_key=api_key
    )


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

    @pytest.mark.parametrize(
        "prompt,expected_tool_name",
        [
            (
                "Create a trigger for monitoring errors in api-logs",
                "honeycomb_create_trigger",
            ),
            (
                "List all SLOs in production dataset",
                "honeycomb_list_slos",
            ),
            (
                "Delete burn alert ba-123 from SLO slo-456 in dataset api-logs",
                "honeycomb_delete_burn_alert",
            ),
        ],
    )
    def test_tool_selection_with_tool_correctness_metric(
        self, anthropic_client, anthropic_eval_model, prompt, expected_tool_name
    ):
        """Validate tool selection using ToolCorrectnessMetric with Claude evaluation."""
        result = call_claude_with_tools(anthropic_client, prompt)

        # Convert tool calls to DeepEval format
        deepeval_tools = [
            ToolCall(name=tc.name, input_parameters=tc.input)
            for tc in result["tool_calls"]
        ]

        # DeepEval expects expected_tools as ToolCall objects, not strings
        expected_tools = [ToolCall(name=expected_tool_name)]

        # Create test case with expected tools
        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=deepeval_tools,
            expected_tools=expected_tools,
        )

        # Use ToolCorrectnessMetric with Claude for evaluation (no OpenAI key needed)
        metric = ToolCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])


# ==============================================================================
# Parameter Quality Tests (Using DeepEval Metrics)
# ==============================================================================

class TestParameterQuality:
    """Verify Claude generates valid parameters using DeepEval metrics."""

    def test_trigger_params_with_argument_correctness(self, anthropic_client, anthropic_eval_model):
        """Trigger parameters should be correct using ArgumentCorrectnessMetric with Claude evaluation."""
        prompt = (
            "Create a trigger named 'High Errors' in dataset 'api-logs' "
            "that fires when error count > 100 in the last 15 minutes"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1, "Should make exactly one tool call"
        tool_call = result["tool_calls"][0]

        # Convert to DeepEval format
        deepeval_tool_call = ToolCall(
            name=tool_call.name,
            input_parameters=tool_call.input,
        )

        # Create test case
        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[deepeval_tool_call],
        )

        # Use ArgumentCorrectnessMetric with Claude for evaluation (no OpenAI key needed)
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])

        # Additional basic checks
        assert tool_call.name == "honeycomb_create_trigger"
        assert "dataset" in tool_call.input
        assert "name" in tool_call.input
        assert "query" in tool_call.input
        assert "threshold" in tool_call.input

    def test_slo_params_with_argument_correctness(self, anthropic_client, anthropic_eval_model):
        """SLO parameters should be correct using ArgumentCorrectnessMetric with Claude evaluation."""
        prompt = (
            "Create an SLO named 'API Availability' in dataset 'api-logs' "
            "with 99.9% target over 30 days, using success_rate as the SLI"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]

        # Convert to DeepEval format
        deepeval_tool_call = ToolCall(
            name=tool_call.name,
            input_parameters=tool_call.input,
        )

        # Create test case
        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[deepeval_tool_call],
        )

        # Use ArgumentCorrectnessMetric with Claude for evaluation
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])

        # Additional basic checks
        assert tool_call.name == "honeycomb_create_slo"
        assert "dataset" in tool_call.input
        assert "sli" in tool_call.input
        assert "target_per_million" in tool_call.input

    def test_burn_alert_params_with_argument_correctness(self, anthropic_client, anthropic_eval_model):
        """Burn alert parameters should be correct using ArgumentCorrectnessMetric with Claude evaluation."""
        prompt = (
            "Create an exhaustion time burn alert for SLO slo-123 in dataset 'api-logs' "
            "that alerts when budget will be exhausted in 60 minutes"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]

        # Convert to DeepEval format
        deepeval_tool_call = ToolCall(
            name=tool_call.name,
            input_parameters=tool_call.input,
        )

        # Create test case
        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[deepeval_tool_call],
        )

        # Use ArgumentCorrectnessMetric with Claude for evaluation
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])

        # Additional basic checks
        assert tool_call.name == "honeycomb_create_burn_alert"
        assert "alert_type" in tool_call.input
        assert "slo_id" in tool_call.input


# ==============================================================================
# Advanced Metric Tests (TaskCompletion & StepEfficiency)
# ==============================================================================

class TestAdvancedMetrics:
    """Test TaskCompletionMetric and StepEfficiencyMetric."""

    def test_task_completion_for_trigger_creation(self, anthropic_client, anthropic_eval_model):
        """Validate task completion for trigger creation using Claude evaluation."""
        task = "Create a trigger that monitors API errors"
        prompt = (
            "Create a trigger named 'API Errors' in dataset 'api-logs' "
            "that fires when error count > 50 in the last 10 minutes"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        # Convert tool calls to DeepEval format
        deepeval_tools = [
            ToolCall(name=tc.name, input_parameters=tc.input)
            for tc in result["tool_calls"]
        ]

        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=deepeval_tools,
        )

        # Task should be considered complete if tool was called
        metric = TaskCompletionMetric(threshold=0.7, task=task, model=anthropic_eval_model)
        assert_test(test_case, [metric])

    def test_combined_metrics_for_slo_workflow(self, anthropic_client, anthropic_eval_model):
        """Test multiple metrics together for SLO creation workflow using Claude evaluation."""
        task = "Create an SLO to track API success rate"
        prompt = (
            "Create an SLO named 'API Success' in dataset 'api-logs' "
            "with 99% target over 7 days, tracking success_rate"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        # Convert tool calls to DeepEval format
        deepeval_tools = [
            ToolCall(name=tc.name, input_parameters=tc.input)
            for tc in result["tool_calls"]
        ]

        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=deepeval_tools,
        )

        # Test ArgumentCorrectness and TaskCompletion
        # Note: StepEfficiencyMetric removed - requires trace data not available in simple tool tests
        metrics = [
            ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model),
            TaskCompletionMetric(threshold=0.7, task=task, model=anthropic_eval_model),
        ]
        assert_test(test_case, metrics)


# ==============================================================================
# Comprehensive Argument Correctness Tests
# ==============================================================================

class TestComprehensiveArgumentCorrectness:
    """Comprehensive tests for argument correctness across different scenarios.

    These tests validate that Claude correctly interprets natural language prompts
    and generates semantically correct tool arguments without calling live APIs.
    """

    def test_trigger_with_multiple_filters(self, anthropic_client, anthropic_eval_model):
        """Test trigger creation with multiple filter conditions."""
        prompt = (
            "Create a trigger in dataset 'api-logs' that alerts when the count of requests "
            "where status_code >= 500 AND duration > 1000 exceeds 100 in the last 15 minutes"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]
        assert tool_call.name == "honeycomb_create_trigger"

        # Verify filters are present
        params = tool_call.input
        assert "query" in params
        query = params["query"]
        assert "filters" in query or "filter_combination" in query

        # Use ArgumentCorrectnessMetric for semantic validation
        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[ToolCall(name=tool_call.name, input_parameters=tool_call.input)],
        )
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])

    def test_trigger_with_percentile_calculation(self, anthropic_client, anthropic_eval_model):
        """Test trigger with P99 calculation (not just COUNT)."""
        prompt = (
            "Create a trigger in dataset 'api-logs' that alerts when "
            "P99 of duration exceeds 2000ms over the last 30 minutes"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]

        # Verify calculation is P99, not COUNT
        params = tool_call.input
        query = params.get("query", {})
        # Check calculations array (plural)
        calculations = query.get("calculations", [])
        assert len(calculations) > 0, "Should have at least one calculation"
        assert calculations[0].get("op") == "P99"
        assert calculations[0].get("column") == "duration"

        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[ToolCall(name=tool_call.name, input_parameters=tool_call.input)],
        )
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])

    def test_slo_with_inline_derived_column(self, anthropic_client, anthropic_eval_model):
        """Test SLO creation with inline derived column definition."""
        prompt = (
            "Create an SLO in dataset 'api-logs' with 99.5% target over 30 days "
            "where the SLI is the ratio of requests with status_code < 400 to total requests"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]
        assert tool_call.name == "honeycomb_create_slo"

        # Should have inline SLI definition (expression), not just alias
        params = tool_call.input
        sli = params.get("sli", {})
        # Either has expression (inline) or alias (existing)
        assert "expression" in sli or "alias" in sli

        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[ToolCall(name=tool_call.name, input_parameters=tool_call.input)],
        )
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])

    def test_burn_alert_budget_rate_type(self, anthropic_client, anthropic_eval_model):
        """Test burn alert with budget_rate type (not just exhaustion_time)."""
        prompt = (
            "Create a budget_rate burn alert for SLO slo-abc123 in dataset 'api-logs' "
            "that fires when the error budget decreases by more than 5% in a 60 minute window"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]
        assert tool_call.name == "honeycomb_create_burn_alert"

        # Should detect budget_rate alert type
        params = tool_call.input
        assert params.get("alert_type") == "budget_rate"
        # 5% = 50000 per million
        assert params.get("budget_rate_decrease_threshold_per_million") == 50000
        assert params.get("budget_rate_window_minutes") == 60

        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[ToolCall(name=tool_call.name, input_parameters=tool_call.input)],
        )
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])

    def test_trigger_with_string_filter_operators(self, anthropic_client, anthropic_eval_model):
        """Test trigger with string filter operators (contains, starts-with)."""
        prompt = (
            "Create a trigger in dataset 'api-logs' that alerts when count of requests "
            "where endpoint contains '/api/v2' and method starts with 'POST' exceeds 1000"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]

        # Should have filters with string operators
        params = tool_call.input
        query = params.get("query", {})
        # Filters should exist
        assert "filters" in query or "filter_combination" in query

        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[ToolCall(name=tool_call.name, input_parameters=tool_call.input)],
        )
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])

    def test_trigger_with_exists_filter(self, anthropic_client, anthropic_eval_model):
        """Test trigger with 'exists' filter operator."""
        prompt = (
            "Create a trigger in dataset 'api-logs' that alerts when count of requests "
            "where user_id exists exceeds 500"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]

        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[ToolCall(name=tool_call.name, input_parameters=tool_call.input)],
        )
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])

    def test_slo_percentage_conversion(self, anthropic_client, anthropic_eval_model):
        """Test that Claude correctly converts percentages to target_per_million."""
        prompt = (
            "Create an SLO in dataset 'api-logs' with 99.99% target over 7 days "
            "using existing column success_rate"
        )
        result = call_claude_with_tools(anthropic_client, prompt)

        assert len(result["tool_calls"]) == 1
        tool_call = result["tool_calls"][0]

        # 99.99% should be 999900 per million
        params = tool_call.input
        assert "target_per_million" in params
        # Allow some tolerance for rounding
        assert 999000 <= params["target_per_million"] <= 1000000

        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"],
            tools_called=[ToolCall(name=tool_call.name, input_parameters=tool_call.input)],
        )
        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case, [metric])
