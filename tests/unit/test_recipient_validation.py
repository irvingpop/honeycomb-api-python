"""Test strict validation for recipient models."""

import pytest
from pydantic import ValidationError

from honeycomb import (
    EmailRecipientDetails,
    PagerDutyRecipientDetails,
    RecipientCreate,
    RecipientType,
    SlackRecipientDetails,
    WebhookRecipientDetails,
)


class TestEmailRecipientValidation:
    """Test email recipient validation."""

    def test_valid_email_recipient(self) -> None:
        """Test creating a valid email recipient."""
        recipient = RecipientCreate(
            type=RecipientType.EMAIL,
            details=EmailRecipientDetails(email_address="test@example.com"),
        )
        assert recipient.type == RecipientType.EMAIL
        assert recipient.details.email_address == "test@example.com"

    def test_valid_email_recipient_from_dict(self) -> None:
        """Test creating email recipient from dict."""
        recipient = RecipientCreate(
            type=RecipientType.EMAIL, details={"email_address": "test@example.com"}
        )
        assert recipient.type == RecipientType.EMAIL
        assert recipient.details.email_address == "test@example.com"

    def test_invalid_email_field_name(self) -> None:
        """Test that wrong field name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RecipientCreate(type=RecipientType.EMAIL, details={"address": "test@example.com"})

        error = exc_info.value
        assert "email_address" in str(error)
        assert "Field required" in str(error)

    def test_missing_email_address(self) -> None:
        """Test that missing email_address raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RecipientCreate(type=RecipientType.EMAIL, details={})

        error = exc_info.value
        assert "email_address" in str(error)

    def test_extra_fields_rejected(self) -> None:
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError):
            RecipientCreate(
                type=RecipientType.EMAIL,
                details={"email_address": "test@example.com", "unexpected_field": "value"},
            )


class TestSlackRecipientValidation:
    """Test Slack recipient validation."""

    def test_valid_slack_recipient(self) -> None:
        """Test creating a valid Slack recipient."""
        recipient = RecipientCreate(
            type=RecipientType.SLACK, details=SlackRecipientDetails(slack_channel="#alerts")
        )
        assert recipient.type == RecipientType.SLACK
        assert recipient.details.slack_channel == "#alerts"

    def test_invalid_slack_field_name(self) -> None:
        """Test that wrong field name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RecipientCreate(type=RecipientType.SLACK, details={"channel": "#alerts"})

        error = exc_info.value
        assert "slack_channel" in str(error)


class TestPagerDutyRecipientValidation:
    """Test PagerDuty recipient validation."""

    def test_valid_pagerduty_recipient(self) -> None:
        """Test creating a valid PagerDuty recipient."""
        recipient = RecipientCreate(
            type=RecipientType.PAGERDUTY,
            details=PagerDutyRecipientDetails(
                pagerduty_integration_key="7zOwh1edS8xHGcwfb2bA4sqY8E6PJzSK",
                pagerduty_integration_name="Test Integration",
            ),
        )
        assert recipient.type == RecipientType.PAGERDUTY
        assert recipient.details.pagerduty_integration_key == "7zOwh1edS8xHGcwfb2bA4sqY8E6PJzSK"

    def test_pagerduty_key_length_validation(self) -> None:
        """Test that PagerDuty key must be exactly 32 characters."""
        with pytest.raises(ValidationError) as exc_info:
            RecipientCreate(
                type=RecipientType.PAGERDUTY,
                details={
                    "pagerduty_integration_key": "short",
                    "pagerduty_integration_name": "Test",
                },
            )

        error = exc_info.value
        assert "32" in str(error) or "length" in str(error).lower()


class TestWebhookRecipientValidation:
    """Test webhook recipient validation."""

    def test_valid_webhook_recipient(self) -> None:
        """Test creating a valid webhook recipient."""
        recipient = RecipientCreate(
            type=RecipientType.WEBHOOK,
            details=WebhookRecipientDetails(
                webhook_url="https://example.com/webhook", webhook_name="Test Webhook"
            ),
        )
        assert recipient.type == RecipientType.WEBHOOK
        assert recipient.details.webhook_url == "https://example.com/webhook"

    def test_webhook_with_headers(self) -> None:
        """Test webhook with headers."""
        recipient = RecipientCreate(
            type=RecipientType.WEBHOOK,
            details={
                "webhook_url": "https://example.com/webhook",
                "webhook_name": "Test Webhook",
                "webhook_headers": [{"header": "Authorization", "value": "Bearer token"}],
            },
        )
        assert len(recipient.details.webhook_headers) == 1
        assert recipient.details.webhook_headers[0].header == "Authorization"

    def test_webhook_header_max_length(self) -> None:
        """Test webhook header validation."""
        with pytest.raises(ValidationError):
            RecipientCreate(
                type=RecipientType.WEBHOOK,
                details={
                    "webhook_url": "https://example.com/webhook",
                    "webhook_name": "Test Webhook",
                    "webhook_headers": [{"header": "A" * 100}],  # Too long
                },
            )

    def test_webhook_url_max_length(self) -> None:
        """Test webhook URL max length validation."""
        with pytest.raises(ValidationError):
            RecipientCreate(
                type=RecipientType.WEBHOOK,
                details={
                    "webhook_url": "https://example.com/" + "a" * 3000,  # Too long
                    "webhook_name": "Test Webhook",
                },
            )


class TestRecipientSerialization:
    """Test recipient serialization for API."""

    def test_email_serialization(self) -> None:
        """Test email recipient serializes correctly for API."""
        recipient = RecipientCreate(
            type=RecipientType.EMAIL, details={"email_address": "test@example.com"}
        )
        api_data = recipient.model_dump_for_api()
        assert api_data == {
            "type": "email",
            "details": {"email_address": "test@example.com"},
        }

    def test_webhook_serialization(self) -> None:
        """Test webhook recipient serializes correctly for API."""
        recipient = RecipientCreate(
            type=RecipientType.WEBHOOK,
            details={
                "webhook_url": "https://example.com/webhook",
                "webhook_name": "Test Webhook",
                "webhook_secret": "secret123",
            },
        )
        api_data = recipient.model_dump_for_api()
        assert api_data["type"] == "webhook"
        assert api_data["details"]["webhook_url"] == "https://example.com/webhook"
        assert api_data["details"]["webhook_name"] == "Test Webhook"
        assert api_data["details"]["webhook_secret"] == "secret123"
