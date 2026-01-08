"""Triggers tool definitions for Claude API.

This module provides tool generators and descriptions for
triggers resources.
"""

from typing import Any

from honeycomb.models import TriggerCreate
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Triggers Descriptions
# ==============================================================================

TRIGGER_DESCRIPTIONS = {
    "honeycomb_list_triggers": (
        "Lists all triggers (alerts) configured in a Honeycomb dataset. "
        "Use this to discover existing alerting rules before creating new ones or when migrating from another observability platform. "
        "Requires the dataset slug parameter to specify which dataset's triggers to retrieve. "
        "Returns a list of trigger objects with their IDs, names, thresholds, and recipient configurations."
    ),
    "honeycomb_get_trigger": (
        "Retrieves detailed configuration for a specific trigger by ID. "
        "Use this to inspect an existing trigger's query specification, threshold settings, frequency, and recipients before modifying or replicating it. "
        "Requires both the dataset slug and trigger ID parameters. "
        "Returns the complete trigger configuration including the query spec, threshold operator and value, evaluation frequency, and notification recipients."
    ),
    "honeycomb_create_trigger": (
        "Creates a new trigger (alert) that fires when query results cross a threshold. "
        "Use this when setting up alerting rules for service health monitoring, error rates, latency thresholds, or when migrating Datadog monitors to Honeycomb. "
        "Requires a dataset, query specification with calculations and filters, threshold operator and value, and evaluation frequency in seconds. "
        "The query can be provided inline with calculations, filters, and time range. "
        "IMPORTANT: Recipients can be provided inline using the 'recipients' array - each recipient needs 'type' (email/webhook/slack/pagerduty/msteams) and 'target' (email address/URL/channel). "
        "Inline recipient creation is PREFERRED - create trigger and recipients in one call for efficiency. Alternatively, you can reference existing recipient IDs. "
        "Note: Trigger queries have a maximum time_range of 3600 seconds (1 hour) and support only a single calculation."
    ),
    "honeycomb_update_trigger": (
        "Updates an existing trigger's configuration including its query, threshold, frequency, or recipients. "
        "Use this to adjust alerting thresholds, change notification targets, or update query filters as service behavior evolves. "
        "Requires the dataset slug, trigger ID, and the complete updated trigger configuration. "
        "Note: This replaces the entire trigger configuration, so include all fields you want to preserve."
    ),
    "honeycomb_delete_trigger": (
        "Permanently deletes a trigger from Honeycomb. "
        "Use this when decommissioning services, consolidating redundant alerts, or cleaning up test triggers. "
        "Requires both the dataset slug and trigger ID. "
        "Warning: This action cannot be undone. The trigger will stop firing immediately and historical alert data will be lost."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return TRIGGER_DESCRIPTIONS[tool_name]


def create_tool_definition(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    input_examples: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a Claude tool definition."""
    from honeycomb.tools.descriptions import validate_description
    from honeycomb.tools.schemas import add_metadata_fields, validate_schema, validate_tool_name

    validate_tool_name(name)
    validate_description(description)
    validate_schema(input_schema)
    add_metadata_fields(input_schema)

    definition: dict[str, Any] = {
        "name": name,
        "description": description,
        "input_schema": input_schema,
    }

    if input_examples:
        definition["input_examples"] = input_examples

    return definition


# ==============================================================================
# Triggers Tool Definitions
# ==============================================================================


def generate_list_triggers_tool() -> dict[str, Any]:
    """Generate honeycomb_list_triggers tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}

    add_parameter(
        schema,
        "dataset",
        "string",
        "The dataset slug to list triggers from",
        required=True,
    )

    examples = [
        {"dataset": "api-logs"},
        {"dataset": "production"},
    ]

    return create_tool_definition(
        name="honeycomb_list_triggers",
        description=get_description("honeycomb_list_triggers"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_trigger_tool() -> dict[str, Any]:
    """Generate honeycomb_get_trigger tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "trigger_id"],
    }

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "trigger_id", "string", "The trigger ID to retrieve", required=True)

    examples = [
        {"dataset": "api-logs", "trigger_id": "aBcD123"},
        {"dataset": "production", "trigger_id": "xyz789"},
    ]

    return create_tool_definition(
        name="honeycomb_get_trigger",
        description=get_description("honeycomb_get_trigger"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_trigger_tool() -> dict[str, Any]:
    """Generate honeycomb_create_trigger tool definition."""
    # Start with TriggerCreate schema
    base_schema = generate_schema_from_model(
        TriggerCreate,
        exclude_fields={"created_at", "updated_at", "id"},
    )

    # Add dataset parameter
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(
        schema, "dataset", "string", "The dataset slug to create the trigger in", required=True
    )

    # Merge with TriggerCreate schema
    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add definitions if present
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples = [
        # Minimal example with COUNT
        {
            "dataset": "api-logs",
            "name": "High Error Rate",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": ">=", "value": 500}],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        },
        # P99 latency with recipients
        {
            "dataset": "production",
            "name": "P99 Latency Alert",
            "description": "Alerts when P99 latency exceeds 2 seconds",
            "query": {
                "time_range": 3600,
                "calculations": [{"op": "P99", "column": "duration_ms"}],
            },
            "threshold": {"op": ">=", "value": 2000},
            "frequency": 3600,
            "recipients": [{"type": "email", "target": "oncall@example.com"}],
            "alert_type": "on_change",
        },
        # Advanced: Multiple filters with string operations and tags
        {
            "dataset": "api-logs",
            "name": "API Gateway Errors",
            "description": "Monitors error rates for specific service with path filtering",
            "query": {
                "time_range": 1800,
                "calculations": [{"op": "COUNT"}],
                "filters": [
                    {"column": "status_code", "op": ">=", "value": 500},
                    {"column": "service_name", "op": "=", "value": "api-gateway"},
                    {"column": "path", "op": "starts-with", "value": "/api/v2"},
                ],
                "filter_combination": "AND",
                "breakdowns": ["endpoint"],
            },
            "threshold": {"op": ">", "value": 50, "exceeded_limit": 2},
            "frequency": 900,
            "recipients": [
                {"type": "slack", "target": "#alerts"},
                {
                    "type": "pagerduty",
                    "target": "routing-key-123",
                    "details": {"severity": "critical"},
                },
            ],
            "tags": [
                {"key": "team", "value": "platform"},
                {"key": "severity", "value": "high"},
            ],
        },
        # HEATMAP calculation example
        {
            "dataset": "traces",
            "name": "Request Duration Distribution",
            "query": {
                "time_range": 3600,
                "calculations": [{"op": "HEATMAP", "column": "duration_ms"}],
            },
            "threshold": {"op": ">", "value": 1000},
            "frequency": 3600,
        },
        # COUNT_DISTINCT example
        {
            "dataset": "api-logs",
            "name": "Unique Error Messages",
            "query": {
                "time_range": 3600,
                "calculations": [{"op": "COUNT_DISTINCT", "column": "error_message"}],
                "filters": [{"column": "level", "op": "=", "value": "error"}],
            },
            "threshold": {"op": ">", "value": 10},
            "frequency": 1800,
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_trigger",
        description=get_description("honeycomb_create_trigger"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_trigger_tool() -> dict[str, Any]:
    """Generate honeycomb_update_trigger tool definition."""
    base_schema = generate_schema_from_model(
        TriggerCreate,
        exclude_fields={"created_at", "updated_at", "id"},
    )

    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "trigger_id"],
    }
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "trigger_id", "string", "The trigger ID to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples = [
        {
            "dataset": "api-logs",
            "trigger_id": "abc123",
            "name": "Updated High Error Rate",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": ">=", "value": 500}],
            },
            "threshold": {"op": ">", "value": 150},  # Updated threshold
            "frequency": 900,
        },
    ]

    return create_tool_definition(
        name="honeycomb_update_trigger",
        description=get_description("honeycomb_update_trigger"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_trigger_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_trigger tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "trigger_id"],
    }

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "trigger_id", "string", "The trigger ID to delete", required=True)

    examples = [
        {"dataset": "api-logs", "trigger_id": "abc123"},
        {"dataset": "production", "trigger_id": "xyz789"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_trigger",
        description=get_description("honeycomb_delete_trigger"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all triggers tool definitions."""
    return [
        generate_list_triggers_tool(),
        generate_get_trigger_tool(),
        generate_create_trigger_tool(),
        generate_update_trigger_tool(),
        generate_delete_trigger_tool(),
    ]
