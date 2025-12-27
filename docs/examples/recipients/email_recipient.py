"""Email recipient creation examples.

These examples demonstrate creating email recipients using both
the RecipientBuilder and manual construction patterns.
"""

from __future__ import annotations

from honeycomb import HoneycombClient, RecipientBuilder, RecipientCreate, RecipientType


# start_example:email_with_builder
async def create_email_recipient(client: HoneycombClient) -> str:
    """Create an email recipient using RecipientBuilder.

    Returns:
        The created recipient ID
    """
    recipient = RecipientBuilder.email("alerts@example.com")
    created = await client.recipients.create_async(recipient)
    return created.id


# end_example:email_with_builder


# start_example:email_manual
async def create_email_recipient_manual(client: HoneycombClient) -> str:
    """Create an email recipient using manual construction.

    Returns:
        The created recipient ID
    """
    recipient = RecipientCreate(
        type=RecipientType.EMAIL,
        details={"email_address": "alerts@example.com"},
    )
    created = await client.recipients.create_async(recipient)
    return created.id


# end_example:email_manual


# TEST_ASSERTIONS
async def test_assertions(client: HoneycombClient, recipient_id: str) -> None:
    """Verify the example worked correctly."""
    recipient = await client.recipients.get_async(recipient_id)
    assert recipient.type == RecipientType.EMAIL
    assert recipient.details is not None


# CLEANUP
async def cleanup(client: HoneycombClient, recipient_id: str) -> None:
    """Clean up resources created by example."""
    await client.recipients.delete_async(recipient_id)
