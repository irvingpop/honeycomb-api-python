"""Analysis tool definitions for Claude API.

This module provides tool generators and descriptions for
cross-cutting analysis tools that operate across multiple resources.
"""

from typing import Any

from honeycomb.tools.schemas import add_parameter

# ==============================================================================
# Analysis Tool Descriptions
# ==============================================================================

ANALYSIS_DESCRIPTIONS = {
    "honeycomb_search_columns": (
        "Search for columns in Honeycomb datasets by name pattern. "
        "Use this tool to find columns that match metrics from source dashboards, "
        "discover available fields for querying, or understand your data schema. "
        "Returns column names, types, descriptions, and which dataset they belong to. "
        "Includes both regular columns and derived columns. "
        "Supports fuzzy matching with similarity scores and pagination. "
        "Also returns related derived columns that reference the matched columns."
    ),
    "honeycomb_get_environment_summary": (
        "Get a summary of all datasets in the Honeycomb environment. "
        "Use this tool to understand what datasets exist and their characteristics "
        "before deciding which dataset(s) to use for queries or translations. "
        "Returns dataset names, descriptions, column counts, derived column counts, "
        "and detects OpenTelemetry semantic convention groups (HTTP, traces, DB, K8s, etc.). "
        "Also extracts custom columns unique to each dataset that are not standard OTel fields. "
        "Useful for environment discovery, data inventory, and migration planning."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return ANALYSIS_DESCRIPTIONS[tool_name]


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
# Analysis Tool Definitions
# ==============================================================================


def generate_search_columns_tool() -> dict[str, Any]:
    """Generate honeycomb_search_columns tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["query"]}

    add_parameter(
        schema,
        "query",
        "string",
        "Search query (partial column name, supports fuzzy matching)",
        required=True,
    )
    add_parameter(
        schema,
        "dataset",
        "string",
        "Optional: specific dataset slug to search. If omitted, searches all datasets.",
        required=False,
    )
    add_parameter(
        schema,
        "limit",
        "integer",
        "Maximum results to return (default: 50, max: 1000)",
        required=False,
    )
    add_parameter(
        schema,
        "offset",
        "integer",
        "Offset for pagination (default: 0)",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {"query": "latency"},
        {"query": "error", "dataset": "api-logs"},
        {"query": "http.status", "limit": 100},
        {"query": "duration", "offset": 50, "limit": 50},
    ]

    return create_tool_definition(
        name="honeycomb_search_columns",
        description=get_description("honeycomb_search_columns"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_environment_summary_tool() -> dict[str, Any]:
    """Generate honeycomb_get_environment_summary tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    add_parameter(
        schema,
        "include_sample_columns",
        "boolean",
        "Include sample custom column names for each dataset (default: true)",
        required=False,
    )
    add_parameter(
        schema,
        "sample_column_count",
        "integer",
        "Number of sample custom columns per dataset (default: 10, max: 50)",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {},
        {"include_sample_columns": True},
        {"include_sample_columns": True, "sample_column_count": 20},
        {"include_sample_columns": False},
    ]

    return create_tool_definition(
        name="honeycomb_get_environment_summary",
        description=get_description("honeycomb_get_environment_summary"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all analysis tool definitions."""
    return [
        generate_search_columns_tool(),
        generate_get_environment_summary_tool(),
    ]
