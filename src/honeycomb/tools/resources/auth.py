"""Auth tool definitions for Claude API.

This module provides tool generators and descriptions for
auth resources.
"""

from typing import Any

from honeycomb.tools.schemas import add_parameter

# ==============================================================================
# Auth Descriptions
# ==============================================================================

AUTH_DESCRIPTIONS = {
    "honeycomb_get_auth": (
        "Returns metadata about the API key used to authenticate with Honeycomb. "
        "Use this to verify authentication is working correctly, check key permissions and scopes, "
        "or discover which team and environment the key belongs to. "
        "Automatically detects whether to use the v1 endpoint (for regular API keys) or "
        "v2 endpoint (for management keys) based on the configured credentials. "
        "Set use_v2=true to explicitly request management key information, which includes "
        "scopes and team details. Returns an error if use_v2=true but management credentials "
        "are not configured."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return AUTH_DESCRIPTIONS[tool_name]


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
# Auth Tool Definitions
# ==============================================================================


def generate_get_auth_tool() -> dict[str, Any]:
    """Generate the honeycomb_get_auth tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    add_parameter(
        schema,
        "use_v2",
        "boolean",
        (
            "Force use of v2 endpoint for management key info. "
            "If not specified, auto-detects based on configured credentials."
        ),
        required=False,
    )

    examples = [
        {},
        {"use_v2": True},
    ]

    return create_tool_definition(
        name="honeycomb_get_auth",
        description=get_description("honeycomb_get_auth"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all auth tool definitions."""
    return [
        generate_get_auth_tool(),
    ]
