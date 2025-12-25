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


class BurnAlertCreate(BaseModel):
    """Model for creating a new burn alert."""

    alert_type: BurnAlertType = Field(description="Type of burn alert")
    slo_id: str = Field(description="ID of the SLO to monitor")
    description: str | None = Field(default=None, description="Description of the burn alert")

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
        data: dict[str, Any] = {"alert_type": self.alert_type.value, "slo_id": self.slo_id}

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

    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}
