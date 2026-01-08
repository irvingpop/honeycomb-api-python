"""Derived Columns tool definitions for Claude API.

This module provides tool generators and descriptions for
derived columns resources.
"""

from typing import Any

from honeycomb.models import DerivedColumnCreate
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Derived Columns Descriptions
# ==============================================================================

_DERIVED_COLUMN_SYNTAX_GUIDE = """
EXPRESSION SYNTAX REFERENCE:
- Column refs: $column_name or $"column with spaces" (CASE-SENSITIVE)
- Strings: double quotes ("value")
- Regex patterns: backticks (`pattern`)
- DCs operate on ONE ROW at a time - they are NOT aggregation functions

CONDITIONALS:
- IF(cond, true_val, false_val) - e.g., IF(LT($status, 400), "ok", "error")
- SWITCH($field, "case1", result1, "case2", result2, default) - string matching
- COALESCE(a, b, c) - first non-null value

COMPARISONS (return bool):
- LT, LTE, GT, GTE - e.g., LT($duration_ms, 1000)
- EQUALS($a, $b) - e.g., EQUALS($method, "GET")
- IN($field, val1, val2, ...) - e.g., IN($status, 200, 201, 204)

BOOLEAN:
- EXISTS($field) - true if field is non-null
- NOT(cond), AND(a, b, ...), OR(a, b, ...)

MATH: MIN, MAX, SUM, SUB, MUL, DIV, MOD, LOG10

STRING:
- CONCAT($a, " ", $b) - join strings
- STARTS_WITH($str, "prefix"), ENDS_WITH, CONTAINS - return bool
- TO_LOWER($str), LENGTH($str)

REGEX (use backticks for patterns):
- REG_MATCH($str, `pattern`) - returns bool
- REG_VALUE($str, `^/api/(.+)`) - extracts first capture group
- REG_COUNT($str, `pattern`) - count matches

TIME:
- EVENT_TIMESTAMP() - event time as Unix timestamp
- UNIX_TIMESTAMP($field) - parse field as timestamp
- FORMAT_TIME("%Y-%m-%d", $timestamp_field) - strftime formatting

DATA: BUCKET($val, size) - numeric bucketing

TYPE CONVERSION: INT(), FLOAT(), BOOL(), STRING()

COMMON PATTERNS:
- SLI for SLOs (MUST return boolean; 1/0 coerced to true/false): LT($status_code, 500)
- Root span detection: NOT(EXISTS($trace.parent_id))
- Error classification: IF(GTE($status, 500), "server_error", IF(GTE($status, 400), "client_error", "success"))
"""

DERIVED_COLUMN_DESCRIPTIONS = {
    "honeycomb_list_derived_columns": (
        "Lists all derived columns (calculated fields) in a dataset. "
        "Use this to discover existing calculated fields before creating new ones, understand available computed metrics, or audit data transformations. "
        "Requires the dataset slug parameter (use '__all__' to list environment-wide derived columns). "
        "Returns a list of derived column objects including their IDs, aliases, expressions, and descriptions."
    ),
    "honeycomb_get_derived_column": (
        "Retrieves detailed configuration for a specific derived column by ID. "
        "Use this to inspect a derived column's expression syntax, alias, and description before modifying it. "
        "Requires both the dataset slug and derived column ID parameters. "
        "Returns the complete derived column configuration including the calculation expression and metadata."
    ),
    "honeycomb_create_derived_column": (
        "Creates a new standalone derived column that calculates values from event fields using expressions. "
        "Use this for general-purpose computed metrics, data normalization, or calculations that will be used in multiple queries. "
        "NOTE: If you are creating a derived column specifically for an SLO, use honeycomb_create_slo instead with an inline SLI expression - it creates both in one operation. "
        "Requires the dataset slug (use '__all__' for environment-wide), an alias (the column name), and an expression. "
        "Optional description parameter documents the column's purpose for team members. "
        + _DERIVED_COLUMN_SYNTAX_GUIDE
    ),
    "honeycomb_update_derived_column": (
        "Updates an existing derived column's alias, expression, or description. "
        "Use this to fix calculation logic, rename computed fields, or improve documentation as your understanding evolves. "
        "Requires the dataset slug, derived column ID, and the complete updated configuration. "
        "Note: Changing the expression only affects new queries - existing query results are not recalculated. "
        + _DERIVED_COLUMN_SYNTAX_GUIDE
    ),
    "honeycomb_delete_derived_column": (
        "Permanently deletes a derived column from a dataset. "
        "Use this when removing unused calculated fields or cleaning up temporary analysis columns. "
        "Requires both the dataset slug and derived column ID parameters. "
        "Warning: This action cannot be undone. SLOs, triggers, or queries using this derived column may break if they reference it."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return DERIVED_COLUMN_DESCRIPTIONS[tool_name]


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


def get_tools() -> list[dict[str, Any]]:
    """Get all derived columns tool definitions."""
    return [
        generate_list_derived_columns_tool(),
        generate_get_derived_column_tool(),
        generate_create_derived_column_tool(),
        generate_update_derived_column_tool(),
        generate_delete_derived_column_tool(),
    ]
