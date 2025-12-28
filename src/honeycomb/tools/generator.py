"""Core tool definition generator for Claude API.

This module generates Claude-compatible tool definitions for Honeycomb API operations.
"""

import json
from typing import Any

from honeycomb.models import (
    BurnAlertCreate,
    ColumnCreate,
    DatasetCreate,
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
        # Exhaustion time alert with ID-based recipient
        {
            "dataset": "api-logs",
            "alert_type": "exhaustion_time",
            "slo_id": "slo-123",
            "exhaustion_minutes": 60,
            "recipients": [{"id": "recip-123"}],
        },
        # Budget rate alert with inline recipients
        {
            "dataset": "production",
            "alert_type": "budget_rate",
            "slo_id": "slo-456",
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
            "slo_id": "slo-789",
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

    add_parameter(schema, "dataset", "string", "The dataset slug to list columns from", required=True)

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
# Generator Functions
# ==============================================================================


def generate_all_tools() -> list[dict[str, Any]]:
    """Generate all tool definitions.

    Returns:
        List of 25 tool definitions:
        - Priority 1: Triggers (5), SLOs (5), Burn Alerts (5) = 15 tools
        - Batch 1: Datasets (5), Columns (5) = 10 tools
    """
    tools = [
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
    ]

    return tools


def generate_tools_for_resource(resource: str) -> list[dict[str, Any]]:
    """Generate tool definitions for a specific resource.

    Args:
        resource: Resource name (triggers, slos, burn_alerts, datasets, columns)

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
