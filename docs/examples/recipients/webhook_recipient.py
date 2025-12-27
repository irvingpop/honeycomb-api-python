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
            "url": "https://your-webhook.example.com/alerts",
            "name": "Custom Webhook",
        },
    )
    created = await client.recipients.create_async(recipient)
    return created.id


# end_example:webhook_manual


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
