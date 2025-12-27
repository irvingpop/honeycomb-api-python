"""Pydantic models for Honeycomb Burn Alerts."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class BurnAlertType(str, Enum):
    """Burn alert types."""

    EXHAUSTION_TIME = "exhaustion_time"
    BUDGET_RATE = "budget_rate"


class BurnAlertRecipient(BaseModel):
    """A recipient for burn alert notifications.

    Either id (recommended) OR type+target (deprecated) must be provided.
    """

    id: str | None = Field(default=None, description="ID of the recipient")
    type: str | None = Field(default=None, description="Type of recipient (email, slack, etc)")
    target: str | None = Field(default=None, description="Target address (for backwards compat)")
    details: dict[str, Any] | None = Field(default=None, description="Additional details")


class BurnAlertCreate(BaseModel):
    """Model for creating a new burn alert."""

    alert_type: BurnAlertType = Field(description="Type of burn alert")
    slo_id: str = Field(description="ID of the SLO to monitor")
    description: str | None = Field(default=None, description="Description of the burn alert")
    recipients: list[BurnAlertRecipient] = Field(
        default_factory=list,
        description="List of recipients to notify when alert fires",
    )

    # Exhaustion time fields (required when alert_type=exhaustion_time)
    exhaustion_minutes: int | None = Field(
        default=None,
        description="Minutes until SLO budget exhaustion (for exhaustion_time alerts)",
    )

    # Budget rate fields (required when alert_type=budget_rate)
    budget_rate_window_minutes: int | None = Field(
        default=None, description="Time window in minutes (for budget_rate alerts)"
    )
    budget_rate_decrease_threshold_per_million: int | None = Field(
        default=None,
        description="Budget decrease threshold per million (for budget_rate alerts)",
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        # Build recipient list - support both id-based and inline (type+target) formats
        recipients_data = []
        for r in self.recipients:
            recipient_dict: dict[str, Any] = {}
            if r.id:
                # ID-based recipient (recommended)
                recipient_dict["id"] = r.id
                if r.type:
                    recipient_dict["type"] = r.type
            else:
                # Inline recipient (deprecated but still supported)
                if r.type:
                    recipient_dict["type"] = r.type
                if r.target:
                    recipient_dict["target"] = r.target
                if r.details:
                    recipient_dict["details"] = r.details
            recipients_data.append(recipient_dict)

        data: dict[str, Any] = {
            "alert_type": self.alert_type.value,
            "slo": {"id": self.slo_id},
            "recipients": recipients_data,
        }

        if self.description:
            data["description"] = self.description

        if self.alert_type == BurnAlertType.EXHAUSTION_TIME and self.exhaustion_minutes:
            data["exhaustion_minutes"] = self.exhaustion_minutes
        elif self.alert_type == BurnAlertType.BUDGET_RATE:
            if self.budget_rate_window_minutes:
                data["budget_rate_window_minutes"] = self.budget_rate_window_minutes
            if self.budget_rate_decrease_threshold_per_million:
                data["budget_rate_decrease_threshold_per_million"] = (
                    self.budget_rate_decrease_threshold_per_million
                )

        return data


class BurnAlert(BaseModel):
    """A Honeycomb burn alert (response model)."""

    id: str = Field(description="Unique identifier")
    alert_type: BurnAlertType = Field(description="Type of burn alert")
    slo_id: str | None = Field(default=None, description="ID of the associated SLO")
    description: str | None = Field(default=None, description="Description of the burn alert")
    triggered: bool = Field(default=False, description="Whether alert is currently triggered")

    # Exhaustion time fields
    exhaustion_minutes: int | None = Field(default=None, description="Minutes until exhaustion")

    # Budget rate fields
    budget_rate_window_minutes: int | None = Field(default=None, description="Time window")
    budget_rate_decrease_threshold_per_million: int | None = Field(
        default=None, description="Budget decrease threshold"
    )

    recipients: list[dict] | None = Field(default=None, description="List of recipients")
    slo: dict | None = Field(default=None, description="SLO details")

    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}
