"""Pydantic models for Honeycomb Triggers."""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from honeycomb._generated_models import (
    BaseTriggerAlertType,
    BaseTriggerThreshold,
    BaseTriggerThresholdOp,
)
from honeycomb._generated_models import (
    TriggerResponse as _TriggerResponseGenerated,
)
from honeycomb._generated_models import (
    TriggerWithInlineQuery as _TriggerWithInlineQueryGenerated,
)

# Re-export generated enums with our names
TriggerThresholdOp = BaseTriggerThresholdOp  # GREATER_THAN, GREATER_THAN_OR_EQUAL, etc.
TriggerAlertType = BaseTriggerAlertType  # on_change, on_true

# Re-export threshold model
TriggerThreshold = BaseTriggerThreshold


class TriggerCreate(_TriggerWithInlineQueryGenerated):
    """Model for creating a trigger (extends generated TriggerWithInlineQuery).

    Use TriggerBuilder for fluent construction with validation.
    For query by reference, set query_id instead of query.

    Note: Both query and query_id are supported. The API uses a union type
    where you provide either an inline query dict or a query_id reference.
    """

    # Field overrides to make required fields explicit for tool schema
    name: str = Field(description="A short, human-readable name for this Trigger")
    threshold: BaseTriggerThreshold = Field(
        description="The threshold over which the trigger will fire"
    )

    # Add query_id field (from TriggerWithQueryReference) for complete API support
    query_id: str | None = Field(
        default=None,
        description="The ID of a Query that meets the criteria for being used as a Trigger.",
    )

    # Field override to add description for tool schema
    baseline_details: dict[str, Any] | None = Field(
        default=None,
        description="Baseline threshold configuration for comparing against historical data. "
        "Allows dynamic thresholds based on past values (e.g., alert if 20% higher than 1 day ago).",
    )

    @field_validator("frequency")
    @classmethod
    def validate_frequency_multiple(cls, v: int | None) -> int | None:
        """Validate that frequency is a multiple of 60."""
        if v is not None and v % 60 != 0:
            raise ValueError(f"Frequency must be a multiple of 60 seconds, got {v}")
        return v


class Trigger(_TriggerResponseGenerated):
    """A Honeycomb trigger (response model).

    Extends generated TriggerResponse with convenience properties.

    NOTE: extra="allow" used only for response model to handle
    API fields not in spec. NOT for input validation.
    """

    model_config = {"extra": "allow"}

    @property
    def dataset(self) -> str:
        """Alias for dataset_slug for convenience."""
        return self.dataset_slug or ""
