"""Marker Settings tool definitions for Claude API.

This module provides tool generators and descriptions for
marker settings resources.
"""

from typing import Any

from honeycomb.models import MarkerSettingCreate
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Marker Settings Descriptions
# ==============================================================================

MARKER_SETTING_DESCRIPTIONS = {
    "honeycomb_list_marker_settings": (
        "Lists all marker type-to-color mappings for a dataset. "
        "Use this as the primary way to view all marker settings, see which marker types have custom colors, or audit marker visualization configuration. "
        "Requires the dataset slug parameter (or '__all__' for environment-wide settings). "
        "Returns a list of all marker settings showing type names (e.g., 'deploy', 'incident') and their associated hex color codes."
    ),
    "honeycomb_get_marker_setting": (
        "Retrieves a specific marker setting by its ID. "
        "Use this rarely when you need a specific setting by ID - prefer list_marker_settings to view all settings. "
        "Requires both the dataset slug and setting ID parameters. "
        "Returns the marker setting configuration including type name and color code."
    ),
    "honeycomb_create_marker_setting": (
        "Creates a new marker type-to-color mapping. "
        "Use this to assign colors to marker types for visual consistency (e.g., deployments in green, incidents in red). "
        "Requires the dataset slug (or '__all__' for environment-wide), marker type name, and hex color code (e.g., '#00FF00'). "
        "Once created, all markers of this type will display in the specified color on graphs and timelines."
    ),
    "honeycomb_update_marker_setting": (
        "Updates an existing marker setting's type or color. "
        "Use this to change marker colors for better visual distinction or rename marker types. "
        "Requires the dataset slug, setting ID, and updated configuration (type and color). "
        "The color change applies immediately to all existing and future markers of this type."
    ),
    "honeycomb_delete_marker_setting": (
        "Permanently deletes a marker setting. "
        "Use this when removing unused marker types or resetting color customizations. "
        "Requires both the dataset slug and setting ID parameters. "
        "Warning: Existing markers of this type will lose their custom color and revert to default visualization."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return MARKER_SETTING_DESCRIPTIONS[tool_name]


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
# Marker Settings Tool Definitions
# ==============================================================================


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


def get_tools() -> list[dict[str, Any]]:
    """Get all marker settings tool definitions."""
    return [
        generate_list_marker_settings_tool(),
        generate_get_marker_setting_tool(),
        generate_create_marker_setting_tool(),
        generate_update_marker_setting_tool(),
        generate_delete_marker_setting_tool(),
    ]
