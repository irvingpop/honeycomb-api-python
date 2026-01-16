"""Boards tool definitions for Claude API.

This module provides tool generators and descriptions for
boards resources.
"""

from typing import Any

from honeycomb.models import BoardCreate
from honeycomb.models.tool_inputs import BoardToolInput
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Boards Descriptions
# ==============================================================================

BOARD_DESCRIPTIONS = {
    "honeycomb_list_boards": (
        "Lists all boards (dashboards) in your Honeycomb environment (no parameters required). "
        "Use this to discover existing dashboards before creating new ones, audit dashboard organization, or find boards to update. "
        "This operation requires no parameters - it automatically lists all boards you have access to. "
        "Returns a list of board objects including their IDs, names, descriptions, panel configurations, and layout settings."
    ),
    "honeycomb_get_board": (
        "Retrieves detailed configuration for a specific board by its ID. "
        "Use this to inspect a board's panel layout, query configurations, SLO displays, and text content before modifying it. "
        "Requires the board ID parameter. "
        "Returns the complete board configuration including all panel definitions, layout mode (auto or manual), tags, and links to visualizations."
    ),
    "honeycomb_create_board": (
        "Creates a new board (dashboard) with panels, board views, and preset filters in a single operation. "
        "Use this to build comprehensive dashboards for service monitoring, create SRE views, or consolidate related visualizations. "
        "Requires a name and a 'panels' array. Each panel has a 'type' field: "
        "'query' (inline query panel - needs name, dataset, calculations), "
        "'text' (markdown panel - needs content), "
        "'slo' (inline SLO panel - needs name, dataset, sli, target_percentage), "
        "'existing_slo' (reference existing SLO by slo_id). "
        "IMPORTANT: Panels appear in the exact order specified in the array - this controls the visual layout. "
        "Query panels can include calculated_fields (derived columns) - see honeycomb_create_derived_column for expression syntax. "
        "For inline SLO panels with SLI expressions: must return boolean, use $ prefix for columns. Example: LT($status_code, 500). "
        "Board views allow creating filtered perspectives (max 50 per board): each view has a name and filters array with column, operation (=, !=, >, >=, <, <=, contains, starts-with, ends-with, exists, in), and value. "
        "Preset filters (max 5) allow dynamic filtering of board data: each has column and alias properties. "
        "Layout defaults to auto-layout (Honeycomb arranges panels) but supports manual layout with explicit positioning. "
        "The tool orchestrates: creating all inline queries with annotations, inline SLOs, board views, preset filters, assembling panel configurations, and creating the board with all components in one API call."
    ),
    "honeycomb_update_board": (
        "Updates an existing board's name, description, or panel configuration. "
        "Use this to add new panels, reorder visualizations, update board metadata, or reorganize dashboards as monitoring needs evolve. "
        "Requires the board ID and the complete updated board configuration. "
        "Note: This replaces the entire board configuration, so include all panels you want to preserve."
    ),
    "honeycomb_delete_board": (
        "Permanently deletes a board from Honeycomb. "
        "Use this when removing outdated dashboards, cleaning up test boards, or consolidating overlapping views. "
        "Requires the board ID parameter. "
        "Warning: This action cannot be undone. The board and its panel configurations will be permanently deleted, but the underlying queries and SLOs are preserved."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return BOARD_DESCRIPTIONS[tool_name]


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
# Boards Tool Definitions
# ==============================================================================


def generate_list_boards_tool() -> dict[str, Any]:
    """Generate honeycomb_list_boards tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    # No parameters - tool lists all boards in the environment
    # Empty examples cause API 500 errors, so we provide None to skip examples
    examples = None

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
    # Use Pydantic model for schema generation (replaces 300+ lines of manual schema building)
    schema = BoardToolInput.model_json_schema()

    examples: list[dict[str, Any]] = [
        # Simple: query panels with auto-layout
        {
            "name": "API Dashboard",
            "layout_generation": "auto",
            "panels": [
                {
                    "type": "query",
                    "name": "Error Count",
                    "dataset": "api-logs",
                    "time_range": 3600,
                    "calculations": [{"op": "COUNT"}],
                    "filters": [{"column": "status_code", "op": ">=", "value": 500}],
                },
                {
                    "type": "query",
                    "name": "P99 Latency",
                    "dataset": "api-logs",
                    "time_range": 3600,
                    "calculations": [{"op": "P99", "column": "duration_ms"}],
                },
            ],
        },
        # Mixed panel types - order is preserved
        {
            "name": "Service Overview",
            "description": "Main service health dashboard",
            "layout_generation": "auto",
            "panels": [
                {"type": "text", "content": "## Service Status\nMonitor during peak hours"},
                {
                    "type": "query",
                    "name": "Request Rate",
                    "dataset": "production",
                    "time_range": 7200,
                    "calculations": [{"op": "COUNT"}],
                    "breakdowns": ["endpoint"],
                },
            ],
        },
        # Complex: interleaved panel types with existing SLO
        {
            "name": "SRE Dashboard",
            "layout_generation": "auto",
            "panels": [
                {
                    "type": "query",
                    "name": "Error Rate",
                    "dataset": "api-logs",
                    "time_range": 3600,
                    "calculations": [{"op": "COUNT"}],
                    "filters": [{"column": "status_code", "op": ">=", "value": 500}],
                    "breakdowns": ["service"],
                    "orders": [{"op": "COUNT", "order": "descending"}],
                    "limit": 20,
                },
                {"type": "existing_slo", "slo_id": "slo-123"},
                {"type": "text", "content": "## Alerts\nCheck PagerDuty for incidents"},
            ],
            "tags": [{"key": "team", "value": "platform"}],
        },
        # Advanced: inline SLO creation with derived column
        {
            "name": "Production Monitoring",
            "layout_generation": "auto",
            "panels": [
                {
                    "type": "query",
                    "name": "Request Count",
                    "dataset": "production",
                    "time_range": 86400,
                    "calculations": [{"op": "COUNT"}],
                    "breakdowns": ["service"],
                },
                {
                    "type": "slo",
                    "name": "API Availability",
                    "dataset": "api-logs",
                    "sli": {
                        "alias": "success_rate",
                        "expression": "IF(LT($status_code, 400), 1, 0)",
                        "description": "1 if successful, 0 if error",
                    },
                    "target_percentage": 99.9,
                    "time_period_days": 30,
                    "description": "99.9% availability target",
                },
                {"type": "text", "content": "## SLO Policy\nReview weekly"},
            ],
        },
        # With board views for filtered perspectives
        {
            "name": "Service Dashboard",
            "layout_generation": "auto",
            "panels": [
                {
                    "type": "query",
                    "name": "Request Metrics",
                    "dataset": "api-logs",
                    "time_range": 3600,
                    "calculations": [{"op": "COUNT"}],
                    "breakdowns": ["service"],
                },
            ],
            "views": [
                {
                    "name": "Active Services",
                    "filters": [{"column": "status", "operation": "=", "value": "active"}],
                },
                {
                    "name": "Production Errors",
                    "filters": [
                        {"column": "environment", "operation": "=", "value": "production"},
                        {"column": "status_code", "operation": ">=", "value": 500},
                    ],
                },
            ],
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

    # Include $defs for nested models (QueryPanel, SLOPanel, etc.)
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

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


def get_tools() -> list[dict[str, Any]]:
    """Get all boards tool definitions."""
    return [
        generate_list_boards_tool(),
        generate_get_board_tool(),
        generate_create_board_tool(),
        generate_update_board_tool(),
        generate_delete_board_tool(),
    ]
