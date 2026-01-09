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

    def webhook(
        self,
        url: str,
        name: str = "Webhook",
        secret: str | None = None,
        headers: list[dict[str, str]] | None = None,
    ) -> Self:
        """Add a webhook recipient (inline format for triggers/burn alerts).

        Args:
            url: Webhook URL to POST to.
            name: A name for this webhook (default: "Webhook").
            secret: Optional webhook secret for signing.
            headers: Optional HTTP headers (max 5). Each dict should have
                    'header' (required) and optionally 'value'.
                    Example: [{"header": "Authorization", "value": "Bearer xyz"}]

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
        if headers:
            details["webhook_headers"] = headers

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
        headers: list[dict[str, str]] | None = None,
        payload_templates: dict[str, dict[str, str]] | None = None,
        template_variables: list[dict[str, str]] | None = None,
    ) -> RecipientCreate:
        """Create a webhook recipient.

        Args:
            url: Webhook URL to POST to (max 2048 chars).
            name: A name for this webhook (max 255 chars).
            secret: Optional webhook secret for signing (max 255 chars).
            headers: Optional HTTP headers (max 5). Each dict should have
                    'header' (required, max 64 chars) and optionally 'value' (max 750 chars).
                    Example: [{"header": "Authorization", "value": "Bearer xyz"}]
            payload_templates: Optional custom payload templates for different alert types.
                    Example: {"trigger": {"body": "{\"custom\": \"json\"}"}}
            template_variables: Optional template variables for payload substitution (max 10).
                    Example: [{"name": "severity", "default_value": "warning"}]

        Returns:
            RecipientCreate object.

        Example:
            >>> # Basic webhook
            >>> RecipientBuilder.webhook("https://example.com/webhook")

            >>> # Webhook with auth header
            >>> RecipientBuilder.webhook(
            ...     "https://example.com/webhook",
            ...     headers=[{"header": "Authorization", "value": "Bearer token123"}]
            ... )

            >>> # Advanced webhook with custom payload
            >>> RecipientBuilder.webhook(
            ...     "https://example.com/webhook",
            ...     template_variables=[{"name": "env", "default_value": "prod"}],
            ...     payload_templates={"trigger": {"body": "{\"environment\": \"{{env}}\"}"}}
            ... )
        """
        details: dict[str, Any] = {
            "webhook_url": url,
            "webhook_name": name,
        }
        if secret:
            details["webhook_secret"] = secret
        if headers:
            details["webhook_headers"] = headers
        if template_variables or payload_templates:
            webhook_payloads: dict[str, Any] = {}
            if template_variables:
                webhook_payloads["template_variables"] = template_variables
            if payload_templates:
                webhook_payloads["payload_templates"] = payload_templates
            details["webhook_payloads"] = webhook_payloads
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
