"""Data-driven Claude API evaluation tests using DeepEval.

Scalable architecture for testing all 58 tools across 12 resources.

Test data is organized in test_cases/ directory, with one file per resource.
This allows easy addition of new test cases without modifying test execution logic.

Requirements:
    - ANTHROPIC_API_KEY environment variable

Installation:
    poetry install --with evals

Usage:
    # Run all eval tests
    direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v

    # Run tests for specific resource
    direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k triggers

    # Run specific test by ID
    direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k trigger_p99_percentile

    # Fast mode (basic assertions only, ~30 seconds)
    direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k basic

    # LLM eval mode (comprehensive validation, ~5 minutes)
    direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k llm_eval
"""

import os

import pytest

# DeepEval and Anthropic are optional dependencies
deepeval = pytest.importorskip(
    "deepeval", reason="DeepEval not installed. Run: poetry install --with evals"
)
anthropic_module = pytest.importorskip(
    "anthropic", reason="Anthropic SDK not installed. Run: poetry install --with evals"
)

from deepeval import assert_test  # noqa: E402
from deepeval.metrics import (  # noqa: E402
    ArgumentCorrectnessMetric,
    ToolCorrectnessMetric,
)
from deepeval.models import AnthropicModel  # noqa: E402
from deepeval.test_case import LLMTestCase, ToolCall  # noqa: E402

from honeycomb.tools import HONEYCOMB_TOOLS  # noqa: E402

from .test_cases import get_all_test_cases  # noqa: E402

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
    """Create DeepEval AnthropicModel for metric evaluation.

    Uses Claude for evaluation instead of requiring OpenAI API key.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return AnthropicModel(model="claude-sonnet-4-5-20250929", api_key=api_key)


# ==============================================================================
# Helper Functions
# ==============================================================================


def call_claude_with_tools(client, prompt: str) -> dict:
    """Call Claude with Honeycomb tools.

    Args:
        client: Anthropic client
        prompt: User prompt

    Returns:
        Dict with tool_calls, text, and stop_reason
    """
    system_prompt = (
        "You are a Honeycomb API automation assistant. "
        "When the user asks you to perform operations on Honeycomb resources, "
        "you MUST use the available tools rather than providing conversational responses. "
        "Always call the appropriate tool, even if some parameters are not explicitly specified - "
        "use reasonable defaults. "
        "Only respond conversationally if no appropriate tool is available."
    )

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        tools=HONEYCOMB_TOOLS,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    tool_calls = [b for b in response.content if b.type == "tool_use"]
    text_content = " ".join(b.text for b in response.content if hasattr(b, "text"))

    return {
        "tool_calls": tool_calls,
        "text": text_content,
        "stop_reason": response.stop_reason,
    }


def check_assertion(assertion_expr: str, params: dict) -> bool:
    """Evaluate assertion expression against parameters.

    Args:
        assertion_expr: Python expression to evaluate (e.g., "params['threshold']['value'] >= 100")
        params: Tool parameters to check

    Returns:
        True if assertion passes

    Raises:
        AssertionError: If assertion fails
    """
    # Make params available in scope for eval
    result = eval(assertion_expr, {"params": params})
    if not result:
        raise AssertionError(f"Assertion failed: {assertion_expr}")
    return True


# ==============================================================================
# Data-Driven Tests
# ==============================================================================


class TestToolSelection:
    """Test correct tool selection using test case data."""

    @pytest.mark.parametrize("test_case", get_all_test_cases(), ids=lambda tc: tc["id"])
    def test_tool_selection_basic(self, anthropic_client, test_case):
        """Verify Claude selects the correct tool (fast, no LLM evaluation)."""
        result = call_claude_with_tools(anthropic_client, test_case["prompt"])

        # Verify tool was called
        assert len(result["tool_calls"]) >= 1, (
            f"No tool calls for: {test_case['description']}"
        )

        # Verify correct tool selected
        actual_tool = result["tool_calls"][0].name
        expected_tool = test_case["expected_tool"]
        assert actual_tool == expected_tool, (
            f"{test_case['id']}: Expected '{expected_tool}' but got '{actual_tool}'"
        )

    @pytest.mark.parametrize("test_case", get_all_test_cases(), ids=lambda tc: tc["id"])
    def test_tool_selection_with_llm_eval(
        self, anthropic_client, anthropic_eval_model, test_case
    ):
        """Verify tool selection using ToolCorrectnessMetric (slower, LLM-based)."""
        result = call_claude_with_tools(anthropic_client, test_case["prompt"])

        # Convert to DeepEval format
        deepeval_tools = [
            ToolCall(name=tc.name, input_parameters=tc.input) for tc in result["tool_calls"]
        ]
        expected_tools = [ToolCall(name=test_case["expected_tool"])]

        test_case_obj = LLMTestCase(
            input=test_case["prompt"],
            actual_output=result["text"],
            tools_called=deepeval_tools,
            expected_tools=expected_tools,
        )

        metric = ToolCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case_obj, [metric])


class TestArgumentCorrectness:
    """Test argument correctness using test case data."""

    @pytest.mark.parametrize("test_case", get_all_test_cases(), ids=lambda tc: tc["id"])
    def test_argument_basic_assertions(self, anthropic_client, test_case):
        """Verify basic parameter assertions (fast, no LLM evaluation)."""
        result = call_claude_with_tools(anthropic_client, test_case["prompt"])

        assert len(result["tool_calls"]) >= 1, (
            f"No tool calls for: {test_case['description']}"
        )
        tool_call = result["tool_calls"][0]
        params = tool_call.input

        # Check expected parameters (partial match)
        for key, expected_value in test_case.get("expected_params", {}).items():
            if "." in key:
                # Nested field access (e.g., "threshold.op")
                parts = key.split(".")
                current = params
                for part in parts[:-1]:
                    current = current.get(part, {})
                actual_value = current.get(parts[-1])
            else:
                actual_value = params.get(key)

            # For dict values, do deep equality
            if isinstance(expected_value, dict):
                for nested_key, nested_val in expected_value.items():
                    assert actual_value.get(nested_key) == nested_val, (
                        f"{test_case['id']}: {key}.{nested_key} = {actual_value.get(nested_key)}, "
                        f"expected {nested_val}"
                    )
            else:
                assert actual_value == expected_value, (
                    f"{test_case['id']}: {key} = {actual_value}, expected {expected_value}"
                )

        # Run custom assertions
        for assertion in test_case.get("assertion_checks", []):
            check_assertion(assertion, params)

    @pytest.mark.parametrize("test_case", get_all_test_cases(), ids=lambda tc: tc["id"])
    def test_argument_with_llm_eval(
        self, anthropic_client, anthropic_eval_model, test_case
    ):
        """Verify arguments using ArgumentCorrectnessMetric (slower, LLM-based)."""
        result = call_claude_with_tools(anthropic_client, test_case["prompt"])

        assert len(result["tool_calls"]) >= 1
        tool_call = result["tool_calls"][0]

        # Convert to DeepEval format
        test_case_obj = LLMTestCase(
            input=test_case["prompt"],
            actual_output=result["text"],
            tools_called=[
                ToolCall(name=tool_call.name, input_parameters=tool_call.input)
            ],
        )

        metric = ArgumentCorrectnessMetric(threshold=0.7, model=anthropic_eval_model)
        assert_test(test_case_obj, [metric])


# ==============================================================================
# Schema Validation Tests
# ==============================================================================


class TestToolSchemas:
    """Validate tool schemas are accepted by Claude API."""

    def test_all_tools_accepted(self, anthropic_client):
        """Claude should parse all tool definitions without error."""
        result = call_claude_with_tools(anthropic_client, "What tools do you have?")
        assert result["stop_reason"] in ("end_turn", "tool_use")

    def test_system_prompt_encourages_tool_use(self, anthropic_client):
        """System prompt should bias toward tool usage."""
        prompt = "Create a trigger for errors in api-logs"
        result = call_claude_with_tools(anthropic_client, prompt)

        # With our system prompt, should make tool calls
        assert len(result["tool_calls"]) >= 1, (
            "System prompt should encourage tool use, but got conversational response"
        )
