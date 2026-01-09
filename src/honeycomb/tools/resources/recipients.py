"""Recipients tool definitions for Claude API.

This module provides tool generators and descriptions for
recipients resources.
"""

from typing import Any

from honeycomb.models.tool_inputs import RecipientCreateToolInput
from honeycomb.tools.schemas import add_parameter, generate_schema_from_model

# ==============================================================================
# Recipients Descriptions
# ==============================================================================

RECIPIENT_DESCRIPTIONS = {
    "honeycomb_list_recipients": (
        "Lists all notification recipients configured in your Honeycomb environment (no parameters required). "
        "Use this to discover existing notification targets before creating triggers, avoid duplicate recipients, or audit alerting destinations. "
        "This operation requires no parameters - it automatically lists all recipients across all types (email, Slack, PagerDuty, webhooks, MS Teams). "
        "Returns a list of recipient objects including their IDs, types, and configuration details."
    ),
    "honeycomb_get_recipient": (
        "Retrieves detailed configuration for a specific recipient by ID. "
        "Use this to inspect a recipient's type and delivery details before updating it or when troubleshooting notification issues. "
        "Requires the recipient ID parameter. "
        "Returns the complete recipient configuration including type-specific details like email addresses, Slack channels, or webhook URLs."
    ),
    "honeycomb_create_recipient": (
        "Creates a new notification recipient for alert delivery. "
        "Use this when setting up alerting for triggers or burn alerts, adding new on-call notification channels, or migrating alert destinations from another platform. "
        "Requires a type (email, slack, pagerduty, webhook, msteams_workflow) and type-specific details object. "
        "For email: provide 'email_address'. "
        "For Slack: provide 'slack_channel'. "
        "For PagerDuty: provide 'pagerduty_integration_key' and 'pagerduty_integration_name'. "
        "For webhooks: provide 'webhook_url' and 'webhook_name', optionally 'webhook_secret', 'webhook_headers' (max 5, for auth), and 'webhook_payloads' (for custom JSON templates with variables). "
        "For MS Teams: provide 'webhook_url' and 'webhook_name'. "
        "Recipients can be referenced by ID when creating or updating triggers and burn alerts."
    ),
    "honeycomb_update_recipient": (
        "Updates an existing recipient's configuration including its type or delivery details. "
        "Use this to change notification destinations, update Slack channels, rotate webhook secrets, or fix incorrect email addresses. "
        "Requires the recipient ID and the complete updated recipient configuration. "
        "Note: This replaces the entire recipient configuration, so include all fields you want to preserve."
    ),
    "honeycomb_delete_recipient": (
        "Permanently deletes a recipient from Honeycomb. "
        "Use this when removing unused notification channels, cleaning up test recipients, or decommissioning alert destinations. "
        "Requires the recipient ID parameter. "
        "Warning: This action cannot be undone. Any triggers or burn alerts using this recipient will have it removed from their notification list."
    ),
    "honeycomb_get_recipient_triggers": (
        "Retrieves all triggers that are configured to send notifications to a specific recipient. "
        "Use this before deleting a recipient to understand impact, when auditing alert routing, or troubleshooting why notifications aren't being sent. "
        "Requires the recipient ID parameter. "
        "Returns a list of trigger objects that reference this recipient, showing which datasets and alerts would be affected by changes."
    ),
}


def get_description(tool_name: str) -> str:
    """Get the description for a tool in this resource."""
    return RECIPIENT_DESCRIPTIONS[tool_name]


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
# Recipients Tool Definitions
# ==============================================================================


def generate_list_recipients_tool() -> dict[str, Any]:
    """Generate honeycomb_list_recipients tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    examples: list[dict[str, Any]] = [
        {},  # List all recipients
    ]

    return create_tool_definition(
        name="honeycomb_list_recipients",
        description=get_description("honeycomb_list_recipients"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_recipient_tool() -> dict[str, Any]:
    """Generate honeycomb_get_recipient tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["recipient_id"]}

    add_parameter(schema, "recipient_id", "string", "The recipient ID to retrieve", required=True)

    examples: list[dict[str, Any]] = [
        {"recipient_id": "rec-123"},
        {"recipient_id": "rec-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_recipient",
        description=get_description("honeycomb_get_recipient"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_create_recipient_tool() -> dict[str, Any]:
    """Generate honeycomb_create_recipient tool definition."""
    base_schema = generate_schema_from_model(
        RecipientCreateToolInput,
        exclude_fields={"id", "created_at", "updated_at"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add definitions if present
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples: list[dict[str, Any]] = [
        # Email recipient
        {
            "type": "email",
            "details": {"email_address": "alerts@example.com"},
        },
        # Slack channel
        {
            "type": "slack",
            "details": {"slack_channel": "#alerts"},
        },
        # PagerDuty
        {
            "type": "pagerduty",
            "details": {
                "pagerduty_integration_key": "1234567890abcdef1234567890abcdef",
                "pagerduty_integration_name": "Production Alerts",
            },
        },
        # Basic webhook
        {
            "type": "webhook",
            "details": {
                "webhook_url": "https://hooks.example.com/alerts",
                "webhook_name": "Alert Webhook",
                "webhook_secret": "webhook-secret-key",
            },
        },
        # Advanced webhook with auth header
        {
            "type": "webhook",
            "details": {
                "webhook_url": "https://api.example.com/notifications",
                "webhook_name": "Authenticated Webhook",
                "webhook_headers": [
                    {"header": "Authorization", "value": "Bearer api-key-123"},
                    {"header": "X-Environment", "value": "production"},
                ],
            },
        },
        # MS Teams workflow
        {
            "type": "msteams_workflow",
            "details": {
                "webhook_url": "https://test.logic.azure.com/workflows/abc/triggers/manual/paths/invoke",
                "webhook_name": "Team Alerts Channel",
            },
        },
    ]

    return create_tool_definition(
        name="honeycomb_create_recipient",
        description=get_description("honeycomb_create_recipient"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_update_recipient_tool() -> dict[str, Any]:
    """Generate honeycomb_update_recipient tool definition."""
    base_schema = generate_schema_from_model(
        RecipientCreateToolInput,
        exclude_fields={"id", "created_at", "updated_at"},
    )

    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["recipient_id"]}
    add_parameter(schema, "recipient_id", "string", "The recipient ID to update", required=True)

    schema["properties"].update(base_schema["properties"])
    schema["required"].extend(base_schema.get("required", []))

    # Add definitions if present
    if "$defs" in base_schema:
        schema["$defs"] = base_schema["$defs"]

    examples: list[dict[str, Any]] = [
        {
            "recipient_id": "rec-123",
            "type": "email",
            "details": {"email_address": "new-alerts@example.com"},
        },
        {
            "recipient_id": "rec-456",
            "type": "slack",
            "details": {"channel": "#new-alerts"},
        },
    ]

    return create_tool_definition(
        name="honeycomb_update_recipient",
        description=get_description("honeycomb_update_recipient"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_delete_recipient_tool() -> dict[str, Any]:
    """Generate honeycomb_delete_recipient tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["recipient_id"]}

    add_parameter(schema, "recipient_id", "string", "The recipient ID to delete", required=True)

    examples: list[dict[str, Any]] = [
        {"recipient_id": "rec-123"},
        {"recipient_id": "rec-456"},
    ]

    return create_tool_definition(
        name="honeycomb_delete_recipient",
        description=get_description("honeycomb_delete_recipient"),
        input_schema=schema,
        input_examples=examples,
    )


def generate_get_recipient_triggers_tool() -> dict[str, Any]:
    """Generate honeycomb_get_recipient_triggers tool definition."""
    schema: dict[str, Any] = {"type": "object", "properties": {}, "required": ["recipient_id"]}

    add_parameter(
        schema,
        "recipient_id",
        "string",
        "The recipient ID to get associated triggers for",
        required=True,
    )

    examples: list[dict[str, Any]] = [
        {"recipient_id": "rec-123"},
        {"recipient_id": "rec-456"},
    ]

    return create_tool_definition(
        name="honeycomb_get_recipient_triggers",
        description=get_description("honeycomb_get_recipient_triggers"),
        input_schema=schema,
        input_examples=examples,
    )


def get_tools() -> list[dict[str, Any]]:
    """Get all recipients tool definitions."""
    return [
        generate_list_recipients_tool(),
        generate_get_recipient_tool(),
        generate_create_recipient_tool(),
        generate_update_recipient_tool(),
        generate_delete_recipient_tool(),
        generate_get_recipient_triggers_tool(),
    ]
