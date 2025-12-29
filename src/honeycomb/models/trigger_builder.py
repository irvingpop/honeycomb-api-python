"""Builder pattern for Honeycomb Triggers with integrated query building."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from typing_extensions import Self

from .query_builder import QueryBuilder
from .recipient_builder import RecipientMixin
from .tags_mixin import TagsMixin
from .triggers import (
    TriggerAlertType,
    TriggerCreate,
    TriggerQuery,
    TriggerThreshold,
    TriggerThresholdOp,
)

if TYPE_CHECKING:
    pass


@dataclass
class TriggerBundle:
    """Bundle for trigger creation with inline recipients.

    Orchestrates:
    1. Create inline recipients via Recipients API
    2. Create trigger with recipient IDs

    Attributes:
        dataset: Dataset slug or "__all__" for environment-wide
        trigger: The TriggerCreate object
        inline_recipients: Recipients without 'id' field (need creation)
    """

    dataset: str
    trigger: TriggerCreate
    inline_recipients: list[dict[str, Any]]


class TriggerBuilder(QueryBuilder, RecipientMixin, TagsMixin):
    """Fluent builder for triggers with integrated query building.

    Extends QueryBuilder with trigger-specific constraints:
    - Only one calculation allowed
    - Time range limited to 3600 seconds (1 hour)
    - No absolute time ranges (start_time/end_time)
    - Dataset is optional (can be dataset-scoped or environment-wide)

    Example - Dataset-scoped trigger:
        >>> trigger = (
        ...     TriggerBuilder("High Error Rate")
        ...     .dataset("api-logs")
        ...     .last_30_minutes()
        ...     .count()
        ...     .gte("status", 500)
        ...     .threshold_gt(100)
        ...     .every_5_minutes()
        ...     .email("oncall@example.com")
        ...     .slack("#alerts")
        ...     .build()
        ... )
        >>> await client.triggers.create_async(trigger.get_dataset(), trigger)

    Example - Environment-wide trigger:
        >>> trigger = (
        ...     TriggerBuilder("Global Error Spike")
        ...     .environment_wide()
        ...     .last_10_minutes()
        ...     .count()
        ...     .eq("level", "error")
        ...     .threshold_gt(1000)
        ...     .every_minute()
        ...     .pagerduty("routing-key-123", severity="critical")
        ...     .build()
        ... )
        >>> await client.triggers.create_environment_wide_async(trigger)
    """

    def __init__(self, name: str):
        """Initialize TriggerBuilder with a name.

        Args:
            name: Human-readable name for the trigger.
        """
        QueryBuilder.__init__(self)
        RecipientMixin.__init__(self)
        TagsMixin.__init__(self)
        self._name = name
        self._description: str | None = None
        self._dataset: str | None = None  # None = environment-wide
        self._threshold_op: TriggerThresholdOp | None = None
        self._threshold_value: float | None = None
        self._exceeded_limit: int | None = None
        self._frequency: int = 900  # Default 15 minutes
        self._alert_type: TriggerAlertType = TriggerAlertType.ON_CHANGE
        self._disabled: bool = False
        self._baseline_details: dict[str, int | str] | None = None

    # -------------------------------------------------------------------------
    # Scope
    # -------------------------------------------------------------------------

    def description(self, desc: str) -> Self:
        """Set trigger description.

        Args:
            desc: Longer description for the trigger.

        Returns:
            Self for method chaining.
        """
        self._description = desc
        return self

    def dataset(self, dataset_slug: str) -> Self:
        """Scope trigger to a specific dataset.

        If not called, trigger will be environment-wide.

        Args:
            dataset_slug: Dataset slug to scope trigger to.

        Returns:
            Self for method chaining.
        """
        self._dataset = dataset_slug
        return self

    def environment_wide(self) -> Self:
        """Explicitly mark trigger as environment-wide (no dataset).

        Returns:
            Self for method chaining.
        """
        self._dataset = None
        return self

    # -------------------------------------------------------------------------
    # Threshold shortcuts
    # -------------------------------------------------------------------------

    def threshold_gt(self, value: float) -> Self:
        """Trigger when value > threshold.

        Args:
            value: Threshold value.

        Returns:
            Self for method chaining.
        """
        self._threshold_op = TriggerThresholdOp.GREATER_THAN
        self._threshold_value = value
        return self

    def threshold_gte(self, value: float) -> Self:
        """Trigger when value >= threshold.

        Args:
            value: Threshold value.

        Returns:
            Self for method chaining.
        """
        self._threshold_op = TriggerThresholdOp.GREATER_THAN_OR_EQUAL
        self._threshold_value = value
        return self

    def threshold_lt(self, value: float) -> Self:
        """Trigger when value < threshold.

        Args:
            value: Threshold value.

        Returns:
            Self for method chaining.
        """
        self._threshold_op = TriggerThresholdOp.LESS_THAN
        self._threshold_value = value
        return self

    def threshold_lte(self, value: float) -> Self:
        """Trigger when value <= threshold.

        Args:
            value: Threshold value.

        Returns:
            Self for method chaining.
        """
        self._threshold_op = TriggerThresholdOp.LESS_THAN_OR_EQUAL
        self._threshold_value = value
        return self

    def exceeded_limit(self, times: int) -> Self:
        """Require threshold to be exceeded N times before alerting.

        Args:
            times: Number of times threshold must be exceeded (1-5).

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If times is not between 1 and 5.
        """
        if not 1 <= times <= 5:
            raise ValueError("exceeded_limit must be between 1 and 5")
        self._exceeded_limit = times
        return self

    # -------------------------------------------------------------------------
    # Frequency presets
    # -------------------------------------------------------------------------

    def every_minute(self) -> Self:
        """Check trigger every minute (60 seconds).

        Returns:
            Self for method chaining.
        """
        self._frequency = 60
        return self

    def every_5_minutes(self) -> Self:
        """Check trigger every 5 minutes (300 seconds).

        Returns:
            Self for method chaining.
        """
        self._frequency = 300
        return self

    def every_15_minutes(self) -> Self:
        """Check trigger every 15 minutes (900 seconds) - default.

        Returns:
            Self for method chaining.
        """
        self._frequency = 900
        return self

    def every_30_minutes(self) -> Self:
        """Check trigger every 30 minutes (1800 seconds).

        Returns:
            Self for method chaining.
        """
        self._frequency = 1800
        return self

    def every_hour(self) -> Self:
        """Check trigger every hour (3600 seconds).

        Returns:
            Self for method chaining.
        """
        self._frequency = 3600
        return self

    def frequency(self, seconds: int) -> Self:
        """Set custom frequency in seconds (60-86400).

        Args:
            seconds: Check frequency in seconds (60-86400).

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If frequency is outside valid range.
        """
        if not 60 <= seconds <= 86400:
            raise ValueError("Frequency must be between 60 and 86400 seconds")
        self._frequency = seconds
        return self

    # -------------------------------------------------------------------------
    # Alert behavior
    # -------------------------------------------------------------------------

    def alert_on_change(self) -> Self:
        """Alert only when state changes (default).

        Returns:
            Self for method chaining.
        """
        self._alert_type = TriggerAlertType.ON_CHANGE
        return self

    def alert_on_true(self) -> Self:
        """Alert every time threshold is exceeded.

        Returns:
            Self for method chaining.
        """
        self._alert_type = TriggerAlertType.ON_TRUE
        return self

    def disabled(self, is_disabled: bool = True) -> Self:
        """Create trigger in disabled state.

        Args:
            is_disabled: Whether trigger should be disabled.

        Returns:
            Self for method chaining.
        """
        self._disabled = is_disabled
        return self

    # -------------------------------------------------------------------------
    # Baseline thresholds
    # -------------------------------------------------------------------------

    def baseline_1_hour_ago(
        self, comparison_type: Literal["percentage", "value"] = "percentage"
    ) -> Self:
        """Compare against results from 1 hour ago.

        Args:
            comparison_type: "percentage" for (current-baseline)/baseline,
                           "value" for current-baseline

        Returns:
            Self for method chaining.
        """
        self._baseline_details = {"offset_minutes": 60, "type": comparison_type}
        return self

    def baseline_1_day_ago(
        self, comparison_type: Literal["percentage", "value"] = "percentage"
    ) -> Self:
        """Compare against results from 1 day ago.

        Args:
            comparison_type: "percentage" or "value"

        Returns:
            Self for method chaining.
        """
        self._baseline_details = {"offset_minutes": 1440, "type": comparison_type}
        return self

    def baseline_1_week_ago(
        self, comparison_type: Literal["percentage", "value"] = "percentage"
    ) -> Self:
        """Compare against results from 1 week ago.

        Args:
            comparison_type: "percentage" or "value"

        Returns:
            Self for method chaining.
        """
        self._baseline_details = {"offset_minutes": 10080, "type": comparison_type}
        return self

    def baseline_4_weeks_ago(
        self, comparison_type: Literal["percentage", "value"] = "percentage"
    ) -> Self:
        """Compare against results from 4 weeks ago.

        Args:
            comparison_type: "percentage" or "value"

        Returns:
            Self for method chaining.
        """
        self._baseline_details = {"offset_minutes": 40320, "type": comparison_type}
        return self

    def baseline(
        self, offset_minutes: int, comparison_type: Literal["percentage", "value"]
    ) -> Self:
        """Set custom baseline comparison.

        Args:
            offset_minutes: How far back to compare. Must be one of: 60, 1440, 10080, 40320.
            comparison_type: "percentage" or "value"

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If offset_minutes is not a valid value.
        """
        valid_offsets = {60, 1440, 10080, 40320}
        if offset_minutes not in valid_offsets:
            raise ValueError(
                f"offset_minutes must be one of {valid_offsets} (1 hour, 1 day, 7 days, or 28 days)"
            )
        self._baseline_details = {"offset_minutes": offset_minutes, "type": comparison_type}
        return self

    # -------------------------------------------------------------------------
    # Build
    # -------------------------------------------------------------------------

    def _validate_and_get_components(
        self,
    ) -> tuple[
        TriggerThreshold,
        TriggerQuery,
        list[dict[str, Any]] | None,
        list[dict[str, str]] | None,
        dict[str, int | str] | None,
    ]:
        """Validate trigger configuration and return components.

        Returns:
            Tuple of (threshold, query, recipients, tags, baseline_details)

        Raises:
            ValueError: If constraints are violated
        """
        # Validate single calculation
        if len(self._calculations) > 1:
            raise ValueError(
                f"Triggers can only have one calculation, got {len(self._calculations)}. "
                "Use multiple triggers for multiple calculations."
            )

        # Validate no absolute time
        if self._start_time is not None or self._end_time is not None:
            raise ValueError(
                "Triggers do not support absolute time ranges. "
                "Use time_range() or time presets like last_30_minutes()."
            )

        # Validate time range
        time_range = self._time_range or 3600  # Default 1 hour
        if time_range > 3600:
            raise ValueError(
                f"Trigger time range must be <= 3600 seconds (1 hour), got {time_range}. "
                "Use a shorter time preset like last_30_minutes()."
            )

        # Validate frequency vs duration constraint
        # API rule: duration <= frequency * 4
        if time_range > self._frequency * 4:
            raise ValueError(
                f"Time range ({time_range}s) cannot be more than 4x frequency ({self._frequency}s). "
                f"Maximum time range for this frequency: {self._frequency * 4}s. "
                f"Either increase frequency or decrease time range."
            )

        # Validate threshold
        if self._threshold_op is None or self._threshold_value is None:
            raise ValueError(
                "Threshold is required. Use threshold_gt(), threshold_gte(), "
                "threshold_lt(), or threshold_lte()."
            )

        # Build threshold
        threshold = TriggerThreshold(
            op=self._threshold_op,
            value=self._threshold_value,
            exceeded_limit=self._exceeded_limit,
        )

        # Build query
        query = TriggerQuery(
            time_range=time_range,
            granularity=self._granularity,
            calculations=self._calculations if self._calculations else None,
            filters=self._filters if self._filters else None,
            breakdowns=self._breakdowns if self._breakdowns else None,
            filter_combination=self._filter_combination,
        )

        # Get recipients, tags, baseline if any
        recipients = self._get_all_recipients() if self._get_all_recipients() else None
        tags = self._get_all_tags()
        baseline = self._baseline_details

        return threshold, query, recipients, tags, baseline

    def build(self) -> TriggerBundle:  # type: ignore[override]
        """Build TriggerBundle with validation for orchestrated creation.

        Returns:
            TriggerBundle containing trigger and inline recipients

        Raises:
            ValueError: If constraints are violated:
                - More than one calculation
                - Time range > 3600 seconds
                - Absolute time used
                - Missing threshold
                - Frequency vs duration constraint (duration <= frequency * 4)
        """
        threshold, query, recipients, tags, baseline = self._validate_and_get_components()

        # Separate inline recipients (without 'id') from those with IDs
        inline_recipients: list[dict[str, Any]] = []
        recipients_with_ids: list[dict[str, Any]] = []

        if recipients:
            for recip in recipients:
                if "id" in recip:
                    recipients_with_ids.append(recip)
                else:
                    inline_recipients.append(recip.copy())

        # Build trigger with only the recipients that already have IDs
        trigger = TriggerCreate(
            name=self._name,
            description=self._description,
            threshold=threshold,
            frequency=self._frequency,
            query=query,
            disabled=self._disabled,
            alert_type=self._alert_type,
            recipients=recipients_with_ids if recipients_with_ids else None,
            tags=tags,
            baseline_details=baseline,
        )

        return TriggerBundle(
            dataset=self.get_dataset(),
            trigger=trigger,
            inline_recipients=inline_recipients,
        )

    def build_trigger(self) -> TriggerCreate:
        """Build TriggerCreate with validation (legacy method).

        Deprecated: Use build() which returns TriggerBundle for better orchestration.

        Returns:
            TriggerCreate object ready for API submission.

        Raises:
            ValueError: If constraints are violated (same as build())
        """
        threshold, query, recipients, tags, baseline = self._validate_and_get_components()

        return TriggerCreate(
            name=self._name,
            description=self._description,
            threshold=threshold,
            frequency=self._frequency,
            query=query,
            disabled=self._disabled,
            alert_type=self._alert_type,
            recipients=recipients,
            tags=tags,
            baseline_details=baseline,
        )

    def get_dataset(self) -> str:
        """Get the dataset this trigger is scoped to.

        Returns:
            Dataset slug or "__all__" for environment-wide triggers.
        """
        return self._dataset if self._dataset else "__all__"
