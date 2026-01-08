"""Service Map tool definitions for Claude API.

This module provides tool generators and descriptions for
service map resources.
"""

from typing import Any

from honeycomb.models import ServiceMapDependencyRequestCreate
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Service Map Descriptions
# ==============================================================================

SERVICE_MAP_DESCRIPTIONS = {
    "honeycomb_query_service_map": (
        "Queries service dependencies and relationships from distributed trace data with automatic polling and pagination. "
        "Use this to discover service-to-service call patterns, identify dependencies, visualize system architecture, or debug cross-service issues. "
        "Requires a time range specification (time_range in seconds, or start_time/end_time as Unix timestamps). "
        "Optional filters parameter allows narrowing to specific services by name. "
        "This tool performs create + poll + paginate operations automatically: creates async query, polls until ready, fetches all pages of results (up to 64K dependencies). "
        "Warning: Large time ranges may return thousands of dependencies across hundreds of API pages - use max_pages parameter to limit."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return SERVICE_MAP_DESCRIPTIONS[tool_name]


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
# Service Map Tool Definitions
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

    # Add definitions if present (for nested models like ServiceMapNode)
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

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


def get_tools() -> list[dict[str, Any]]:
    """Get all service map tool definitions."""
    return [
        generate_query_service_map_tool(),
    ]
