"""SLO Builder - Fluent interface for creating SLOs with burn alerts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from honeycomb.models.burn_alerts import BurnAlertType
from honeycomb.models.recipient_builder import RecipientMixin
from honeycomb.models.slos import SLI, SLOCreate
from honeycomb.validation.slos import validate_slo_target_percentage, validate_slo_time_period

if TYPE_CHECKING:
    from honeycomb.models.derived_columns import DerivedColumnCreate


@dataclass
class SLIDefinition:
    """SLI definition - either references existing DC or creates new one."""

    alias: str
    expression: str | None = None  # None = use existing DC
    description: str | None = None

    def is_new_derived_column(self) -> bool:
        """Check if this SLI requires creating a new derived column."""
        return self.expression is not None


@dataclass
class BurnAlertDefinition:
    """Burn alert definition with embedded recipients."""

    alert_type: BurnAlertType
    description: str | None = None
    # Exhaustion time fields
    exhaustion_minutes: int | None = None
    # Budget rate fields
    budget_rate_window_minutes: int | None = None
    budget_rate_decrease_percent: float | None = None
    # Recipients
    recipients: list[dict] = field(default_factory=list)


@dataclass
class SLOBundle:
    """Bundle containing SLO and related resources to create.

    Attributes:
        slo: The SLOCreate object
        datasets: List of dataset slugs (single or multiple)
        derived_column: DerivedColumnCreate if SLI needs new DC
        derived_column_environment_wide: True if multi-dataset
        burn_alerts: List of burn alert definitions
    """

    slo: SLOCreate
    datasets: list[str]
    derived_column: DerivedColumnCreate | None
    derived_column_environment_wide: bool
    burn_alerts: list[BurnAlertDefinition]


class BurnAlertBuilder(RecipientMixin):
    """Builder for burn alerts with recipients.

    Example - Exhaustion time alert:
        alert = (
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            .exhaustion_minutes(60)
            .description("Alert when budget exhausts in 1 hour")
            .email("oncall@example.com")
            .slack("#alerts")
            .build()
        )

    Example - Budget rate alert:
        alert = (
            BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
            .window_minutes(60)
            .threshold_percent(1.0)
            .pagerduty("routing-key", severity="critical")
            .build()
        )
    """

    def __init__(self, alert_type: BurnAlertType):
        RecipientMixin.__init__(self)
        self._alert_type = alert_type
        self._description: str | None = None
        self._exhaustion_minutes: int | None = None
        self._budget_rate_window_minutes: int | None = None
        self._budget_rate_decrease_percent: float | None = None

    def description(self, desc: str) -> BurnAlertBuilder:
        """Set burn alert description."""
        self._description = desc
        return self

    # -------------------------------------------------------------------------
    # Exhaustion time config
    # -------------------------------------------------------------------------

    def exhaustion_minutes(self, minutes: int) -> BurnAlertBuilder:
        """Set exhaustion time threshold in minutes.

        Alert triggers when error budget will be exhausted within this timeframe.

        Args:
            minutes: Minutes until exhaustion threshold (e.g., 60 = 1 hour)
        """
        self._exhaustion_minutes = minutes
        return self

    # -------------------------------------------------------------------------
    # Budget rate config
    # -------------------------------------------------------------------------

    def window_minutes(self, minutes: int) -> BurnAlertBuilder:
        """Set budget rate window in minutes.

        Args:
            minutes: Time window for budget rate calculation
        """
        self._budget_rate_window_minutes = minutes
        return self

    def threshold_percent(self, percent: float) -> BurnAlertBuilder:
        """Set budget decrease threshold as percentage.

        Args:
            percent: Budget decrease threshold (e.g., 1.0 = 1%)
        """
        self._budget_rate_decrease_percent = percent
        return self

    # -------------------------------------------------------------------------
    # Build
    # -------------------------------------------------------------------------

    def build(self) -> BurnAlertDefinition:
        """Build BurnAlertDefinition with validation.

        Returns:
            BurnAlertDefinition with all configured settings

        Raises:
            ValueError: If required fields for alert type are missing
        """
        # Validate alert type specific fields
        if self._alert_type == BurnAlertType.EXHAUSTION_TIME:
            if self._exhaustion_minutes is None:
                raise ValueError(
                    "exhaustion_minutes is required for EXHAUSTION_TIME alerts. "
                    "Use exhaustion_minutes()."
                )
        elif self._alert_type == BurnAlertType.BUDGET_RATE:
            if self._budget_rate_window_minutes is None:
                raise ValueError(
                    "window_minutes is required for BUDGET_RATE alerts. Use window_minutes()."
                )
            if self._budget_rate_decrease_percent is None:
                raise ValueError(
                    "threshold_percent is required for BUDGET_RATE alerts. Use threshold_percent()."
                )

        return BurnAlertDefinition(
            alert_type=self._alert_type,
            description=self._description,
            exhaustion_minutes=self._exhaustion_minutes,
            budget_rate_window_minutes=self._budget_rate_window_minutes,
            budget_rate_decrease_percent=self._budget_rate_decrease_percent,
            recipients=self._get_all_recipients(),
        )


class SLOBuilder:
    """Fluent builder for SLOs with burn alerts and derived columns.

    Example - Single dataset with existing derived column:
        slo = (
            SLOBuilder("API Availability")
            .dataset("api-logs")
            .target_percentage(99.9)
            .time_period_days(30)
            .sli(alias="api_success_rate")
            .exhaustion_alert(
                BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
                .exhaustion_minutes(60)
                .email("oncall@example.com")
            )
            .build()
        )

    Example - Multiple datasets with new derived column:
        slo = (
            SLOBuilder("Cross-Service Availability")
            .datasets(["api-logs", "web-logs", "worker-logs"])
            .target_percentage(99.9)
            .sli(
                alias="service_success",
                expression="IF(EQUALS($status, 200), 1, 0)",
                description="1 for success, 0 for failure"
            )
            .budget_rate_alert(
                BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
                .window_minutes(60)
                .threshold_percent(1.0)
                .pagerduty("routing-key", severity="critical")
            )
            .build()
        )
    """

    def __init__(self, name: str):
        self._name = name
        self._description: str | None = None
        self._datasets: list[str] = []
        self._target_per_million: int | None = None
        self._time_period_days: int = 30
        self._sli: SLIDefinition | None = None
        self._burn_alerts: list[BurnAlertDefinition] = []
        self._tags: list[dict[str, str]] = []

    # -------------------------------------------------------------------------
    # Basic configuration
    # -------------------------------------------------------------------------

    def description(self, desc: str) -> SLOBuilder:
        """Set SLO description."""
        self._description = desc
        return self

    def tag(self, key: str, value: str) -> SLOBuilder:
        """Add a tag key-value pair for organizing the SLO.

        Tags are useful for filtering and grouping SLOs by team, service,
        criticality, or other dimensions.

        Args:
            key: Tag key (lowercase letters, max 32 chars)
            value: Tag value (alphanumeric, /, -, max 128 chars)

        Example:
            >>> builder.tag("team", "platform").tag("service", "api")

        Returns:
            self for chaining
        """
        self._tags.append({"key": key, "value": value})
        return self

    # -------------------------------------------------------------------------
    # Dataset scope
    # -------------------------------------------------------------------------

    def dataset(self, dataset_slug: str) -> SLOBuilder:
        """Scope SLO to a single dataset.

        Args:
            dataset_slug: Dataset slug
        """
        self._datasets = [dataset_slug]
        return self

    def datasets(self, dataset_slugs: list[str]) -> SLOBuilder:
        """Scope SLO to multiple datasets.

        Note: When using multiple datasets, any new derived column
        will be created as environment-wide.

        Args:
            dataset_slugs: List of dataset slugs
        """
        self._datasets = dataset_slugs
        return self

    # -------------------------------------------------------------------------
    # Target configuration
    # -------------------------------------------------------------------------

    def target_percentage(self, percent: float) -> SLOBuilder:
        """Set target as percentage (e.g., 99.9 -> 999000 per million).

        Args:
            percent: Target percentage (e.g., 99.9)

        Raises:
            ValueError: If percent is outside 0-100 range
        """
        validate_slo_target_percentage(percent)
        self._target_per_million = int(percent * 10000)
        return self

    def target_per_million(self, value: int) -> SLOBuilder:
        """Set target directly as per-million value.

        Args:
            value: Target per million (e.g., 999000 = 99.9%)
        """
        self._target_per_million = value
        return self

    # -------------------------------------------------------------------------
    # Time period
    # -------------------------------------------------------------------------

    def time_period_days(self, days: int) -> SLOBuilder:
        """Set SLO time period in days (1-90).

        Args:
            days: Time period in days

        Raises:
            ValueError: If days not in range 1-90
        """
        validate_slo_time_period(days)
        self._time_period_days = days
        return self

    def time_period_weeks(self, weeks: int) -> SLOBuilder:
        """Set SLO time period in weeks.

        Args:
            weeks: Time period in weeks
        """
        return self.time_period_days(weeks * 7)

    # -------------------------------------------------------------------------
    # SLI definition
    # -------------------------------------------------------------------------

    def sli(
        self,
        alias: str,
        expression: str | None = None,
        description: str | None = None,
    ) -> SLOBuilder:
        """Define the SLI (Service Level Indicator).

        Args:
            alias: Name of the derived column (existing or new)
            expression: If provided, creates a new derived column.
                        If None, uses an existing derived column.
            description: Description for new derived column (ignored if using existing)

        Examples:
            # Use existing derived column
            .sli(alias="api_success_rate")

            # Create new derived column
            .sli(
                alias="request_success",
                expression="IF(LT($status_code, 400), 1, 0)",
                description="1 if request succeeded, 0 otherwise"
            )
        """
        self._sli = SLIDefinition(
            alias=alias,
            expression=expression,
            description=description,
        )
        return self

    # -------------------------------------------------------------------------
    # Burn alerts
    # -------------------------------------------------------------------------

    def exhaustion_alert(self, builder: BurnAlertBuilder) -> SLOBuilder:
        """Add an exhaustion time burn alert.

        Args:
            builder: BurnAlertBuilder configured with EXHAUSTION_TIME type

        Example:
            .exhaustion_alert(
                BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
                .exhaustion_minutes(60)
                .description("Alert when budget exhausts in 1 hour")
                .email("oncall@example.com")
            )

        Raises:
            ValueError: If builder is not EXHAUSTION_TIME type
        """
        if builder._alert_type != BurnAlertType.EXHAUSTION_TIME:
            raise ValueError("exhaustion_alert() requires EXHAUSTION_TIME alert type")
        self._burn_alerts.append(builder.build())
        return self

    def budget_rate_alert(self, builder: BurnAlertBuilder) -> SLOBuilder:
        """Add a budget rate burn alert.

        Args:
            builder: BurnAlertBuilder configured with BUDGET_RATE type

        Example:
            .budget_rate_alert(
                BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
                .window_minutes(60)
                .threshold_percent(1.0)
                .pagerduty("routing-key")
            )

        Raises:
            ValueError: If builder is not BUDGET_RATE type
        """
        if builder._alert_type != BurnAlertType.BUDGET_RATE:
            raise ValueError("budget_rate_alert() requires BUDGET_RATE alert type")
        self._burn_alerts.append(builder.build())
        return self

    # -------------------------------------------------------------------------
    # Build
    # -------------------------------------------------------------------------

    def build(self) -> SLOBundle:
        """Build SLO bundle with validation.

        Returns:
            SLOBundle containing:
            - slo: The SLOCreate object
            - datasets: List of dataset slugs
            - derived_column: DerivedColumnCreate if SLI needs new DC
            - derived_column_environment_wide: True if multi-dataset
            - burn_alerts: List of burn alert definitions

        Raises:
            ValueError: If required fields are missing
        """
        if not self._datasets:
            raise ValueError("At least one dataset is required. Use dataset() or datasets().")

        if self._target_per_million is None:
            raise ValueError("Target is required. Use target_percentage() or target_per_million().")

        if self._sli is None:
            raise ValueError("SLI is required. Use sli(alias=...) to define it.")

        # Determine if derived column should be environment-wide
        is_multi_dataset = len(self._datasets) > 1

        # Build derived column if needed
        derived_column = None
        if self._sli.is_new_derived_column():
            # Import here to avoid circular dependency
            from honeycomb.models.derived_columns import DerivedColumnCreate

            derived_column = DerivedColumnCreate(
                alias=self._sli.alias,
                expression=self._sli.expression,
                description=self._sli.description,
            )

        # Build SLO
        slo = SLOCreate(
            name=self._name,
            description=self._description,
            sli=SLI(alias=self._sli.alias),
            time_period_days=self._time_period_days,
            target_per_million=self._target_per_million,
            tags=self._tags if self._tags else None,
            dataset_slugs=self._datasets if is_multi_dataset else None,
        )

        return SLOBundle(
            slo=slo,
            datasets=self._datasets,
            derived_column=derived_column,
            derived_column_environment_wide=is_multi_dataset,
            burn_alerts=self._burn_alerts,
        )
