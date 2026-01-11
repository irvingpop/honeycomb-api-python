"""Pydantic models for Honeycomb Recipients."""

from __future__ import annotations

from typing import Any

from pydantic import AwareDatetime

# Import and re-export all generated recipient types
# noqa comments prevent linter from removing re-export imports
from honeycomb._generated_models import (
    EmailRecipient,
    EmailRecipientDetails,  # noqa: F401
    MSTeamsRecipient,
    MSTeamsRecipientDetails,  # noqa: F401
    MSTeamsWorkflowRecipient,
    MSTeamsWorkflowRecipientDetails,  # noqa: F401
    PagerDutyRecipient,
    PagerDutyRecipientDetails,  # noqa: F401
    RecipientType,  # noqa: F401
    SlackRecipient,
    SlackRecipientDetails,  # noqa: F401
    TemplateVariableDefinition,
    WebhookHeader,  # noqa: F401
    WebhookRecipient,
    WebhookRecipientDetails,  # noqa: F401
    WebhookRecipientDetailsWebhookPayloads,
    WebhookRecipientDetailsWebhookPayloadsPayloadTemplates,
)
from honeycomb._generated_models import Recipient as _RecipientGenerated

# Backward-compatible aliases for webhook payload classes (shortened names)
WebhookPayloads = WebhookRecipientDetailsWebhookPayloads  # noqa: F401
WebhookPayloadTemplate = WebhookRecipientDetailsWebhookPayloadsPayloadTemplates  # noqa: F401
WebhookTemplateVariable = TemplateVariableDefinition  # noqa: F401

# Backward compatibility: RecipientCreate is a union of all recipient types
RecipientCreate = (
    EmailRecipient
    | SlackRecipient
    | PagerDutyRecipient
    | WebhookRecipient
    | MSTeamsRecipient
    | MSTeamsWorkflowRecipient
)

# Helper function for mapping recipient type to class
_RECIPIENT_TYPE_TO_CLASS = {
    RecipientType.email: EmailRecipient,
    RecipientType.slack: SlackRecipient,
    RecipientType.pagerduty: PagerDutyRecipient,
    RecipientType.webhook: WebhookRecipient,
    RecipientType.msteams: MSTeamsRecipient,
    RecipientType.msteams_workflow: MSTeamsWorkflowRecipient,
}


def get_recipient_class(recipient_type: RecipientType | str) -> type[RecipientCreate]:
    """Get the specific recipient class for a given type.

    Args:
        recipient_type: RecipientType enum or string value

    Returns:
        The appropriate recipient class (EmailRecipient, SlackRecipient, etc.)

    Example:
        >>> get_recipient_class(RecipientType.email)
        <class 'EmailRecipient'>
        >>> get_recipient_class("slack")
        <class 'SlackRecipient'>
    """
    if isinstance(recipient_type, str):
        recipient_type = RecipientType(recipient_type)
    return _RECIPIENT_TYPE_TO_CLASS[recipient_type]  # type: ignore[return-value]


class Recipient(_RecipientGenerated):
    """A Honeycomb notification recipient (response model, extends generated Recipient RootModel)."""

    @property
    def type(self) -> str:
        """Get recipient type from the discriminated union."""
        return self.root.type

    @property
    def details(self) -> Any:
        """Get recipient details from the discriminated union."""
        return self.root.details

    @property
    def id(self) -> str | None:
        """Get recipient ID from the discriminated union."""
        return self.root.id

    @property
    def created_at(self) -> AwareDatetime | None:
        """Get created_at from the discriminated union."""
        return self.root.created_at

    @property
    def updated_at(self) -> AwareDatetime | None:
        """Get updated_at from the discriminated union."""
        return self.root.updated_at
