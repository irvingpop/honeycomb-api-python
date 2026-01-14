"""Tests for RecipientsResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from tests.factories import (
    EmailRecipientFactory,
    WebhookRecipientFactory,
    mock_response,
)

# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_recipients_async():
    """Test listing recipients (async)."""
    # Mix of email and webhook recipients
    mock_data = [
        mock_response(EmailRecipientFactory, id="recip-1"),
        mock_response(WebhookRecipientFactory, id="recip-2"),
    ]
    respx.get("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(200, json=mock_data)
    )

    async with HoneycombClient(api_key="test-key") as client:
        recipients = await client.recipients.list_async()
        assert len(recipients) == 2
        assert recipients[0].id == "recip-1"
        assert recipients[1].id == "recip-2"


@pytest.mark.asyncio
@respx.mock
async def test_list_recipients_empty_async():
    """Test listing recipients returns empty list (async)."""
    respx.get("https://api.honeycomb.io/1/recipients").mock(return_value=Response(200, json=[]))

    async with HoneycombClient(api_key="test-key") as client:
        recipients = await client.recipients.list_async()
        assert len(recipients) == 0


@pytest.mark.asyncio
@respx.mock
async def test_get_recipient_async():
    """Test getting a specific recipient (async)."""
    respx.get("https://api.honeycomb.io/1/recipients/recip-123").mock(
        return_value=Response(
            200,
            json=mock_response(EmailRecipientFactory, id="recip-123", type="email"),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        recipient = await client.recipients.get_async(recipient_id="recip-123")
        assert recipient.id == "recip-123"
        assert recipient.type == "email"


@pytest.mark.asyncio
@respx.mock
async def test_create_email_recipient_async():
    """Test creating an email recipient (async)."""
    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(
            201, json=mock_response(EmailRecipientFactory, id="new-recip", type="email")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = EmailRecipientFactory.build()
        recipient = await client.recipients.create_async(recipient=request)
        assert recipient.id == "new-recip"
        assert recipient.type == "email"


@pytest.mark.asyncio
@respx.mock
async def test_create_webhook_recipient_async():
    """Test creating a webhook recipient (async)."""
    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(
            201,
            json=mock_response(WebhookRecipientFactory, id="new-webhook", type="webhook"),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = WebhookRecipientFactory.build()
        recipient = await client.recipients.create_async(recipient=request)
        assert recipient.id == "new-webhook"
        assert recipient.type == "webhook"


@pytest.mark.asyncio
@respx.mock
async def test_update_recipient_async():
    """Test updating a recipient (async)."""
    respx.put("https://api.honeycomb.io/1/recipients/recip-123").mock(
        return_value=Response(
            200,
            json=mock_response(EmailRecipientFactory, id="recip-123"),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = EmailRecipientFactory.build()
        recipient = await client.recipients.update_async(
            recipient_id="recip-123", recipient=request
        )
        assert recipient.id == "recip-123"


@pytest.mark.asyncio
@respx.mock
async def test_delete_recipient_async():
    """Test deleting a recipient (async)."""
    respx.delete("https://api.honeycomb.io/1/recipients/recip-123").mock(return_value=Response(204))

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.recipients.delete_async(recipient_id="recip-123")


@pytest.mark.asyncio
@respx.mock
async def test_get_recipient_triggers_async():
    """Test getting triggers associated with a recipient (async)."""
    triggers_data = [
        {"id": "trigger-1", "name": "Error rate alert"},
        {"id": "trigger-2", "name": "Latency alert"},
    ]
    respx.get("https://api.honeycomb.io/1/recipients/recip-123/triggers").mock(
        return_value=Response(200, json=triggers_data)
    )

    async with HoneycombClient(api_key="test-key") as client:
        triggers = await client.recipients.get_triggers_async(recipient_id="recip-123")
        assert len(triggers) == 2
        assert triggers[0]["id"] == "trigger-1"
        assert triggers[1]["id"] == "trigger-2"


@pytest.mark.asyncio
@respx.mock
async def test_get_recipient_triggers_empty_async():
    """Test getting triggers returns empty list (async)."""
    respx.get("https://api.honeycomb.io/1/recipients/recip-123/triggers").mock(
        return_value=Response(200, json=[])
    )

    async with HoneycombClient(api_key="test-key") as client:
        triggers = await client.recipients.get_triggers_async(recipient_id="recip-123")
        assert len(triggers) == 0


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_list_recipients_sync():
    """Test listing recipients (sync)."""
    mock_data = [
        mock_response(EmailRecipientFactory, id="recip-1"),
        mock_response(WebhookRecipientFactory, id="recip-2"),
    ]
    respx.get("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(200, json=mock_data)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        recipients = client.recipients.list()
        assert len(recipients) == 2
        assert recipients[0].id == "recip-1"
        assert recipients[1].id == "recip-2"


@respx.mock
def test_list_recipients_empty_sync():
    """Test listing recipients returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/1/recipients").mock(return_value=Response(200, json=[]))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        recipients = client.recipients.list()
        assert len(recipients) == 0


@respx.mock
def test_get_recipient_sync():
    """Test getting a specific recipient (sync)."""
    respx.get("https://api.honeycomb.io/1/recipients/recip-123").mock(
        return_value=Response(200, json=mock_response(EmailRecipientFactory, id="recip-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        recipient = client.recipients.get(recipient_id="recip-123")
        assert recipient.id == "recip-123"


@respx.mock
def test_create_email_recipient_sync():
    """Test creating an email recipient (sync)."""
    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(
            201, json=mock_response(EmailRecipientFactory, id="new-recip", type="email")
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = EmailRecipientFactory.build()
        recipient = client.recipients.create(recipient=request)
        assert recipient.id == "new-recip"
        assert recipient.type == "email"


@respx.mock
def test_create_webhook_recipient_sync():
    """Test creating a webhook recipient (sync)."""
    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(
            201, json=mock_response(WebhookRecipientFactory, id="new-webhook", type="webhook")
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = WebhookRecipientFactory.build()
        recipient = client.recipients.create(recipient=request)
        assert recipient.id == "new-webhook"
        assert recipient.type == "webhook"


@respx.mock
def test_update_recipient_sync():
    """Test updating a recipient (sync)."""
    respx.put("https://api.honeycomb.io/1/recipients/recip-123").mock(
        return_value=Response(200, json=mock_response(EmailRecipientFactory, id="recip-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = EmailRecipientFactory.build()
        recipient = client.recipients.update(recipient_id="recip-123", recipient=request)
        assert recipient.id == "recip-123"


@respx.mock
def test_delete_recipient_sync():
    """Test deleting a recipient (sync)."""
    respx.delete("https://api.honeycomb.io/1/recipients/recip-123").mock(return_value=Response(204))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.recipients.delete(recipient_id="recip-123")


@respx.mock
def test_get_recipient_triggers_sync():
    """Test getting triggers associated with a recipient (sync)."""
    triggers_data = [
        {"id": "trigger-1", "name": "Error rate alert"},
    ]
    respx.get("https://api.honeycomb.io/1/recipients/recip-123/triggers").mock(
        return_value=Response(200, json=triggers_data)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        triggers = client.recipients.get_triggers(recipient_id="recip-123")
        assert len(triggers) == 1
        assert triggers[0]["id"] == "trigger-1"


@respx.mock
def test_get_recipient_triggers_empty_sync():
    """Test getting triggers returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/1/recipients/recip-123/triggers").mock(
        return_value=Response(200, json=[])
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        triggers = client.recipients.get_triggers(recipient_id="recip-123")
        assert len(triggers) == 0


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.recipients.list()

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.recipients.get(recipient_id="recip-123")

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = EmailRecipientFactory.build()
        client.recipients.create(recipient=request)

    with pytest.raises(RuntimeError, match="Use update_async"):
        request = EmailRecipientFactory.build()
        client.recipients.update(recipient_id="recip-123", recipient=request)

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.recipients.delete(recipient_id="recip-123")

    with pytest.raises(RuntimeError, match="Use get_triggers_async"):
        client.recipients.get_triggers(recipient_id="recip-123")
