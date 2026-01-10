"""Pydantic models for Honeycomb Recipients."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, Field, field_validator


class RecipientType(str, Enum):
    """Recipient notification types."""

    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    MSTEAMS = "msteams"
    MSTEAMS_WORKFLOW = "msteams_workflow"


# Recipient Details Models


class EmailRecipientDetails(BaseModel):
    """Details for email recipient."""

    model_config = {"extra": "forbid"}

    email_address: str = Field(description="Email address to notify")


class SlackRecipientDetails(BaseModel):
    """Details for Slack recipient."""

    model_config = {"extra": "forbid"}

    slack_channel: str = Field(description="Slack channel name (e.g., '#alerts')")


class PagerDutyRecipientDetails(BaseModel):
    """Details for PagerDuty recipient."""

    model_config = {"extra": "forbid"}

    pagerduty_integration_key: str = Field(
        description="PagerDuty integration key (32 characters)", min_length=32, max_length=32
    )
    pagerduty_integration_name: str = Field(description="Name for this PagerDuty integration")


class WebhookHeader(BaseModel):
    """HTTP header for webhook requests."""

    header: str = Field(description="Header name", max_length=64)
    value: str | None = Field(default=None, description="Header value", max_length=750)


class WebhookPayloadTemplate(BaseModel):
    """Template for webhook payload."""

    body: str = Field(description="Template body")


class WebhookTemplateVariable(BaseModel):
    """Template variable for webhook payloads."""

    name: str = Field(description="Variable name")
    default_value: str = Field(description="Default value for variable")


class WebhookPayloads(BaseModel):
    """Webhook payload configuration."""

    template_variables: list[WebhookTemplateVariable] | None = Field(
        default=None, max_length=10, description="Template variables (max 10)"
    )
    payload_templates: dict[str, WebhookPayloadTemplate] | None = Field(
        default=None, description="Payload templates by alert type"
    )


class WebhookRecipientDetails(BaseModel):
    """Details for webhook recipient."""

    model_config = {"extra": "forbid"}

    webhook_url: str = Field(description="Webhook URL to POST to", max_length=2048)
    webhook_name: str = Field(description="Name for this webhook", max_length=255)
    webhook_secret: str | None = Field(
        default=None, description="Optional webhook secret for signing", max_length=255
    )
    webhook_headers: list[WebhookHeader] | None = Field(
        default=None, max_length=5, description="Optional HTTP headers (max 5)"
    )
    webhook_payloads: WebhookPayloads | None = Field(
        default=None, description="Optional custom payload configuration"
    )


class MSTeamsRecipientDetails(BaseModel):
    """Details for MS Teams recipient (deprecated - use MSTeamsWorkflowRecipientDetails)."""

    model_config = {"extra": "forbid"}

    webhook_url: str = Field(description="MS Teams webhook URL", max_length=2048)
    webhook_name: str = Field(description="Name for this webhook", max_length=255)


class MSTeamsWorkflowRecipientDetails(BaseModel):
    """Details for MS Teams Workflow recipient."""

    model_config = {"extra": "forbid"}

    webhook_url: str = Field(description="MS Teams workflow webhook URL", max_length=2048)
    webhook_name: str = Field(description="Name for this webhook", max_length=255)


# Union type for all recipient details
RecipientDetails = Annotated[
    EmailRecipientDetails
    | SlackRecipientDetails
    | PagerDutyRecipientDetails
    | WebhookRecipientDetails
    | MSTeamsRecipientDetails
    | MSTeamsWorkflowRecipientDetails,
    Field(discriminator="type"),
]


class RecipientCreate(BaseModel):
    """Model for creating a new recipient with strict validation."""

    type: RecipientType = Field(description="Type of recipient")
    details: (
        EmailRecipientDetails
        | SlackRecipientDetails
        | PagerDutyRecipientDetails
        | WebhookRecipientDetails
        | MSTeamsRecipientDetails
        | MSTeamsWorkflowRecipientDetails
    ) = Field(description="Recipient-specific configuration (varies by type)")

    @field_validator("details", mode="before")
    @classmethod
    def validate_details_match_type(cls, v: Any, info: Any) -> Any:
        """Validate that details match the recipient type."""
        if not isinstance(v, dict):
            return v

        recipient_type = info.data.get("type")
        if not recipient_type:
            return v

        # Map types to detail classes
        type_to_details = {
            RecipientType.EMAIL: EmailRecipientDetails,
            RecipientType.SLACK: SlackRecipientDetails,
            RecipientType.PAGERDUTY: PagerDutyRecipientDetails,
            RecipientType.WEBHOOK: WebhookRecipientDetails,
            RecipientType.MSTEAMS: MSTeamsRecipientDetails,
            RecipientType.MSTEAMS_WORKFLOW: MSTeamsWorkflowRecipientDetails,
        }

        details_class = type_to_details.get(recipient_type)
        if details_class:
            return details_class(**v)
        return v

    def model_dump_for_api(self) -> dict:
        """Serialize for API request."""
        return {"type": self.type.value, "details": self.details.model_dump()}


class Recipient(BaseModel):
    """A Honeycomb notification recipient (response model)."""

    id: str = Field(description="Unique identifier")
    type: RecipientType = Field(description="Type of recipient")
    details: dict[str, Any] = Field(description="Recipient-specific configuration (varies by type)")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}
