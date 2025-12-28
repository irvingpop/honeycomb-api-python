"""Tool execution handler for Claude API tool calls.

This module executes Claude tool calls against the Honeycomb API,
converting tool inputs to API operations and returning JSON results.
"""

import json
from typing import TYPE_CHECKING, Any

from honeycomb.models import (
    BurnAlertCreate,
    BurnAlertRecipient,
    SLOCreate,
)
from honeycomb.tools.builders import _build_slo, _build_trigger

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
    else:
        raise ValueError(
            f"Unknown tool: {tool_name}. "
            "Valid tools: honeycomb_list_triggers, honeycomb_get_trigger, honeycomb_create_trigger, "
            "honeycomb_update_trigger, honeycomb_delete_trigger, honeycomb_list_slos, honeycomb_get_slo, "
            "honeycomb_create_slo, honeycomb_update_slo, honeycomb_delete_slo, honeycomb_list_burn_alerts, "
            "honeycomb_get_burn_alert, honeycomb_create_burn_alert, honeycomb_update_burn_alert, "
            "honeycomb_delete_burn_alert"
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

    Uses TriggerBuilder for convenience, then calls create_async.
    """
    dataset = tool_input.pop("dataset")  # Remove dataset from tool_input

    # Use builder to construct trigger
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


__all__ = [
    "execute_tool",
]
