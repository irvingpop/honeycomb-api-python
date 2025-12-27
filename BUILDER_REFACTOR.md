# Builder Refactor Plan

## Overview

This document outlines a comprehensive refactor to create an integrated, elegant builder system for the Honeycomb Python client. The design prioritizes:

1. **No duplicated capabilities** - Shared functionality lives in one place
2. **Clean composition** - Builders compose smaller pieces rather than duplicate
3. **Constraint enforcement** - Builders enforce API constraints at build time
4. **Flexibility** - Support both simple and advanced use cases

## Architecture

### Shared Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        RecipientMixin                           │
│  .email() .slack() .pagerduty() .webhook() .msteams()          │
│  .recipient_id()                                                │
└─────────────────────────────────────────────────────────────────┘
                              ▲
              ┌───────────────┼───────────────┐
              │               │               │
      TriggerBuilder    BurnAlertBuilder    (future)

┌─────────────────────────────────────────────────────────────────┐
│                        QueryBuilder                             │
│  Time: .last_1_hour() .time_range() .start_time() .end_time()  │
│  Calcs: .count() .avg() .p99() .sum() .max() .min() ...        │
│  Filters: .eq() .gte() .contains() .exists() .filter_with()    │
│  Grouping: .group_by() .order_by() .limit()                    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ (extends with restrictions)
                              │
                      TriggerBuilder
```

### File Structure

```
src/honeycomb/models/
├── query_builder.py          # QueryBuilder (refactored)
├── trigger_builder.py        # TriggerBuilder
├── recipient_builder.py      # RecipientBuilder + RecipientMixin
├── slo_builder.py            # SLOBuilder + SLOBundle
├── burn_alert_builder.py     # BurnAlertBuilder (uses RecipientMixin)
├── marker_builder.py         # MarkerBuilder
├── board_builder.py          # BoardBuilder + BoardItem types
├── derived_column_builder.py # DerivedColumnBuilder (new resource wrapper)
└── __init__.py               # Export all builders
```

---

## 1. RecipientMixin + RecipientBuilder

### RecipientMixin (for embedding in other builders)

```python
class RecipientMixin:
    """Mixin providing recipient creation methods."""

    def __init__(self):
        self._recipients: list[dict] = []           # Existing recipient IDs
        self._new_recipients: list[dict] = []       # Inline-created recipients

    def email(self, address: str) -> Self:
        """Add an email recipient."""
        self._new_recipients.append({
            "type": "email",
            "target": address,
        })
        return self

    def slack(self, channel: str) -> Self:
        """Add a Slack recipient."""
        self._new_recipients.append({
            "type": "slack",
            "target": channel,
        })
        return self

    def pagerduty(
        self,
        routing_key: str,
        severity: Literal["info", "warning", "error", "critical"] = "critical"
    ) -> Self:
        """Add a PagerDuty recipient."""
        self._new_recipients.append({
            "type": "pagerduty",
            "target": routing_key,
            "details": {"severity": severity},
        })
        return self

    def webhook(self, url: str, secret: str | None = None) -> Self:
        """Add a webhook recipient."""
        details = {"url": url}
        if secret:
            details["secret"] = secret
        self._new_recipients.append({
            "type": "webhook",
            "target": url,
            "details": details,
        })
        return self

    def msteams(self, workflow_url: str) -> Self:
        """Add an MS Teams workflow recipient."""
        self._new_recipients.append({
            "type": "msteams_workflow",
            "target": workflow_url,
        })
        return self

    def recipient_id(self, recipient_id: str) -> Self:
        """Reference an existing recipient by ID."""
        self._recipients.append({"id": recipient_id})
        return self

    def _get_all_recipients(self) -> list[dict]:
        """Get combined list of recipients for API."""
        return self._recipients + self._new_recipients
```

### RecipientBuilder (standalone factory)

```python
class RecipientBuilder:
    """Factory for creating standalone RecipientCreate objects."""

    @staticmethod
    def email(address: str) -> RecipientCreate:
        return RecipientCreate(
            type=RecipientType.EMAIL,
            details={"address": address}
        )

    @staticmethod
    def slack(channel: str) -> RecipientCreate:
        return RecipientCreate(
            type=RecipientType.SLACK,
            details={"channel": channel}
        )

    @staticmethod
    def pagerduty(
        routing_key: str,
        severity: Literal["info", "warning", "error", "critical"] = "critical"
    ) -> RecipientCreate:
        return RecipientCreate(
            type=RecipientType.PAGERDUTY,
            details={"routing_key": routing_key, "severity": severity}
        )

    @staticmethod
    def webhook(url: str, secret: str | None = None) -> RecipientCreate:
        details = {"url": url}
        if secret:
            details["secret"] = secret
        return RecipientCreate(type=RecipientType.WEBHOOK, details=details)

    @staticmethod
    def msteams(workflow_url: str) -> RecipientCreate:
        return RecipientCreate(
            type=RecipientType.MSTEAMS_WORKFLOW,
            details={"url": workflow_url}
        )
```

---

## 2. TriggerBuilder

### Key Constraints (enforced at build time)
- **Single calculation only** - Triggers can only have one calculation
- **Time range max 3600 seconds** - Trigger queries limited to 1 hour
- **No absolute time** - Triggers use relative time only
- **Dataset optional** - Can be dataset-scoped or environment-wide

### Design

```python
class TriggerBuilder(QueryBuilder, RecipientMixin):
    """Fluent builder for triggers with integrated query building.

    Extends QueryBuilder with trigger-specific constraints:
    - Only one calculation allowed
    - Time range limited to 3600 seconds (1 hour)
    - No absolute time ranges (start_time/end_time)

    Example:
        trigger = (
            TriggerBuilder("High Error Rate")
            .dataset("my-dataset")           # Optional - omit for environment-wide
            .last_30_minutes()
            .count()                          # Single calculation only
            .gte("status", 500)
            .threshold_gt(100)
            .every_5_minutes()
            .email("oncall@example.com")
            .slack("#alerts")
            .build()
        )
    """

    def __init__(self, name: str):
        QueryBuilder.__init__(self)
        RecipientMixin.__init__(self)
        self._name = name
        self._description: str | None = None
        self._dataset: str | None = None      # None = environment-wide
        self._threshold_op: TriggerThresholdOp | None = None
        self._threshold_value: float | None = None
        self._exceeded_limit: int | None = None
        self._frequency: int = 900            # Default 15 minutes
        self._alert_type: TriggerAlertType = TriggerAlertType.ON_CHANGE
        self._disabled: bool = False

    # -------------------------------------------------------------------------
    # Scope
    # -------------------------------------------------------------------------

    def dataset(self, dataset_slug: str) -> TriggerBuilder:
        """Scope trigger to a specific dataset.

        If not called, trigger will be environment-wide.
        """
        self._dataset = dataset_slug
        return self

    def environment_wide(self) -> TriggerBuilder:
        """Explicitly mark trigger as environment-wide (no dataset)."""
        self._dataset = None
        return self

    # -------------------------------------------------------------------------
    # Threshold shortcuts
    # -------------------------------------------------------------------------

    def threshold_gt(self, value: float) -> TriggerBuilder:
        """Trigger when value > threshold."""
        self._threshold_op = TriggerThresholdOp.GREATER_THAN
        self._threshold_value = value
        return self

    def threshold_gte(self, value: float) -> TriggerBuilder:
        """Trigger when value >= threshold."""
        self._threshold_op = TriggerThresholdOp.GREATER_THAN_OR_EQUAL
        self._threshold_value = value
        return self

    def threshold_lt(self, value: float) -> TriggerBuilder:
        """Trigger when value < threshold."""
        self._threshold_op = TriggerThresholdOp.LESS_THAN
        self._threshold_value = value
        return self

    def threshold_lte(self, value: float) -> TriggerBuilder:
        """Trigger when value <= threshold."""
        self._threshold_op = TriggerThresholdOp.LESS_THAN_OR_EQUAL
        self._threshold_value = value
        return self

    def exceeded_limit(self, times: int) -> TriggerBuilder:
        """Require threshold to be exceeded N times before alerting."""
        self._exceeded_limit = times
        return self

    # -------------------------------------------------------------------------
    # Frequency presets
    # -------------------------------------------------------------------------

    def every_minute(self) -> TriggerBuilder:
        self._frequency = 60
        return self

    def every_5_minutes(self) -> TriggerBuilder:
        self._frequency = 300
        return self

    def every_15_minutes(self) -> TriggerBuilder:
        self._frequency = 900
        return self

    def every_30_minutes(self) -> TriggerBuilder:
        self._frequency = 1800
        return self

    def every_hour(self) -> TriggerBuilder:
        self._frequency = 3600
        return self

    def frequency(self, seconds: int) -> TriggerBuilder:
        """Set custom frequency in seconds (60-86400)."""
        if not 60 <= seconds <= 86400:
            raise ValueError("Frequency must be between 60 and 86400 seconds")
        self._frequency = seconds
        return self

    # -------------------------------------------------------------------------
    # Alert behavior
    # -------------------------------------------------------------------------

    def alert_on_change(self) -> TriggerBuilder:
        """Alert only when state changes (default)."""
        self._alert_type = TriggerAlertType.ON_CHANGE
        return self

    def alert_on_true(self) -> TriggerBuilder:
        """Alert every time threshold is exceeded."""
        self._alert_type = TriggerAlertType.ON_TRUE
        return self

    def disabled(self, is_disabled: bool = True) -> TriggerBuilder:
        """Create trigger in disabled state."""
        self._disabled = is_disabled
        return self

    # -------------------------------------------------------------------------
    # Build
    # -------------------------------------------------------------------------

    def build(self) -> TriggerCreate:
        """Build TriggerCreate with validation.

        Raises:
            ValueError: If constraints are violated:
                - More than one calculation
                - Time range > 3600 seconds
                - Absolute time used
                - Missing threshold
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

        return TriggerCreate(
            name=self._name,
            description=self._description,
            threshold=threshold,
            frequency=self._frequency,
            query=query,
            disabled=self._disabled,
            alert_type=self._alert_type,
            recipients=self._get_all_recipients() if self._get_all_recipients() else None,
        )

    def get_dataset(self) -> str | None:
        """Get the dataset this trigger is scoped to (None = environment-wide)."""
        return self._dataset
```

### Usage Examples

```python
# Dataset-scoped trigger
trigger = (
    TriggerBuilder("High Error Rate")
    .dataset("api-logs")
    .last_30_minutes()
    .count()
    .gte("status", 500)
    .threshold_gt(100)
    .every_5_minutes()
    .email("oncall@example.com")
    .build()
)
await client.triggers.create_async(trigger.get_dataset(), trigger)

# Environment-wide trigger (no dataset)
trigger = (
    TriggerBuilder("Global Error Spike")
    .environment_wide()
    .last_10_minutes()
    .count()
    .eq("level", "error")
    .threshold_gt(1000)
    .every_minute()
    .pagerduty("routing-key-123", severity="critical")
    .build()
)
await client.triggers.create_environment_wide_async(trigger)
```

---

## 3. SLOBuilder

### Key Features
- `.sli(alias, expression=None)` - Unified SLI definition
  - If `expression` is None: uses existing derived column
  - If `expression` is provided: creates new derived column
- Dataset can be single or multiple
- If multiple datasets: derived column must be environment-wide
- Burn alerts have embedded recipients

### Design

```python
@dataclass
class SLIDefinition:
    """SLI definition - either references existing DC or creates new one."""
    alias: str
    expression: str | None = None  # None = use existing DC
    description: str | None = None

    def is_new_derived_column(self) -> bool:
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
    """Bundle containing SLO and related resources to create."""
    slo: SLOCreate
    datasets: list[str]                           # Single or multiple
    derived_column: DerivedColumnCreate | None    # If SLI needs new DC
    derived_column_environment_wide: bool         # True if multi-dataset
    burn_alerts: list[BurnAlertDefinition]


class BurnAlertBuilder(RecipientMixin):
    """Builder for burn alerts with recipients."""

    def __init__(self, alert_type: BurnAlertType):
        RecipientMixin.__init__(self)
        self._alert_type = alert_type
        self._description: str | None = None
        self._exhaustion_minutes: int | None = None
        self._budget_rate_window_minutes: int | None = None
        self._budget_rate_decrease_percent: float | None = None

    def description(self, desc: str) -> BurnAlertBuilder:
        self._description = desc
        return self

    # Exhaustion time config
    def exhaustion_minutes(self, minutes: int) -> BurnAlertBuilder:
        self._exhaustion_minutes = minutes
        return self

    # Budget rate config
    def window_minutes(self, minutes: int) -> BurnAlertBuilder:
        self._budget_rate_window_minutes = minutes
        return self

    def threshold_percent(self, percent: float) -> BurnAlertBuilder:
        """Budget decrease threshold as percentage (e.g., 1.0 = 1%)."""
        self._budget_rate_decrease_percent = percent
        return self

    def build(self) -> BurnAlertDefinition:
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
            .sli(alias="api_success_rate")  # Uses existing DC
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
            .target_nines(3)  # 99.9%
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

    # -------------------------------------------------------------------------
    # Dataset scope
    # -------------------------------------------------------------------------

    def dataset(self, dataset_slug: str) -> SLOBuilder:
        """Scope SLO to a single dataset."""
        self._datasets = [dataset_slug]
        return self

    def datasets(self, dataset_slugs: list[str]) -> SLOBuilder:
        """Scope SLO to multiple datasets.

        Note: When using multiple datasets, any new derived column
        will be created as environment-wide.
        """
        self._datasets = dataset_slugs
        return self

    # -------------------------------------------------------------------------
    # Target configuration
    # -------------------------------------------------------------------------

    def target_percentage(self, percent: float) -> SLOBuilder:
        """Set target as percentage (e.g., 99.9 -> 999000 per million)."""
        self._target_per_million = int(percent * 10000)
        return self

    def target_nines(self, nines: int) -> SLOBuilder:
        """Set target by number of nines.

        Examples:
            2 nines = 99%
            3 nines = 99.9%
            4 nines = 99.99%
        """
        percentage = 100 - (100 / (10 ** nines))
        return self.target_percentage(percentage)

    def target_per_million(self, value: int) -> SLOBuilder:
        """Set target directly as per-million value."""
        self._target_per_million = value
        return self

    # -------------------------------------------------------------------------
    # Time period
    # -------------------------------------------------------------------------

    def time_period_days(self, days: int) -> SLOBuilder:
        """Set SLO time period in days (1-90)."""
        if not 1 <= days <= 90:
            raise ValueError("Time period must be between 1 and 90 days")
        self._time_period_days = days
        return self

    def time_period_weeks(self, weeks: int) -> SLOBuilder:
        """Set SLO time period in weeks."""
        return self.time_period_days(weeks * 7)

    # -------------------------------------------------------------------------
    # SLI definition
    # -------------------------------------------------------------------------

    def sli(
        self,
        alias: str,
        expression: str | None = None,
        description: str | None = None
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

        Example:
            .exhaustion_alert(
                BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
                .exhaustion_minutes(60)
                .description("Alert when budget exhausts in 1 hour")
                .email("oncall@example.com")
            )
        """
        if builder._alert_type != BurnAlertType.EXHAUSTION_TIME:
            raise ValueError("exhaustion_alert() requires EXHAUSTION_TIME alert type")
        self._burn_alerts.append(builder.build())
        return self

    def budget_rate_alert(self, builder: BurnAlertBuilder) -> SLOBuilder:
        """Add a budget rate burn alert.

        Example:
            .budget_rate_alert(
                BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
                .window_minutes(60)
                .threshold_percent(1.0)
                .pagerduty("routing-key")
            )
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
            raise ValueError("Target is required. Use target_percentage(), target_nines(), or target_per_million().")

        if self._sli is None:
            raise ValueError("SLI is required. Use sli(alias=...) to define it.")

        # Determine if derived column should be environment-wide
        is_multi_dataset = len(self._datasets) > 1

        # Build derived column if needed
        derived_column = None
        if self._sli.is_new_derived_column():
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
        )

        return SLOBundle(
            slo=slo,
            datasets=self._datasets,
            derived_column=derived_column,
            derived_column_environment_wide=is_multi_dataset,
            burn_alerts=self._burn_alerts,
        )
```

---

## 4. MarkerBuilder

```python
class MarkerBuilder:
    """Fluent builder for markers.

    Example - Point marker:
        marker = (
            MarkerBuilder("Deployed v1.2.3")
            .type("deploy")
            .url("https://github.com/org/repo/releases/v1.2.3")
            .build()
        )

    Example - Duration marker:
        marker = (
            MarkerBuilder("Maintenance window")
            .type("maintenance")
            .start_time(1703980800)
            .end_time(1703984400)
            .build()
        )

    Example - Duration from now:
        marker = (
            MarkerBuilder("Load test in progress")
            .type("test")
            .duration_minutes(30)
            .build()
        )
    """

    def __init__(self, message: str):
        self._message = message
        self._type: str | None = None
        self._start_time: int | None = None
        self._end_time: int | None = None
        self._url: str | None = None

    def type(self, marker_type: str) -> MarkerBuilder:
        """Set marker type (groups similar markers)."""
        self._type = marker_type
        return self

    def url(self, url: str) -> MarkerBuilder:
        """Set target URL for the marker."""
        self._url = url
        return self

    def start_time(self, timestamp: int) -> MarkerBuilder:
        """Set start time as Unix timestamp."""
        self._start_time = timestamp
        return self

    def end_time(self, timestamp: int) -> MarkerBuilder:
        """Set end time as Unix timestamp (for duration markers)."""
        self._end_time = timestamp
        return self

    def duration_minutes(self, minutes: int) -> MarkerBuilder:
        """Set duration from now."""
        import time
        now = int(time.time())
        self._start_time = now
        self._end_time = now + (minutes * 60)
        return self

    def duration_hours(self, hours: int) -> MarkerBuilder:
        """Set duration from now in hours."""
        return self.duration_minutes(hours * 60)

    @staticmethod
    def setting(marker_type: str, color: str) -> MarkerSettingCreate:
        """Create a marker setting (color configuration).

        Args:
            marker_type: Type of marker to configure
            color: Hex color code (e.g., '#F96E11')
        """
        return MarkerSettingCreate(type=marker_type, color=color)

    def build(self) -> MarkerCreate:
        """Build MarkerCreate with validation."""
        if not self._type:
            raise ValueError("Marker type is required. Use type().")

        return MarkerCreate(
            message=self._message,
            type=self._type,
            start_time=self._start_time,
            end_time=self._end_time,
            url=self._url,
        )
```

---

## 5. BoardBuilder

### Key Features
- Add queries with position/size or auto-layout
- Add SLO references
- Add text boxes
- Layout options: multi-column, single-column
- Style options: visual (graphs), list

### Design

```python
@dataclass
class BoardPosition:
    """Position and size of a board item."""
    x: int = 0       # Column position (0-based)
    y: int = 0       # Row position (0-based)
    width: int = 1   # Width in columns
    height: int = 1  # Height in rows


class BoardItemType(str, Enum):
    QUERY = "query"
    SLO = "slo"
    TEXT = "text"


@dataclass
class BoardItem:
    """An item on a board (query, SLO, or text)."""
    item_type: BoardItemType
    # Query-specific
    query_spec: QuerySpec | None = None
    query_id: str | None = None
    query_style: str = "graph"  # "graph", "table", "combo"
    # SLO-specific
    slo_id: str | None = None
    # Text-specific
    text_content: str | None = None
    # Common
    caption: str | None = None
    position: BoardPosition | None = None  # None = auto-layout


class BoardBuilder:
    """Fluent builder for boards with queries, SLOs, and text.

    Example - Auto-layout:
        board = (
            BoardBuilder("Service Dashboard")
            .description("Overview of API health")
            .query(
                QueryBuilder()
                .last_1_hour()
                .count()
                .group_by("service"),
                caption="Requests by Service"
            )
            .query(
                QueryBuilder()
                .last_1_hour()
                .p99("duration_ms")
                .group_by("endpoint"),
                caption="P99 Latency"
            )
            .slo("slo-id-123", caption="API Availability")
            .text("## Notes\nMonitor during peak hours")
            .build()
        )

    Example - Manual layout:
        board = (
            BoardBuilder("Custom Layout")
            .layout_multi()
            .query(
                QueryBuilder().last_1_hour().count(),
                caption="Total Requests",
                position=BoardPosition(x=0, y=0, width=2, height=1)
            )
            .query(
                QueryBuilder().last_1_hour().avg("duration_ms"),
                caption="Avg Latency",
                position=BoardPosition(x=0, y=1, width=1, height=1)
            )
            .slo(
                "slo-123",
                caption="SLO Status",
                position=BoardPosition(x=1, y=1, width=1, height=1)
            )
            .build()
        )
    """

    def __init__(self, name: str):
        self._name = name
        self._description: str | None = None
        self._column_layout: str = "multi"
        self._style: str = "visual"
        self._items: list[BoardItem] = []
        self._auto_layout: bool = True

    def description(self, desc: str) -> BoardBuilder:
        self._description = desc
        return self

    # -------------------------------------------------------------------------
    # Layout configuration
    # -------------------------------------------------------------------------

    def layout_multi(self) -> BoardBuilder:
        """Use multi-column layout (default)."""
        self._column_layout = "multi"
        return self

    def layout_single(self) -> BoardBuilder:
        """Use single-column layout."""
        self._column_layout = "single"
        return self

    def style_visual(self) -> BoardBuilder:
        """Use visual/graph style (default)."""
        self._style = "visual"
        return self

    def style_list(self) -> BoardBuilder:
        """Use list style."""
        self._style = "list"
        return self

    def auto_layout(self) -> BoardBuilder:
        """Use automatic layout positioning (default)."""
        self._auto_layout = True
        return self

    def manual_layout(self) -> BoardBuilder:
        """Use manual layout - positions must be specified."""
        self._auto_layout = False
        return self

    # -------------------------------------------------------------------------
    # Add items
    # -------------------------------------------------------------------------

    def query(
        self,
        query: QueryBuilder,
        caption: str | None = None,
        position: BoardPosition | None = None,
        style: Literal["graph", "table", "combo"] = "graph"
    ) -> BoardBuilder:
        """Add a query to the board.

        Args:
            query: QueryBuilder instance (will call .build() automatically)
            caption: Display caption for the query
            position: Manual position/size (None for auto-layout)
            style: Display style - "graph", "table", or "combo"
        """
        self._items.append(BoardItem(
            item_type=BoardItemType.QUERY,
            query_spec=query.build(),
            caption=caption,
            position=position,
            query_style=style,
        ))
        return self

    def query_id(
        self,
        query_id: str,
        caption: str | None = None,
        position: BoardPosition | None = None,
        style: Literal["graph", "table", "combo"] = "graph"
    ) -> BoardBuilder:
        """Add an existing saved query by ID."""
        self._items.append(BoardItem(
            item_type=BoardItemType.QUERY,
            query_id=query_id,
            caption=caption,
            position=position,
            query_style=style,
        ))
        return self

    def slo(
        self,
        slo_id: str,
        caption: str | None = None,
        position: BoardPosition | None = None
    ) -> BoardBuilder:
        """Add an SLO to the board."""
        self._items.append(BoardItem(
            item_type=BoardItemType.SLO,
            slo_id=slo_id,
            caption=caption,
            position=position,
        ))
        return self

    def text(
        self,
        content: str,
        position: BoardPosition | None = None
    ) -> BoardBuilder:
        """Add a text box to the board (supports markdown)."""
        self._items.append(BoardItem(
            item_type=BoardItemType.TEXT,
            text_content=content,
            position=position,
        ))
        return self

    # -------------------------------------------------------------------------
    # Build
    # -------------------------------------------------------------------------

    def build(self) -> BoardCreate:
        """Build BoardCreate with items.

        Note: The actual query/SLO creation and board assembly
        may need to happen in multiple API calls. This returns
        the board definition; the client handles orchestration.
        """
        if not self._auto_layout:
            # Validate all items have positions
            for i, item in enumerate(self._items):
                if item.position is None:
                    raise ValueError(
                        f"Manual layout requires position for all items. "
                        f"Item {i} ({item.item_type.value}) has no position."
                    )

        # Build board create object
        # Note: queries list format depends on Honeycomb API structure
        queries = []
        for item in self._items:
            query_data = {}
            if item.query_spec:
                query_data["query"] = item.query_spec.model_dump_for_api()
            if item.query_id:
                query_data["query_id"] = item.query_id
            if item.slo_id:
                query_data["slo_id"] = item.slo_id
            if item.text_content:
                query_data["text"] = item.text_content
            if item.caption:
                query_data["caption"] = item.caption
            if item.position:
                query_data["position"] = {
                    "x": item.position.x,
                    "y": item.position.y,
                    "width": item.position.width,
                    "height": item.position.height,
                }
            if item.query_style:
                query_data["graph_settings"] = {"style": item.query_style}
            queries.append(query_data)

        return BoardCreate(
            name=self._name,
            description=self._description,
            column_layout=self._column_layout,
            style=self._style,
            # Note: queries field may need adjustment based on actual API
        )

    def get_items(self) -> list[BoardItem]:
        """Get board items for client-side orchestration."""
        return self._items
```

---

## 6. DerivedColumnBuilder (New Resource)

Need to add wrapper for Calculated Fields (Derived Columns) API.

```python
class DerivedColumnCreate(BaseModel):
    """Model for creating a derived column (calculated field)."""
    alias: str = Field(description="Name of the derived column")
    expression: str = Field(description="Expression to calculate the value")
    description: str | None = Field(default=None, description="Human-readable description")

    def model_dump_for_api(self) -> dict:
        data = {"alias": self.alias, "expression": self.expression}
        if self.description:
            data["description"] = self.description
        return data


class DerivedColumn(BaseModel):
    """A derived column (calculated field) response model."""
    id: str
    alias: str
    expression: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DerivedColumnBuilder:
    """Builder for derived columns.

    Example:
        dc = (
            DerivedColumnBuilder("request_success")
            .expression("IF(LT($status_code, 400), 1, 0)")
            .description("1 if request succeeded, 0 otherwise")
            .build()
        )
    """

    def __init__(self, alias: str):
        self._alias = alias
        self._expression: str | None = None
        self._description: str | None = None

    def expression(self, expr: str) -> DerivedColumnBuilder:
        """Set the expression for the derived column."""
        self._expression = expr
        return self

    def description(self, desc: str) -> DerivedColumnBuilder:
        """Set the description."""
        self._description = desc
        return self

    def build(self) -> DerivedColumnCreate:
        if not self._expression:
            raise ValueError("Expression is required")
        return DerivedColumnCreate(
            alias=self._alias,
            expression=self._expression,
            description=self._description,
        )
```

---

## Implementation Order

1. **Phase 1: Foundation** ✅
   - [x] RecipientMixin + RecipientBuilder
   - [x] DerivedColumnCreate model + DerivedColumns resource wrapper

2. **Phase 2: TriggerBuilder** ✅
   - [x] TriggerBuilder extending QueryBuilder
   - [x] Update triggers.md docs
   - [x] Add unit tests

2.5. **Phase 2.5: Enhanced TriggerBuilder + TagsMixin** ✅
   - [x] Add TagsMixin (for Triggers, Boards, SLOs)
   - [x] Add tags support to TriggerBuilder
   - [x] Add baseline threshold support to TriggerBuilder
   - [x] Add frequency vs duration validation
   - [x] Add exceeded_limit range validation (1-5)
   - [x] Add tests for tags, baseline, and validation
   - [x] Update triggers.md docs

3. **Phase 3: SLOBuilder**
   - [x] BurnAlertBuilder
   - [x] SLOBuilder + SLOBundle
   - [x] Client methods for creating SLO bundles
   - [x] Update slos.md docs

4. **Phase 4: MarkerBuilder**
   - [x] MarkerBuilder
   - [x] Update markers.md docs

5. **Phase 5: BoardBuilder**
   - [ ] BoardBuilder + BoardItem types
   - [ ] Client orchestration for board creation
   - [ ] Update boards.md docs

6. **Phase 6: Cleanup**
   - [ ] Update all example code
   - [ ] Update README.md
   - [ ] Run full CI

---

## Documentation Guidelines for Builders

Based on lessons learned from TriggerBuilder documentation:

### 1. Use Async/Sync Tabs

Use Material for MkDocs tab syntax for all code examples:

```markdown
=== "Async"

    ```python
    async with HoneycombClient(api_key="...") as client:
        result = await client.resource.method_async(...)
    ```

=== "Sync"

    ```python
    with HoneycombClient(api_key="...", sync=True) as client:
        result = client.resource.method(...)
    ```
```

### 2. Progressive Complexity Examples

Show 3 examples that build in complexity:

**Simple** - Minimal viable example (5-7 lines)
- Single filter
- Basic threshold/configuration
- One recipient
- Purpose: Show the quickest path to success

**Moderate** - Real-world usage (10-15 lines)
- Multiple filters or grouping
- Advanced configuration (exceeded_limit, custom frequency, etc.)
- 2-3 recipients
- Purpose: Show common production patterns

**High Complexity** - Full feature showcase (15-25 lines)
- All/most builder features used
- Multiple recipients of different types
- Advanced options (alert_on_true, environment-wide, etc.)
- Purpose: Demonstrate full capabilities

### 3. Reference Tables Not Code Dumps

**DON'T** show every option in code:
```python
# Bad - showing all threshold methods in one code block
.threshold_gt(100)
.threshold_gte(100)
.threshold_lt(100)
.threshold_lte(100)
```

**DO** use tables for comprehensive reference:

| Method | Description |
|--------|-------------|
| `.threshold_gt(value)` | Trigger when result > value |
| `.threshold_gte(value)` | Trigger when result >= value |
| `.threshold_lt(value)` | Trigger when result < value |
| `.threshold_lte(value)` | Trigger when result <= value |

### 4. Concise Composition Explanations

**DON'T** use marketing language:
> "Key Benefits: Amazing fluent interface! Convenient shortcuts! Super powerful!"

**DO** explain technical composition concisely:
> "`TriggerBuilder` composes `QueryBuilder` (for query specification) and `RecipientMixin` (for notification management) into a single fluent interface, allowing you to define queries, thresholds, and recipients in one expression without separately constructing each component."

### 5. Include Advanced Usage Section

Always provide non-builder alternatives in an "Advanced Usage" section:

- **Manual construction** - Building with separate components
- **Alternative APIs** - Other ways to achieve the same result (e.g., saved queries)
- **Low-level APIs** - Direct model construction when needed

This shows users:
- The builder is optional, not mandatory
- How to work around builder limitations
- The underlying API structure

### 6. Document Structure Template

```markdown
# Working with [Resource]

Brief overview of what the resource does.

## Basic Operations

### List [Resources]
=== "Async" / === "Sync" examples

### Get a Specific [Resource]
Simple async example

### Delete a [Resource]
Simple async example

## Creating [Resources] with [Builder]

One sentence explaining what the builder composes.

### Simple Example
=== "Async" / === "Sync" tabs

### Moderate Complexity
=== "Async" / === "Sync" tabs

### High Complexity
=== "Async" / === "Sync" tabs

## [Builder] Reference

### [Category] Methods
Table of methods

### [Category] Methods (from Parent)
Brief summary + link to full parent docs + inline highlights

## Important Constraints

### [Constraint Name]
Code example showing valid + invalid with error messages

## Advanced Usage

### Building Without [Builder]
=== "Async" / === "Sync" tabs showing manual construction

### [Alternative Approach]
Alternative patterns (saved queries, direct models, etc.)

## Updating [Resources]
=== "Async" / === "Sync" update examples

## See Also
- Links to API reference
- Links to related guides
```

### 7. Validation Requirements

All documentation code examples must pass `make validate-docs` which:
- Compiles all code blocks for syntax errors
- Ensures imports are correct
- Validates examples work with current API

---

## Breaking Changes

Since this client isn't shipped yet, we can make breaking changes freely:

1. **TriggerCreate** - Will still work, but TriggerBuilder is preferred
2. **QueryBuilder.build_for_trigger()** - Keep for backwards compat, but TriggerBuilder is preferred
3. **RecipientCreate** - Will still work, RecipientBuilder is a convenience

---

## Export Updates

```python
# src/honeycomb/__init__.py
from honeycomb.models.query_builder import (
    QueryBuilder,
    Calculation,
    Filter,
    Order,
    Having,
    CalcOp,
    FilterOp,
    OrderDirection,
    FilterCombination,
)
from honeycomb.models.trigger_builder import TriggerBuilder
from honeycomb.models.recipient_builder import RecipientBuilder, RecipientMixin
from honeycomb.models.slo_builder import SLOBuilder, SLOBundle, BurnAlertBuilder
from honeycomb.models.marker_builder import MarkerBuilder
from honeycomb.models.board_builder import BoardBuilder, BoardPosition, BoardItem
from honeycomb.models.derived_column_builder import DerivedColumnBuilder, DerivedColumnCreate
```
