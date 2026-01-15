"""Data-driven Claude API evaluation tests.

Scalable architecture for testing all 57 tools across 13 resources.

Test data is organized in test_cases/ directory, with one file per resource.
This allows easy addition of new test cases without modifying test execution logic.

Tool call results are cached to disk to speed up repeated test runs.

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

    # Clear cache for fresh run
    rm -rf tests/integration/.tool_call_cache/

Environment Variables:
    ANTHROPIC_API_KEY: Required for all tests
    EVAL_USE_CACHE: Use cached results (default: true)
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pytest

anthropic_module = pytest.importorskip(
    "anthropic", reason="Anthropic SDK not installed. Run: poetry install --with evals"
)

from honeycomb.tools import HONEYCOMB_TOOLS  # noqa: E402

from .test_cases import get_all_test_cases  # noqa: E402

pytestmark = [
    pytest.mark.evals,  # Requires ANTHROPIC_API_KEY
]


# ==============================================================================
# Tool Call Caching
# ==============================================================================


CACHE_DIR = Path(__file__).parent / ".tool_call_cache"


def get_cache_key(prompt: str) -> str:
    """Generate a cache key for a prompt."""
    return hashlib.sha256(prompt.encode()).hexdigest()


class CachedToolCall:
    """Wrapper to match Anthropic tool call interface."""

    def __init__(self, name: str, input_params: dict):
        self.name = name
        self.input = input_params


def load_cached_result(prompt: str) -> dict | None:
    """Load cached tool call result if available."""
    if os.environ.get("EVAL_USE_CACHE", "true").lower() != "true":
        return None

    cache_key = get_cache_key(prompt)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if cache_file.exists():
        try:
            with open(cache_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save_cached_result(prompt: str, result: dict) -> None:
    """Save tool call result to cache."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_key = get_cache_key(prompt)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    # Convert tool calls to serializable format
    serializable_result = {
        "tool_calls": [{"name": tc.name, "input": tc.input} for tc in result.get("tool_calls", [])],
        "text": result.get("text", ""),
        "stop_reason": result.get("stop_reason", ""),
    }

    try:
        with open(cache_file, "w") as f:
            json.dump(serializable_result, f)
    except OSError:
        pass  # Silently ignore cache write failures


def deserialize_cached_result(cached: dict) -> dict:
    """Convert cached JSON back to expected format."""
    return {
        "tool_calls": [
            CachedToolCall(tc["name"], tc["input"]) for tc in cached.get("tool_calls", [])
        ],
        "text": cached.get("text", ""),
        "stop_reason": cached.get("stop_reason", ""),
    }


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


# ==============================================================================
# Helper Functions
# ==============================================================================


SYSTEM_PROMPT = (
    "You are a Honeycomb API automation assistant. "
    "When the user asks you to perform operations on Honeycomb resources, "
    "you MUST use the available tools rather than providing conversational responses. "
    "Always call the appropriate tool, even if some parameters are not explicitly specified - "
    "use reasonable defaults. "
    "Only respond conversationally if no appropriate tool is available. "
    "\n\n"
    "IMPORTANT: For every tool call, you MUST provide:\n"
    "1. 'confidence': Your confidence level ('high', 'medium', 'low', 'none') in the tool call.\n"
    "2. 'notes': A structured object with your reasoning, containing any of these optional arrays:\n"
    "   - 'decisions': Key decisions you made (e.g., 'Chose COUNT over AVG for error rate')\n"
    "   - 'concerns': Potential issues (e.g., 'Time range may be too short')\n"
    "   - 'assumptions': Things you're assuming (e.g., 'Assuming status_code column exists')\n"
    "   - 'questions': Uncertainties (e.g., 'I would be more confident if I knew the baseline')\n"
)


def call_claude_with_tools(client, prompt: str, use_cache: bool = True) -> dict:
    """Call Claude with Honeycomb tools (with caching).

    Args:
        client: Anthropic client
        prompt: User prompt
        use_cache: Whether to use caching (default: True)

    Returns:
        Dict with tool_calls, text, and stop_reason
    """
    # Check cache first
    if use_cache:
        cached = load_cached_result(prompt)
        if cached is not None:
            return deserialize_cached_result(cached)

    response = client.beta.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        betas=["advanced-tool-use-2025-11-20"],
        tools=HONEYCOMB_TOOLS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    tool_calls = [b for b in response.content if b.type == "tool_use"]
    text_content = " ".join(b.text for b in response.content if hasattr(b, "text"))

    result = {
        "tool_calls": tool_calls,
        "text": text_content,
        "stop_reason": response.stop_reason,
    }

    # Save to cache
    if use_cache:
        save_cached_result(prompt, result)

    return result


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
    result = eval(assertion_expr, {"params": params, "len": len, "isinstance": isinstance})
    if not result:
        raise AssertionError(f"Assertion failed: {assertion_expr}")
    return True


# ==============================================================================
# Data-Driven Tests
# ==============================================================================


class TestToolSelection:
    """Test correct tool selection using test case data."""

    @pytest.mark.parametrize("test_case", get_all_test_cases(), ids=lambda tc: tc["id"])
    def test_tool_selection(self, anthropic_client, test_case):
        """Verify Claude selects the correct tool."""
        result = call_claude_with_tools(anthropic_client, test_case["prompt"])

        # Verify tool was called
        assert len(result["tool_calls"]) >= 1, f"No tool calls for: {test_case['description']}"

        # Verify correct tool selected
        actual_tool = result["tool_calls"][0].name
        expected_tool = test_case["expected_tool"]
        assert actual_tool == expected_tool, (
            f"{test_case['id']}: Expected '{expected_tool}' but got '{actual_tool}'"
        )


class TestArgumentCorrectness:
    """Test argument correctness using test case data."""

    def _validate_via_executor(self, tool_name: str, tool_input: dict[str, Any]) -> None:
        """Validate tool params using the same logic as the executor.

        This mirrors the executor's validation flow without making API calls.
        Raises ValidationError or other exceptions if params are invalid.

        By calling the same builder functions and model constructors that the
        executor uses, we ensure our tests validate exactly what production validates.
        """
        # Import all validation dependencies (same as executor uses)
        from honeycomb.models import (
            ColumnCreate,
            DerivedColumnCreate,
            MarkerCreate,
            MarkerSettingCreate,
            QueryAnnotationCreate,
        )
        from honeycomb.models.datasets import DatasetCreate, DatasetUpdate

        # Strip metadata fields (executor does this via strip_metadata_fields)
        params = {k: v for k, v in tool_input.items() if k not in ("confidence", "notes")}

        # Route to appropriate validator - mirrors executor routing
        # Triggers/SLOs/Boards - use builders (they validate internally)
        if tool_name in ("honeycomb_create_trigger", "honeycomb_update_trigger"):
            from honeycomb.tools.builders import _build_trigger
            _build_trigger(params)  # Validates via TriggerToolInput.model_validate()

        elif tool_name in ("honeycomb_create_slo", "honeycomb_update_slo"):
            from honeycomb.tools.builders import _build_slo
            _build_slo(params)  # Validates via SLOToolInput.model_validate()

        elif tool_name in ("honeycomb_create_board", "honeycomb_update_board"):
            from honeycomb.tools.builders import _build_board
            _build_board(params)  # Validates via BoardToolInput.model_validate()

        # Recipients - use get_recipient_class to get the right discriminated union class
        elif tool_name in ("honeycomb_create_recipient", "honeycomb_update_recipient"):
            from honeycomb.models.recipients import get_recipient_class
            params_copy = params.copy()
            params_copy.pop("recipient_id", None)  # Routing param for update
            recipient_class = get_recipient_class(params_copy["type"])
            recipient_class(**params_copy)  # Validates via Pydantic __init__

        # Direct model instantiation (validates via Pydantic __init__)
        elif tool_name == "honeycomb_create_dataset":
            DatasetCreate(**params)

        elif tool_name == "honeycomb_update_dataset":
            params_copy = params.copy()
            params_copy.pop("slug", None)  # Routing param, not model field
            DatasetUpdate(**params_copy)

        elif tool_name in ("honeycomb_create_column", "honeycomb_update_column"):
            params_copy = params.copy()
            params_copy.pop("dataset", None)
            params_copy.pop("column_id", None)
            ColumnCreate(**params_copy)

        elif tool_name in ("honeycomb_create_derived_column", "honeycomb_update_derived_column"):
            params_copy = params.copy()
            params_copy.pop("dataset", None)
            params_copy.pop("derived_column_id", None)
            DerivedColumnCreate(**params_copy)

        elif tool_name in ("honeycomb_create_marker", "honeycomb_update_marker"):
            params_copy = params.copy()
            params_copy.pop("dataset", None)
            params_copy.pop("marker_id", None)
            MarkerCreate(**params_copy)

        elif tool_name in ("honeycomb_create_marker_setting", "honeycomb_update_marker_setting"):
            params_copy = params.copy()
            params_copy.pop("dataset", None)
            params_copy.pop("setting_id", None)
            MarkerSettingCreate(**params_copy)

        elif tool_name in ("honeycomb_create_query_annotation", "honeycomb_update_query_annotation"):
            params_copy = params.copy()
            params_copy.pop("dataset", None)
            params_copy.pop("annotation_id", None)
            QueryAnnotationCreate(**params_copy)

        # Queries - direct QuerySpec instantiation (see executor.py:893, 915)
        elif tool_name in ("honeycomb_create_query", "honeycomb_run_query"):
            from honeycomb.models.queries import QuerySpec
            params_copy = params.copy()
            params_copy.pop("dataset", None)
            params_copy.pop("annotation_name", None)  # Not supported yet, executor removes it
            QuerySpec(**params_copy)  # Validates

        # Skip validation for:
        # - List/get/delete operations (no complex validation needed)
        # - Environments/API keys (v2 JSON:API wrappers - executor uses convenience params)
        # - Burn alerts (nested structure - executor converts flat to nested)

    @pytest.mark.parametrize("test_case", get_all_test_cases(), ids=lambda tc: tc["id"])
    def test_argument_assertions(self, anthropic_client, test_case):
        """Verify parameter assertions."""
        result = call_claude_with_tools(anthropic_client, test_case["prompt"])

        if len(result["tool_calls"]) < 1:
            # Print debug info when no tool calls made
            print("\n" + "=" * 80)
            print(f"NO TOOL CALLS MADE: {test_case['id']}")
            print("=" * 80)
            print(f"\nPROMPT:\n{test_case['prompt']}\n")
            print(f"CLAUDE'S RESPONSE:\n{result['text']}\n")
            print(f"STOP REASON: {result['stop_reason']}\n")
            print("=" * 80 + "\n")
            raise AssertionError(f"No tool calls for: {test_case['description']}")

        tool_call = result["tool_calls"][0]
        params = tool_call.input

        # Skip parameter validation for parameter-less operations
        expected_params = test_case.get("expected_params", {})
        if expected_params is None or expected_params == {}:
            # For parameter-less operations, only verify tool selection (already done above)
            return

        # VALIDATE PARAMS using executor's validation logic
        # This ensures params would pass the same validation as production
        try:
            self._validate_via_executor(tool_call.name, params)
        except Exception as e:
            # Validation failed - print debug info
            from pydantic import ValidationError
            print("\n" + "=" * 80)
            print(f"EXECUTOR VALIDATION FAILED: {test_case['id']}")
            print("=" * 80)
            print(f"\nPROMPT:\n{test_case['prompt']}\n")
            print(f"CLAUDE'S OUTPUT:\n{result['text']}\n")
            print(f"TOOL: {tool_call.name}")
            print(f"RAW PARAMS: {params}\n")
            if isinstance(e, ValidationError):
                print(f"VALIDATION ERRORS:\n{e}\n")
            else:
                print(f"ERROR: {e}\n")
            print("=" * 80 + "\n")
            raise AssertionError(
                f"Executor validation failed for {test_case['id']}: {e}"
            ) from e

        # Check expected parameters (partial match)
        try:
            for key, expected_value in expected_params.items():
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
        except AssertionError:
            # On failure, print detailed debug information
            print("\n" + "=" * 80)
            print(f"TEST FAILURE: {test_case['id']}")
            print("=" * 80)
            print(f"\nPROMPT:\n{test_case['prompt']}\n")
            print(f"CLAUDE'S REASONING:\n{result['text']}\n")
            print(f"TOOL CALLED: {tool_call.name}\n")
            print(f"TOOL PARAMETERS:\n{json.dumps(params, indent=2)}\n")
            print("=" * 80 + "\n")
            raise


# ==============================================================================
# Confidence Validation Tests
# ==============================================================================


class TestConfidenceLevel:
    """Test that Claude provides adequate confidence for all tool calls."""

    @pytest.mark.parametrize("test_case", get_all_test_cases(), ids=lambda tc: tc["id"])
    def test_confidence_is_medium_or_higher(self, anthropic_client, test_case):
        """Verify Claude provides 'medium' or 'high' confidence for tool calls.

        If confidence is missing, it defaults to 'none' which fails the test.
        When confidence is too low, the test outputs the notes for debugging.
        """
        result = call_claude_with_tools(anthropic_client, test_case["prompt"])

        if len(result["tool_calls"]) < 1:
            pytest.skip(f"No tool calls made for: {test_case['description']}")

        tool_call = result["tool_calls"][0]
        params = tool_call.input

        # Extract confidence (default to "none" if missing)
        confidence = params.get("confidence", "none")
        notes = params.get("notes", {})

        # Confidence must be "high" or "medium" to pass
        if confidence not in ("high", "medium"):
            print("\n" + "=" * 80)
            print(f"LOW CONFIDENCE: {test_case['id']}")
            print("=" * 80)
            print(f"\nCONFIDENCE: {confidence}")
            print("\nNOTES:")
            print(json.dumps(notes, indent=2))
            print(f"\nPROMPT:\n{test_case['prompt']}\n")
            print(f"CLAUDE'S REASONING:\n{result['text']}\n")
            print(f"TOOL CALLED: {tool_call.name}")
            print("=" * 80 + "\n")
            raise AssertionError(
                f"Confidence '{confidence}' is below 'medium' threshold for {test_case['id']}"
            )


# ==============================================================================
# Schema Validation Tests
# ==============================================================================


class TestToolSchemas:
    """Validate tool schemas are accepted by Claude API."""

    def test_all_tools_accepted(self, anthropic_client):
        """Claude should parse all tool definitions without error."""
        result = call_claude_with_tools(anthropic_client, "What tools do you have?")
        # max_tokens is acceptable - means tools were accepted, response was just truncated
        assert result["stop_reason"] in ("end_turn", "tool_use", "max_tokens")

    def test_system_prompt_encourages_tool_use(self, anthropic_client):
        """System prompt should bias toward tool usage."""
        prompt = "Create a trigger for errors in api-logs"
        result = call_claude_with_tools(anthropic_client, prompt)

        # With our system prompt, should make tool calls
        assert len(result["tool_calls"]) >= 1, (
            "System prompt should encourage tool use, but got conversational response"
        )
