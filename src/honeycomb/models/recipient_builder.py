"""Builder pattern for Honeycomb Recipients."""

from __future__ import annotations

from typing import Any, Literal

from typing_extensions import Self

from .recipients import RecipientCreate, RecipientType


class RecipientMixin:
    """Mixin providing recipient creation methods.

    This mixin is designed to be composed into other builders (TriggerBuilder,
    BurnAlertBuilder) to provide fluent methods for adding recipients.
    """

    def __init__(self) -> None:
        """Initialize recipient storage."""
        self._recipients: list[dict[str, Any]] = []  # Existing recipient IDs
        self._new_recipients: list[dict[str, Any]] = []  # Inline-created recipients

    def email(self, address: str) -> Self:
        """Add an email recipient.

        Args:
            address: Email address to notify.

        Returns:
            Self for method chaining.
        """
        self._new_recipients.append(
            {
                "type": "email",
                "target": address,
            }
        )
        return self

    def slack(self, channel: str) -> Self:
        """Add a Slack recipient.

        Args:
            channel: Slack channel name (e.g., "#alerts").

        Returns:
            Self for method chaining.
        """
        self._new_recipients.append(
            {
                "type": "slack",
                "target": channel,
            }
        )
        return self

    def pagerduty(
        self,
        routing_key: str,
        severity: Literal["info", "warning", "error", "critical"] = "critical",
    ) -> Self:
        """Add a PagerDuty recipient.

        Args:
            routing_key: PagerDuty integration routing key.
            severity: Alert severity level.

        Returns:
            Self for method chaining.
        """
        self._new_recipients.append(
            {
                "type": "pagerduty",
                "target": routing_key,
                "details": {"severity": severity},
            }
        )
        return self

    def webhook(self, url: str, name: str = "Webhook", secret: str | None = None) -> Self:
        """Add a webhook recipient (inline format for triggers/burn alerts).

        Args:
            url: Webhook URL to POST to.
            name: A name for this webhook (default: "Webhook").
            secret: Optional webhook secret for signing.

        Returns:
            Self for method chaining.

        Note:
            This creates inline recipients for triggers/burn alerts.
            For standalone recipient creation via Recipients API, use RecipientBuilder.webhook().
        """
        details: dict[str, Any] = {
            "webhook_url": url,
            "webhook_name": name,
        }
        if secret:
            details["webhook_secret"] = secret

        self._new_recipients.append(
            {
                "type": "webhook",
                "target": url,
                "details": details,
            }
        )
        return self

    def msteams(self, workflow_url: str) -> Self:
        """Add an MS Teams workflow recipient.

        Args:
            workflow_url: MS Teams workflow webhook URL.

        Returns:
            Self for method chaining.
        """
        self._new_recipients.append(
            {
                "type": "msteams_workflow",
                "target": workflow_url,
            }
        )
        return self

    def recipient_id(self, recipient_id: str) -> Self:
        """Reference an existing recipient by ID.

        Args:
            recipient_id: ID of an existing recipient.

        Returns:
            Self for method chaining.
        """
        self._recipients.append({"id": recipient_id})
        return self

    def _get_all_recipients(self) -> list[dict[str, Any]]:
        """Get combined list of recipients for API.

        Returns:
            List of recipient dictionaries.
        """
        return self._recipients + self._new_recipients


class RecipientBuilder:
    """Factory for creating standalone RecipientCreate objects.

    This builder provides convenient factory methods for creating recipients
    that can be saved independently using the Recipients API.

    Example:
        >>> recipient = RecipientBuilder.email("oncall@example.com")
        >>> await client.recipients.create_async(recipient)
    """

    @staticmethod
    def email(address: str) -> RecipientCreate:
        """Create an email recipient.

        Args:
            address: Email address to notify.

        Returns:
            RecipientCreate object.
        """
        return RecipientCreate(type=RecipientType.EMAIL, details={"email_address": address})

    @staticmethod
    def slack(channel: str) -> RecipientCreate:
        """Create a Slack recipient.

        Args:
            channel: Slack channel name (e.g., "#alerts").

        Returns:
            RecipientCreate object.
        """
        return RecipientCreate(type=RecipientType.SLACK, details={"slack_channel": channel})

    @staticmethod
    def pagerduty(
        integration_key: str,
        integration_name: str = "PagerDuty Integration",
    ) -> RecipientCreate:
        """Create a PagerDuty recipient.

        Args:
            integration_key: PagerDuty integration key (32 characters).
            integration_name: A name for this integration.

        Returns:
            RecipientCreate object.
        """
        return RecipientCreate(
            type=RecipientType.PAGERDUTY,
            details={
                "pagerduty_integration_key": integration_key,
                "pagerduty_integration_name": integration_name,
            },
        )

    @staticmethod
    def webhook(
        url: str,
        name: str = "Webhook",
        secret: str | None = None,
    ) -> RecipientCreate:
        """Create a webhook recipient.

        Args:
            url: Webhook URL to POST to.
            name: A name for this webhook.
            secret: Optional webhook secret for signing.

        Returns:
            RecipientCreate object.
        """
        details: dict[str, Any] = {
            "webhook_url": url,
            "webhook_name": name,
        }
        if secret:
            details["webhook_secret"] = secret
        return RecipientCreate(type=RecipientType.WEBHOOK, details=details)

    @staticmethod
    def msteams(workflow_url: str, name: str = "MS Teams") -> RecipientCreate:
        """Create an MS Teams workflow recipient.

        Args:
            workflow_url: MS Teams workflow webhook URL.
            name: A name for this recipient.

        Returns:
            RecipientCreate object.
        """
        return RecipientCreate(
            type=RecipientType.MSTEAMS_WORKFLOW,
            details={
                "webhook_url": workflow_url,
                "webhook_name": name,
            },
        )
