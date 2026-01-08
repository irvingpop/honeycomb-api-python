"""Markers tool definitions for Claude API.

This module provides tool generators and descriptions for
markers resources.
"""

from typing import Any

from honeycomb.models import MarkerCreate
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Markers Descriptions
# ==============================================================================

MARKER_DESCRIPTIONS = {
    "honeycomb_list_markers": (
        "Lists all markers (event annotations) in a dataset. "
        "Use this to view deployment history, configuration changes, incidents, or other significant events marked on your data. "
        "Requires the dataset slug parameter. "
        "Returns a list of marker objects including their IDs, messages, types, timestamps, colors, and URLs."
    ),
    "honeycomb_create_marker": (
        "Creates a new marker to annotate your data with significant events like deployments, configuration changes, or incidents. "
        "Use this to track deployments, mark maintenance windows, document configuration changes, or flag incidents for correlation with metrics. "
        "Requires dataset slug (or '__all__' for environment-wide), message, and type parameters. "
        "Optional color parameter (hex code like '#FF5733') can be provided for visual customization - if the marker setting for that type doesn't exist, it should be created first. "
        "Optional start_time and end_time (Unix timestamps) create time-range markers, otherwise defaults to current time as a point marker."
    ),
    "honeycomb_update_marker": (
        "Updates an existing marker's message, type, timestamps, or URL. "
        "Use this to correct marker details, update deployment notes, or adjust time ranges for maintenance windows. "
        "Requires the dataset slug, marker ID, and updated marker configuration. "
        "Note: Colors are controlled by marker settings, not directly on markers."
    ),
    "honeycomb_delete_marker": (
        "Permanently deletes a marker from a dataset. "
        "Use this when removing incorrect markers, cleaning up test annotations, or removing outdated event tracking. "
        "Requires both the dataset slug and marker ID parameters. "
        "Warning: This action cannot be undone. The marker will be removed from all visualizations."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return MARKER_DESCRIPTIONS[tool_name]


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


def get_tools() -> list[dict[str, Any]]:
    """Get all markers tool definitions."""
    return [
        generate_list_markers_tool(),
        generate_create_marker_tool(),
        generate_update_marker_tool(),
        generate_delete_marker_tool(),
    ]
