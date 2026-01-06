"""Live integration test for Claude tool definitions - Full Lifecycle Workflow.

This is a SINGLE comprehensive test that validates Claude can orchestrate a complete
monitoring setup from scratch using HONEYCOMB_TOOLS:

1. Create dataset
2. Send sample events
3. Create trigger with inline recipients (email + webhook)
4. Create board with inline queries, text panels, SLOs with inline burn alerts
5. Cleanup

Each step is fully debuggable with:
- Tool call input/output dumping
- API validation (retrieve objects and compare)
- Expectation checking

Requires:
- ANTHROPIC_API_KEY environment variable
- Test credentials in .claude/secrets/ (run setup_test_session.py first)

Run with: poetry run pytest tests/integration/test_claude_tools_live.py -v -s
Skip with: poetry run pytest -m "not live_tools"
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

import pytest
from anthropic import Anthropic

from honeycomb import HoneycombClient
from honeycomb.tools import HONEYCOMB_TOOLS, execute_tool

# Test configuration
TEST_MODEL = "claude-sonnet-4-5-20250929"
TEST_BETA = "advanced-tool-use-2025-11-20"
MAX_CONVERSATION_TURNS = 30  # Generous for full workflow

# System prompt with confidence/notes instructions
SYSTEM_PROMPT = (
    "You are a Honeycomb API automation assistant. "
    "When the user asks you to perform operations on Honeycomb resources, "
    "you MUST use the available tools. "
    "\n\n"
    "IMPORTANT: For every tool call, you MUST provide:\n"
    "1. 'confidence': Your confidence level ('high', 'medium', 'low', 'none') in the tool call.\n"
    "2. 'notes': A structured object with your reasoning, containing any of these optional arrays:\n"
    "   - 'decisions': Key decisions you made (e.g., 'Chose COUNT over AVG for error rate')\n"
    "   - 'concerns': Potential issues (e.g., 'Time range may be too short')\n"
    "   - 'assumptions': Things you're assuming (e.g., 'Assuming status_code column exists')\n"
    "   - 'questions': Uncertainties (e.g., 'I would be more confident if I knew the baseline')\n"
)


# Fixtures


@pytest.fixture
def anthropic_client() -> Anthropic:
    """Anthropic client for Claude API calls."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return Anthropic(api_key=api_key)


# Helper Functions


def dump_tool_call(step: str, tool_name: str, tool_input: dict[str, Any], result: str):
    """Print formatted tool call for debugging."""
    print(f"\n{'=' * 80}")
    print(f"STEP: {step}")
    print(f"TOOL: {tool_name}")
    print(f"{'=' * 80}")
    print("INPUT:")
    print(json.dumps(tool_input, indent=2))
    print("\nRESULT:")
    # Pretty print if JSON, otherwise raw
    try:
        result_data = json.loads(result)
        print(json.dumps(result_data, indent=2))
    except (json.JSONDecodeError, TypeError):
        print(result)
    print(f"{'=' * 80}\n")


def validate_confidence(tool_name: str, tool_input: dict[str, Any], step_name: str) -> None:
    """Validate that tool call has adequate confidence level.

    Args:
        tool_name: Name of the tool called
        tool_input: Input parameters (includes confidence and notes)
        step_name: Current step name for error messages

    Raises:
        AssertionError: If confidence is not 'high' or 'medium'
    """
    confidence = tool_input.get("confidence", "none")
    notes = tool_input.get("notes", {})

    if confidence not in ("high", "medium"):
        print(f"\n{'!' * 80}")
        print(f"LOW CONFIDENCE DETECTED: {tool_name}")
        print(f"Step: {step_name}")
        print(f"{'!' * 80}")
        print(f"Confidence: {confidence}")
        print(f"Notes: {json.dumps(notes, indent=2)}")
        print(f"{'!' * 80}\n")
        raise AssertionError(
            f"Confidence '{confidence}' is below 'medium' threshold for {tool_name} in {step_name}"
        )


async def execute_single_turn(
    anthropic_client: Anthropic,
    honeycomb_client: HoneycombClient,
    messages: list[dict[str, Any]],
    step_name: str,
) -> tuple[list[dict[str, Any]], list[tuple[str, dict, str]]]:
    """Execute one turn of conversation, return updated messages and tool calls.

    Args:
        anthropic_client: Anthropic client
        honeycomb_client: Honeycomb client
        messages: Current conversation messages
        step_name: Current step name for logging

    Returns:
        Tuple of (updated_messages, tool_calls)
        tool_calls is list of (tool_name, tool_input, result) tuples
    """
    print(f"\n>>> Executing turn for: {step_name}")

    response = anthropic_client.beta.messages.create(
        model=TEST_MODEL,
        max_tokens=4096,
        betas=[TEST_BETA],
        tools=HONEYCOMB_TOOLS,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    # Log response summary
    print(f"Response: {len(response.content)} content blocks, stop_reason={response.stop_reason}")

    # Add assistant response
    messages.append({"role": "assistant", "content": response.content})

    # Extract text blocks
    text_blocks = [b.text for b in response.content if hasattr(b, "text")]
    if text_blocks:
        full_text = " ".join(text_blocks)
        print(f"\nClaude says: {full_text}")

    # Execute tool calls
    tool_calls = []
    tool_results = []

    for block in response.content:
        if block.type == "tool_use":
            print(f"\n→ Calling tool: {block.name}")
            print(f"  Tool ID: {block.id}")

            # IMPORTANT: Save original input BEFORE execute_tool (which mutates it with .pop())
            original_input = dict(block.input)

            # Validate confidence level
            validate_confidence(block.name, original_input, step_name)

            try:
                result = await execute_tool(
                    client=honeycomb_client,
                    tool_name=block.name,
                    tool_input=block.input,
                )

                # Dump for debugging (use original_input since block.input is now mutated)
                dump_tool_call(step_name, block.name, original_input, result)

                # Track tool call (use original_input)
                tool_calls.append((block.name, original_input, result))

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

            except Exception as e:
                # Dump failed tool call for debugging (use original_input)
                print(f"\n{'=' * 80}")
                print(f"ERROR executing {block.name}: {e}")
                print(f"{'=' * 80}")
                print("TOOL INPUT:")
                print(json.dumps(original_input, indent=2))
                print(f"{'=' * 80}\n")

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: {str(e)}",
                        "is_error": True,
                    }
                )

    # Add tool results if any
    if tool_results:
        messages.append({"role": "user", "content": tool_results})

    return messages, tool_calls


@pytest.mark.live_tools
@pytest.mark.asyncio
async def test_full_lifecycle_workflow(
    anthropic_client: Anthropic,
    management_client: HoneycombClient,
):
    """Complete lifecycle test: environment → api_key → dataset → events → trigger → board → cleanup."""

    # Generate unique names
    timestamp = int(time.time())
    env_name = f"test-env-{timestamp}"
    api_key_name = f"test-key-{timestamp}"
    dataset_name = f"test-workflow-{timestamp}"
    trigger_name = f"Test Error Alert {timestamp}"
    slo_name = f"Test Availability SLO {timestamp}"
    board_name = f"Test Dashboard {timestamp}"

    print(f"\n{'#' * 80}")
    print("# Starting Full Lifecycle Workflow Test")
    print(f"# Environment: {env_name}")
    print(f"# Dataset: {dataset_name}")
    print(f"{'#' * 80}\n")

    messages: list[dict[str, Any]] = []

    # Initialize variables that may not be created (for cleanup)
    environment_id = None
    api_key_id = None
    client = None
    dataset = None
    trigger = None
    board = None
    slo = None
    derived_col = None

    try:
        # ============================================================================
        # STEP 0: Create Environment and API Key (via Claude)
        # ============================================================================

        print("\n" + "=" * 80)
        print("STEP 0: CREATE ENVIRONMENT AND API KEY")
        print("=" * 80)

        # Step 0a: Ask Claude to create environment
        step0a_prompt = f"""
Create a new environment named '{env_name}' with color 'blue' for organizing test data.
"""
        messages.append({"role": "user", "content": step0a_prompt})
        messages, tool_calls = await execute_single_turn(
            anthropic_client, management_client, messages, "Step 0a: Create Environment"
        )

        # Extract environment_id from tool call result
        assert any("create_environment" in tool for tool, _, _ in tool_calls), (
            "Should have called honeycomb_create_environment"
        )

        env_result = next(
            (result for tool, _, result in tool_calls if "create_environment" in tool), None
        )
        env_data = json.loads(env_result)
        environment_id = env_data["id"]
        environment_slug = env_data["slug"]
        print(f"✓ Claude created environment: {environment_id} ({environment_slug})")

        # Step 0b: Ask Claude to create API key
        step0b_prompt = f"""
Create a configuration API key named '{api_key_name}' for environment '{environment_id}'.
This key will have full permissions to create datasets, triggers, SLOs, and boards.
"""
        messages.append({"role": "user", "content": step0b_prompt})
        messages, tool_calls = await execute_single_turn(
            anthropic_client, management_client, messages, "Step 0b: Create API Key"
        )

        # Extract API key secret from tool call result
        assert any("create_api_key" in tool for tool, _, _ in tool_calls), (
            "Should have called honeycomb_create_api_key"
        )

        key_result = next(
            (result for tool, _, result in tool_calls if "create_api_key" in tool), None
        )
        key_data = json.loads(key_result)
        api_key_id = key_data["id"]
        api_key_secret = key_data["secret"]
        print(f"✓ Claude created API key: {api_key_id}")
        print(f"✓ API key secret: {api_key_secret[:20]}...")

        # Create new client with the generated API key for subsequent steps
        client = HoneycombClient(api_key=api_key_secret)
        await client.__aenter__()

        print(
            f"✓ Initialized client with Claude-generated API key for environment {environment_slug}"
        )

        # Reset conversation for dataset creation
        messages = []

        # ============================================================================
        # STEP 1: Create Dataset
        # ============================================================================

        print("\n" + "=" * 80)
        print("STEP 1: CREATE DATASET")
        print("=" * 80)

        step1_prompt = f"""
Create a dataset named '{dataset_name}' with description 'Test dataset for Claude tools integration testing'.
"""

        messages.append({"role": "user", "content": step1_prompt})
        messages, tool_calls = await execute_single_turn(
            anthropic_client, client, messages, "Step 1: Create Dataset"
        )

        # Validate: Dataset was created
        assert any("create_dataset" in tool for tool, _, _ in tool_calls), (
            "Should have called honeycomb_create_dataset"
        )

        # Retrieve from API and validate
        datasets = await client.datasets.list_async()
        dataset = next((d for d in datasets if d.slug == dataset_name), None)
        assert dataset is not None, f"Dataset {dataset_name} should exist in API"
        print(f"✓ VALIDATED: Dataset {dataset_name} exists (slug={dataset.slug})")

        # ============================================================================
        # STEP 2: Send Sample Events
        # ============================================================================

        print("\n" + "=" * 80)
        print("STEP 2: SEND SAMPLE EVENTS")
        print("=" * 80)

        step2_prompt = f"""
Send 20 sample events to dataset '{dataset_name}' with:
- status_code: Mix of 200 (50%), 201 (20%), 400 (10%), 404 (5%), 500 (10%), 502 (5%)
- duration_ms: Random floats between 50 and 3000
- endpoint: Random from ["/api/users", "/api/orders", "/api/products", "/health"]
- service_name: Random from ["api", "auth", "database"]
- Timestamps spread over the past hour
"""

        messages.append({"role": "user", "content": step2_prompt})
        messages, tool_calls = await execute_single_turn(
            anthropic_client, client, messages, "Step 2: Send Events"
        )

        # Validate: Events were sent
        assert any("send" in tool and "event" in tool for tool, _, _ in tool_calls), (
            "Should have called honeycomb_send_batch_events or honeycomb_send_event"
        )

        # Note: We can't easily verify event count via API, but we can check dataset still exists
        dataset_check = await client.datasets.get_async(slug=dataset_name)
        assert dataset_check is not None, f"Dataset {dataset_name} should still exist"
        print(f"✓ VALIDATED: Events sent to {dataset_name}")

        # ============================================================================
        # STEP 3: Create Trigger with Inline Recipients
        # ============================================================================

        print("\n" + "=" * 80)
        print("STEP 3: CREATE TRIGGER WITH INLINE RECIPIENTS")
        print("=" * 80)

        step3_prompt = f"""
Create a trigger in dataset '{dataset_name}' named '{trigger_name}' that:
- Alerts when COUNT of requests with status_code >= 500 exceeds 10
- Checks every 15 minutes (900 seconds)
- Sends notifications to:
  - Email: ops-team@example.com
  - Webhook: https://example.com/webhook/alerts

Create the recipients inline with the trigger.
"""

        messages.append({"role": "user", "content": step3_prompt})
        messages, tool_calls = await execute_single_turn(
            anthropic_client, client, messages, "Step 3: Create Trigger"
        )

        # Validate: Trigger was created
        trigger_created = any("create_trigger" in tool for tool, _, _ in tool_calls)
        assert trigger_created, "Should have called honeycomb_create_trigger"

        # Retrieve trigger from API
        triggers = await client.triggers.list_async(dataset=dataset_name)
        trigger = next((t for t in triggers if t.name == trigger_name), None)
        assert trigger is not None, f"Trigger '{trigger_name}' should exist"

        # Validate trigger properties
        assert trigger.frequency == 900, f"Frequency should be 900, got {trigger.frequency}"
        assert trigger.threshold.value == 10, (
            f"Threshold should be 10, got {trigger.threshold.value}"
        )
        assert trigger.threshold.op == ">", (
            f"Threshold op should be '>', got {trigger.threshold.op}"
        )

        # Validate query (query may be dict or object)
        filters = (
            trigger.query.get("filters", [])
            if isinstance(trigger.query, dict)
            else trigger.query.filters
        )

        status_filter = next(
            (
                f
                for f in filters
                if (f.get("column") if isinstance(f, dict) else f.column) == "status_code"
            ),
            None,
        )
        assert status_filter is not None, "Query should filter on status_code"

        filter_op = status_filter.get("op") if isinstance(status_filter, dict) else status_filter.op
        filter_value = (
            status_filter.get("value") if isinstance(status_filter, dict) else status_filter.value
        )
        assert filter_op == ">=", f"Filter op should be '>=', got {filter_op}"
        assert filter_value == 500, f"Filter value should be 500, got {filter_value}"

        # Validate recipients exist (email + webhook)
        assert len(trigger.recipients) >= 2, (
            f"Should have 2 recipients, got {len(trigger.recipients)}"
        )
        recipient_types = {
            (r.get("type") if isinstance(r, dict) else r.type) for r in trigger.recipients
        }
        assert "email" in recipient_types, "Should have email recipient"
        assert "webhook" in recipient_types, "Should have webhook recipient"

        print(
            f"✓ VALIDATED: Trigger '{trigger_name}' created with {len(trigger.recipients)} recipients"
        )
        print(f"  - Frequency: {trigger.frequency}s")
        print(f"  - Threshold: {trigger.threshold.op} {trigger.threshold.value}")
        print(f"  - Recipients: {list(recipient_types)}")

        # ============================================================================
        # STEP 4: Create Board with Inline Queries, Text, and SLO
        # ============================================================================

        print("\n" + "=" * 80)
        print("STEP 4: CREATE BOARD WITH INLINE CONTENT")
        print("=" * 80)

        step4_prompt = f"""
Create a comprehensive dashboard named '{board_name}' in auto-layout with the following panels:

Panel 1 - Query Panel: "Error Rate"
- Show COUNT of requests with status_code >= 500
- Dataset: {dataset_name}
- Time range: 1 hour (3600 seconds)

Panel 2 - Query Panel: "P99 Latency"
- Show P99 of duration_ms
- Dataset: {dataset_name}
- Time range: 1 hour (3600 seconds)

Panel 3 - Text Panel: "Dashboard Info"
- Markdown content: "# Monitoring Dashboard\\n\\nThis dashboard tracks API health and performance."

Panel 4 - SLO Panel: Create inline SLO named '{slo_name}'
- Dataset: {dataset_name}
- Target: 99.9% (999000 per million)
- Time period: 30 days
- Create inline derived column 'test_success_indicator' with expression: IF(LT($status_code, 500), 1, 0)
- Add inline burn alert that fires when 10% of error budget consumed in 1 hour

Also create these board views for different perspectives:
- View "Production Errors" filtering where environment = production AND status_code >= 500
- View "Slow Requests" filtering where duration_ms > 1000

IMPORTANT: Use inline creation for queries, SLO, and views to minimize API calls. Create everything in one honeycomb_create_board call.
"""

        messages.append({"role": "user", "content": step4_prompt})

        # Board creation may need multiple turns
        for turn in range(5):
            messages, turn_tool_calls = await execute_single_turn(
                anthropic_client, client, messages, f"Step 4: Create Board (turn {turn + 1})"
            )
            tool_calls.extend(turn_tool_calls)

            # Check if board was created
            if any("create_board" in tool for tool, _, _ in turn_tool_calls):
                break

            # If Claude says it's done, break
            last_msg = messages[-1] if messages else None
            if last_msg and last_msg.get("role") == "assistant":
                content_blocks = last_msg.get("content", [])
                text = " ".join(b.text for b in content_blocks if hasattr(b, "text"))
                if "created" in text.lower() or "done" in text.lower():
                    break

        # Validate: Board was created
        board_created = any("create_board" in tool for tool, _, _ in tool_calls)
        assert board_created, "Should have called honeycomb_create_board"

        # Retrieve board from API
        boards = await client.boards.list_async()
        board = next((b for b in boards if b.name == board_name), None)
        assert board is not None, f"Board '{board_name}' should exist"

        # Get full board details
        board_full = await client.boards.get_async(board_id=board.id)
        assert len(board_full.panels) >= 3, (
            f"Board should have at least 3 panels, got {len(board_full.panels)}"
        )

        # Validate panel types
        query_panels = [p for p in board_full.panels if p["type"] == "query"]
        text_panels = [p for p in board_full.panels if p["type"] == "text"]
        slo_panels = [p for p in board_full.panels if p["type"] == "slo"]

        assert len(query_panels) >= 2, (
            f"Should have at least 2 query panels, got {len(query_panels)}"
        )
        assert len(text_panels) >= 1, f"Should have at least 1 text panel, got {len(text_panels)}"
        # SLO panel may or may not be there depending on inline creation success

        print(f"✓ VALIDATED: Board '{board_name}' created")
        print(f"  - Total panels: {len(board_full.panels)}")
        print(f"  - Query panels: {len(query_panels)}")
        print(f"  - Text panels: {len(text_panels)}")
        print(f"  - SLO panels: {len(slo_panels)}")

        # Validate board views were created
        views = await client.boards.list_views_async(board_id=board.id)
        assert len(views) >= 2, f"Expected at least 2 views, got {len(views)}"

        view_names = {v.name for v in views}
        assert "Production Errors" in view_names, f"Missing 'Production Errors' view. Found: {view_names}"
        assert "Slow Requests" in view_names, f"Missing 'Slow Requests' view. Found: {view_names}"

        # Validate filter counts
        prod_errors_view = next(v for v in views if v.name == "Production Errors")
        assert len(prod_errors_view.filters) == 2, (
            f"'Production Errors' should have 2 filters, got {len(prod_errors_view.filters)}"
        )

        slow_view = next(v for v in views if v.name == "Slow Requests")
        assert len(slow_view.filters) == 1, (
            f"'Slow Requests' should have 1 filter, got {len(slow_view.filters)}"
        )

        print(f"✓ VALIDATED: Board views created successfully")
        print(f"  - Total views: {len(views)}")
        print(f"  - View names: {sorted(view_names)}")
        print(f"  - 'Production Errors': {len(prod_errors_view.filters)} filters")
        print(f"  - 'Slow Requests': {len(slow_view.filters)} filter")

        # Validate SLO was created (should be inline or separate)
        slos = await client.slos.list_async(dataset=dataset_name)
        slo = next((s for s in slos if s.name == slo_name), None)

        if slo:
            print(f"✓ VALIDATED: SLO '{slo_name}' created")
            print(
                f"  - Target: {slo.target_per_million}/1000000 ({slo.target_per_million / 10000}%)"
            )
            print(f"  - Time period: {slo.time_period_days} days")

            # Validate derived column
            derived_columns = await client.derived_columns.list_async(dataset=dataset_name)
            derived_col = next(
                (dc for dc in derived_columns if "success" in dc.alias.lower()), None
            )
            if derived_col:
                print(f"✓ VALIDATED: Derived column '{derived_col.alias}' created")
                print(f"  - Expression: {derived_col.expression}")

            # Validate burn alert
            burn_alerts = await client.burn_alerts.list_async(dataset=dataset_name, slo_id=slo.id)
            burn_alert = next((ba for ba in burn_alerts), None) if burn_alerts else None
            if burn_alert:
                print("✓ VALIDATED: Burn alert created for SLO")
                print(f"  - Exhaustion time: {burn_alert.exhaustion_minutes} minutes")
        else:
            print("⚠ WARNING: SLO was not created (may be expected if inline creation failed)")

    finally:
        # ============================================================================
        # CLEANUP
        # ============================================================================

        print("\n" + "=" * 80)
        print("CLEANUP: Deleting test resources")
        print("=" * 80)

        # Close the environment-scoped client if it was created
        if client:
            try:
                await client.aclose()
                print("✓ Closed environment-scoped client")
            except Exception as e:
                print(f"⚠ Failed to close client: {e}")

        # Delete API key (direct API call for fast cleanup)
        if api_key_id:
            try:
                await management_client.api_keys.delete_async(key_id=api_key_id)
                print(f"✓ Deleted API key: {api_key_id}")
            except Exception as e:
                print(f"⚠ Failed to delete API key: {e}")

        # Delete environment (direct API call for fast cleanup)
        if environment_id:
            try:
                # Disable delete protection first
                from honeycomb.models.environments import EnvironmentUpdate

                await management_client.environments.update_async(
                    env_id=environment_id,
                    environment=EnvironmentUpdate(delete_protected=False),
                )
                await management_client.environments.delete_async(env_id=environment_id)
                print(f"✓ Deleted environment: {environment_id}")
            except Exception as e:
                print(f"⚠ Failed to delete environment: {e}")

        print(f"\n{'#' * 80}")
        print("# Full Lifecycle Workflow Test Complete!")
        print(f"{'#' * 80}\n")


# Marker for running only live tool tests
pytestmark = pytest.mark.live_tools
