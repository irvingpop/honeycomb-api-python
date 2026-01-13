"""Test strict validation for recipient models."""

import pytest
from pydantic import ValidationError

from honeycomb import (
    EmailRecipient,
    EmailRecipientDetails,
    PagerDutyRecipient,
    PagerDutyRecipientDetails,
    SlackRecipient,
    SlackRecipientDetails,
    WebhookRecipient,
    WebhookRecipientDetails,
)


class TestEmailRecipientValidation:
    """Test email recipient validation."""

    def test_valid_email_recipient(self) -> None:
        """Test creating a valid email recipient."""
        recipient = EmailRecipient(
            type="email",
            details=EmailRecipientDetails(email_address="test@example.com"),
        )
        assert recipient.type == "email"
        assert recipient.details.email_address == "test@example.com"

    def test_valid_email_recipient_from_dict(self) -> None:
        """Test creating email recipient from dict."""
        recipient = EmailRecipient(
            type="email",
            details={"email_address": "test@example.com"},  # type: ignore
        )
        assert recipient.type == "email"
        assert recipient.details.email_address == "test@example.com"

    def test_invalid_email_field_name(self) -> None:
        """Test that wrong field name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            EmailRecipient(type="email", details={"address": "test@example.com"})  # type: ignore

        error = exc_info.value
        assert "email_address" in str(error)
        assert "Field required" in str(error)

    def test_missing_email_address(self) -> None:
        """Test that missing email_address raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            EmailRecipient(type="email", details={})  # type: ignore

        error = exc_info.value
        assert "email_address" in str(error)

    def test_extra_fields_rejected(self) -> None:
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError):
            EmailRecipient(
                type="email",
                details={"email_address": "test@example.com", "unexpected_field": "value"},  # type: ignore
            )


class TestSlackRecipientValidation:
    """Test Slack recipient validation."""

    def test_valid_slack_recipient(self) -> None:
        """Test creating a valid Slack recipient."""
        recipient = SlackRecipient(
            type="slack", details=SlackRecipientDetails(slack_channel="#alerts")
        )
        assert recipient.type == "slack"
        assert recipient.details.slack_channel == "#alerts"

    def test_invalid_slack_field_name(self) -> None:
        """Test that wrong field name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SlackRecipient(type="slack", details={"channel": "#alerts"})  # type: ignore

        error = exc_info.value
        assert "slack_channel" in str(error)


class TestPagerDutyRecipientValidation:
    """Test PagerDuty recipient validation."""

    def test_valid_pagerduty_recipient(self) -> None:
        """Test creating a valid PagerDuty recipient."""
        recipient = PagerDutyRecipient(
            type="pagerduty",
            details=PagerDutyRecipientDetails(
                pagerduty_integration_key="7zOwh1edS8xHGcwfb2bA4sqY8E6PJzSK",
                pagerduty_integration_name="Test Integration",
            ),
        )
        assert recipient.type == "pagerduty"
        assert recipient.details.pagerduty_integration_key == "7zOwh1edS8xHGcwfb2bA4sqY8E6PJzSK"

    def test_pagerduty_key_length_validation(self) -> None:
        """Test that PagerDuty key must be exactly 32 characters."""
        with pytest.raises(ValidationError) as exc_info:
            PagerDutyRecipient(
                type="pagerduty",
                details={
                    "pagerduty_integration_key": "short",
                    "pagerduty_integration_name": "Test",
                },  # type: ignore
            )

        error = exc_info.value
        assert "32" in str(error) or "length" in str(error).lower()


class TestWebhookRecipientValidation:
    """Test webhook recipient validation."""

    def test_valid_webhook_recipient(self) -> None:
        """Test creating a valid webhook recipient."""
        recipient = WebhookRecipient(
            type="webhook",
            details=WebhookRecipientDetails(
                webhook_url="https://example.com/webhook", webhook_name="Test Webhook"
            ),
        )
        assert recipient.type == "webhook"
        assert recipient.details.webhook_url == "https://example.com/webhook"

    def test_webhook_with_headers(self) -> None:
        """Test webhook with headers."""
        recipient = WebhookRecipient(
            type="webhook",
            details={
                "webhook_url": "https://example.com/webhook",
                "webhook_name": "Test Webhook",
                "webhook_headers": [{"header": "Authorization", "value": "Bearer token"}],
            },  # type: ignore
        )
        assert len(recipient.details.webhook_headers) == 1
        assert recipient.details.webhook_headers[0].header == "Authorization"

    def test_webhook_header_max_length(self) -> None:
        """Test webhook header validation."""
        with pytest.raises(ValidationError):
            WebhookRecipient(
                type="webhook",
                details={
                    "webhook_url": "https://example.com/webhook",
                    "webhook_name": "Test Webhook",
                    "webhook_headers": [{"header": "A" * 100}],  # Too long
                },  # type: ignore
            )

    def test_webhook_url_max_length(self) -> None:
        """Test webhook URL max length validation."""
        with pytest.raises(ValidationError):
            WebhookRecipient(
                type="webhook",
                details={
                    "webhook_url": "https://example.com/" + "a" * 3000,  # Too long
                    "webhook_name": "Test Webhook",
                },  # type: ignore
            )


class TestRecipientSerialization:
    """Test recipient serialization for API."""

    def test_email_serialization(self) -> None:
        """Test email recipient serializes correctly for API."""
        from honeycomb.models.recipients import EmailRecipient

        recipient = EmailRecipient(
            type="email",
            details={"email_address": "test@example.com"},  # type: ignore
        )
        api_data = recipient.model_dump(mode="json", exclude_none=True)
        assert api_data == {
            "type": "email",
            "details": {"email_address": "test@example.com"},
        }

    def test_webhook_serialization(self) -> None:
        """Test webhook recipient serializes correctly for API."""
        from honeycomb.models.recipients import WebhookRecipient

        recipient = WebhookRecipient(
            type="webhook",
            details={
                "webhook_url": "https://example.com/webhook",
                "webhook_name": "Test Webhook",
                "webhook_secret": "secret123",
            },  # type: ignore
        )
        api_data = recipient.model_dump(mode="json", exclude_none=True)
        assert api_data["type"] == "webhook"
        assert api_data["details"]["webhook_url"] == "https://example.com/webhook"
        assert api_data["details"]["webhook_name"] == "Test Webhook"
        assert api_data["details"]["webhook_secret"] == "secret123"
