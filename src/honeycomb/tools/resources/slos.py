"""SLOs tool definitions for Claude API.

This module provides tool generators and descriptions for
slos resources.
"""

from typing import Any

from honeycomb.models import SLOCreate
from honeycomb.models.tool_inputs import SLOToolInput
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# SLOs Descriptions
# ==============================================================================

SLO_DESCRIPTIONS = {
    "honeycomb_list_slos": (
        "Lists all Service Level Objectives (SLOs) defined in a Honeycomb dataset. "
        "Use this to discover existing SLOs, review service reliability targets, or before creating related burn alerts. "
        "Requires the dataset slug parameter. "
        "Returns a list of SLO objects with their IDs, names, target percentages, time periods, and SLI (Service Level Indicator) definitions."
    ),
    "honeycomb_get_slo": (
        "Retrieves detailed configuration for a specific SLO by ID. "
        "Use this to inspect an SLO's target percentage, time period, SLI expression, and associated burn alerts. "
        "Requires both the dataset slug and SLO ID. "
        "Returns the complete SLO configuration including the derived column used for the SLI calculation."
    ),
    "honeycomb_create_slo": (
        "Creates a new Service Level Objective (SLO) to track reliability targets, with automatic derived column creation if needed. "
        "IMPORTANT: Use this tool (not honeycomb_create_derived_column) when you want to create an SLO - it will create both the SLI derived column AND the SLO in one operation. "
        "Use this when defining reliability targets for services, such as 99.9% availability or p99 latency targets. "
        "Requires a dataset, SLO name, target (as percentage, per-million, or nines), time period in days, and an SLI definition. "
        "For the SLI, provide an alias and optionally an expression - if expression is provided, a new derived column is created inline; if only alias is provided, it uses an existing derived column. "
        "SLI EXPRESSION SYNTAX: Must return boolean (1/0 coerced). Use $ prefix for columns (case-sensitive). "
        "Example: LT($status_code, 500) or AND(LT($status_code, 500), LT($duration_ms, 1000)). "
        "See honeycomb_create_derived_column for full expression syntax (conditionals, comparisons, regex, etc.). "
        "You can also add burn alerts inline to notify when error budget depletes too quickly. "
        "Supports both single-dataset and multi-dataset SLOs."
    ),
    "honeycomb_update_slo": (
        "Updates an existing SLO's target percentage, time period, or SLI configuration. "
        "Use this to adjust reliability targets as service requirements change or to associate different derived columns. "
        "Requires the dataset slug, SLO ID, and the complete updated SLO configuration. "
        "Note: This replaces the entire SLO configuration. To update burn alerts separately, use burn alert tools instead."
    ),
    "honeycomb_delete_slo": (
        "Permanently deletes an SLO from Honeycomb. "
        "Use this when decommissioning services, consolidating reliability metrics, or removing test SLOs. "
        "Requires both the dataset slug and SLO ID. "
        "Warning: This action cannot be undone. Associated burn alerts will also be deleted."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return SLO_DESCRIPTIONS[tool_name]


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
# SLOs Tool Definitions
# ==============================================================================


def generate_list_slos_tool() -> dict[str, Any]:
    """Generate honeycomb_list_slos tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}

    add_parameter(schema, "dataset", "string", "The dataset slug to list SLOs from", required=True)

    examples = [
        {"dataset": "api-logs"},
        {"dataset": "production"},
    ]

    return create_tool_definition(
        name="honeycomb_list_slos",
        description=get_description("honeycomb_list_slos"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_slo_tool() -> dict[str, Any]:
    """Generate honeycomb_get_slo tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset", "slo_id"]}

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "slo_id", "string", "The SLO ID to retrieve", required=True)

    examples = [
        {"dataset": "api-logs", "slo_id": "slo-123"},
        {"dataset": "production", "slo_id": "slo-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_slo",
        description=get_description("honeycomb_get_slo"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_slo_tool() -> dict[str, Any]:
    """Generate honeycomb_create_slo tool definition."""
    # Use Pydantic model for schema generation with strict validation
    schema = SLOToolInput.model_json_schema()

    examples = [
        # Minimal with existing derived column (single dataset)
        {
            "datasets": ["api-logs"],
            "name": "API Availability",
            "sli": {"alias": "success_rate"},
            "target_percentage": 99.9,
            "time_period_days": 30,
        },
        # With NEW derived column created inline
        {
            "datasets": ["production"],
            "name": "Request Success Rate",
            "description": "Percentage of requests that succeed (status < 500)",
            "sli": {
                "alias": "request_success",
                "expression": "IF(LT($status_code, 500), 1, 0)",
                "description": "1 if status < 500, else 0",
            },
            "target_percentage": 99.5,
            "time_period_days": 7,
        },
        # Multi-dataset SLO with environment-wide derived column
        {
            "datasets": ["api-logs", "production", "staging"],
            "name": "Cross-Service Availability",
            "description": "Environment-wide availability tracking",
            "sli": {
                "alias": "request_success",
                "expression": "IF(LT($status_code, 400), 1, 0)",
            },
            "target_percentage": 99.9,
            "time_period_days": 30,
        },
        # With burn alerts inline (creates SLO + derived column + burn alerts in one call)
        {
            "datasets": ["api-logs"],
            "name": "Critical API Availability",
            "description": "High-priority SLO with burn rate alerting",
            "sli": {
                "alias": "api_success",
                "expression": "IF(LT($status_code, 500), 1, 0)",
            },
            "target_percentage": 99.99,
            "time_period_days": 30,
            "burn_alerts": [
                {
                    "alert_type": "exhaustion_time",
                    "exhaustion_minutes": 60,
                    "description": "Budget exhausting in 1 hour",
                    "recipients": [
                        {"type": "email", "target": "oncall@example.com"},
                        {"type": "webhook", "target": "https://example.com/webhook"},
                    ],
                },
                {
                    "alert_type": "budget_rate",
                    "budget_rate_window_minutes": 60,
                    "budget_rate_decrease_threshold_per_million": 10000,  # 1% drop in 1 hour
                    "description": "Error budget dropping too fast",
                    "recipients": [{"type": "email", "target": "sre-team@example.com"}],
                },
            ],
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_slo",
        description=get_description("honeycomb_create_slo"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_slo_tool() -> dict[str, Any]:
    """Generate honeycomb_update_slo tool definition."""
    base_schema = generate_schema_from_model(
        SLOCreate,
        exclude_fields={"created_at", "updated_at", "id"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset", "slo_id"]}
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "slo_id", "string", "The SLO ID to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples = [
        {
            "dataset": "api-logs",
            "slo_id": "slo-123",
            "name": "API Availability (Updated)",
            "sli": {"alias": "success_rate"},
            "target_per_million": 999500,  # Updated from 999000 to 999500 (99.95%)
            "time_period_days": 30,
        },
    ]

    return create_tool_definition(
        name="honeycomb_update_slo",
        description=get_description("honeycomb_update_slo"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_slo_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_slo tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset", "slo_id"]}

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "slo_id", "string", "The SLO ID to delete", required=True)

    examples = [
        {"dataset": "api-logs", "slo_id": "slo-123"},
        {"dataset": "production", "slo_id": "slo-456"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_slo",
        description=get_description("honeycomb_delete_slo"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all slos tool definitions."""
    return [
        generate_list_slos_tool(),
        generate_get_slo_tool(),
        generate_create_slo_tool(),
        generate_update_slo_tool(),
        generate_delete_slo_tool(),
    ]
