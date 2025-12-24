"""Pydantic models for Honeycomb Triggers."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TriggerThresholdOp(str, Enum):
    """Threshold comparison operators."""

    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="


class TriggerAlertType(str, Enum):
    """How often to fire an alert when threshold is crossed."""

    ON_CHANGE = "on_change"
    ON_TRUE = "on_true"


class TriggerThreshold(BaseModel):
    """Threshold configuration for a trigger."""

    op: TriggerThresholdOp = Field(description="Comparison operator")
    value: float = Field(description="Threshold value")
    exceeded_limit: int | None = Field(
        default=None, description="Number of times threshold must be exceeded"
    )


class QueryCalculation(BaseModel):
    """A calculation in a query."""

    op: str = Field(description="Calculation operation (COUNT, AVG, P99, etc.)")
    column: str | None = Field(default=None, description="Column to calculate on")


class QueryFilter(BaseModel):
    """A filter in a query."""

    column: str = Field(description="Column to filter on")
    op: str = Field(description="Filter operator (=, !=, >, <, contains, etc.)")
    value: Any = Field(description="Filter value")


class TriggerQuery(BaseModel):
    """Inline query specification for a trigger.

    Note: time_range must be <= 3600 (1 hour) for triggers.
    """

    time_range: int = Field(
        default=3600,
        le=3600,
        description="Query time range in seconds (max 3600 for triggers)",
    )
    granularity: int | None = Field(default=None, description="Time granularity in seconds")
    calculations: list[QueryCalculation] = Field(
        default_factory=lambda: [QueryCalculation(op="COUNT")],
        description="Calculations to perform",
    )
    filters: list[QueryFilter] | None = Field(default=None, description="Query filters")
    breakdowns: list[str] | None = Field(default=None, description="Columns to group by")
    filter_combination: str | None = Field(
        default=None, description="How to combine filters (AND/OR)"
    )


class TriggerCreate(BaseModel):
    """Model for creating a new trigger."""

    name: str = Field(description="Human-readable name for the trigger")
    description: str | None = Field(default=None, description="Longer description")
    threshold: TriggerThreshold = Field(description="Threshold configuration")
    frequency: int = Field(
        default=900,
        ge=60,
        le=86400,
        description="Check frequency in seconds (60-86400)",
    )
    query: TriggerQuery | None = Field(default=None, description="Inline query")
    query_id: str | None = Field(default=None, description="Reference to saved query")
    disabled: bool = Field(default=False, description="Whether trigger is disabled")
    alert_type: TriggerAlertType = Field(
        default=TriggerAlertType.ON_CHANGE,
        description="When to send alerts",
    )
    recipients: list[dict] | None = Field(default=None, description="Notification recipients")

    def model_dump_for_api(self) -> dict:
        """Serialize for API request, handling nested models."""
        data: dict[str, Any] = {
            "name": self.name,
            "threshold": {
                "op": self.threshold.op.value,
                "value": self.threshold.value,
            },
            "frequency": self.frequency,
            "disabled": self.disabled,
            "alert_type": self.alert_type.value,
        }

        if self.description:
            data["description"] = self.description

        if self.threshold.exceeded_limit is not None:
            data["threshold"]["exceeded_limit"] = self.threshold.exceeded_limit

        if self.query:
            query_data: dict[str, Any] = {"time_range": self.query.time_range}
            if self.query.granularity:
                query_data["granularity"] = self.query.granularity
            if self.query.calculations:
                query_data["calculations"] = [
                    {"op": c.op, "column": c.column} if c.column else {"op": c.op}
                    for c in self.query.calculations
                ]
            if self.query.filters:
                query_data["filters"] = [
                    {"column": f.column, "op": f.op, "value": f.value} for f in self.query.filters
                ]
            if self.query.breakdowns:
                query_data["breakdowns"] = self.query.breakdowns
            if self.query.filter_combination:
                query_data["filter_combination"] = self.query.filter_combination
            data["query"] = query_data

        if self.query_id:
            data["query_id"] = self.query_id

        if self.recipients:
            data["recipients"] = self.recipients

        return data


class Trigger(BaseModel):
    """A Honeycomb trigger (response model)."""

    id: str = Field(description="Unique identifier")
    name: str = Field(description="Human-readable name")
    description: str | None = Field(default=None, description="Longer description")
    dataset_slug: str = Field(description="Dataset this trigger belongs to")
    threshold: TriggerThreshold = Field(description="Threshold configuration")
    frequency: int = Field(description="Check frequency in seconds")
    query: dict | None = Field(default=None, description="Inline query")
    query_id: str | None = Field(default=None, description="Reference to saved query")
    disabled: bool = Field(default=False, description="Whether trigger is disabled")
    triggered: bool = Field(default=False, description="Whether currently triggered")
    alert_type: str = Field(default="on_change", description="When to send alerts")
    recipients: list[dict] | None = Field(default=None, description="Notification recipients")
    evaluation_schedule_type: str | None = Field(default=None)
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}
