"""Factories for Recipient models (discriminated union).

Since Recipients use a discriminated union with a type field, we create separate
factories for each recipient type rather than trying to handle the union directly.
"""

from honeycomb._generated_models import (
    EmailRecipientDetails,
    WebhookHeader,
    WebhookRecipientDetails,
)
from honeycomb.models import EmailRecipient, Recipient, WebhookRecipient

from .base import HoneycombFactory

# =============================================================================
# Email Recipient Factories
# =============================================================================


class EmailRecipientDetailsFactory(HoneycombFactory):
    """Factory for EmailRecipientDetails."""

    __model__ = EmailRecipientDetails

    email_address = lambda: f"alerts-{HoneycombFactory._honeycomb_id()}@example.com"


class EmailRecipientFactory(HoneycombFactory):
    """Factory for EmailRecipient.

    Example:
        recipient = EmailRecipientFactory.build()
        recipient_with_email = EmailRecipientFactory.build(
            details=EmailRecipientDetailsFactory.build(email_address="custom@example.com")
        )
    """

    __model__ = EmailRecipient

    id = lambda: HoneycombFactory._honeycomb_id()
    type = "email"
    created_at = lambda: HoneycombFactory._honeycomb_timestamp()
    updated_at = lambda: HoneycombFactory._honeycomb_timestamp()


# =============================================================================
# Webhook Recipient Factories
# =============================================================================


class WebhookHeaderFactory(HoneycombFactory):
    """Factory for WebhookHeader."""

    __model__ = WebhookHeader

    header = "Authorization"
    value = lambda: f"Bearer {HoneycombFactory._honeycomb_id()}"


class WebhookRecipientDetailsFactory(HoneycombFactory):
    """Factory for WebhookRecipientDetails."""

    __model__ = WebhookRecipientDetails

    webhook_name = lambda: f"Test Webhook {HoneycombFactory._honeycomb_id()}"
    webhook_url = lambda: f"https://webhook.example.com/{HoneycombFactory._honeycomb_id()}"


class WebhookRecipientFactory(HoneycombFactory):
    """Factory for WebhookRecipient.

    Example:
        recipient = WebhookRecipientFactory.build()
    """

    __model__ = WebhookRecipient

    id = lambda: HoneycombFactory._honeycomb_id()
    type = "webhook"
    created_at = lambda: HoneycombFactory._honeycomb_timestamp()
    updated_at = lambda: HoneycombFactory._honeycomb_timestamp()


# =============================================================================
# Recipient (RootModel) Factory
# =============================================================================


class RecipientFactory(HoneycombFactory):
    """Factory for Recipient (RootModel wrapper).

    Since Recipient is a discriminated union, you should typically use
    the specific factories (EmailRecipientFactory, WebhookRecipientFactory)
    directly. This factory wraps EmailRecipient by default.

    Example:
        recipient = RecipientFactory.build()  # Returns email recipient
    """

    __model__ = Recipient

    @classmethod
    def build(cls, **kwargs):
        """Build a Recipient with EmailRecipient as default root."""
        if "root" not in kwargs:
            kwargs["root"] = EmailRecipientFactory.build()
        return super().build(**kwargs)

    @classmethod
    def build_email(cls, **details_kwargs):
        """Build an email recipient."""
        details = EmailRecipientDetailsFactory.build(**details_kwargs)
        return cls.build(root=EmailRecipientFactory.build(details=details))

    @classmethod
    def build_webhook(cls, **details_kwargs):
        """Build a webhook recipient."""
        details = WebhookRecipientDetailsFactory.build(**details_kwargs)
        return cls.build(root=WebhookRecipientFactory.build(details=details))
