"""Pydantic models for Honeycomb Triggers."""

from __future__ import annotations

from typing import Any

from pydantic import Field

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
from honeycomb._generated_models import (
    TriggerWithQueryReference as _TriggerWithQueryReferenceGenerated,
)

# Re-export generated enums with our names
TriggerThresholdOp = BaseTriggerThresholdOp  # GREATER_THAN, GREATER_THAN_OR_EQUAL, etc.
TriggerAlertType = BaseTriggerAlertType  # on_change, on_true

# Re-export threshold model
TriggerThreshold = BaseTriggerThreshold


# Wrap generated types to add field descriptions (Ground Rule #5: minimal overrides for tool schemas)
class TriggerWithInlineQuery(_TriggerWithInlineQueryGenerated):
    """Trigger creation with inline query (extends generated TriggerWithInlineQuery).

    Minimal wrapper to add field descriptions required for Claude tool schema generation.
    """

    # Override to add description for tool schema
    name: str = Field(description="A short, human-readable name for this Trigger")
    threshold: BaseTriggerThreshold = Field(
        description="The threshold over which the trigger will fire"
    )
    baseline_details: dict[str, Any] | None = Field(
        default=None,
        description="Baseline threshold configuration for comparing against historical data. "
        "Allows dynamic thresholds based on past values (e.g., alert if 20% higher than 1 day ago).",
    )


class TriggerWithQueryReference(_TriggerWithQueryReferenceGenerated):
    """Trigger creation with query reference (extends generated TriggerWithQueryReference).

    Minimal wrapper to add field descriptions required for Claude tool schema generation.
    """

    # Override to add description for tool schema
    name: str = Field(description="A short, human-readable name for this Trigger")
    threshold: BaseTriggerThreshold = Field(
        description="The threshold over which the trigger will fire"
    )
    query_id: str | None = Field(
        default=None,
        description="The ID of a Query that meets the criteria for being used as a Trigger.",
    )
    baseline_details: dict[str, Any] | None = Field(
        default=None,
        description="Baseline threshold configuration for comparing against historical data. "
        "Allows dynamic thresholds based on past values (e.g., alert if 20% higher than 1 day ago).",
    )


# Type union for trigger creation (vanilla - matches API structure)
# API accepts either inline query OR query reference (discriminated union)
TriggerCreate = TriggerWithInlineQuery | TriggerWithQueryReference


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
