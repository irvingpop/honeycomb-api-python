"""Core tool definition generator for Claude API.

This module aggregates tool definitions from resource-specific modules.
"""

import json
from typing import Any

from honeycomb.tools import resources


# Re-export create_tool_definition for backwards compatibility
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


# Resource module mapping
RESOURCE_MODULES = {
    "api_keys": resources.api_keys,
    "auth": resources.auth,
    "boards": resources.boards,
    "burn_alerts": resources.burn_alerts,
    "columns": resources.columns,
    "datasets": resources.datasets,
    "derived_columns": resources.derived_columns,
    "environments": resources.environments,
    "events": resources.events,
    "marker_settings": resources.marker_settings,
    "markers": resources.markers,
    "queries": resources.queries,
    "recipients": resources.recipients,
    "service_map": resources.service_map,
    "slos": resources.slos,
    "triggers": resources.triggers,
}


def generate_all_tools() -> list[dict[str, Any]]:
    """Generate all tool definitions.

    Returns:
        List of 67 tool definitions from all resources.
    """
    tools = []

    # Order matters for logical grouping
    resource_order = [
        "auth",
        "api_keys",
        "environments",
        "triggers",
        "slos",
        "burn_alerts",
        "datasets",
        "columns",
        "recipients",
        "derived_columns",
        "queries",
        "boards",
        "markers",
        "marker_settings",
        "events",
        "service_map",
    ]

    for resource in resource_order:
        module = RESOURCE_MODULES[resource]
        tools.extend(module.get_tools())

    return tools


def generate_tools_for_resource(resource: str) -> list[dict[str, Any]]:
    """Generate tool definitions for a specific resource.

    Args:
        resource: Resource name (triggers, slos, burn_alerts, etc.)

    Returns:
        List of tool definitions for that resource

    Raises:
        ValueError: If resource name is invalid
    """
    if resource not in RESOURCE_MODULES:
        raise ValueError(
            f"Invalid resource '{resource}'. "
            f"Valid resources: {', '.join(sorted(RESOURCE_MODULES.keys()))}"
        )

    return RESOURCE_MODULES[resource].get_tools()


def export_tools_json(tools: list[dict[str, Any]], output_path: str) -> None:
    """Export tool definitions to a JSON file.

    Args:
        tools: List of tool definitions
        output_path: Path to write JSON file
    """
    output = {"tools": tools}

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)


def export_tools_python(tools: list[dict[str, Any]], output_path: str) -> None:
    """Export tool definitions to a Python module.

    Args:
        tools: List of tool definitions
        output_path: Path to write Python file
    """
    from datetime import datetime, timezone

    code = f'''"""Auto-generated Honeycomb tool definitions for Claude API.

Generated at: {datetime.now(timezone.utc).isoformat()}
Version: 0.1.0
Tool count: {len(tools)}
"""

from typing import Any

HONEYCOMB_TOOLS: list[dict[str, Any]] = {json.dumps(tools, indent=4)}


def get_tool(name: str) -> dict[str, Any] | None:
    """Get a tool definition by name."""
    for tool in HONEYCOMB_TOOLS:
        if tool["name"] == name:
            return tool
    return None


def get_all_tools() -> list[dict[str, Any]]:
    """Get all tool definitions."""
    return HONEYCOMB_TOOLS.copy()


def list_tool_names() -> list[str]:
    """Get list of all tool names."""
    return [tool["name"] for tool in HONEYCOMB_TOOLS]
'''

    with open(output_path, "w") as f:
        f.write(code)
