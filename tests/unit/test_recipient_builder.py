"""Tests for RecipientBuilder and RecipientMixin."""

from honeycomb import RecipientBuilder, RecipientCreate, RecipientMixin, RecipientType


class TestRecipientBuilder:
    """Tests for the RecipientBuilder factory methods."""

    def test_email(self):
        """Test creating email recipient."""
        recipient = RecipientBuilder.email("oncall@example.com")
        assert isinstance(recipient, RecipientCreate)
        assert recipient.type == RecipientType.EMAIL
        assert recipient.details == {"email_address": "oncall@example.com"}

    def test_slack(self):
        """Test creating Slack recipient."""
        recipient = RecipientBuilder.slack("#alerts")
        assert recipient.type == RecipientType.SLACK
        assert recipient.details == {"slack_channel": "#alerts"}

    def test_pagerduty_default_severity(self):
        """Test creating PagerDuty recipient with default integration name."""
        recipient = RecipientBuilder.pagerduty("routing-key-123")
        assert recipient.type == RecipientType.PAGERDUTY
        assert recipient.details == {
            "pagerduty_integration_key": "routing-key-123",
            "pagerduty_integration_name": "PagerDuty Integration",
        }

    def test_pagerduty_custom_name(self):
        """Test creating PagerDuty recipient with custom integration name."""
        recipient = RecipientBuilder.pagerduty("routing-key-123", integration_name="My PD")
        assert recipient.type == RecipientType.PAGERDUTY
        assert recipient.details == {
            "pagerduty_integration_key": "routing-key-123",
            "pagerduty_integration_name": "My PD",
        }

    def test_pagerduty_all_severities(self):
        """Test PagerDuty recipient preserves integration key length requirement."""
        # PagerDuty integration keys must be exactly 32 characters
        key_32_chars = "a" * 32
        recipient = RecipientBuilder.pagerduty(key_32_chars)
        assert recipient.details["pagerduty_integration_key"] == key_32_chars

    def test_webhook_without_secret(self):
        """Test creating webhook recipient without secret."""
        recipient = RecipientBuilder.webhook("https://example.com/webhook")
        assert recipient.type == RecipientType.WEBHOOK
        assert recipient.details == {
            "webhook_url": "https://example.com/webhook",
            "webhook_name": "Webhook",
        }

    def test_webhook_with_secret(self):
        """Test creating webhook recipient with secret."""
        recipient = RecipientBuilder.webhook("https://example.com/webhook", secret="secret123")
        assert recipient.type == RecipientType.WEBHOOK
        assert recipient.details == {
            "webhook_url": "https://example.com/webhook",
            "webhook_name": "Webhook",
            "webhook_secret": "secret123",
        }

    def test_msteams(self):
        """Test creating MS Teams workflow recipient."""
        recipient = RecipientBuilder.msteams("https://outlook.office.com/webhook/...")
        assert recipient.type == RecipientType.MSTEAMS_WORKFLOW
        assert recipient.details == {
            "webhook_url": "https://outlook.office.com/webhook/...",
            "webhook_name": "MS Teams",
        }

    def test_model_dump_for_api(self):
        """Test that RecipientCreate serializes correctly for API."""
        recipient = RecipientBuilder.email("test@example.com")
        data = recipient.model_dump_for_api()
        assert data == {"type": "email", "details": {"email_address": "test@example.com"}}


class TestRecipientMixin:
    """Tests for the RecipientMixin used in builders."""

    def test_initialization(self):
        """Test RecipientMixin initialization."""
        mixin = RecipientMixin()
        assert mixin._recipients == []
        assert mixin._new_recipients == []

    def test_email(self):
        """Test adding email recipient via mixin."""
        mixin = RecipientMixin()
        result = mixin.email("oncall@example.com")
        assert result is mixin  # Method chaining
        assert len(mixin._new_recipients) == 1
        assert mixin._new_recipients[0] == {
            "type": "email",
            "target": "oncall@example.com",
        }

    def test_slack(self):
        """Test adding Slack recipient via mixin."""
        mixin = RecipientMixin()
        mixin.slack("#alerts")
        assert len(mixin._new_recipients) == 1
        assert mixin._new_recipients[0] == {
            "type": "slack",
            "target": "#alerts",
        }

    def test_pagerduty_default(self):
        """Test adding PagerDuty recipient with default severity."""
        mixin = RecipientMixin()
        mixin.pagerduty("routing-key-123")
        assert len(mixin._new_recipients) == 1
        assert mixin._new_recipients[0] == {
            "type": "pagerduty",
            "target": "routing-key-123",
            "details": {"severity": "critical"},
        }

    def test_pagerduty_custom_severity(self):
        """Test adding PagerDuty recipient with custom severity."""
        mixin = RecipientMixin()
        mixin.pagerduty("routing-key-123", severity="warning")
        assert mixin._new_recipients[0]["details"]["severity"] == "warning"

    def test_webhook_without_secret(self):
        """Test adding webhook without secret (inline format for triggers)."""
        mixin = RecipientMixin()
        mixin.webhook("https://example.com/webhook")
        assert len(mixin._new_recipients) == 1
        assert mixin._new_recipients[0] == {
            "type": "webhook",
            "target": "https://example.com/webhook",
            "details": {
                "webhook_url": "https://example.com/webhook",
                "webhook_name": "Webhook",
            },
        }

    def test_webhook_with_secret(self):
        """Test adding webhook with secret (inline format for triggers)."""
        mixin = RecipientMixin()
        mixin.webhook("https://example.com/webhook", name="My Webhook", secret="secret123")
        assert mixin._new_recipients[0] == {
            "type": "webhook",
            "target": "https://example.com/webhook",
            "details": {
                "webhook_url": "https://example.com/webhook",
                "webhook_name": "My Webhook",
                "webhook_secret": "secret123",
            },
        }

    def test_msteams(self):
        """Test adding MS Teams workflow recipient."""
        mixin = RecipientMixin()
        mixin.msteams("https://outlook.office.com/webhook/...")
        assert len(mixin._new_recipients) == 1
        assert mixin._new_recipients[0] == {
            "type": "msteams_workflow",
            "target": "https://outlook.office.com/webhook/...",
        }

    def test_recipient_id(self):
        """Test adding recipient by ID."""
        mixin = RecipientMixin()
        mixin.recipient_id("recipient-123")
        assert len(mixin._recipients) == 1
        assert mixin._recipients[0] == {"id": "recipient-123"}

    def test_multiple_recipients(self):
        """Test adding multiple recipients."""
        mixin = RecipientMixin()
        mixin.email("oncall@example.com")
        mixin.slack("#alerts")
        mixin.pagerduty("routing-key-123")
        assert len(mixin._new_recipients) == 3

    def test_mixed_recipients_and_ids(self):
        """Test mixing new recipients and existing IDs."""
        mixin = RecipientMixin()
        mixin.recipient_id("existing-1")
        mixin.email("new@example.com")
        mixin.recipient_id("existing-2")
        mixin.slack("#alerts")

        assert len(mixin._recipients) == 2
        assert len(mixin._new_recipients) == 2

    def test_get_all_recipients_empty(self):
        """Test getting recipients when none added."""
        mixin = RecipientMixin()
        recipients = mixin._get_all_recipients()
        assert recipients == []

    def test_get_all_recipients_combines_lists(self):
        """Test that _get_all_recipients combines both lists."""
        mixin = RecipientMixin()
        mixin.recipient_id("existing-1")
        mixin.email("new@example.com")
        mixin.recipient_id("existing-2")
        mixin.slack("#alerts")

        all_recipients = mixin._get_all_recipients()
        assert len(all_recipients) == 4
        # Existing recipients should come first
        assert all_recipients[0] == {"id": "existing-1"}
        assert all_recipients[1] == {"id": "existing-2"}
        # New recipients follow
        assert all_recipients[2]["type"] == "email"
        assert all_recipients[3]["type"] == "slack"

    def test_method_chaining(self):
        """Test that all methods support method chaining."""
        mixin = RecipientMixin()
        result = (
            mixin.email("oncall@example.com")
            .slack("#alerts")
            .pagerduty("routing-key", severity="critical")
            .webhook("https://example.com/webhook")
            .msteams("https://outlook.office.com/webhook/...")
            .recipient_id("existing-1")
        )
        assert result is mixin
        assert len(mixin._get_all_recipients()) == 6

    def test_order_preserved(self):
        """Test that recipient order is preserved."""
        mixin = RecipientMixin()
        mixin.email("first@example.com")
        mixin.slack("#second")
        mixin.pagerduty("third")

        recipients = mixin._get_all_recipients()
        assert recipients[0]["target"] == "first@example.com"
        assert recipients[1]["target"] == "#second"
        assert recipients[2]["target"] == "third"
