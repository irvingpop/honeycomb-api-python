"""Core tool definition generator for Claude API.

This module generates Claude-compatible tool definitions for Honeycomb API operations.
"""

import json
from typing import Any

from honeycomb.models import (
    BoardCreate,
    BurnAlertCreate,
    ColumnCreate,
    DatasetCreate,
    DerivedColumnCreate,
    MarkerCreate,
    MarkerSettingCreate,
    QuerySpec,
    RecipientCreate,
    ServiceMapDependencyRequestCreate,
    SLOCreate,
    TriggerCreate,
)
from honeycomb.tools.descriptions import get_description, validate_description
from honeycomb.tools.schemas import (
    add_parameter,
    generate_schema_from_model,
    validate_schema,
    validate_tool_name,
)

# ==============================================================================
# Tool Definition Structure
# ==============================================================================


def create_tool_definition(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    input_examples: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a Claude tool definition.

    Args:
        name: Tool name (must match ^[a-zA-Z0-9_-]{1,64}$)
        description: Tool description (>= 50 chars)
        input_schema: JSON Schema for tool inputs
        input_examples: Optional list of example inputs

    Returns:
        Complete tool definition dict

    Raises:
        ValueError: If validation fails
    """
    # Validate
    validate_tool_name(name)
    validate_description(description)
    validate_schema(input_schema)

    # Build definition
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
    base_schema = generate_schema_from_model(
        SLOCreate,
        exclude_fields={"created_at", "updated_at", "id"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(
        schema, "dataset", "string", "The dataset slug to create the SLO in", required=True
    )

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples = [
        # Minimal with existing derived column
        {
            "dataset": "api-logs",
            "name": "API Availability",
            "sli": {"alias": "success_rate"},
            "target_per_million": 999000,  # 99.9%
            "time_period_days": 30,
        },
        # With NEW derived column created inline
        {
            "dataset": "production",
            "name": "Request Success Rate",
            "description": "Percentage of requests that succeed (status < 500)",
            "sli": {
                "alias": "request_success",
                "expression": "IF(LT($status_code, 500), 1, 0)",
                "description": "1 if status < 500, else 0",
            },
            "target_per_million": 995000,  # 99.5%
            "time_period_days": 7,
        },
        # With burn alerts inline (creates SLO + derived column + burn alerts in one call)
        {
            "dataset": "api-logs",
            "name": "Critical API Availability",
            "description": "High-priority SLO with burn rate alerting",
            "sli": {
                "alias": "api_success",
                "expression": "IF(LT($status_code, 500), 1, 0)",
            },
            "target_per_million": 999900,  # 99.99%
            "time_period_days": 30,
            "burn_alerts": [
                {
                    "alert_type": "exhaustion_time",
                    "exhaustion_minutes": 60,
                    "description": "Budget exhausting in 1 hour",
                    "recipients": [
                        {"type": "email", "target": "oncall@example.com"},
                        {"type": "slack", "target": "#critical-alerts"},
                    ],
                },
                {
                    "alert_type": "budget_rate",
                    "budget_rate_window_minutes": 60,
                    "budget_rate_decrease_threshold_per_million": 10000,  # 1% drop in 1 hour
                    "description": "Error budget dropping too fast",
                    "recipients": [{"type": "pagerduty", "target": "routing-key-123"}],
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


# ==============================================================================
# Datasets Tool Definitions
# ==============================================================================


def generate_list_datasets_tool() -> dict[str, Any]:
    """Generate honeycomb_list_datasets tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    examples: list[dict[str, Any]] = [
        {},  # List all datasets
    ]

    return create_tool_definition(
        name="honeycomb_list_datasets",
        description=get_description("honeycomb_list_datasets"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_dataset_tool() -> dict[str, Any]:
    """Generate honeycomb_get_dataset tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["slug"]}

    add_parameter(schema, "slug", "string", "The dataset slug to retrieve", required=True)

    examples: list[dict[str, Any]] = [
        {"slug": "api-logs"},
        {"slug": "production"},
    ]

    return create_tool_definition(
        name="honeycomb_get_dataset",
        description=get_description("honeycomb_get_dataset"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_dataset_tool() -> dict[str, Any]:
    """Generate honeycomb_create_dataset tool definition."""
    # Start with DatasetCreate schema
    base_schema = generate_schema_from_model(
        DatasetCreate,
        exclude_fields={"created_at", "last_written_at", "slug", "regular_columns_count"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        # Minimal example
        {"name": "api-logs"},
        # With description
        {
            "name": "production-logs",
            "description": "Production API logs from main services",
        },
        # With JSON expansion
        {
            "name": "trace-data",
            "description": "Distributed traces with nested JSON",
            "expand_json_depth": 3,
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_dataset",
        description=get_description("honeycomb_create_dataset"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_dataset_tool() -> dict[str, Any]:
    """Generate honeycomb_update_dataset tool definition."""
    base_schema = generate_schema_from_model(
        DatasetCreate,
        exclude_fields={"created_at", "last_written_at", "slug", "regular_columns_count"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["slug"]}
    add_parameter(schema, "slug", "string", "The dataset slug to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        {"slug": "api-logs", "name": "API Logs", "description": "Updated description"},
        {"slug": "production", "name": "Production", "expand_json_depth": 5},
    ]

    return create_tool_definition(
        name="honeycomb_update_dataset",
        description=get_description("honeycomb_update_dataset"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_dataset_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_dataset tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["slug"]}

    add_parameter(schema, "slug", "string", "The dataset slug to delete", required=True)

    examples: list[dict[str, Any]] = [
        {"slug": "test-dataset"},
        {"slug": "old-logs"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_dataset",
        description=get_description("honeycomb_delete_dataset"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Columns Tool Definitions
# ==============================================================================


def generate_list_columns_tool() -> dict[str, Any]:
    """Generate honeycomb_list_columns tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}

    add_parameter(
        schema, "dataset", "string", "The dataset slug to list columns from", required=True
    )

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs"},
        {"dataset": "production"},
    ]

    return create_tool_definition(
        name="honeycomb_list_columns",
        description=get_description("honeycomb_list_columns"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_column_tool() -> dict[str, Any]:
    """Generate honeycomb_get_column tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "column_id"],
    }

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "column_id", "string", "The column ID to retrieve", required=True)

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs", "column_id": "col-123"},
        {"dataset": "production", "column_id": "col-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_column",
        description=get_description("honeycomb_get_column"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_column_tool() -> dict[str, Any]:
    """Generate honeycomb_create_column tool definition."""
    base_schema = generate_schema_from_model(
        ColumnCreate,
        exclude_fields={"id", "created_at", "updated_at", "last_written"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add definitions if present
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples: list[dict[str, Any]] = [
        # Minimal example (string column)
        {"dataset": "api-logs", "key_name": "endpoint", "type": "string"},
        # With description and type
        {
            "dataset": "api-logs",
            "key_name": "duration_ms",
            "type": "float",
            "description": "Request duration in milliseconds",
        },
        # Hidden column
        {
            "dataset": "production",
            "key_name": "internal_id",
            "type": "integer",
            "hidden": True,
            "description": "Internal debugging ID",
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_column",
        description=get_description("honeycomb_create_column"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_column_tool() -> dict[str, Any]:
    """Generate honeycomb_update_column tool definition."""
    base_schema = generate_schema_from_model(
        ColumnCreate,
        exclude_fields={"id", "created_at", "updated_at", "last_written"},
    )

    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "column_id"],
    }
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "column_id", "string", "The column ID to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add definitions if present
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples: list[dict[str, Any]] = [
        {
            "dataset": "api-logs",
            "column_id": "col-123",
            "key_name": "endpoint",
            "type": "string",
            "description": "API endpoint path",
        },
        {
            "dataset": "production",
            "column_id": "col-456",
            "key_name": "status_code",
            "type": "integer",
            "hidden": False,
        },
    ]

    return create_tool_definition(
        name="honeycomb_update_column",
        description=get_description("honeycomb_update_column"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_column_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_column tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "column_id"],
    }

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "column_id", "string", "The column ID to delete", required=True)

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs", "column_id": "col-123"},
        {"dataset": "production", "column_id": "col-456"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_column",
        description=get_description("honeycomb_delete_column"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Recipients Tool Definitions
# ==============================================================================


def generate_list_recipients_tool() -> dict[str, Any]:
    """Generate honeycomb_list_recipients tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    examples: list[dict[str, Any]] = [
        {},  # List all recipients
    ]

    return create_tool_definition(
        name="honeycomb_list_recipients",
        description=get_description("honeycomb_list_recipients"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_recipient_tool() -> dict[str, Any]:
    """Generate honeycomb_get_recipient tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["recipient_id"]}

    add_parameter(schema, "recipient_id", "string", "The recipient ID to retrieve", required=True)

    examples: list[dict[str, Any]] = [
        {"recipient_id": "rec-123"},
        {"recipient_id": "rec-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_recipient",
        description=get_description("honeycomb_get_recipient"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_recipient_tool() -> dict[str, Any]:
    """Generate honeycomb_create_recipient tool definition."""
    base_schema = generate_schema_from_model(
        RecipientCreate,
        exclude_fields={"id", "created_at", "updated_at"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add definitions if present
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples: list[dict[str, Any]] = [
        # Email recipient
        {
            "type": "email",
            "details": {"email_address": "alerts@example.com"},
        },
        # Slack channel
        {
            "type": "slack",
            "details": {"channel": "#alerts"},
        },
        # PagerDuty
        {
            "type": "pagerduty",
            "details": {"routing_key": "abc123def456"},
        },
        # Webhook
        {
            "type": "webhook",
            "details": {
                "url": "https://hooks.example.com/alerts",
                "secret": "webhook-secret-key",
            },
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_recipient",
        description=get_description("honeycomb_create_recipient"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_recipient_tool() -> dict[str, Any]:
    """Generate honeycomb_update_recipient tool definition."""
    base_schema = generate_schema_from_model(
        RecipientCreate,
        exclude_fields={"id", "created_at", "updated_at"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["recipient_id"]}
    add_parameter(schema, "recipient_id", "string", "The recipient ID to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add definitions if present
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples: list[dict[str, Any]] = [
        {
            "recipient_id": "rec-123",
            "type": "email",
            "details": {"email_address": "new-alerts@example.com"},
        },
        {
            "recipient_id": "rec-456",
            "type": "slack",
            "details": {"channel": "#new-alerts"},
        },
    ]

    return create_tool_definition(
        name="honeycomb_update_recipient",
        description=get_description("honeycomb_update_recipient"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_recipient_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_recipient tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["recipient_id"]}

    add_parameter(schema, "recipient_id", "string", "The recipient ID to delete", required=True)

    examples: list[dict[str, Any]] = [
        {"recipient_id": "rec-123"},
        {"recipient_id": "rec-456"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_recipient",
        description=get_description("honeycomb_delete_recipient"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_recipient_triggers_tool() -> dict[str, Any]:
    """Generate honeycomb_get_recipient_triggers tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["recipient_id"]}

    add_parameter(
        schema,
        "recipient_id",
        "string",
        "The recipient ID to get associated triggers for",
        required=True,
    )

    examples: list[dict[str, Any]] = [
        {"recipient_id": "rec-123"},
        {"recipient_id": "rec-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_recipient_triggers",
        description=get_description("honeycomb_get_recipient_triggers"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Derived Columns Tool Definitions
# ==============================================================================


def generate_list_derived_columns_tool() -> dict[str, Any]:
    """Generate honeycomb_list_derived_columns tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}

    add_parameter(
        schema,
        "dataset",
        "string",
        "The dataset slug to list derived columns from (use '__all__' for environment-wide)",
        required=True,
    )

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs"},
        {"dataset": "__all__"},
    ]

    return create_tool_definition(
        name="honeycomb_list_derived_columns",
        description=get_description("honeycomb_list_derived_columns"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_derived_column_tool() -> dict[str, Any]:
    """Generate honeycomb_get_derived_column tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "derived_column_id"],
    }

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(
        schema, "derived_column_id", "string", "The derived column ID to retrieve", required=True
    )

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs", "derived_column_id": "dc-123"},
        {"dataset": "__all__", "derived_column_id": "dc-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_derived_column",
        description=get_description("honeycomb_get_derived_column"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_derived_column_tool() -> dict[str, Any]:
    """Generate honeycomb_create_derived_column tool definition."""
    base_schema = generate_schema_from_model(
        DerivedColumnCreate,
        exclude_fields={"id", "created_at", "updated_at"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(
        schema,
        "dataset",
        "string",
        "The dataset slug (use '__all__' for environment-wide)",
        required=True,
    )

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        # Boolean flag
        {
            "dataset": "api-logs",
            "alias": "is_error",
            "expression": "IF(GTE($status_code, 500), 1, 0)",
            "description": "1 if error, 0 otherwise",
        },
        # Categorization
        {
            "dataset": "api-logs",
            "alias": "status_category",
            "expression": "IF(LT($status_code, 400), 'success', IF(LT($status_code, 500), 'client_error', 'server_error'))",
        },
        # Environment-wide
        {
            "dataset": "__all__",
            "alias": "request_success",
            "expression": "IF(LT($status_code, 400), 1, 0)",
            "description": "Success indicator for all datasets",
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_derived_column",
        description=get_description("honeycomb_create_derived_column"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_derived_column_tool() -> dict[str, Any]:
    """Generate honeycomb_update_derived_column tool definition."""
    base_schema = generate_schema_from_model(
        DerivedColumnCreate,
        exclude_fields={"id", "created_at", "updated_at"},
    )

    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "derived_column_id"],
    }
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(
        schema, "derived_column_id", "string", "The derived column ID to update", required=True
    )

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        {
            "dataset": "api-logs",
            "derived_column_id": "dc-123",
            "alias": "is_error",
            "expression": "IF(GTE($status_code, 500), 1, 0)",
            "description": "Updated error flag",
        },
    ]

    return create_tool_definition(
        name="honeycomb_update_derived_column",
        description=get_description("honeycomb_update_derived_column"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_derived_column_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_derived_column tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "derived_column_id"],
    }

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(
        schema, "derived_column_id", "string", "The derived column ID to delete", required=True
    )

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs", "derived_column_id": "dc-123"},
        {"dataset": "__all__", "derived_column_id": "dc-456"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_derived_column",
        description=get_description("honeycomb_delete_derived_column"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Boards Tool Definitions
# ==============================================================================


def generate_list_boards_tool() -> dict[str, Any]:
    """Generate honeycomb_list_boards tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    examples: list[dict[str, Any]] = [
        {},  # List all boards
    ]

    return create_tool_definition(
        name="honeycomb_list_boards",
        description=get_description("honeycomb_list_boards"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_board_tool() -> dict[str, Any]:
    """Generate honeycomb_get_board tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["board_id"]}

    add_parameter(schema, "board_id", "string", "The board ID to retrieve", required=True)

    examples: list[dict[str, Any]] = [
        {"board_id": "board-123"},
        {"board_id": "board-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_board",
        description=get_description("honeycomb_get_board"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_board_tool() -> dict[str, Any]:
    """Generate honeycomb_create_board tool definition."""
    # Build schema manually for complex nested structure
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["name"],
    }

    add_parameter(schema, "name", "string", "Board name", required=True)
    add_parameter(schema, "description", "string", "Board description", required=False)
    add_parameter(
        schema,
        "layout_generation",
        "string",
        "Layout mode: 'auto' or 'manual' (default: auto)",
        required=False,
    )

    # Inline query panels array
    schema["properties"]["inline_query_panels"] = {
        "type": "array",
        "description": "Array of query panels to create inline (each creates a new query)",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Panel/query name"},
                "dataset": {"type": "string", "description": "Dataset slug"},
                "time_range": {"type": "integer", "description": "Time range in seconds"},
                "calculations": {
                    "type": "array",
                    "description": "Array of calculation objects",
                    "items": {"type": "object"},
                },
                "filters": {
                    "type": "array",
                    "description": "Array of filter objects",
                    "items": {"type": "object"},
                },
                "breakdowns": {
                    "type": "array",
                    "description": "Fields to group by",
                    "items": {"type": "string"},
                },
                "orders": {
                    "type": "array",
                    "description": "Ordering specifications",
                    "items": {"type": "object"},
                },
                "limit": {"type": "integer", "description": "Result limit"},
                "style": {
                    "type": "string",
                    "description": "Panel style: graph, table, or combo",
                },
            },
            "required": ["name"],  # dataset is optional (defaults to environment-wide)
        },
    }

    # Inline SLO panels array
    schema["properties"]["inline_slo_panels"] = {
        "type": "array",
        "description": "Array of SLO definitions to create inline",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "SLO name"},
                "dataset": {"type": "string", "description": "Dataset slug"},
                "sli": {
                    "type": "object",
                    "description": "SLI definition (alias + optional expression for inline creation)",
                    "properties": {
                        "alias": {"type": "string", "description": "Derived column alias"},
                        "expression": {
                            "type": "string",
                            "description": "Optional expression (creates derived column inline)",
                        },
                        "description": {"type": "string"},
                    },
                    "required": ["alias"],
                },
                "target_per_million": {"type": "integer"},
                "target_percentage": {"type": "number"},
                "target_nines": {"type": "integer"},
                "time_period_days": {"type": "integer"},
                "time_period_weeks": {"type": "integer"},
                "description": {"type": "string"},
            },
            "required": ["name", "dataset", "sli"],
        },
    }

    # Text panels array
    schema["properties"]["text_panels"] = {
        "type": "array",
        "description": "Array of markdown text panels",
        "items": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Markdown text content"},
            },
            "required": ["content"],
        },
    }

    # SLO panels array (IDs)
    schema["properties"]["slo_panels"] = {
        "type": "array",
        "description": "Array of existing SLO IDs to display as panels",
        "items": {"type": "string"},
    }

    # Tags
    schema["properties"]["tags"] = {
        "type": "array",
        "description": "Array of tag objects",
        "items": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "value": {"type": "string"},
            },
        },
    }

    examples: list[dict[str, Any]] = [
        # Simple: inline query panels with auto-layout
        {
            "name": "API Dashboard",
            "layout_generation": "auto",
            "inline_query_panels": [
                {
                    "name": "Error Count",
                    "dataset": "api-logs",
                    "time_range": 3600,
                    "calculations": [{"op": "COUNT"}],
                    "filters": [{"column": "status_code", "op": ">=", "value": 500}],
                },
                {
                    "name": "P99 Latency",
                    "dataset": "api-logs",
                    "time_range": 3600,
                    "calculations": [{"op": "P99", "column": "duration_ms"}],
                },
            ],
        },
        # With text panel
        {
            "name": "Service Overview",
            "description": "Main service health dashboard",
            "layout_generation": "auto",
            "inline_query_panels": [
                {
                    "name": "Request Rate",
                    "dataset": "production",
                    "time_range": 7200,
                    "calculations": [{"op": "COUNT"}],
                    "breakdowns": ["endpoint"],
                }
            ],
            "text_panels": [{"content": "## Service Status\nMonitor during peak hours"}],
        },
        # Complex: with existing SLO ID
        {
            "name": "SRE Dashboard",
            "layout_generation": "auto",
            "inline_query_panels": [
                {
                    "name": "Error Rate",
                    "dataset": "api-logs",
                    "time_range": 3600,
                    "calculations": [{"op": "COUNT"}],
                    "filters": [{"column": "status_code", "op": ">=", "value": 500}],
                    "breakdowns": ["service"],
                    "orders": [{"op": "COUNT", "order": "descending"}],
                    "limit": 20,
                }
            ],
            "slo_panels": ["slo-123"],
            "text_panels": [{"content": "## Alerts\nCheck PagerDuty for incidents"}],
            "tags": [{"key": "team", "value": "platform"}],
        },
        # Advanced: inline SLO creation with derived column
        {
            "name": "Production Monitoring",
            "layout_generation": "auto",
            "inline_query_panels": [
                {
                    "name": "Request Count",
                    "dataset": "production",
                    "time_range": 86400,
                    "calculations": [{"op": "COUNT"}],
                    "breakdowns": ["service"],
                }
            ],
            "inline_slo_panels": [
                {
                    "name": "API Availability",
                    "dataset": "api-logs",
                    "sli": {
                        "alias": "success_rate",
                        "expression": "IF(LT($status_code, 400), 1, 0)",
                        "description": "1 if successful, 0 if error",
                    },
                    "target_nines": 3,
                    "time_period_days": 30,
                    "description": "99.9% availability target",
                }
            ],
            "text_panels": [{"content": "## SLO Policy\nReview weekly"}],
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_board",
        description=get_description("honeycomb_create_board"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_board_tool() -> dict[str, Any]:
    """Generate honeycomb_update_board tool definition."""
    base_schema = generate_schema_from_model(
        BoardCreate,
        exclude_fields={"id", "links"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["board_id"]}
    add_parameter(schema, "board_id", "string", "The board ID to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        {
            "board_id": "board-123",
            "name": "Updated Dashboard",
            "description": "New description",
        },
    ]

    return create_tool_definition(
        name="honeycomb_update_board",
        description=get_description("honeycomb_update_board"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_board_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_board tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["board_id"]}

    add_parameter(schema, "board_id", "string", "The board ID to delete", required=True)

    examples: list[dict[str, Any]] = [
        {"board_id": "board-123"},
        {"board_id": "board-456"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_board",
        description=get_description("honeycomb_delete_board"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Queries Tool Definitions
# ==============================================================================


def generate_create_query_tool() -> dict[str, Any]:
    """Generate honeycomb_create_query tool definition."""
    base_schema = generate_schema_from_model(
        QuerySpec,
        exclude_fields={"id", "created_at", "updated_at"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)

    # Add optional annotation_name parameter
    add_parameter(
        schema,
        "annotation_name",
        "string",
        "Optional name for the query annotation (saves query with a display name)",
        required=False,
    )

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add definitions if present
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples: list[dict[str, Any]] = [
        # Simple COUNT query
        {
            "dataset": "api-logs",
            "time_range": 3600,
            "calculations": [{"op": "COUNT"}],
        },
        # P99 with filters
        {
            "dataset": "api-logs",
            "time_range": 3600,
            "calculations": [{"op": "P99", "column": "duration_ms"}],
            "filters": [{"column": "status_code", "op": ">=", "value": 200}],
        },
        # With annotation name
        {
            "dataset": "api-logs",
            "annotation_name": "Error Rate Dashboard",
            "time_range": 7200,
            "calculations": [{"op": "COUNT"}],
            "filters": [{"column": "status_code", "op": ">=", "value": 500}],
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_query",
        description=get_description("honeycomb_create_query"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_query_tool() -> dict[str, Any]:
    """Generate honeycomb_get_query tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "query_id"],
    }

    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "query_id", "string", "The query ID to retrieve", required=True)

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs", "query_id": "q-123"},
        {"dataset": "production", "query_id": "q-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_query",
        description=get_description("honeycomb_get_query"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_run_query_tool() -> dict[str, Any]:
    """Generate honeycomb_run_query tool definition."""
    base_schema = generate_schema_from_model(
        QuerySpec,
        exclude_fields={"id", "created_at", "updated_at"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add definitions if present
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples: list[dict[str, Any]] = [
        # Count in last hour
        {
            "dataset": "api-logs",
            "time_range": 3600,
            "calculations": [{"op": "COUNT"}],
        },
        # P99 with breakdowns
        {
            "dataset": "api-logs",
            "time_range": 7200,
            "calculations": [{"op": "P99", "column": "duration_ms"}],
            "breakdowns": ["endpoint"],
        },
        # Multiple calculations with filters and ordering
        {
            "dataset": "api-logs",
            "time_range": 3600,
            "calculations": [
                {"op": "COUNT"},
                {"op": "AVG", "column": "duration_ms"},
                {"op": "P99", "column": "duration_ms"},
            ],
            "filters": [{"column": "status_code", "op": ">=", "value": 500}],
            "orders": [{"column": "COUNT", "order": "descending"}],
            "limit": 100,
        },
    ]

    return create_tool_definition(
        name="honeycomb_run_query",
        description=get_description("honeycomb_run_query"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Markers Tool Definitions
# ==============================================================================


def generate_list_markers_tool() -> dict[str, Any]:
    """Generate honeycomb_list_markers tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)

    examples: list[dict[str, Any]] = [{"dataset": "api-logs"}, {"dataset": "production"}]

    return create_tool_definition(
        name="honeycomb_list_markers",
        description=get_description("honeycomb_list_markers"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_marker_tool() -> dict[str, Any]:
    """Generate honeycomb_create_marker tool definition."""
    base_schema = generate_schema_from_model(
        MarkerCreate, exclude_fields={"id", "created_at", "updated_at", "color"}
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(
        schema,
        "dataset",
        "string",
        "The dataset slug (or '__all__' for environment-wide)",
        required=True,
    )
    add_parameter(schema, "color", "string", "Optional hex color (e.g., '#FF5733')", required=False)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs", "message": "deploy v1.2.3", "type": "deploy"},
        {
            "dataset": "__all__",
            "message": "maintenance window",
            "type": "maintenance",
            "start_time": 1640000000,
            "end_time": 1640003600,
        },
        {"dataset": "production", "message": "config change", "type": "config", "color": "#FF5733"},
    ]

    return create_tool_definition(
        name="honeycomb_create_marker",
        description=get_description("honeycomb_create_marker"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_marker_tool() -> dict[str, Any]:
    """Generate honeycomb_update_marker tool definition."""
    base_schema = generate_schema_from_model(
        MarkerCreate, exclude_fields={"id", "created_at", "updated_at", "color"}
    )

    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "marker_id"],
    }
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "marker_id", "string", "The marker ID to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        {
            "dataset": "api-logs",
            "marker_id": "abc123",
            "message": "updated deploy v1.2.4",
            "type": "deploy",
        },
    ]

    return create_tool_definition(
        name="honeycomb_update_marker",
        description=get_description("honeycomb_update_marker"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_marker_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_marker tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "marker_id"],
    }
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "marker_id", "string", "The marker ID to delete", required=True)

    examples: list[dict[str, Any]] = [{"dataset": "api-logs", "marker_id": "abc123"}]

    return create_tool_definition(
        name="honeycomb_delete_marker",
        description=get_description("honeycomb_delete_marker"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_list_marker_settings_tool() -> dict[str, Any]:
    """Generate honeycomb_list_marker_settings tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(
        schema,
        "dataset",
        "string",
        "The dataset slug (or '__all__' for environment-wide)",
        required=True,
    )

    examples: list[dict[str, Any]] = [{"dataset": "api-logs"}, {"dataset": "__all__"}]

    return create_tool_definition(
        name="honeycomb_list_marker_settings",
        description=get_description("honeycomb_list_marker_settings"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_marker_setting_tool() -> dict[str, Any]:
    """Generate honeycomb_get_marker_setting tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "setting_id"],
    }
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "setting_id", "string", "The marker setting ID", required=True)

    examples: list[dict[str, Any]] = [{"dataset": "api-logs", "setting_id": "set-123"}]

    return create_tool_definition(
        name="honeycomb_get_marker_setting",
        description=get_description("honeycomb_get_marker_setting"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_marker_setting_tool() -> dict[str, Any]:
    """Generate honeycomb_create_marker_setting tool definition."""
    base_schema = generate_schema_from_model(
        MarkerSettingCreate, exclude_fields={"id", "created_at", "updated_at"}
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset"]}
    add_parameter(
        schema,
        "dataset",
        "string",
        "The dataset slug (or '__all__' for environment-wide)",
        required=True,
    )

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs", "type": "deploy", "color": "#00FF00"},
        {"dataset": "__all__", "type": "incident", "color": "#FF0000"},
    ]

    return create_tool_definition(
        name="honeycomb_create_marker_setting",
        description=get_description("honeycomb_create_marker_setting"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_marker_setting_tool() -> dict[str, Any]:
    """Generate honeycomb_update_marker_setting tool definition."""
    base_schema = generate_schema_from_model(
        MarkerSettingCreate, exclude_fields={"id", "created_at", "updated_at"}
    )

    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "setting_id"],
    }
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "setting_id", "string", "The marker setting ID to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    examples: list[dict[str, Any]] = [
        {"dataset": "api-logs", "setting_id": "set-123", "type": "deploy", "color": "#0000FF"},
    ]

    return create_tool_definition(
        name="honeycomb_update_marker_setting",
        description=get_description("honeycomb_update_marker_setting"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_marker_setting_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_marker_setting tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["dataset", "setting_id"],
    }
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "setting_id", "string", "The marker setting ID to delete", required=True)

    examples: list[dict[str, Any]] = [{"dataset": "api-logs", "setting_id": "set-123"}]

    return create_tool_definition(
        name="honeycomb_delete_marker_setting",
        description=get_description("honeycomb_delete_marker_setting"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Events Tool Definitions
# ==============================================================================


def generate_send_event_tool() -> dict[str, Any]:
    """Generate honeycomb_send_event tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset", "data"]}
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)
    add_parameter(schema, "data", "object", "Event data as key-value pairs", required=True)
    add_parameter(schema, "timestamp", "integer", "Unix timestamp for the event", required=False)
    add_parameter(schema, "samplerate", "integer", "Sample rate (default: 1)", required=False)

    examples: list[dict[str, Any]] = [
        {
            "dataset": "api-logs",
            "data": {"endpoint": "/api/users", "duration_ms": 42, "status_code": 200},
        },
        {
            "dataset": "production",
            "data": {"service": "auth", "latency": 15},
            "timestamp": 1640000000,
        },
    ]

    return create_tool_definition(
        name="honeycomb_send_event",
        description=get_description("honeycomb_send_event"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_send_batch_events_tool() -> dict[str, Any]:
    """Generate honeycomb_send_batch_events tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["dataset", "events"]}
    add_parameter(schema, "dataset", "string", "The dataset slug", required=True)

    schema["properties"]["events"] = {
        "type": "array",
        "description": "Array of event objects. Each event must have a 'data' field with event payload.",
        "items": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Event payload as key-value pairs (required for each event)",
                },
                "time": {
                    "type": "string",
                    "description": "Event timestamp in ISO8601 format (e.g., '2024-01-15T10:30:00Z'). Optional, defaults to server time.",
                },
                "samplerate": {
                    "type": "integer",
                    "description": "Sample rate for this event (optional, defaults to 1)",
                },
            },
            "required": ["data"],
        },
    }

    examples: list[dict[str, Any]] = [
        {
            "dataset": "api-logs",
            "events": [
                {
                    "data": {"endpoint": "/api/users", "duration_ms": 42, "status_code": 200},
                    "time": "2024-01-15T10:30:00Z",
                },
                {
                    "data": {"endpoint": "/api/posts", "duration_ms": 18, "status_code": 201},
                    "time": "2024-01-15T10:30:15Z",
                },
            ],
        },
    ]

    return create_tool_definition(
        name="honeycomb_send_batch_events",
        description=get_description("honeycomb_send_batch_events"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Service Map Dependencies Tool Definitions
# ==============================================================================


def generate_query_service_map_tool() -> dict[str, Any]:
    """Generate honeycomb_query_service_map tool definition."""
    base_schema = generate_schema_from_model(
        ServiceMapDependencyRequestCreate,
        exclude_fields={"id", "status"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add max_pages parameter
    add_parameter(
        schema,
        "max_pages",
        "integer",
        "Maximum pages to fetch (default: 640, up to 64K results)",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        # Simple: last 2 hours
        {"time_range": 7200},
        # With filters
        {"time_range": 3600, "filters": [{"name": "user-service"}]},
        # Absolute time range
        {"start_time": 1640000000, "end_time": 1640003600},
    ]

    return create_tool_definition(
        name="honeycomb_query_service_map",
        description=get_description("honeycomb_query_service_map"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Auth Tool Definitions
# ==============================================================================


def generate_get_auth_tool() -> dict[str, Any]:
    """Generate the honeycomb_get_auth tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    add_parameter(
        schema,
        "use_v2",
        "boolean",
        (
            "Force use of v2 endpoint for management key info. "
            "If not specified, auto-detects based on configured credentials."
        ),
        required=False,
    )

    examples = [
        {},
        {"use_v2": True},
    ]

    return create_tool_definition(
        name="honeycomb_get_auth",
        description=get_description("honeycomb_get_auth"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# API Keys Tool Definitions (v2)
# ==============================================================================


def generate_list_api_keys_tool() -> dict[str, Any]:
    """Generate honeycomb_list_api_keys tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    add_parameter(
        schema,
        "key_type",
        "string",
        "Filter by key type: 'ingest' or 'configuration'",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {},
        {"key_type": "ingest"},
    ]

    return create_tool_definition(
        name="honeycomb_list_api_keys",
        description=get_description("honeycomb_list_api_keys"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_api_key_tool() -> dict[str, Any]:
    """Generate honeycomb_get_api_key tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["key_id"]}

    add_parameter(schema, "key_id", "string", "The API key ID", required=True)

    examples: list[dict[str, Any]] = [{"key_id": "hcaik_123"}]

    return create_tool_definition(
        name="honeycomb_get_api_key",
        description=get_description("honeycomb_get_api_key"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_api_key_tool() -> dict[str, Any]:
    """Generate honeycomb_create_api_key tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["name", "key_type", "environment_id"],
    }

    add_parameter(schema, "name", "string", "Display name for the API key", required=True)
    add_parameter(
        schema,
        "key_type",
        "string",
        "Type of key: 'ingest' or 'configuration'",
        required=True,
    )
    add_parameter(
        schema, "environment_id", "string", "Environment ID to scope the key to", required=True
    )
    add_parameter(
        schema,
        "permissions",
        "object",
        (
            "Permissions for configuration keys (REQUIRED for 'configuration' type). "
            "Object with boolean properties: 'create_datasets', 'send_events', 'manage_markers', "
            "'manage_triggers', 'manage_boards', 'run_queries', 'manage_columns', "
            "'manage_slos', 'manage_recipients', 'manage_privateBoards'. "
            "Example: {'create_datasets': true, 'send_events': true, 'manage_triggers': true}. "
            "Not needed for 'ingest' keys."
        ),
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {
            "name": "Production Ingest Key",
            "key_type": "ingest",
            "environment_id": "hcaen_123",
        },
        {
            "name": "Full Access Config Key",
            "key_type": "configuration",
            "environment_id": "hcaen_123",
            "permissions": {
                "create_datasets": True,
                "send_events": True,
                "manage_markers": True,
                "manage_triggers": True,
                "manage_boards": True,
                "run_queries": True,
                "manage_columns": True,
                "manage_slos": True,
                "manage_recipients": True,
                "manage_privateBoards": True,
            },
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_api_key",
        description=get_description("honeycomb_create_api_key"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_api_key_tool() -> dict[str, Any]:
    """Generate honeycomb_update_api_key tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["key_id"]}

    add_parameter(schema, "key_id", "string", "The API key ID", required=True)
    add_parameter(schema, "name", "string", "New name for the key", required=False)
    add_parameter(schema, "disabled", "boolean", "Set to true to disable the key", required=False)

    examples: list[dict[str, Any]] = [
        {"key_id": "hcaik_123", "name": "New Name"},
        {"key_id": "hcaik_123", "disabled": True},
    ]

    return create_tool_definition(
        name="honeycomb_update_api_key",
        description=get_description("honeycomb_update_api_key"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_api_key_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_api_key tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["key_id"]}

    add_parameter(schema, "key_id", "string", "The API key ID to delete", required=True)

    examples: list[dict[str, Any]] = [{"key_id": "hcaik_123"}]

    return create_tool_definition(
        name="honeycomb_delete_api_key",
        description=get_description("honeycomb_delete_api_key"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Environments Tool Definitions (v2)
# ==============================================================================


def generate_list_environments_tool() -> dict[str, Any]:
    """Generate honeycomb_list_environments tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    examples: list[dict[str, Any]] = [{}]

    return create_tool_definition(
        name="honeycomb_list_environments",
        description=get_description("honeycomb_list_environments"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_environment_tool() -> dict[str, Any]:
    """Generate honeycomb_get_environment tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["env_id"]}

    add_parameter(schema, "env_id", "string", "The environment ID", required=True)
    add_parameter(
        schema,
        "with_datasets",
        "boolean",
        "Also return list of datasets in this environment",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {"env_id": "hcaen_123"},
        {"env_id": "hcaen_123", "with_datasets": True},
    ]

    return create_tool_definition(
        name="honeycomb_get_environment",
        description=get_description("honeycomb_get_environment"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_environment_tool() -> dict[str, Any]:
    """Generate honeycomb_create_environment tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["name"]}

    add_parameter(schema, "name", "string", "Environment name", required=True)
    add_parameter(schema, "description", "string", "Environment description", required=False)
    add_parameter(
        schema,
        "color",
        "string",
        "Display color (blue, green, gold, red, purple, or light variants)",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {"name": "Production"},
        {"name": "Staging", "color": "blue", "description": "Staging env"},
    ]

    return create_tool_definition(
        name="honeycomb_create_environment",
        description=get_description("honeycomb_create_environment"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_environment_tool() -> dict[str, Any]:
    """Generate honeycomb_update_environment tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["env_id"]}

    add_parameter(schema, "env_id", "string", "The environment ID", required=True)
    add_parameter(schema, "description", "string", "New description", required=False)
    add_parameter(schema, "color", "string", "New color", required=False)
    add_parameter(
        schema,
        "delete_protected",
        "boolean",
        "Enable (true) or disable (false) delete protection",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {"env_id": "hcaen_123", "description": "Updated description"},
        {"env_id": "hcaen_123", "delete_protected": False},
    ]

    return create_tool_definition(
        name="honeycomb_update_environment",
        description=get_description("honeycomb_update_environment"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_environment_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_environment tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["env_id"]}

    add_parameter(schema, "env_id", "string", "The environment ID to delete", required=True)

    examples: list[dict[str, Any]] = [{"env_id": "hcaen_123"}]

    return create_tool_definition(
        name="honeycomb_delete_environment",
        description=get_description("honeycomb_delete_environment"),
        input_schema=schema,
        input_examples=examples,
    )


# ==============================================================================
# Generator Functions
# ==============================================================================


def generate_all_tools() -> list[dict[str, Any]]:
    """Generate all tool definitions.

    Returns:
        List of 67 tool definitions:
        - Auth (1) = 1 tool
        - API Keys (5) + Environments (5) = 10 tools
        - Priority 1: Triggers (5), SLOs (5), Burn Alerts (5) = 15 tools
        - Batch 1: Datasets (5), Columns (5) = 10 tools
        - Batch 2: Recipients (6), Derived Columns (5) = 11 tools
        - Batch 3a: Queries (3) = 3 tools
        - Batch 3b: Boards (5) = 5 tools
        - Batch 4: Markers (4), Marker Settings (5), Events (2), Service Map (1) = 12 tools
    """
    tools = [
        # Auth (foundational)
        generate_get_auth_tool(),
        # Team Management (v2)
        generate_list_api_keys_tool(),
        generate_get_api_key_tool(),
        generate_create_api_key_tool(),
        generate_update_api_key_tool(),
        generate_delete_api_key_tool(),
        generate_list_environments_tool(),
        generate_get_environment_tool(),
        generate_create_environment_tool(),
        generate_update_environment_tool(),
        generate_delete_environment_tool(),
        # Priority 1: Triggers
        generate_list_triggers_tool(),
        generate_get_trigger_tool(),
        generate_create_trigger_tool(),
        generate_update_trigger_tool(),
        generate_delete_trigger_tool(),
        # Priority 1: SLOs
        generate_list_slos_tool(),
        generate_get_slo_tool(),
        generate_create_slo_tool(),
        generate_update_slo_tool(),
        generate_delete_slo_tool(),
        # Priority 1: Burn Alerts
        generate_list_burn_alerts_tool(),
        generate_get_burn_alert_tool(),
        generate_create_burn_alert_tool(),
        generate_update_burn_alert_tool(),
        generate_delete_burn_alert_tool(),
        # Batch 1: Datasets
        generate_list_datasets_tool(),
        generate_get_dataset_tool(),
        generate_create_dataset_tool(),
        generate_update_dataset_tool(),
        generate_delete_dataset_tool(),
        # Batch 1: Columns
        generate_list_columns_tool(),
        generate_get_column_tool(),
        generate_create_column_tool(),
        generate_update_column_tool(),
        generate_delete_column_tool(),
        # Batch 2: Recipients
        generate_list_recipients_tool(),
        generate_get_recipient_tool(),
        generate_create_recipient_tool(),
        generate_update_recipient_tool(),
        generate_delete_recipient_tool(),
        generate_get_recipient_triggers_tool(),
        # Batch 2: Derived Columns
        generate_list_derived_columns_tool(),
        generate_get_derived_column_tool(),
        generate_create_derived_column_tool(),
        generate_update_derived_column_tool(),
        generate_delete_derived_column_tool(),
        # Batch 3a: Queries
        generate_create_query_tool(),
        generate_get_query_tool(),
        generate_run_query_tool(),
        # Batch 3b: Boards
        generate_list_boards_tool(),
        generate_get_board_tool(),
        generate_create_board_tool(),
        generate_update_board_tool(),
        generate_delete_board_tool(),
        # Batch 4: Markers
        generate_list_markers_tool(),
        generate_create_marker_tool(),
        generate_update_marker_tool(),
        generate_delete_marker_tool(),
        # Batch 4: Marker Settings
        generate_list_marker_settings_tool(),
        generate_get_marker_setting_tool(),
        generate_create_marker_setting_tool(),
        generate_update_marker_setting_tool(),
        generate_delete_marker_setting_tool(),
        # Batch 4: Events
        generate_send_event_tool(),
        generate_send_batch_events_tool(),
        # Batch 4: Service Map
        generate_query_service_map_tool(),
    ]

    return tools


def generate_tools_for_resource(resource: str) -> list[dict[str, Any]]:
    """Generate tool definitions for a specific resource.

    Args:
        resource: Resource name (triggers, slos, burn_alerts, datasets, columns, recipients, derived_columns, queries, boards)

    Returns:
        List of tool definitions for that resource

    Raises:
        ValueError: If resource name is invalid
    """
    generators = {
        "triggers": [
            generate_list_triggers_tool,
            generate_get_trigger_tool,
            generate_create_trigger_tool,
            generate_update_trigger_tool,
            generate_delete_trigger_tool,
        ],
        "slos": [
            generate_list_slos_tool,
            generate_get_slo_tool,
            generate_create_slo_tool,
            generate_update_slo_tool,
            generate_delete_slo_tool,
        ],
        "burn_alerts": [
            generate_list_burn_alerts_tool,
            generate_get_burn_alert_tool,
            generate_create_burn_alert_tool,
            generate_update_burn_alert_tool,
            generate_delete_burn_alert_tool,
        ],
        "datasets": [
            generate_list_datasets_tool,
            generate_get_dataset_tool,
            generate_create_dataset_tool,
            generate_update_dataset_tool,
            generate_delete_dataset_tool,
        ],
        "columns": [
            generate_list_columns_tool,
            generate_get_column_tool,
            generate_create_column_tool,
            generate_update_column_tool,
            generate_delete_column_tool,
        ],
        "recipients": [
            generate_list_recipients_tool,
            generate_get_recipient_tool,
            generate_create_recipient_tool,
            generate_update_recipient_tool,
            generate_delete_recipient_tool,
            generate_get_recipient_triggers_tool,
        ],
        "derived_columns": [
            generate_list_derived_columns_tool,
            generate_get_derived_column_tool,
            generate_create_derived_column_tool,
            generate_update_derived_column_tool,
            generate_delete_derived_column_tool,
        ],
        "queries": [
            generate_create_query_tool,
            generate_get_query_tool,
            generate_run_query_tool,
        ],
        "boards": [
            generate_list_boards_tool,
            generate_get_board_tool,
            generate_create_board_tool,
            generate_update_board_tool,
            generate_delete_board_tool,
        ],
        "markers": [
            generate_list_markers_tool,
            generate_create_marker_tool,
            generate_update_marker_tool,
            generate_delete_marker_tool,
        ],
        "marker_settings": [
            generate_list_marker_settings_tool,
            generate_get_marker_setting_tool,
            generate_create_marker_setting_tool,
            generate_update_marker_setting_tool,
            generate_delete_marker_setting_tool,
        ],
        "events": [
            generate_send_event_tool,
            generate_send_batch_events_tool,
        ],
        "service_map": [
            generate_query_service_map_tool,
        ],
    }

    if resource not in generators:
        raise ValueError(
            f"Invalid resource '{resource}'. Valid resources: {', '.join(generators.keys())}"
        )

    return [gen() for gen in generators[resource]]


def export_tools_json(tools: list[dict[str, Any]], output_path: str) -> None:
    """Export tool definitions to a JSON file.

    Args:
        tools: List of tool definitions
        output_path: Path to write JSON file
    """
    from datetime import datetime, timezone

    output = {
        "tools": tools,
        "version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(tools),
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)


def export_tools_python(tools: list[dict[str, Any]], output_path: str) -> None:
    """Export tool definitions to a Python module.

    Args:
        tools: List of tool definitions
        output_path: Path to write Python file
    """
    from datetime import datetime, timezone

    # Generate the Python code
    code = f'''"""Auto-generated Honeycomb tool definitions for Claude API.

Generated at: {datetime.now(timezone.utc).isoformat()}
Version: 0.1.0
Tool count: {len(tools)}
"""

from typing import Any

HONEYCOMB_TOOLS: list[dict[str, Any]] = {json.dumps(tools, indent=4)}


def get_tool(name: str) -> dict[str, Any] | None:
    """Get a tool definition by name.

    Args:
        name: Tool name (e.g., "honeycomb_create_trigger")

    Returns:
        Tool definition dict or None if not found
    """
    for tool in HONEYCOMB_TOOLS:
        if tool["name"] == name:
            return tool
    return None


def get_all_tools() -> list[dict[str, Any]]:
    """Get all tool definitions.

    Returns:
        List of all tool definitions
    """
    return HONEYCOMB_TOOLS.copy()


def list_tool_names() -> list[str]:
    """Get list of all tool names.

    Returns:
        List of tool names
    """
    return [tool["name"] for tool in HONEYCOMB_TOOLS]
'''

    with open(output_path, "w") as f:
        f.write(code)
