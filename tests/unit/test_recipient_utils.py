"""Tests for _recipient_utils module."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from honeycomb.exceptions import HoneycombAPIError
from honeycomb.resources._recipient_utils import process_inline_recipients
from tests.factories import EmailRecipientFactory, WebhookRecipientFactory, mock_response


@pytest.mark.asyncio
@respx.mock
async def test_process_recipients_with_existing_ids():
    """Test that recipients with IDs are returned unchanged."""
    respx.get("https://api.honeycomb.io/1/recipients").mock(return_value=Response(200, json=[]))

    async with HoneycombClient(api_key="test-key") as client:
        recipients = [
            {"id": "existing-1"},
            {"id": "existing-2"},
        ]
        result = await process_inline_recipients(client, recipients)
        assert result == recipients


@pytest.mark.asyncio
@respx.mock
async def test_process_inline_email_recipient_creates_new():
    """Test creating new inline email recipient."""
    respx.get("https://api.honeycomb.io/1/recipients").mock(return_value=Response(200, json=[]))

    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(201, json=mock_response(EmailRecipientFactory, id="new-email"))
    )

    async with HoneycombClient(api_key="test-key") as client:
        recipients = [{"type": "email", "target": "alerts@example.com"}]
        result = await process_inline_recipients(client, recipients)
        assert len(result) == 1
        assert result[0]["id"] == "new-email"


@pytest.mark.asyncio
@respx.mock
async def test_process_inline_webhook_recipient_creates_new():
    """Test creating new inline webhook recipient."""
    respx.get("https://api.honeycomb.io/1/recipients").mock(return_value=Response(200, json=[]))

    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(201, json=mock_response(WebhookRecipientFactory, id="new-webhook"))
    )

    async with HoneycombClient(api_key="test-key") as client:
        recipients = [
            {"type": "webhook", "target": "https://example.com/webhook", "name": "My Webhook"}
        ]
        result = await process_inline_recipients(client, recipients)
        assert len(result) == 1
        assert result[0]["id"] == "new-webhook"


@pytest.mark.asyncio
@respx.mock
async def test_process_inline_recipient_reuses_existing():
    """Test that matching existing recipient is reused."""
    # Mock existing email recipient
    existing_data = mock_response(EmailRecipientFactory, id="existing-email", type="email")
    existing_data["details"] = {"email_address": "alerts@example.com"}

    respx.get("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(200, json=[existing_data])
    )

    # Should NOT call POST - it reuses existing
    async with HoneycombClient(api_key="test-key") as client:
        recipients = [{"type": "email", "target": "alerts@example.com"}]
        result = await process_inline_recipients(client, recipients)
        assert len(result) == 1
        assert result[0]["id"] == "existing-email"


@pytest.mark.asyncio
@respx.mock
async def test_process_inline_recipient_409_retry():
    """Test 409 conflict handling (race condition)."""
    # Initial list shows no recipients
    respx.get("https://api.honeycomb.io/1/recipients").mock(
        side_effect=[
            Response(200, json=[]),  # First call - empty
            Response(  # Second call after 409 - recipient now exists
                200,
                json=[
                    {
                        **mock_response(EmailRecipientFactory, id="race-email", type="email"),
                        "details": {"email_address": "race@example.com"},
                    }
                ],
            ),
        ]
    )

    # Create returns 409 conflict
    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(409, json={"error": "Recipient already exists"})
    )

    async with HoneycombClient(api_key="test-key") as client:
        recipients = [{"type": "email", "target": "race@example.com"}]
        result = await process_inline_recipients(client, recipients)
        # Should find it on retry
        assert len(result) == 1
        assert result[0]["id"] == "race-email"


@pytest.mark.asyncio
@respx.mock
async def test_process_inline_recipient_409_not_found_reraises():
    """Test 409 conflict that doesn't resolve on retry re-raises."""
    # Initial list shows no recipients
    respx.get("https://api.honeycomb.io/1/recipients").mock(
        side_effect=[
            Response(200, json=[]),  # First call - empty
            Response(200, json=[]),  # Second call after 409 - still not found!
        ]
    )

    # Create returns 409 conflict
    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(409, json={"error": "Recipient already exists"})
    )

    async with HoneycombClient(api_key="test-key") as client:
        recipients = [{"type": "email", "target": "mystery@example.com"}]
        with pytest.raises(HoneycombAPIError) as exc_info:
            await process_inline_recipients(client, recipients)
        assert exc_info.value.status_code == 409


@pytest.mark.asyncio
@respx.mock
async def test_process_inline_recipient_with_custom_details():
    """Test processing inline recipient with custom details provided."""
    respx.get("https://api.honeycomb.io/1/recipients").mock(return_value=Response(200, json=[]))

    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(201, json=mock_response(EmailRecipientFactory, id="new-custom"))
    )

    async with HoneycombClient(api_key="test-key") as client:
        recipients = [
            {
                "type": "email",
                "target": "alerts@example.com",
                "details": {"email_address": "custom@example.com"},  # Custom details
            }
        ]
        result = await process_inline_recipients(client, recipients)
        assert len(result) == 1
        assert result[0]["id"] == "new-custom"


@pytest.mark.asyncio
@respx.mock
async def test_process_mixed_recipients():
    """Test processing mix of existing IDs and inline recipients."""
    respx.get("https://api.honeycomb.io/1/recipients").mock(return_value=Response(200, json=[]))

    respx.post("https://api.honeycomb.io/1/recipients").mock(
        return_value=Response(201, json=mock_response(EmailRecipientFactory, id="new-inline"))
    )

    async with HoneycombClient(api_key="test-key") as client:
        recipients = [
            {"id": "existing-123"},  # Has ID
            {"type": "email", "target": "new@example.com"},  # Inline
        ]
        result = await process_inline_recipients(client, recipients)
        assert len(result) == 2
        assert result[0]["id"] == "existing-123"
        assert result[1]["id"] == "new-inline"
