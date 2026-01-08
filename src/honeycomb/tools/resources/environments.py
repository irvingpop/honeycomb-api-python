"""Environments tool definitions for Claude API.

This module provides tool generators and descriptions for
environments resources.
"""

from typing import Any

from honeycomb.tools.schemas import add_parameter

# ==============================================================================
# Environments Descriptions
# ==============================================================================

ENVIRONMENT_DESCRIPTIONS = {
    "honeycomb_list_environments": (
        "Lists all environments for your authenticated team. "
        "Use this to discover existing environments, understand team organization, or before creating API keys scoped to specific environments. "
        "Requires management key authentication. The team is automatically detected from your credentials (no team parameter needed). "
        "Returns a list of environment objects with their IDs, names, slugs, colors, descriptions, and delete protection status. "
        "Environments help organize your telemetry data by separating production, staging, development, etc."
    ),
    "honeycomb_get_environment": (
        "Retrieves detailed information about a specific environment by ID, optionally including its datasets. "
        "Use this to inspect an environment's configuration or get a complete view of an environment including all its datasets. "
        "Requires only the environment ID parameter - the team is automatically detected from your management key. "
        "Set with_datasets=true to also return the list of datasets in this environment (useful for understanding environment contents). "
        "Returns the environment configuration plus optionally a datasets array with all datasets in this environment."
    ),
    "honeycomb_create_environment": (
        "Creates a new environment for organizing telemetry data within your authenticated team. "
        "Use this when setting up new deployment stages (production, staging, dev), isolating customer data, or creating test environments. "
        "Requires only the environment name - the team is automatically detected from your management key. "
        "Optional parameters include description for documentation and color (blue, green, gold, red, purple, or light variants) for visual distinction. "
        "The environment slug is auto-generated from the name and used for API operations and dataset scoping. "
        "New environments are delete-protected by default to prevent accidental deletion."
    ),
    "honeycomb_update_environment": (
        "Updates an existing environment's description, color, or delete protection status. "
        "Use this to add documentation, change visual appearance, or enable/disable delete protection for production environments. "
        "Requires environment ID and at least one of: description, color, or delete_protected (boolean). The team is automatically detected from your credentials. "
        "Note: The name and slug cannot be changed after creation. Setting delete_protected=true prevents accidental deletion. "
        "To delete a protected environment, you must first update it with delete_protected=false."
    ),
    "honeycomb_delete_environment": (
        "Permanently deletes an environment from Honeycomb. "
        "Use this when decommissioning deployment stages, cleaning up test environments, or reorganizing team structure. "
        "Requires only the environment ID parameter - the team is automatically detected from your management key. "
        "Warning: This action cannot be undone. The environment must not be delete-protected. "
        "All API keys scoped to this environment will become invalid. Datasets are NOT deleted automatically."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return ENVIRONMENT_DESCRIPTIONS[tool_name]


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
# Environments Tool Definitions
# ==============================================================================


def generate_list_environments_tool() -> dict[str, Any]:
    """Generate honeycomb_list_environments tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    examples: list[dict[str, Any]] = [{}]

    return create_tool_definition(
        name="honeycomb_list_environments",
        description=get_description("honeycomb_list_environments"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_environment_tool() -> dict[str, Any]:
    """Generate honeycomb_get_environment tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["env_id"]}

    add_parameter(schema, "env_id", "string", "The environment ID", required=True)
    add_parameter(
        schema,
        "with_datasets",
        "boolean",
        "Also return list of datasets in this environment",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {"env_id": "hcaen_123"},
        {"env_id": "hcaen_123", "with_datasets": True},
    ]

    return create_tool_definition(
        name="honeycomb_get_environment",
        description=get_description("honeycomb_get_environment"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_environment_tool() -> dict[str, Any]:
    """Generate honeycomb_create_environment tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["name"]}

    add_parameter(schema, "name", "string", "Environment name", required=True)
    add_parameter(schema, "description", "string", "Environment description", required=False)
    add_parameter(
        schema,
        "color",
        "string",
        "Display color (blue, green, gold, red, purple, or light variants)",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {"name": "Production"},
        {"name": "Staging", "color": "blue", "description": "Staging env"},
    ]

    return create_tool_definition(
        name="honeycomb_create_environment",
        description=get_description("honeycomb_create_environment"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_environment_tool() -> dict[str, Any]:
    """Generate honeycomb_update_environment tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["env_id"]}

    add_parameter(schema, "env_id", "string", "The environment ID", required=True)
    add_parameter(schema, "description", "string", "New description", required=False)
    add_parameter(schema, "color", "string", "New color", required=False)
    add_parameter(
        schema,
        "delete_protected",
        "boolean",
        "Enable (true) or disable (false) delete protection",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {"env_id": "hcaen_123", "description": "Updated description"},
        {"env_id": "hcaen_123", "delete_protected": False},
    ]

    return create_tool_definition(
        name="honeycomb_update_environment",
        description=get_description("honeycomb_update_environment"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_environment_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_environment tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["env_id"]}

    add_parameter(schema, "env_id", "string", "The environment ID to delete", required=True)

    examples: list[dict[str, Any]] = [{"env_id": "hcaen_123"}]

    return create_tool_definition(
        name="honeycomb_delete_environment",
        description=get_description("honeycomb_delete_environment"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all environments tool definitions."""
    return [
        generate_list_environments_tool(),
        generate_get_environment_tool(),
        generate_create_environment_tool(),
        generate_update_environment_tool(),
        generate_delete_environment_tool(),
    ]
