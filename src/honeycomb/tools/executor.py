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
    DatasetUpdate,
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
# Metadata Field Handling
# ==============================================================================


def strip_metadata_fields(tool_input: dict[str, Any]) -> dict[str, Any]:
    """Strip Claude reasoning metadata fields before API execution.

    These fields are for downstream applications to observe Claude's reasoning
    and are NOT sent to the Honeycomb API.

    Args:
        tool_input: The tool input dict (will be modified in place)

    Returns:
        The same dict with metadata fields removed
    """
    tool_input.pop("confidence", None)
    tool_input.pop("notes", None)
    return tool_input


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
    # Strip metadata fields before processing
    # These are for Claude's reasoning and not sent to Honeycomb API
    strip_metadata_fields(tool_input)

    # Route to appropriate handler
    if tool_name == "honeycomb_get_auth":
        return await _execute_get_auth(client, tool_input)
    # API Keys (v2)
    elif tool_name == "honeycomb_list_api_keys":
        return await _execute_list_api_keys(client, tool_input)
    elif tool_name == "honeycomb_get_api_key":
        return await _execute_get_api_key(client, tool_input)
    elif tool_name == "honeycomb_create_api_key":
        return await _execute_create_api_key(client, tool_input)
    elif tool_name == "honeycomb_update_api_key":
        return await _execute_update_api_key(client, tool_input)
    elif tool_name == "honeycomb_delete_api_key":
        return await _execute_delete_api_key(client, tool_input)
    # Environments (v2)
    elif tool_name == "honeycomb_list_environments":
        return await _execute_list_environments(client, tool_input)
    elif tool_name == "honeycomb_get_environment":
        return await _execute_get_environment(client, tool_input)
    elif tool_name == "honeycomb_create_environment":
        return await _execute_create_environment(client, tool_input)
    elif tool_name == "honeycomb_update_environment":
        return await _execute_update_environment(client, tool_input)
    elif tool_name == "honeycomb_delete_environment":
        return await _execute_delete_environment(client, tool_input)
    elif tool_name == "honeycomb_list_triggers":
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
    # Analysis
    elif tool_name == "honeycomb_search_columns":
        return await _execute_search_columns(client, tool_input)
    elif tool_name == "honeycomb_get_environment_summary":
        return await _execute_get_environment_summary(client, tool_input)
    else:
        raise ValueError(
            f"Unknown tool: {tool_name}. "
            "Valid tools: triggers (5), slos (5), burn_alerts (5), datasets (5), columns (5), "
            "recipients (6), derived_columns (5), queries (3), boards (5), markers (4), "
            "marker_settings (5), events (2), service_map (1), analysis (2)"
        )


# ==============================================================================
# Auth
# ==============================================================================


async def _execute_get_auth(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_auth tool."""
    use_v2 = tool_input.get("use_v2")
    result = await client.auth.get_async(use_v2=use_v2)
    return json.dumps(result.model_dump(), default=str)


# ==============================================================================
# API Keys (v2)
# ==============================================================================


async def _execute_list_api_keys(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_list_api_keys tool."""
    key_type = tool_input.get("key_type")
    keys = await client.api_keys.list_async(key_type=key_type)
    return json.dumps([k.model_dump() for k in keys], default=str)


async def _execute_get_api_key(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_api_key tool."""
    key = await client.api_keys.get_async(key_id=tool_input["key_id"])
    return json.dumps(key.model_dump(), default=str)


async def _execute_create_api_key(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_api_key tool."""
    from honeycomb.models.api_keys import ApiKeyCreate, ApiKeyType

    api_key = ApiKeyCreate(
        name=tool_input["name"],
        key_type=ApiKeyType(tool_input["key_type"]),
        environment_id=tool_input["environment_id"],
        permissions=tool_input.get("permissions"),
    )
    created = await client.api_keys.create_async(api_key=api_key)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_api_key(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_api_key tool."""
    from honeycomb.models.api_keys import ApiKeyUpdate

    update = ApiKeyUpdate(
        name=tool_input.get("name"),
        disabled=tool_input.get("disabled"),
    )
    updated = await client.api_keys.update_async(
        key_id=tool_input["key_id"],
        api_key=update,
    )
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_api_key(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_api_key tool."""
    await client.api_keys.delete_async(key_id=tool_input["key_id"])
    return json.dumps({"status": "deleted", "key_id": tool_input["key_id"]})


# ==============================================================================
# Environments (v2)
# ==============================================================================


async def _execute_list_environments(client: "HoneycombClient", _tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_list_environments tool."""
    envs = await client.environments.list_async()
    return json.dumps([e.model_dump() for e in envs], default=str)


async def _execute_get_environment(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_get_environment tool."""
    env = await client.environments.get_async(env_id=tool_input["env_id"])
    result = env.model_dump()

    # Optionally include datasets (requires environment-scoped API key)
    if tool_input.get("with_datasets"):
        import os

        api_key = os.environ.get("HONEYCOMB_API_KEY")
        if not api_key:
            result["datasets_error"] = (
                "Cannot list datasets: No HONEYCOMB_API_KEY found. "
                "Datasets require an environment-scoped API key."
            )
        else:
            # Create temporary client to verify environment match
            from honeycomb import HoneycombClient

            async with HoneycombClient(api_key=api_key) as api_key_client:
                # Verify the API key is for this environment (force v1 for environment_slug)
                from honeycomb.models.auth import AuthInfo

                auth_info = await api_key_client.auth.get_async(use_v2=False)
                assert isinstance(auth_info, AuthInfo)  # use_v2=False always returns AuthInfo
                if auth_info.environment_slug != result["slug"]:
                    result["datasets_error"] = (
                        f"Cannot list datasets: HONEYCOMB_API_KEY is for environment "
                        f"'{auth_info.environment_slug}' but requested '{result['slug']}'"
                    )
                else:
                    # Environment matches - list datasets
                    datasets = await api_key_client.datasets.list_async()
                    result["datasets"] = [d.model_dump() for d in datasets]

    return json.dumps(result, default=str)


async def _execute_create_environment(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_create_environment tool."""
    from honeycomb.models.environments import EnvironmentColor, EnvironmentCreate

    environment = EnvironmentCreate(
        name=tool_input["name"],
        description=tool_input.get("description"),
        color=EnvironmentColor(tool_input["color"]) if tool_input.get("color") else None,
    )
    created = await client.environments.create_async(environment=environment)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_environment(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_environment tool."""
    from honeycomb.models.environments import EnvironmentColor, EnvironmentUpdate

    environment = EnvironmentUpdate(
        description=tool_input.get("description"),
        color=EnvironmentColor(tool_input["color"]) if tool_input.get("color") else None,
        delete_protected=tool_input.get("delete_protected"),
    )
    updated = await client.environments.update_async(
        env_id=tool_input["env_id"],
        environment=environment,
    )
    return json.dumps(updated.model_dump(), default=str)


async def _execute_delete_environment(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_delete_environment tool."""
    await client.environments.delete_async(env_id=tool_input["env_id"])
    return json.dumps({"status": "deleted", "env_id": tool_input["env_id"]})


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
    """Execute honeycomb_create_trigger using bundle orchestration.

    The bundle handles inline recipient creation with idempotent logic:
    - Checks if recipient already exists (by type + target)
    - Reuses existing ID if found
    - Creates new recipient if not found
    """
    # Build bundle from tool input (includes dataset)
    builder = _build_trigger(tool_input)
    bundle = builder.build()

    # Create via bundle (handles recipient orchestration)
    created = await client.triggers.create_from_bundle_async(bundle)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_trigger(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_trigger."""
    trigger_id = tool_input.pop("trigger_id")

    # Use builder to construct updated trigger
    builder = _build_trigger(tool_input)
    bundle = builder.build()

    # Update via API (use trigger from bundle)
    updated = await client.triggers.update_async(
        dataset=bundle.dataset,
        trigger_id=trigger_id,
        trigger=bundle.trigger,
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

    Always uses SLOBuilder with Pydantic validation and automatic target_percentage conversion.
    Handles SLI expressions, burn alerts, and dataset list processing transparently.
    """
    # Validate and build (tool_input now contains datasets: list[str])
    builder = _build_slo(tool_input)
    bundle = builder.build()

    # Create via bundle (handles derived columns, burn alerts, and all conversions)
    created_slos = await client.slos.create_from_bundle_async(bundle)

    # Return the main SLO (first one created)
    main_slo = list(created_slos.values())[0]
    return json.dumps(main_slo.model_dump(), default=str)


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
    """Execute honeycomb_create_burn_alert with inline recipient handling."""
    from honeycomb.resources._recipient_utils import process_inline_recipients

    dataset = tool_input.pop("dataset")

    # Process inline recipients with idempotent handling
    recipients_data = tool_input.pop("recipients", [])
    processed = await process_inline_recipients(client, recipients_data)
    recipients = [BurnAlertRecipient(**r) for r in processed]

    burn_alert = BurnAlertCreate(**tool_input, recipients=recipients)
    created = await client.burn_alerts.create_async(dataset=dataset, burn_alert=burn_alert)
    return json.dumps(created.model_dump(), default=str)


async def _execute_update_burn_alert(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_update_burn_alert with inline recipient handling."""
    from honeycomb.resources._recipient_utils import process_inline_recipients

    dataset = tool_input.pop("dataset")
    burn_alert_id = tool_input.pop("burn_alert_id")

    # Process inline recipients with idempotent handling
    recipients_data = tool_input.pop("recipients", [])
    processed = await process_inline_recipients(client, recipients_data)
    recipients = [BurnAlertRecipient(**r) for r in processed]

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
    dataset = DatasetUpdate(**tool_input)
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


# ==============================================================================
# Analysis
# ==============================================================================


async def _execute_search_columns(client: "HoneycombClient", tool_input: dict[str, Any]) -> str:
    """Execute honeycomb_search_columns tool."""
    from dataclasses import asdict

    from honeycomb.tools.analysis.column_search import search_columns_async

    result = await search_columns_async(
        client,
        query=tool_input["query"],
        dataset=tool_input.get("dataset"),
        limit=min(tool_input.get("limit", 50), 1000),
        offset=tool_input.get("offset", 0),
    )
    return json.dumps(asdict(result), default=str)


async def _execute_get_environment_summary(
    client: "HoneycombClient", tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_get_environment_summary tool."""
    from dataclasses import asdict

    from honeycomb.tools.analysis.environment_summary import get_environment_summary_async

    result = await get_environment_summary_async(
        client,
        include_sample_columns=tool_input.get("include_sample_columns", True),
        sample_column_count=tool_input.get("sample_column_count", 10),
    )
    return json.dumps(asdict(result), default=str)


__all__ = [
    "execute_tool",
]
