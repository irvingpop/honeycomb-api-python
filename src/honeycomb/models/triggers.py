"""Pydantic models for Honeycomb Triggers."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from honeycomb.models.query_builder import (
    CalcOp,
    Calculation,
    Filter,
    FilterCombination,
)


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
        default=None,
        ge=1,
        le=5,
        description="Number of times threshold must be exceeded (1-5, default 1)",
    )


def _default_calculations() -> list[Calculation | dict[str, Any]]:
    """Default calculations for TriggerQuery."""
    return [Calculation(op=CalcOp.COUNT)]


class TriggerQuery(BaseModel):
    """Inline query specification for a trigger.

    Accepts both typed models and dicts for flexibility:
        >>> # Using typed models
        >>> TriggerQuery(calculations=[Calculation(op=CalcOp.P99, column="duration_ms")])

        >>> # Using dicts
        >>> TriggerQuery(calculations=[{"op": "P99", "column": "duration_ms"}])
    """

    time_range: int = Field(
        default=900,
        ge=300,
        le=3600,
        description="Query time range in seconds (300-3600, i.e. 5 min to 1 hour)",
    )
    granularity: int | None = Field(default=None, description="Time granularity in seconds")
    calculations: list[Calculation | dict[str, Any]] | None = Field(
        default_factory=_default_calculations,
        description="Calculations to perform",
    )
    filters: list[Filter | dict[str, Any]] | None = Field(default=None, description="Query filters")
    breakdowns: list[str] | None = Field(default=None, description="Columns to group by")
    filter_combination: FilterCombination | str | None = Field(
        default=None, description="How to combine filters (AND/OR)"
    )

    @field_validator("calculations")
    @classmethod
    def validate_single_calculation(
        cls, v: list[Calculation | dict[str, Any]] | None
    ) -> list[Calculation | dict[str, Any]] | None:
        """Validate that only one calculation is provided (trigger limitation)."""
        if v is not None and len(v) > 1:
            raise ValueError(
                f"Triggers support only a single calculation, got {len(v)}. "
                "Use multiple triggers or a saved query if you need multiple calculations."
            )
        return v


def _normalize_calculation(calc: Calculation | dict[str, Any]) -> dict[str, Any]:
    """Convert a Calculation or dict to API dict format."""
    if isinstance(calc, Calculation):
        return calc.to_dict()
    return calc


def _normalize_filter(filt: Filter | dict[str, Any]) -> dict[str, Any]:
    """Convert a Filter or dict to API dict format."""
    if isinstance(filt, Filter):
        return filt.to_dict()
    return filt


def _normalize_filter_combination(combo: FilterCombination | str | None) -> str | None:
    """Convert a FilterCombination or string to API format."""
    if combo is None:
        return None
    if isinstance(combo, FilterCombination):
        return combo.value
    return combo


class TriggerCreate(BaseModel):
    """Model for creating a new trigger."""

    name: str = Field(description="Human-readable name for the trigger")
    description: str | None = Field(default=None, description="Longer description")
    threshold: TriggerThreshold = Field(description="Threshold configuration")
    frequency: int = Field(
        default=900,
        ge=60,
        le=86400,
        description="Check frequency in seconds (60-86400, must be multiple of 60)",
        json_schema_extra={"multipleOf": 60},
    )
    query: TriggerQuery | None = Field(default=None, description="Inline query")
    query_id: str | None = Field(default=None, description="Reference to saved query")
    disabled: bool = Field(default=False, description="Whether trigger is disabled")
    alert_type: TriggerAlertType = Field(
        default=TriggerAlertType.ON_CHANGE,
        description="When to send alerts",
    )
    recipients: list[dict] | None = Field(default=None, description="Notification recipients")
    tags: list[dict[str, str]] | None = Field(
        default=None, description="Tags for organizing triggers (max 10)"
    )
    baseline_details: dict[str, Any] | None = Field(
        default=None,
        description="Baseline threshold configuration for comparing against historical data",
    )

    @field_validator("frequency")
    @classmethod
    def validate_frequency_multiple(cls, v: int) -> int:
        """Validate that frequency is a multiple of 60."""
        if v % 60 != 0:
            raise ValueError(f"Frequency must be a multiple of 60 seconds, got {v}")
        return v

    def model_dump_for_api(self) -> dict[str, Any]:
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
                    _normalize_calculation(c) for c in self.query.calculations
                ]
            if self.query.filters:
                query_data["filters"] = [_normalize_filter(f) for f in self.query.filters]
            if self.query.breakdowns:
                query_data["breakdowns"] = self.query.breakdowns
            if self.query.filter_combination:
                query_data["filter_combination"] = _normalize_filter_combination(
                    self.query.filter_combination
                )
            data["query"] = query_data

        if self.query_id:
            data["query_id"] = self.query_id

        if self.recipients:
            data["recipients"] = self.recipients

        if self.tags:
            data["tags"] = self.tags

        if self.baseline_details:
            data["baseline_details"] = self.baseline_details

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
    tags: list[dict[str, str]] | None = Field(
        default=None, description="Tags for organizing triggers"
    )
    baseline_details: dict[str, Any] | None = Field(
        default=None, description="Baseline threshold configuration"
    )
    evaluation_schedule_type: str | None = Field(default=None)
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}

    @property
    def dataset(self) -> str:
        """Alias for dataset_slug for convenience."""
        return self.dataset_slug
