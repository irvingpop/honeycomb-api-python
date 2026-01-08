"""Burn Alerts tool definitions for Claude API.

This module provides tool generators and descriptions for
burn alerts resources.
"""

from typing import Any

from honeycomb.models import BurnAlertCreate
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Burn Alerts Descriptions
# ==============================================================================

BURN_ALERT_DESCRIPTIONS = {
    "honeycomb_list_burn_alerts": (
        "Lists all burn alerts configured for a specific SLO. "
        "Use this to discover existing error budget alerts before creating new ones or when reviewing SLO alerting configuration. "
        "Requires both the dataset slug and SLO ID parameters. "
        "Returns a list of burn alert objects with their IDs, alert types (exhaustion_time or budget_rate), thresholds, and recipients."
    ),
    "honeycomb_get_burn_alert": (
        "Retrieves detailed configuration for a specific burn alert by ID. "
        "Use this to inspect an existing burn alert's threshold, alert type, and recipient configuration. "
        "Requires both the dataset slug and burn alert ID. "
        "Returns the complete burn alert configuration including the SLO it's attached to."
    ),
    "honeycomb_create_burn_alert": (
        "Creates a new burn alert that fires when an SLO's error budget is depleting too quickly. "
        "Use this to get early warning when service reliability is degrading, before completely exhausting your error budget. "
        "Requires a dataset, the SLO ID to attach to, alert type (exhaustion_time or budget_rate), and threshold value. "
        "For exhaustion_time alerts, specify the threshold in minutes (fires when budget will be exhausted in X minutes). "
        "For budget_rate alerts, specify threshold as percentage drop within a time window. "
        "Recipients are OPTIONAL - omit them to create a silent alert, or include inline recipients "
        "(type + target) to create and attach them automatically."
    ),
    "honeycomb_update_burn_alert": (
        "Updates an existing burn alert's threshold, recipients, or alert type. "
        "Use this to adjust alerting sensitivity as you learn about your service's error budget consumption patterns. "
        "Requires the dataset slug, burn alert ID, and the complete updated burn alert configuration. "
        "Note: This replaces the entire burn alert configuration, so include all fields you want to preserve."
    ),
    "honeycomb_delete_burn_alert": (
        "Permanently deletes a burn alert from an SLO. "
        "Use this when adjusting SLO alerting strategy or removing redundant burn alerts. "
        "Requires both the dataset slug and burn alert ID. "
        "Warning: This action cannot be undone. The alert will stop firing immediately."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return BURN_ALERT_DESCRIPTIONS[tool_name]


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
# Burn Alerts Tool Definitions
# ==============================================================================


def generate_list_burn_alerts_tool() -> dict[str, Any]:
    """Generate honeycomb_list_burn_alerts tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset", "slo_id"]}

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "slo_id", "string", "The SLO ID to list burn alerts for", required=True)

    examples = [
        {"dataset": "api-logs", "slo_id": "slo-123"},
        {"dataset": "production", "slo_id": "slo-456"},
    ]

    return create_tool_definition(
        name="honeycomb_list_burn_alerts",
        description=get_description("honeycomb_list_burn_alerts"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_burn_alert_tool() -> dict[str, Any]:
    """Generate honeycomb_get_burn_alert tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "burn_alert_id"],
    }

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "burn_alert_id", "string", "The burn alert ID to retrieve", required=True)

    examples = [
        {"dataset": "api-logs", "burn_alert_id": "ba-123"},
        {"dataset": "production", "burn_alert_id": "ba-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_burn_alert",
        description=get_description("honeycomb_get_burn_alert"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_burn_alert_tool() -> dict[str, Any]:
    """Generate honeycomb_create_burn_alert tool definition."""
    base_schema = generate_schema_from_model(
        BurnAlertCreate,
        exclude_fields={"created_at", "updated_at", "id"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(
        schema, "dataset", "string", "The dataset slug to create the burn alert in", required=True
    )

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples = [
        # Exhaustion time alert without recipients (recipients are optional)
        {
            "dataset": "api-logs",
            "alert_type": "exhaustion_time",
            "slo_id": "slo-123",
            "exhaustion_minutes": 60,
        },
        # Exhaustion time alert with ID-based recipient
        {
            "dataset": "api-logs",
            "alert_type": "exhaustion_time",
            "slo_id": "slo-456",
            "exhaustion_minutes": 60,
            "recipients": [{"id": "recip-123"}],
        },
        # Budget rate alert with inline recipients
        {
            "dataset": "production",
            "alert_type": "budget_rate",
            "slo_id": "slo-789",
            "budget_rate_window_minutes": 60,
            "budget_rate_decrease_threshold_per_million": 10000,  # 1% drop in 1 hour
            "description": "Alert when error budget drops by 1% in 1 hour",
            "recipients": [
                {"type": "email", "target": "sre@example.com"},
                {"type": "slack", "target": "#slo-alerts"},
            ],
        },
        # Critical exhaustion alert with PagerDuty
        {
            "dataset": "critical-services",
            "alert_type": "exhaustion_time",
            "slo_id": "slo-abc",
            "exhaustion_minutes": 30,
            "description": "Critical: Budget exhausting in 30 minutes",
            "recipients": [
                {
                    "type": "pagerduty",
                    "target": "routing-key-critical",
                    "details": {"severity": "critical"},
                },
            ],
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_burn_alert",
        description=get_description("honeycomb_create_burn_alert"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_burn_alert_tool() -> dict[str, Any]:
    """Generate honeycomb_update_burn_alert tool definition."""
    base_schema = generate_schema_from_model(
        BurnAlertCreate,
        exclude_fields={"created_at", "updated_at", "id"},
    )

    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "burn_alert_id"],
    }
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "burn_alert_id", "string", "The burn alert ID to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples = [
        {
            "dataset": "api-logs",
            "burn_alert_id": "ba-123",
            "alert_type": "exhaustion_time",
            "slo_id": "slo-123",
            "exhaustion_minutes": 30,  # Updated from 60 to 30
            "recipients": [{"id": "recip-123"}],
        },
    ]

    return create_tool_definition(
        name="honeycomb_update_burn_alert",
        description=get_description("honeycomb_update_burn_alert"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_burn_alert_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_burn_alert tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "burn_alert_id"],
    }

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "burn_alert_id", "string", "The burn alert ID to delete", required=True)

    examples = [
        {"dataset": "api-logs", "burn_alert_id": "ba-123"},
        {"dataset": "production", "burn_alert_id": "ba-456"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_burn_alert",
        description=get_description("honeycomb_delete_burn_alert"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all burn alerts tool definitions."""
    return [
        generate_list_burn_alerts_tool(),
        generate_get_burn_alert_tool(),
        generate_create_burn_alert_tool(),
        generate_update_burn_alert_tool(),
        generate_delete_burn_alert_tool(),
    ]
