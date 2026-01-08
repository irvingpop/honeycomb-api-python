"""Columns tool definitions for Claude API.

This module provides tool generators and descriptions for
columns resources.
"""

from typing import Any

from honeycomb.models import ColumnCreate
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Columns Descriptions
# ==============================================================================

COLUMN_DESCRIPTIONS = {
    "honeycomb_list_columns": (
        "Lists all columns defined in a dataset's schema. "
        "Use this to discover available fields for querying, understand your data structure, or validate that new columns are being sent correctly. "
        "Requires the dataset slug parameter. "
        "Returns a list of column objects including their IDs, key names, types (string, integer, float, boolean), descriptions, hidden status, and timestamps."
    ),
    "honeycomb_get_column": (
        "Retrieves detailed information about a specific column by its ID. "
        "Use this to inspect a column's configuration including its data type, visibility, description, and usage statistics. "
        "Requires both the dataset slug and column ID parameters. "
        "Returns the complete column configuration including creation timestamp, last update timestamp, and last written timestamp."
    ),
    "honeycomb_create_column": (
        "Creates a new column in a dataset's schema. "
        "Use this to pre-define columns before sending data, add metadata like descriptions, or create hidden columns for internal fields. "
        "Requires the dataset slug and key_name (the column identifier). "
        "Optional parameters include type (string, integer, float, boolean - defaults to string), description for documentation, and hidden flag to exclude from autocomplete. "
        "Columns are automatically created when new fields appear in events, but pre-defining them allows you to set type and visibility."
    ),
    "honeycomb_update_column": (
        "Updates an existing column's description, type, or visibility settings. "
        "Use this to add documentation to columns, change data types, or hide internal debugging fields from query builders. "
        "Requires the dataset slug, column ID, and the complete updated column configuration. "
        "Note: Changing the type doesn't convert existing data, it only affects how the column is displayed and queried in the UI."
    ),
    "honeycomb_delete_column": (
        "Permanently deletes a column from a dataset's schema. "
        "Use this when cleaning up unused columns or removing fields that are no longer being sent. "
        "Requires both the dataset slug and column ID parameters. "
        "Warning: This action cannot be undone. The column definition will be removed, but existing event data containing this field is preserved."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return COLUMN_DESCRIPTIONS[tool_name]


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


def get_tools() -> list[dict[str, Any]]:
    """Get all columns tool definitions."""
    return [
        generate_list_columns_tool(),
        generate_get_column_tool(),
        generate_create_column_tool(),
        generate_update_column_tool(),
        generate_delete_column_tool(),
    ]
