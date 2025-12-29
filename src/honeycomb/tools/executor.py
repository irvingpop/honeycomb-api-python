"""Tool execution handler for Claude API tool calls.

This module executes Claude tool calls against the Honeycomb API,
converting tool inputs to API operations and returning JSON results.
"""

import json
from typing import TYPE_CHECKING, Any

from honeycomb.models import (
    BatchEvent,
    BurnAlertCreate,
    BurnAlertRecipient,
    ColumnCreate,
    DatasetCreate,
    DerivedColumnCreate,
    MarkerCreate,
    MarkerSettingCreate,
    QuerySpec,
    RecipientCreate,
    ServiceMapDependencyRequestCreate,
    SLOCreate,
)
from honeycomb.tools.builders import _build_board, _build_slo, _build_trigger

if TYPE_CHECKING:
    from honeycomb import HoneycombClient


# ==============================================================================
# Main Executor
# ==============================================================================


async def execute_tool(
    client: "HoneycombClient",
    tool_name: str,
    tool_input: dict[str, Any],
) -> str:
    """Execute a Honeycomb tool and return the result as JSON string.

    Args:
        client: HoneycombClient instance (must be async-capable)
        tool_name: Name of the tool to execute (e.g., "honeycomb_create_trigger")
        tool_input: Tool input parameters as dict

    Returns:
        JSON-serialized result string

    Raises:
        ValueError: If tool name is unknown
        HoneycombAPIError: If API call fails

    Example:
        >>> from honeycomb import HoneycombClient
        >>> from honeycomb.tools import execute_tool
        >>>
        >>> async with HoneycombClient(api_key="...") as client:
        ...     result = await execute_tool(
        ...         client,
        ...         "honeycomb_list_triggers",
        ...         {"dataset": "api-logs"}
        ...     )
        ...     print(result)  # JSON string
    """
    # Route to appropriate handler
    if tool_name == "honeycomb_list_triggers":
        return await _execute_list_triggers(client, tool_input)
    elif tool_name == "honeycomb_get_trigger":
        return await _execute_get_trigger(client, tool_input)
    elif tool_name == "honeycomb_create_trigger":
        return await _execute_create_trigger(client, tool_input)
    elif tool_name == "honeycomb_update_trigger":
        return await _execute_update_trigger(client, tool_input)
    elif tool_name == "honeycomb_delete_trigger":
        return await _execute_delete_trigger(client, tool_input)
    elif tool_name == "honeycomb_list_slos":
        return await _execute_list_slos(client, tool_input)
    elif tool_name == "honeycomb_get_slo":
        return await _execute_get_slo(client, tool_input)
    elif tool_name == "honeycomb_create_slo":
        return await _execute_create_slo(client, tool_input)
    elif tool_name == "honeycomb_update_slo":
        return await _execute_update_slo(client, tool_input)
    elif tool_name == "honeycomb_delete_slo":
        return await _execute_delete_slo(client, tool_input)
    elif tool_name == "honeycomb_list_burn_alerts":
        return await _execute_list_burn_alerts(client, tool_input)
    elif tool_name == "honeycomb_get_burn_alert":
        return await _execute_get_burn_alert(client, tool_input)
    elif tool_name == "honeycomb_create_burn_alert":
        return await _execute_create_burn_alert(client, tool_input)
    elif tool_name == "honeycomb_update_burn_alert":
        return await _execute_update_burn_alert(client, tool_input)
    elif tool_name == "honeycomb_delete_burn_alert":
        return await _execute_delete_burn_alert(client, tool_input)
    # Datasets
    elif tool_name == "honeycomb_list_datasets":
        return await _execute_list_datasets(client, tool_input)
    elif tool_name == "honeycomb_get_dataset":
        return await _execute_get_dataset(client, tool_input)
    elif tool_name == "honeycomb_create_dataset":
        return await _execute_create_dataset(client, tool_input)
    elif tool_name == "honeycomb_update_dataset":
        return await _execute_update_dataset(client, tool_input)
    elif tool_name == "honeycomb_delete_dataset":
        return await _execute_delete_dataset(client, tool_input)
    # Columns
    elif tool_name == "honeycomb_list_columns":
        return await _execute_list_columns(client, tool_input)
    elif tool_name == "honeycomb_get_column":
        return await _execute_get_column(client, tool_input)
    elif tool_name == "honeycomb_create_column":
        return await _execute_create_column(client, tool_input)
    elif tool_name == "honeycomb_update_column":
        return await _execute_update_column(client, tool_input)
    elif tool_name == "honeycomb_delete_column":
        return await _execute_delete_column(client, tool_input)
    # Recipients
    elif tool_name == "honeycomb_list_recipients":
        return await _execute_list_recipients(client, tool_input)
    elif tool_name == "honeycomb_get_recipient":
        return await _execute_get_recipient(client, tool_input)
    elif tool_name == "honeycomb_create_recipient":
        return await _execute_create_recipient(client, tool_input)
    elif tool_name == "honeycomb_update_recipient":
        return await _execute_update_recipient(client, tool_input)
    elif tool_name == "honeycomb_delete_recipient":
        return await _execute_delete_recipient(client, tool_input)
    elif tool_name == "honeycomb_get_recipient_triggers":
        return await _execute_get_recipient_triggers(client, tool_input)
    # Derived Columns
    elif tool_name == "honeycomb_list_derived_columns":
        return await _execute_list_derived_columns(client, tool_input)
    elif tool_name == "honeycomb_get_derived_column":
        return await _execute_get_derived_column(client, tool_input)
    elif tool_name == "honeycomb_create_derived_column":
        return await _execute_create_derived_column(client, tool_input)
    elif tool_name == "honeycomb_update_derived_column":
        return await _execute_update_derived_column(client, tool_input)
    elif tool_name == "honeycomb_delete_derived_column":
        return await _execute_delete_derived_column(client, tool_input)
    # Queries
    elif tool_name == "honeycomb_create_query":
        return await _execute_create_query(client, tool_input)
    elif tool_name == "honeycomb_get_query":
        return await _execute_get_query(client, tool_input)
    elif tool_name == "honeycomb_run_query":
        return await _execute_run_query(client, tool_input)
    # Boards
    elif tool_name == "honeycomb_list_boards":
        return await _execute_list_boards(client, tool_input)
    elif tool_name == "honeycomb_get_board":
        return await _execute_get_board(client, tool_input)
    elif tool_name == "honeycomb_create_board":
        return await _execute_create_board(client, tool_input)
    elif tool_name == "honeycomb_update_board":
        return await _execute_update_board(client, tool_input)
    elif tool_name == "honeycomb_delete_board":
        return await _execute_delete_board(client, tool_input)
    # Markers
    elif tool_name == "honeycomb_list_markers":
        return await _execute_list_markers(client, tool_input)
    elif tool_name == "honeycomb_create_marker":
        return await _execute_create_marker(client, tool_input)
    elif tool_name == "honeycomb_update_marker":
        return await _execute_update_marker(client, tool_input)
    elif tool_name == "honeycomb_delete_marker":
        return await _execute_delete_marker(client, tool_input)
    # Marker Settings
    elif tool_name == "honeycomb_list_marker_settings":
        return await _execute_list_marker_settings(client, tool_input)
    elif tool_name == "honeycomb_get_marker_setting":
        return await _execute_get_marker_setting(client, tool_input)
    elif tool_name == "honeycomb_create_marker_setting":
        return await _execute_create_marker_setting(client, tool_input)
    elif tool_name == "honeycomb_update_marker_setting":
        return await _execute_update_marker_setting(client, tool_input)
    elif tool_name == "honeycomb_delete_marker_setting":
        return await _execute_delete_marker_setting(client, tool_input)
    # Events
    elif tool_name == "honeycomb_send_event":
        return await _execute_send_event(client, tool_input)
    elif tool_name == "honeycomb_send_batch_events":
        return await _execute_send_batch_events(client, tool_input)
    # Service Map
    elif tool_name == "honeycomb_query_service_map":
        return await _execute_query_service_map(client, tool_input)
    else:
        raise ValueError(
            f"Unknown tool: {tool_name}. "
            "Valid tools: triggers (5), slos (5), burn_alerts (5), datasets (5), columns (5), "
            "recipients (6), derived_columns (5), queries (3), boards (5), markers (4), "
            "marker_settings (5), events (2), service_map (1)"
        )


# ==============================================================================
# Triggers
# ==============================================================================


async def _execute_list_triggers(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_list_triggers."""
    triggers = await client.triggers.list_async(dataset=tool_input["dataset"])
    return json.dumps([t.model_dump() for t in triggers], default=str)


async def _execute_get_trigger(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_trigger."""
    trigger = await client.triggers.get_async(
        dataset=tool_input["dataset"],
        trigger_id=tool_input["trigger_id"],
    )
    return json.dumps(trigger.model_dump(), default=str)


async def _execute_create_trigger(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_trigger.

    Handles inline recipient creation with idempotent logic:
    - Checks if recipient already exists (by type + target)
    - Reuses existing ID if found
    - Creates new recipient if not found
    """
    from honeycomb.exceptions import HoneycombAPIError
    from honeycomb.models.recipients import RecipientCreate, RecipientType

    dataset = tool_input.pop("dataset")  # Remove dataset from tool_input

    # Get existing recipients once for idempotent checks (environment-wide)
    existing_recipients = await client.recipients.list_async()

    # Process inline recipients - find or create, then replace with IDs
    recipients_input = tool_input.get("recipients", [])
    for recip in recipients_input:
        if "id" not in recip:
            # Inline recipient - find existing or create new
            recip_type = RecipientType(recip["type"])
            target = recip["target"]

            # Check if recipient with matching type and target already exists
            existing = None
            for existing_recip in existing_recipients:
                if existing_recip.type == recip_type:
                    # Check target match based on type
                    existing_target = None
                    if recip_type == RecipientType.EMAIL:
                        existing_target = existing_recip.details.get("email_address")
                    elif recip_type == RecipientType.SLACK:
                        existing_target = existing_recip.details.get("slack_channel")
                    elif recip_type == RecipientType.WEBHOOK:
                        existing_target = existing_recip.details.get("webhook_url")
                    elif recip_type in (RecipientType.MSTEAMS_WORKFLOW, RecipientType.MSTEAMS):
                        existing_target = existing_recip.details.get("webhook_url")
                    elif recip_type == RecipientType.PAGERDUTY:
                        existing_target = existing_recip.details.get("pagerduty_integration_key")

                    if existing_target == target:
                        existing = existing_recip
                        break

            if existing:
                # Reuse existing recipient
                recip.clear()
                recip["id"] = existing.id
            else:
                # Create new recipient - build details based on type (matching API spec)
                details = recip.get("details", {})
                if recip_type == RecipientType.EMAIL:
                    if "email_address" not in details:
                        details = {"email_address": target}
                elif recip_type == RecipientType.SLACK:
                    if "slack_channel" not in details:
                        details = {"slack_channel": target}
                elif recip_type == RecipientType.PAGERDUTY:
                    if "pagerduty_integration_key" not in details:
                        details = {
                            "pagerduty_integration_key": target,
                            "pagerduty_integration_name": "PagerDuty Integration",
                        }
                elif recip_type == RecipientType.WEBHOOK:
                    if "webhook_url" not in details:
                        details = {
                            "webhook_url": target,
                            "webhook_name": recip.get("name", "Webhook"),
                        }
                elif recip_type in (RecipientType.MSTEAMS_WORKFLOW, RecipientType.MSTEAMS):
                    if "webhook_url" not in details:
                        details = {
                            "webhook_url": target,
                            "webhook_name": "MS Teams",
                        }

                # Create recipient via Recipients API
                try:
                    recipient_obj = RecipientCreate(type=recip_type, details=details)
                    created_recip = await client.recipients.create_async(recipient_obj)
                    recip.clear()
                    recip["id"] = created_recip.id
                except HoneycombAPIError as e:
                    if e.status_code == 409:
                        # Conflict - recipient exists but we didn't find it (race condition or bug)
                        # Re-fetch and try to find it
                        existing_recipients = await client.recipients.list_async()
                        for existing_recip in existing_recipients:
                            if existing_recip.type == recip_type:
                                check_target = None
                                if recip_type == RecipientType.EMAIL:
                                    check_target = existing_recip.details.get("email_address")
                                elif recip_type == RecipientType.SLACK:
                                    check_target = existing_recip.details.get("slack_channel")
                                elif recip_type == RecipientType.WEBHOOK:
                                    check_target = existing_recip.details.get("webhook_url")
                                elif recip_type in (RecipientType.MSTEAMS_WORKFLOW, RecipientType.MSTEAMS):
                                    check_target = existing_recip.details.get("webhook_url")
                                elif recip_type == RecipientType.PAGERDUTY:
                                    check_target = existing_recip.details.get("pagerduty_integration_key")

                                if check_target == target:
                                    recip.clear()
                                    recip["id"] = existing_recip.id
                                    break
                        else:
                            # Still not found - re-raise original error
                            raise
                    else:
                        raise

    # Now build trigger with recipient IDs
    builder = _build_trigger(tool_input)
    trigger = builder.build()

    # Create via API
    created = await client.triggers.create_async(dataset=dataset, trigger=trigger)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_trigger(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_trigger."""
    dataset = tool_input.pop("dataset")
    trigger_id = tool_input.pop("trigger_id")

    # Use builder to construct updated trigger
    builder = _build_trigger(tool_input)
    trigger = builder.build()

    # Update via API
    updated = await client.triggers.update_async(
        dataset=dataset,
        trigger_id=trigger_id,
        trigger=trigger,
    )
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_trigger(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_trigger."""
    await client.triggers.delete_async(
        dataset=tool_input["dataset"],
        trigger_id=tool_input["trigger_id"],
    )
    return json.dumps({"success": True, "message": "Trigger deleted"})


# ==============================================================================
# SLOs
# ==============================================================================


async def _execute_list_slos(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_list_slos."""
    slos = await client.slos.list_async(dataset=tool_input["dataset"])
    return json.dumps([s.model_dump() for s in slos], default=str)


async def _execute_get_slo(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_slo."""
    slo = await client.slos.get_async(
        dataset=tool_input["dataset"],
        slo_id=tool_input["slo_id"],
    )
    return json.dumps(slo.model_dump(), default=str)


async def _execute_create_slo(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_slo.

    If SLI expression is provided or burn_alerts are included, uses SLOBuilder
    and create_from_bundle_async for orchestration. Otherwise uses simple create_async.
    """
    dataset = tool_input.pop("dataset")

    # Check if we need bundle orchestration
    sli = tool_input.get("sli", {})
    burn_alerts = tool_input.get("burn_alerts", [])
    needs_bundle = ("expression" in sli) or burn_alerts

    if needs_bundle:
        # Use builder for orchestration
        builder = _build_slo({"dataset": dataset, **tool_input})
        bundle = builder.build()

        # Create via bundle (handles derived columns + burn alerts)
        created_slos = await client.slos.create_from_bundle_async(bundle)

        # Return the main SLO (first one created)
        main_slo = list(created_slos.values())[0]
        return json.dumps(main_slo.model_dump(), default=str)
    else:
        # Simple SLO creation (existing derived column, no burn alerts)
        slo = SLOCreate(**tool_input)
        created = await client.slos.create_async(dataset=dataset, slo=slo)
        return json.dumps(created.model_dump(), default=str)


async def _execute_update_slo(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_slo."""
    dataset = tool_input.pop("dataset")
    slo_id = tool_input.pop("slo_id")

    slo = SLOCreate(**tool_input)
    updated = await client.slos.update_async(
        dataset=dataset,
        slo_id=slo_id,
        slo=slo,
    )
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_slo(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_slo."""
    await client.slos.delete_async(
        dataset=tool_input["dataset"],
        slo_id=tool_input["slo_id"],
    )
    return json.dumps({"success": True, "message": "SLO deleted"})


# ==============================================================================
# Burn Alerts
# ==============================================================================


async def _execute_list_burn_alerts(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_list_burn_alerts."""
    burn_alerts = await client.burn_alerts.list_async(
        dataset=tool_input["dataset"],
        slo_id=tool_input["slo_id"],
    )
    return json.dumps([ba.model_dump() for ba in burn_alerts], default=str)


async def _execute_get_burn_alert(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_burn_alert."""
    burn_alert = await client.burn_alerts.get_async(
        dataset=tool_input["dataset"],
        burn_alert_id=tool_input["burn_alert_id"],
    )
    return json.dumps(burn_alert.model_dump(), default=str)


async def _execute_create_burn_alert(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_burn_alert."""
    dataset = tool_input.pop("dataset")

    # Convert recipients to BurnAlertRecipient model
    recipients_data = tool_input.pop("recipients", [])
    recipients = [BurnAlertRecipient(**r) for r in recipients_data]

    burn_alert = BurnAlertCreate(**tool_input, recipients=recipients)
    created = await client.burn_alerts.create_async(dataset=dataset, burn_alert=burn_alert)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_burn_alert(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_burn_alert."""
    dataset = tool_input.pop("dataset")
    burn_alert_id = tool_input.pop("burn_alert_id")

    # Convert recipients
    recipients_data = tool_input.pop("recipients", [])
    recipients = [BurnAlertRecipient(**r) for r in recipients_data]

    burn_alert = BurnAlertCreate(**tool_input, recipients=recipients)
    updated = await client.burn_alerts.update_async(
        dataset=dataset,
        burn_alert_id=burn_alert_id,
        burn_alert=burn_alert,
    )
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_burn_alert(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_burn_alert."""
    await client.burn_alerts.delete_async(
        dataset=tool_input["dataset"],
        burn_alert_id=tool_input["burn_alert_id"],
    )
    return json.dumps({"success": True, "message": "Burn alert deleted"})


# ==============================================================================
# Datasets
# ==============================================================================


async def _execute_list_datasets(
    client: "HoneycombClient",
    tool_input: dict[str, Any],  # noqa: ARG001
) -> str:
    """Execute honeycomb_list_datasets."""
    datasets = await client.datasets.list_async()
    return json.dumps([d.model_dump() for d in datasets], default=str)


async def _execute_get_dataset(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_dataset."""
    dataset = await client.datasets.get_async(slug=tool_input["slug"])
    return json.dumps(dataset.model_dump(), default=str)


async def _execute_create_dataset(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_dataset."""
    dataset = DatasetCreate(**tool_input)
    created = await client.datasets.create_async(dataset=dataset)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_dataset(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_dataset."""
    slug = tool_input.pop("slug")
    dataset = DatasetCreate(**tool_input)
    updated = await client.datasets.update_async(slug=slug, dataset=dataset)
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_dataset(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_dataset."""
    await client.datasets.delete_async(slug=tool_input["slug"])
    return json.dumps({"success": True, "message": "Dataset deleted"})


# ==============================================================================
# Columns
# ==============================================================================


async def _execute_list_columns(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_list_columns."""
    columns = await client.columns.list_async(dataset=tool_input["dataset"])
    return json.dumps([c.model_dump() for c in columns], default=str)


async def _execute_get_column(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_column."""
    column = await client.columns.get_async(
        dataset=tool_input["dataset"],
        column_id=tool_input["column_id"],
    )
    return json.dumps(column.model_dump(), default=str)


async def _execute_create_column(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_column."""
    dataset = tool_input.pop("dataset")
    column = ColumnCreate(**tool_input)
    created = await client.columns.create_async(dataset=dataset, column=column)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_column(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_column."""
    dataset = tool_input.pop("dataset")
    column_id = tool_input.pop("column_id")
    column = ColumnCreate(**tool_input)
    updated = await client.columns.update_async(
        dataset=dataset,
        column_id=column_id,
        column=column,
    )
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_column(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_column."""
    await client.columns.delete_async(
        dataset=tool_input["dataset"],
        column_id=tool_input["column_id"],
    )
    return json.dumps({"success": True, "message": "Column deleted"})


# ==============================================================================
# Recipients
# ==============================================================================


async def _execute_list_recipients(
    client: "HoneycombClient",
    tool_input: dict[str, Any],  # noqa: ARG001
) -> str:
    """Execute honeycomb_list_recipients."""
    recipients = await client.recipients.list_async()
    return json.dumps([r.model_dump() for r in recipients], default=str)


async def _execute_get_recipient(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_recipient."""
    recipient = await client.recipients.get_async(recipient_id=tool_input["recipient_id"])
    return json.dumps(recipient.model_dump(), default=str)


async def _execute_create_recipient(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_recipient."""
    recipient = RecipientCreate(**tool_input)
    created = await client.recipients.create_async(recipient=recipient)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_recipient(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_recipient."""
    recipient_id = tool_input.pop("recipient_id")
    recipient = RecipientCreate(**tool_input)
    updated = await client.recipients.update_async(recipient_id=recipient_id, recipient=recipient)
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_recipient(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_recipient."""
    await client.recipients.delete_async(recipient_id=tool_input["recipient_id"])
    return json.dumps({"success": True, "message": "Recipient deleted"})


async def _execute_get_recipient_triggers(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_get_recipient_triggers."""
    triggers = await client.recipients.get_triggers_async(recipient_id=tool_input["recipient_id"])
    return json.dumps(triggers, default=str)


# ==============================================================================
# Derived Columns
# ==============================================================================


async def _execute_list_derived_columns(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_list_derived_columns."""
    derived_columns = await client.derived_columns.list_async(dataset=tool_input["dataset"])
    return json.dumps([dc.model_dump() for dc in derived_columns], default=str)


async def _execute_get_derived_column(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_derived_column."""
    derived_column = await client.derived_columns.get_async(
        dataset=tool_input["dataset"],
        column_id=tool_input["derived_column_id"],
    )
    return json.dumps(derived_column.model_dump(), default=str)


async def _execute_create_derived_column(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_create_derived_column."""
    dataset = tool_input.pop("dataset")
    derived_column = DerivedColumnCreate(**tool_input)
    created = await client.derived_columns.create_async(
        dataset=dataset, derived_column=derived_column
    )
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_derived_column(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_update_derived_column."""
    dataset = tool_input.pop("dataset")
    column_id = tool_input.pop("derived_column_id")
    derived_column = DerivedColumnCreate(**tool_input)
    updated = await client.derived_columns.update_async(
        dataset=dataset,
        column_id=column_id,
        derived_column=derived_column,
    )
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_derived_column(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_delete_derived_column."""
    await client.derived_columns.delete_async(
        dataset=tool_input["dataset"],
        column_id=tool_input["derived_column_id"],
    )
    return json.dumps({"success": True, "message": "Derived column deleted"})


# ==============================================================================
# Queries
# ==============================================================================


async def _execute_create_query(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_query.

    Note: annotation_name parameter is accepted but currently ignored.
    QueryBuilder integration required for full annotation support.
    """
    dataset = tool_input.pop("dataset")
    tool_input.pop("annotation_name", None)  # Remove if present, not yet supported

    query_spec = QuerySpec(**tool_input)
    query = await client.queries.create_async(spec=query_spec, dataset=dataset)

    return json.dumps(query.model_dump(), default=str)


async def _execute_get_query(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_query."""
    query = await client.queries.get_async(
        dataset=tool_input["dataset"],
        query_id=tool_input["query_id"],
    )
    return json.dumps(query.model_dump(), default=str)


async def _execute_run_query(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_run_query.

    Runs ephemeral query with automatic polling.
    Returns the QueryResult (not the tuple).
    """
    dataset = tool_input.pop("dataset")
    query_spec = QuerySpec(**tool_input)

    # Run query with polling - returns (Query, QueryResult) tuple
    _, result = await client.query_results.create_and_run_async(
        spec=query_spec,
        dataset=dataset,
    )

    return json.dumps(result.model_dump(), default=str)


# ==============================================================================
# Boards
# ==============================================================================


async def _execute_list_boards(
    client: "HoneycombClient",
    tool_input: dict[str, Any],  # noqa: ARG001
) -> str:
    """Execute honeycomb_list_boards."""
    boards = await client.boards.list_async()
    return json.dumps([b.model_dump() for b in boards], default=str)


async def _execute_get_board(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_board."""
    board = await client.boards.get_async(board_id=tool_input["board_id"])
    return json.dumps(board.model_dump(), default=str)


async def _execute_create_board(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_board.

    Uses BoardBundle orchestration for inline panel creation.
    """
    # Build BoardBuilder and get bundle
    board_builder = _build_board(tool_input)
    bundle = board_builder.build()

    # Create board with orchestration (creates inline queries, assembles panels)
    board = await client.boards.create_from_bundle_async(bundle)

    return json.dumps(board.model_dump(), default=str)


async def _execute_update_board(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_board."""
    board_id = tool_input.pop("board_id")

    # Simple update (no bundle orchestration for updates)
    from honeycomb.models import BoardCreate

    board = BoardCreate(**tool_input)
    updated = await client.boards.update_async(board_id=board_id, board=board)

    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_board(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_board."""
    await client.boards.delete_async(board_id=tool_input["board_id"])
    return json.dumps({"success": True, "message": "Board deleted"})


# ==============================================================================
# Markers
# ==============================================================================


async def _execute_list_markers(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_list_markers."""
    markers = await client.markers.list_async(dataset=tool_input["dataset"])
    return json.dumps([m.model_dump() for m in markers], default=str)


async def _execute_create_marker(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_marker."""
    dataset = tool_input.pop("dataset")
    tool_input.pop("color", None)  # Color handled by marker settings, not markers directly

    marker = MarkerCreate(**tool_input)
    created = await client.markers.create_async(dataset=dataset, marker=marker)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_marker(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_marker."""
    dataset = tool_input.pop("dataset")
    marker_id = tool_input.pop("marker_id")

    marker = MarkerCreate(**tool_input)
    updated = await client.markers.update_async(dataset=dataset, marker_id=marker_id, marker=marker)
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_marker(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_marker."""
    await client.markers.delete_async(
        dataset=tool_input["dataset"], marker_id=tool_input["marker_id"]
    )
    return json.dumps({"success": True, "message": "Marker deleted"})


# ==============================================================================
# Marker Settings
# ==============================================================================


async def _execute_list_marker_settings(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_list_marker_settings."""
    settings = await client.markers.list_settings_async(dataset=tool_input["dataset"])
    return json.dumps([s.model_dump() for s in settings], default=str)


async def _execute_get_marker_setting(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_marker_setting."""
    setting = await client.markers.get_setting_async(
        dataset=tool_input["dataset"],
        setting_id=tool_input["setting_id"],
    )
    return json.dumps(setting.model_dump(), default=str)


async def _execute_create_marker_setting(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_create_marker_setting."""
    dataset = tool_input.pop("dataset")
    setting = MarkerSettingCreate(**tool_input)
    created = await client.markers.create_setting_async(dataset=dataset, setting=setting)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_marker_setting(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_update_marker_setting."""
    dataset = tool_input.pop("dataset")
    setting_id = tool_input.pop("setting_id")
    setting = MarkerSettingCreate(**tool_input)
    updated = await client.markers.update_setting_async(
        dataset=dataset,
        setting_id=setting_id,
        setting=setting,
    )
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_marker_setting(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_delete_marker_setting."""
    await client.markers.delete_setting_async(
        dataset=tool_input["dataset"],
        setting_id=tool_input["setting_id"],
    )
    return json.dumps({"success": True, "message": "Marker setting deleted"})


# ==============================================================================
# Events
# ==============================================================================


async def _execute_send_event(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_send_event."""
    dataset = tool_input.pop("dataset")
    data = tool_input.pop("data")
    timestamp = tool_input.pop("timestamp", None)
    samplerate = tool_input.pop("samplerate", None)

    await client.events.send_async(
        dataset=dataset, data=data, timestamp=timestamp, samplerate=samplerate
    )
    return json.dumps({"success": True, "message": "Event sent"})


async def _execute_send_batch_events(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_send_batch_events."""
    dataset = tool_input.pop("dataset")
    events_data = tool_input.pop("events")

    # Convert to BatchEvent objects
    events = [BatchEvent(**event) for event in events_data]

    results = await client.events.send_batch_async(dataset=dataset, events=events)
    return json.dumps([r.model_dump() for r in results], default=str)


# ==============================================================================
# Service Map Dependencies
# ==============================================================================


async def _execute_query_service_map(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_query_service_map.

    Performs create + poll + paginate automatically.
    """
    max_pages = tool_input.pop("max_pages", 640)
    request = ServiceMapDependencyRequestCreate(**tool_input)

    # Query with polling and pagination - returns ServiceMapDependencyResult
    result = await client.service_map_dependencies.get_async(
        request=request,
        max_pages=max_pages,
    )

    # Return just the dependencies list
    if result.dependencies:
        return json.dumps([d.model_dump() for d in result.dependencies], default=str)
    else:
        return json.dumps([], default=str)


__all__ = [
    "execute_tool",
]
