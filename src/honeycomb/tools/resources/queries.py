"""Queries tool definitions for Claude API.

This module provides tool generators and descriptions for
queries resources.
"""

from typing import Any

from honeycomb.models import QuerySpec
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Queries Descriptions
# ==============================================================================

QUERY_DESCRIPTIONS = {
    "honeycomb_create_query": (
        "Creates a new saved query in a dataset that can be reused in boards, analysis, or referenced by ID. "
        "Use this to save frequently-used queries, create queries for dashboard panels, or prepare queries for trigger definitions. "
        "Requires the dataset slug and query specification including time_range and calculations. "
        "Optional annotation_name parameter creates the query with a display name for easier identification in the UI. "
        "The query specification supports multiple calculations (unlike triggers which allow only one), filters, breakdowns, orders, havings, and limits for comprehensive data analysis."
        "Queries can include calculated_fields (derived columns) - see honeycomb_create_derived_column for expression syntax. "
    ),
    "honeycomb_get_query": (
        "Retrieves a saved query's configuration by its ID. "
        "Use this to inspect an existing query's calculations, filters, time range, and other settings before modifying it or using it as a template. "
        "Requires both the dataset slug and query ID parameters. "
        "Returns the complete query specification including all calculation definitions, filter conditions, breakdown fields, and ordering rules."
    ),
    "honeycomb_run_query": (
        "Creates a saved query, executes it, and returns results with automatic polling until completion. "
        "Use this for ad-hoc data analysis, investigating issues, or when you want both a saved query and immediate results in one operation. "
        "Requires the dataset slug (or '__all__' for environment-wide queries) and query specification (time_range, calculations, optional filters/breakdowns/orders/havings/limit). "
        "This tool performs two operations: first creates a permanent saved query, then executes it with polling and returns the query results including data rows and metadata. "
        "Supports all query features including multiple calculations (COUNT, AVG, SUM, MIN, MAX, P50-P99, HEATMAP, RATE_*), complex filters, breakdowns, ordering, HAVING clauses, and result limits."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return QUERY_DESCRIPTIONS[tool_name]


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


def get_tools() -> list[dict[str, Any]]:
    """Get all queries tool definitions."""
    return [
        generate_create_query_tool(),
        generate_get_query_tool(),
        generate_run_query_tool(),
    ]
