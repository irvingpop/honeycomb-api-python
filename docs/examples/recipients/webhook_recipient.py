"""Webhook recipient creation examples.

These examples demonstrate creating webhook recipients with optional secrets.
"""

from __future__ import annotations

from honeycomb import HoneycombClient, RecipientBuilder, RecipientCreate, RecipientType


# start_example:webhook_with_builder
async def create_webhook_recipient(client: HoneycombClient) -> str:
    """Create a webhook recipient using RecipientBuilder.

    Returns:
        The created recipient ID
    """
    recipient = RecipientBuilder.webhook(
        url="https://your-webhook.example.com/alerts",
        name="Custom Webhook",
        secret="optional-secret-for-validation",
    )
    created = await client.recipients.create_async(recipient)
    return created.id


# end_example:webhook_with_builder


# start_example:webhook_manual
async def create_webhook_recipient_manual(client: HoneycombClient) -> str:
    """Create a webhook recipient using manual construction.

    Returns:
        The created recipient ID
    """
    recipient = RecipientCreate(
        type=RecipientType.WEBHOOK,
        details={
            "webhook_url": "https://your-webhook.example.com/alerts",
            "webhook_name": "Custom Webhook",
        },
    )
    created = await client.recipients.create_async(recipient)
    return created.id


# end_example:webhook_manual


# start_example:webhook_with_auth_headers
async def create_webhook_with_auth_headers(client: HoneycombClient) -> str:
    """Create a webhook recipient with authentication headers.

    Useful for webhooks that require API keys or bearer tokens for authentication.

    Returns:
        The created recipient ID
    """
    recipient = RecipientBuilder.webhook(
        url="https://api.example.com/notifications",
        name="Authenticated Webhook",
        headers=[
            {"header": "Authorization", "value": "Bearer api-key-xyz123"},
            {"header": "X-Environment", "value": "production"},
        ],
    )
    created = await client.recipients.create_async(recipient)
    return created.id


# end_example:webhook_with_auth_headers


# start_example:webhook_with_custom_payload
async def create_webhook_with_custom_payload(client: HoneycombClient) -> str:
    """Create a webhook recipient with custom payload templates.

    Advanced feature for customizing the JSON payload sent to the webhook
    using template variables.

    Returns:
        The created recipient ID
    """
    recipient = RecipientBuilder.webhook(
        url="https://your-webhook.example.com/alerts",
        name="Custom Payload Webhook",
        template_variables=[
            {"name": "environment", "default_value": "production"},
            {"name": "severity", "default_value": "warning"},
        ],
        payload_templates={
            "trigger": {
                "body": '{"env": "{{.environment}}", "level": "{{.severity}}", "type": "trigger"}'
            },
            "budget_rate": {
                "body": '{"env": "{{.environment}}", "level": "critical", "type": "budget_rate"}'
            },
            "exhaustion_time": {
                "body": '{"env": "{{.environment}}", "level": "critical", "type": "exhaustion_time"}'
            },
        },
    )
    created = await client.recipients.create_async(recipient)
    return created.id


# end_example:webhook_with_custom_payload


# TEST_ASSERTIONS
async def test_assertions(client: HoneycombClient, recipient_id: str) -> None:
    """Verify the example worked correctly."""
    recipient = await client.recipients.get_async(recipient_id)
    assert recipient.type == RecipientType.WEBHOOK
    assert recipient.details is not None


# CLEANUP
async def cleanup(client: HoneycombClient, recipient_id: str) -> None:
    """Clean up resources created by example."""
    await client.recipients.delete_async(recipient_id)
