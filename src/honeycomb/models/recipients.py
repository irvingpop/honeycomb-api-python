"""Pydantic models for Honeycomb Recipients."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RecipientType(str, Enum):
    """Recipient notification types."""

    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    MSTEAMS = "msteams"
    MSTEAMS_WORKFLOW = "msteams_workflow"


class RecipientCreate(BaseModel):
    """Model for creating a new recipient."""

    type: RecipientType = Field(description="Type of recipient")
    details: dict[str, Any] = Field(description="Recipient-specific configuration (varies by type)")

    def model_dump_for_api(self) -> dict:
        """Serialize for API request."""
        return {"type": self.type.value, "details": self.details}


class Recipient(BaseModel):
    """A Honeycomb notification recipient (response model)."""

    id: str = Field(description="Unique identifier")
    type: RecipientType = Field(description="Type of recipient")
    details: dict[str, Any] = Field(description="Recipient-specific configuration (varies by type)")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}
