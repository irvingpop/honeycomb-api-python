"""API Keys tool definitions for Claude API.

This module provides tool generators and descriptions for
api keys resources.
"""

from typing import Any

from honeycomb.tools.schemas import add_parameter

# ==============================================================================
# API Keys Descriptions
# ==============================================================================

API_KEY_DESCRIPTIONS = {
    "honeycomb_list_api_keys": (
        "Lists all API keys for your authenticated team with optional filtering by key type. "
        "Use this to audit team API keys, discover existing keys before creating new ones, or when migrating to management key authentication. "
        "Requires management key authentication. The team is automatically detected from your credentials (no team parameter needed). "
        "Optional key_type parameter filters by 'ingest' or 'configuration' keys. "
        "Returns a list of API key objects with their IDs, names, types, environment associations, and disabled status. "
        "Note: The key secrets are not included in list responses for security."
    ),
    "honeycomb_get_api_key": (
        "Retrieves detailed information about a specific API key by ID. "
        "Use this to inspect an API key's configuration including name, type, environment, and disabled status before updating or deleting it. "
        "Requires only the key ID parameter - the team is automatically detected from your management key credentials. "
        "Returns the complete API key configuration but does NOT include the secret (only shown on creation). "
        "Use this to verify key settings or check which environment a key is associated with."
    ),
    "honeycomb_create_api_key": (
        "Creates a new API key for your authenticated team in a specific environment. "
        "Use this when provisioning new services, creating separate keys for different applications, or rotating credentials. "
        "Requires key name, key_type ('ingest' for data sending or 'configuration' for API access), and environment_id. The team is automatically detected from your management key. "
        "CRITICAL FOR CONFIGURATION KEYS: Must include permissions object with boolean properties. Available permissions: 'create_datasets', 'send_events', 'manage_markers', 'manage_triggers', 'manage_boards', 'run_queries', 'manage_columns', 'manage_slos', 'manage_recipients', 'manage_privateBoards'. "
        "Example for full access: {'create_datasets': true, 'send_events': true, 'manage_markers': true, 'manage_triggers': true, 'manage_boards': true, 'run_queries': true, 'manage_columns': true, 'manage_slos': true, 'manage_recipients': true, 'manage_privateBoards': true}. "
        "Without permissions object, configuration keys will have NO permissions and cannot perform any actions. "
        "Ingest keys have fixed permissions (send events, optionally create datasets implicitly) and don't use permissions object. "
        "CRITICAL: The secret is only returned once during creation - save it immediately. "
        "Returns the created API key object including the secret field (only time it's available)."
    ),
    "honeycomb_update_api_key": (
        "Updates an existing API key's name or disabled status. "
        "Use this to rename keys for clarity, disable compromised keys, or re-enable previously disabled keys. "
        "Requires key ID and at least one of: name (new display name) or disabled (true/false). The team is automatically detected from your credentials. "
        "Note: You cannot change the key type or environment after creation. To rotate the secret, delete and create a new key. "
        "The secret value is never returned in update responses."
    ),
    "honeycomb_delete_api_key": (
        "Permanently deletes an API key from Honeycomb. "
        "Use this when decommissioning services, rotating credentials after a security incident, or cleaning up unused keys. "
        "Requires only the key ID parameter - the team is automatically detected from your management key. "
        "Warning: This action cannot be undone. Any services using this key will immediately lose API access. "
        "The secret cannot be recovered - you must create a new key if deleted accidentally."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return API_KEY_DESCRIPTIONS[tool_name]


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
# API Keys Tool Definitions
# ==============================================================================


def generate_list_api_keys_tool() -> dict[str, Any]:
    """Generate honeycomb_list_api_keys tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    add_parameter(
        schema,
        "key_type",
        "string",
        "Filter by key type: 'ingest' or 'configuration'",
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {},
        {"key_type": "ingest"},
    ]

    return create_tool_definition(
        name="honeycomb_list_api_keys",
        description=get_description("honeycomb_list_api_keys"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_api_key_tool() -> dict[str, Any]:
    """Generate honeycomb_get_api_key tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["key_id"]}

    add_parameter(schema, "key_id", "string", "The API key ID", required=True)

    examples: list[dict[str, Any]] = [{"key_id": "hcaik_123"}]

    return create_tool_definition(
        name="honeycomb_get_api_key",
        description=get_description("honeycomb_get_api_key"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_api_key_tool() -> dict[str, Any]:
    """Generate honeycomb_create_api_key tool definition."""
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": ["name", "key_type", "environment_id"],
    }

    add_parameter(schema, "name", "string", "Display name for the API key", required=True)
    add_parameter(
        schema,
        "key_type",
        "string",
        "Type of key: 'ingest' or 'configuration'",
        required=True,
    )
    add_parameter(
        schema, "environment_id", "string", "Environment ID to scope the key to", required=True
    )
    add_parameter(
        schema,
        "permissions",
        "object",
        (
            "Permissions for configuration keys (REQUIRED for 'configuration' type). "
            "Object with boolean properties: 'create_datasets', 'send_events', 'manage_markers', "
            "'manage_triggers', 'manage_boards', 'run_queries', 'manage_columns', "
            "'manage_slos', 'manage_recipients', 'manage_privateBoards'. "
            "Example: {'create_datasets': true, 'send_events': true, 'manage_triggers': true}. "
            "Not needed for 'ingest' keys."
        ),
        required=False,
    )

    examples: list[dict[str, Any]] = [
        {
            "name": "Production Ingest Key",
            "key_type": "ingest",
            "environment_id": "hcaen_123",
        },
        {
            "name": "Full Access Config Key",
            "key_type": "configuration",
            "environment_id": "hcaen_123",
            "permissions": {
                "create_datasets": True,
                "send_events": True,
                "manage_markers": True,
                "manage_triggers": True,
                "manage_boards": True,
                "run_queries": True,
                "manage_columns": True,
                "manage_slos": True,
                "manage_recipients": True,
                "manage_privateBoards": True,
            },
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_api_key",
        description=get_description("honeycomb_create_api_key"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_api_key_tool() -> dict[str, Any]:
    """Generate honeycomb_update_api_key tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["key_id"]}

    add_parameter(schema, "key_id", "string", "The API key ID", required=True)
    add_parameter(schema, "name", "string", "New name for the key", required=False)
    add_parameter(schema, "disabled", "boolean", "Set to true to disable the key", required=False)

    examples: list[dict[str, Any]] = [
        {"key_id": "hcaik_123", "name": "New Name"},
        {"key_id": "hcaik_123", "disabled": True},
    ]

    return create_tool_definition(
        name="honeycomb_update_api_key",
        description=get_description("honeycomb_update_api_key"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_api_key_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_api_key tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["key_id"]}

    add_parameter(schema, "key_id", "string", "The API key ID to delete", required=True)

    examples: list[dict[str, Any]] = [{"key_id": "hcaik_123"}]

    return create_tool_definition(
        name="honeycomb_delete_api_key",
        description=get_description("honeycomb_delete_api_key"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all api keys tool definitions."""
    return [
        generate_list_api_keys_tool(),
        generate_get_api_key_tool(),
        generate_create_api_key_tool(),
        generate_update_api_key_tool(),
        generate_delete_api_key_tool(),
    ]
