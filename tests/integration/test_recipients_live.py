"""Integration tests for Recipients and RecipientBuilder.

Tests the RecipientBuilder pattern against the live Honeycomb API.
"""

from __future__ import annotations

import pytest

from honeycomb import (
    HoneycombClient,
    HoneycombNotFoundError,
    RecipientBuilder,
    RecipientCreate,
    RecipientType,
)


class TestRecipientBuilder:
    """Test RecipientBuilder against live API."""

    @pytest.mark.asyncio
    async def test_email_recipient_builder(self, client: HoneycombClient) -> None:
        """Test creating an email recipient with builder."""
        recipient = RecipientBuilder.email("test-integration@example.com")

        created = await client.recipients.create_async(recipient)
        try:
            assert created.type == RecipientType.EMAIL
            # Verify the recipient details
            assert created.details is not None
        finally:
            await client.recipients.delete_async(created.id)

    @pytest.mark.asyncio
    async def test_webhook_recipient_builder(self, client: HoneycombClient) -> None:
        """Test creating a webhook recipient with builder."""
        recipient = RecipientBuilder.webhook(
            url="https://example.com/webhook",
            name="Test Webhook",
            secret="test-secret-123",
        )

        created = await client.recipients.create_async(recipient)
        try:
            assert created.type == RecipientType.WEBHOOK
        finally:
            await client.recipients.delete_async(created.id)

    @pytest.mark.asyncio
    async def test_recipient_crud_cycle(self, client: HoneycombClient) -> None:
        """Test full CRUD cycle for recipients."""
        # CREATE
        recipient = RecipientBuilder.email("crud-test@example.com")
        created = await client.recipients.create_async(recipient)
        recipient_id = created.id

        # READ
        fetched = await client.recipients.get_async(recipient_id)
        assert fetched.id == recipient_id
        assert fetched.type == RecipientType.EMAIL

        # UPDATE
        updated_recipient = RecipientCreate(
            type=RecipientType.EMAIL,
            details={"email_address": "crud-test-updated@example.com"},
        )
        updated = await client.recipients.update_async(recipient_id, updated_recipient)
        assert updated.id == recipient_id

        # DELETE
        await client.recipients.delete_async(recipient_id)

        # Verify deletion
        with pytest.raises(HoneycombNotFoundError):
            await client.recipients.get_async(recipient_id)


class TestRecipientManualConstruction:
    """Test recipients created without builder."""

    @pytest.mark.asyncio
    async def test_manual_email_recipient(self, client: HoneycombClient) -> None:
        """Test creating email recipient with manual construction."""
        recipient = RecipientCreate(
            type=RecipientType.EMAIL,
            details={"email_address": "manual-test@example.com"},
        )

        created = await client.recipients.create_async(recipient)
        try:
            assert created.type == RecipientType.EMAIL
        finally:
            await client.recipients.delete_async(created.id)


class TestRecipientList:
    """Test listing recipients."""

    @pytest.mark.asyncio
    async def test_list_recipients(self, client: HoneycombClient) -> None:
        """Test listing all recipients."""
        recipients = await client.recipients.list_async()
        assert isinstance(recipients, list)

    def test_list_recipients_sync(self, sync_client: HoneycombClient) -> None:
        """Test listing recipients with sync client."""
        recipients = sync_client.recipients.list()
        assert isinstance(recipients, list)
