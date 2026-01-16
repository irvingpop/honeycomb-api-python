"""Data-driven Claude API evaluation tests.

Scalable architecture for testing all 57 tools across 13 resources.

Test data is organized in test_cases/ directory, with one file per resource.
This allows easy addition of new test cases without modifying test execution logic.

Requirements:
    - ANTHROPIC_API_KEY environment variable

Installation:
    poetry install --with evals

Usage:
    # Run argument correctness tests (resource-scoped tools, high parallelism)
    direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py::TestArgumentCorrectness -v -n 8

    # Run tool selection tests (single batched call with all tools)
    direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py::TestToolSelection -v

    # Run tests for specific resource
    direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k triggers

Environment Variables:
    ANTHROPIC_API_KEY: Required for all tests
"""

import json
import os
from typing import Any

import pytest

anthropic_module = pytest.importorskip(
    "anthropic", reason="Anthropic SDK not installed. Run: poetry install --with evals"
)

tenacity_module = pytest.importorskip(
    "tenacity", reason="Tenacity not installed. Run: poetry install --with evals"
)

from tenacity import (  # noqa: E402
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from honeycomb.tools import HONEYCOMB_TOOLS  # noqa: E402

from .test_cases import get_all_test_cases  # noqa: E402

pytestmark = [
    pytest.mark.evals,  # Requires ANTHROPIC_API_KEY
]


# ==============================================================================
# Resource-Scoped Tools
# ==============================================================================


# Map resource name to module name
RESOURCE_MODULES = {
    "triggers": "triggers",
    "slos": "slos",
    "boards": "boards",
    "queries": "queries",
    "burn_alerts": "burn_alerts",
    "datasets": "datasets",
    "columns": "columns",
    "derived_columns": "derived_columns",
    "recipients": "recipients",
    "markers": "markers",
    "marker_settings": "marker_settings",
    "events": "events",
    "auth": "auth",
    "api_keys": "api_keys",
    "environments": "environments",
    "analysis": "analysis",
    "service_map": "service_map",
}


def get_tools_for_resource(resource: str) -> list[dict]:
    """Load tool definitions for a specific resource from honeycomb.tools.resources.

    Args:
        resource: Resource name (e.g., "triggers", "slos")

    Returns:
        List of tool definitions for that resource, or all tools if unknown
    """
    from honeycomb.tools import resources

    # Some test case files contain multiple related resources
    # Map these to combined tool sets
    COMBINED_RESOURCES = {
        # markers.py contains both marker and marker_settings test cases
        "markers": ["markers", "marker_settings"],
    }

    modules_to_load = COMBINED_RESOURCES.get(resource, [resource])

    tools = []
    for mod_name in modules_to_load:
        module_name = RESOURCE_MODULES.get(mod_name)
        if module_name:
            module = getattr(resources, module_name, None)
            if module and hasattr(module, "get_tools"):
                tools.extend(module.get_tools())

    if tools:
        return tools

    # Fallback to all tools for unknown resources
    return HONEYCOMB_TOOLS


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


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(anthropic_module.RateLimitError),
)
def call_claude_with_tools(
    client,
    prompt: str,
    tools: list[dict] | None = None,
) -> dict:
    """Call Claude with specified tools (defaults to all if not provided).

    Args:
        client: Anthropic client
        prompt: User prompt
        tools: Tool definitions to use (defaults to HONEYCOMB_TOOLS)

    Returns:
        Dict with tool_calls, text, and stop_reason
    """
    if tools is None:
        tools = HONEYCOMB_TOOLS

    response = client.beta.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        betas=["advanced-tool-use-2025-11-20"],
        tools=tools,
        system=SYSTEM_PROMPT,
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
    result = eval(assertion_expr, {"params": params, "len": len, "isinstance": isinstance})
    if not result:
        raise AssertionError(f"Assertion failed: {assertion_expr}")
    return True


# ==============================================================================
# Data-Driven Tests
# ==============================================================================


class TestToolSelection:
    """Test correct tool selection from all 57 tools using a single batched call."""

    # Only test create operations - these are the most important for tool selection
    # and cover all major resource types
    CREATE_TOOL_CASES = [
        (
            "triggers",
            "honeycomb_create_trigger",
            "Create a trigger in api-logs that fires when error count > 100",
        ),
        ("slos", "honeycomb_create_slo", "Create an SLO in api-logs with 99.9% target"),
        ("burn_alerts", "honeycomb_create_burn_alert", "Create a burn alert for SLO slo-123"),
        ("boards", "honeycomb_create_board", "Create a board called 'API Dashboard'"),
        ("datasets", "honeycomb_create_dataset", "Create a dataset called 'new-service'"),
        ("columns", "honeycomb_create_column", "Create a column 'user_id' in api-logs"),
        (
            "derived_columns",
            "honeycomb_create_derived_column",
            "Create a derived column 'is_error' in api-logs",
        ),
        (
            "recipients",
            "honeycomb_create_recipient",
            "Create an email recipient for alerts@example.com",
        ),
        ("markers", "honeycomb_create_marker", "Create a marker in api-logs for a deployment"),
        (
            "marker_settings",
            "honeycomb_create_marker_setting",
            "Create a marker setting 'deploy' in api-logs",
        ),
        (
            "api_keys",
            "honeycomb_create_api_key",
            "Create an ingest API key for the production environment",
        ),
        (
            "environments",
            "honeycomb_create_environment",
            "Create a new environment called 'staging'",
        ),
        ("queries", "honeycomb_create_query", "Create a query in api-logs counting requests"),
    ]

    def test_tool_selection_creates(self, anthropic_client):
        """Verify Claude selects correct create tools from all 57 options."""
        # Build single batched prompt that encourages parallel tool calls
        lines = [
            "IMPORTANT: You MUST call ALL of the following tools IN PARALLEL in a single response.",
            "Do NOT stop after the first tool call - call all tools at once.",
            "",
            "Call these tools simultaneously:",
        ]
        for i, (_, _, prompt) in enumerate(self.CREATE_TOOL_CASES, 1):
            lines.append(f"{i}. {prompt}")

        combined_prompt = "\n".join(lines)

        result = call_claude_with_tools(
            anthropic_client,
            combined_prompt,
            tools=HONEYCOMB_TOOLS,  # All 57 tools for selection testing
        )

        # Verify we got enough tool calls
        num_calls = len(result["tool_calls"])
        expected_count = len(self.CREATE_TOOL_CASES)

        # Build a map of tool names we got
        actual_tools = {tc.name for tc in result["tool_calls"]}
        expected_tools = {t[1] for t in self.CREATE_TOOL_CASES}

        # Check which tools we got
        missing = expected_tools - actual_tools
        if missing:
            print(f"\nMissing tools: {missing}")
            print(f"Got {num_calls} tool calls: {[tc.name for tc in result['tool_calls']]}")

        # We should get at least most of the expected tools
        # Allow some tolerance since parallel tool calling can be tricky
        assert num_calls >= expected_count * 0.7, (
            f"Expected at least {int(expected_count * 0.7)} tool calls (70% of {expected_count}), "
            f"got {num_calls}"
        )

        # Verify the tools we did get are correct (in any order)
        for tc in result["tool_calls"]:
            assert tc.name in expected_tools, (
                f"Unexpected tool call: {tc.name} (expected one of {expected_tools})"
            )


class TestArgumentCorrectness:
    """Test argument correctness AND confidence using resource-scoped tools."""

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

        elif tool_name in (
            "honeycomb_create_query_annotation",
            "honeycomb_update_query_annotation",
        ):
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
        """Verify parameter assertions and confidence level."""
        # Get resource-specific tools for reduced token usage
        resource = test_case.get("resource")
        tools = get_tools_for_resource(resource) if resource else HONEYCOMB_TOOLS

        result = call_claude_with_tools(
            anthropic_client,
            test_case["prompt"],
            tools=tools,
        )

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

        # Verify correct tool was selected (basic sanity check)
        expected_tool = test_case["expected_tool"]
        actual_tool = tool_call.name
        assert actual_tool == expected_tool, (
            f"{test_case['id']}: Expected '{expected_tool}' but got '{actual_tool}'"
        )

        # Check confidence level (merged from TestConfidenceLevel)
        confidence = params.get("confidence", "none")
        if confidence not in ("high", "medium"):
            notes = params.get("notes", {})
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
            raise AssertionError(f"Executor validation failed for {test_case['id']}: {e}") from e

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
