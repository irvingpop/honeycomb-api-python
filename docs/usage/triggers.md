# Working with Triggers

Triggers alert you when query results cross a threshold. They continuously monitor your data and notify you when conditions are met.

## Basic Trigger Operations

### List Triggers

=== "Async"

    ```python
    from honeycomb import HoneycombClient

    async with HoneycombClient(api_key="...") as client:
        triggers = await client.triggers.list_async("my-dataset")

        for trigger in triggers:
            print(f"{trigger.name}: {trigger.threshold.op} {trigger.threshold.value}")
            print(f"  Frequency: every {trigger.frequency}s")
            print(f"  State: {'triggered' if trigger.triggered else 'ok'}")
    ```

=== "Sync"

    ```python
    from honeycomb import HoneycombClient

    with HoneycombClient(api_key="...", sync=True) as client:
        triggers = client.triggers.list("my-dataset")

        for trigger in triggers:
            print(f"{trigger.name}: {trigger.threshold.op} {trigger.threshold.value}")
    ```

### Get a Specific Trigger

```python
trigger = await client.triggers.get_async("my-dataset", "trigger-id")

print(f"Name: {trigger.name}")
print(f"Description: {trigger.description}")
print(f"Query: {trigger.query}")
```

### Delete a Trigger

```python
await client.triggers.delete_async("my-dataset", "trigger-id")
```

## Creating Triggers with TriggerBuilder

`TriggerBuilder` composes `QueryBuilder` (for query specification) and `RecipientMixin` (for notification management) into a single fluent interface, allowing you to define queries, thresholds, and recipients in one expression without separately constructing each component.

### Simple Trigger - Error Count

=== "Async"

    ```python
    from honeycomb import HoneycombClient, TriggerBuilder

    async with HoneycombClient(api_key="...") as client:
        trigger = (
            TriggerBuilder("High Error Count")
            .dataset("api-logs")
            .last_30_minutes()
            .count()
            .gte("status", 500)
            .threshold_gt(100)
            .every_5_minutes()
            .email("oncall@example.com")
            .build()
        )

        created = await client.triggers.create_async(trigger.get_dataset(), trigger)
        print(f"Created trigger: {created.id}")
    ```

=== "Sync"

    ```python
    from honeycomb import HoneycombClient, TriggerBuilder

    with HoneycombClient(api_key="...", sync=True) as client:
        trigger = (
            TriggerBuilder("High Error Count")
            .dataset("api-logs")
            .last_30_minutes()
            .count()
            .gte("status", 500)
            .threshold_gt(100)
            .every_5_minutes()
            .email("oncall@example.com")
            .build()
        )

        created = client.triggers.create(trigger.get_dataset(), trigger)
        print(f"Created trigger: {created.id}")
    ```

### Moderate Complexity - P99 Latency with Multiple Filters

=== "Async"

    ```python
    from honeycomb import TriggerBuilder

    trigger = (
        TriggerBuilder("Slow API Endpoints")
        .description("Alert when API P99 latency exceeds 1 second")
        .dataset("api-logs")
        .last_30_minutes()
        .p99("duration_ms")
        .eq("service", "api")
        .exists("user_id")  # Only authenticated requests
        .group_by("endpoint")
        .threshold_gt(1000)
        .exceeded_limit(3)  # Must exceed 3 consecutive times
        .every_5_minutes()
        .slack("#performance")
        .pagerduty("routing-key-123", severity="warning")
        .build()
    )

    created = await client.triggers.create_async(trigger.get_dataset(), trigger)
    ```

=== "Sync"

    ```python
    from honeycomb import TriggerBuilder

    trigger = (
        TriggerBuilder("Slow API Endpoints")
        .description("Alert when API P99 latency exceeds 1 second")
        .dataset("api-logs")
        .last_30_minutes()
        .p99("duration_ms")
        .eq("service", "api")
        .group_by("endpoint")
        .threshold_gt(1000)
        .exceeded_limit(3)
        .every_5_minutes()
        .slack("#performance")
        .build()
    )

    created = client.triggers.create(trigger.get_dataset(), trigger)
    ```

### High Complexity - Environment-Wide with Tags and Baseline

=== "Async"

    ```python
    from honeycomb import TriggerBuilder

    trigger = (
        TriggerBuilder("Global Critical Error Spike")
        .description("Alert on critical errors across all services")
        .environment_wide()  # Monitor all datasets
        .time_range(240)  # 4 minutes - max for every_minute (60*4=240)
        .count()
        .eq("level", "error")
        .eq("severity", "critical")
        .filter_with("AND")
        .group_by("service")
        .threshold_gt(50)
        .exceeded_limit(2)
        .every_minute()
        .alert_on_true()  # Alert every time, not just on change
        .pagerduty("critical-routing-key", severity="critical")
        .email("oncall@example.com")
        .slack("#incidents")
        .webhook("https://example.com/webhook", secret="secret123")
        .tag("team", "platform")
        .tag("priority", "critical")
        .baseline_1_hour_ago("percentage")  # Compare to 1 hour ago
        .build()
    )

    created = await client.triggers.create_environment_wide_async(trigger)
    ```

=== "Sync"

    ```python
    from honeycomb import TriggerBuilder

    trigger = (
        TriggerBuilder("Global Critical Error Spike")
        .environment_wide()
        .time_range(240)
        .count()
        .eq("level", "error")
        .eq("severity", "critical")
        .threshold_gt(50)
        .every_minute()
        .pagerduty("critical-routing-key", severity="critical")
        .email("oncall@example.com")
        .tag("team", "platform")
        .baseline_1_hour_ago()
        .build()
    )

    created = client.triggers.create_environment_wide(trigger)
    ```

## TriggerBuilder Reference

### Scope Methods

| Method | Description |
|--------|-------------|
| `.dataset(slug)` | Scope trigger to a specific dataset |
| `.environment_wide()` | Create environment-wide trigger (monitors all datasets) |
| `.description(text)` | Add trigger description |

### Query Methods (from QueryBuilder)

TriggerBuilder inherits all QueryBuilder methods. See [Queries documentation](queries.md) for full details.

**Time ranges** (max 3600 seconds for triggers):
- `.last_10_minutes()`, `.last_30_minutes()`, `.last_1_hour()`
- `.time_range(seconds)` - Custom time range

**Calculations** (only one allowed):
- `.count()`, `.avg(column)`, `.sum(column)`, `.min(column)`, `.max(column)`
- `.p50(column)`, `.p90(column)`, `.p95(column)`, `.p99(column)`
- `.count_distinct(column)`, `.heatmap(column)`

**Filters**:
- `.eq(column, value)`, `.ne(column, value)`, `.gt(column, value)`, `.gte(column, value)`, `.lt(column, value)`, `.lte(column, value)`
- `.contains(column, value)`, `.starts_with(column, value)`, `.exists(column)`, `.does_not_exist(column)`
- `.is_in(column, values)`, `.not_in(column, values)`
- `.filter_with("AND" | "OR")` - Combine filters

**Grouping**:
- `.group_by(*columns)` or `.breakdown(*columns)`

### Threshold Methods

| Method | Description |
|--------|-------------|
| `.threshold_gt(value)` | Trigger when result > value |
| `.threshold_gte(value)` | Trigger when result >= value |
| `.threshold_lt(value)` | Trigger when result < value |
| `.threshold_lte(value)` | Trigger when result <= value |
| `.exceeded_limit(times)` | Require threshold exceeded N consecutive times before alerting |

### Frequency Methods

| Method | Description |
|--------|-------------|
| `.every_minute()` | Check every 60 seconds |
| `.every_5_minutes()` | Check every 300 seconds |
| `.every_15_minutes()` | Check every 900 seconds (default) |
| `.every_30_minutes()` | Check every 1800 seconds |
| `.every_hour()` | Check every 3600 seconds |
| `.frequency(seconds)` | Custom frequency (60-86400 seconds) |

### Alert Behavior Methods

| Method | Description |
|--------|-------------|
| `.alert_on_change()` | Alert only when state changes (default) |
| `.alert_on_true()` | Alert every time threshold is exceeded |
| `.disabled(bool)` | Create trigger in disabled state (default: True if no arg) |

### Recipient Methods (from RecipientMixin)

| Method | Description |
|--------|-------------|
| `.email(address)` | Add email recipient |
| `.slack(channel)` | Add Slack channel (e.g., "#alerts") |
| `.pagerduty(routing_key, severity)` | Add PagerDuty recipient (severity: "info", "warning", "error", "critical") |
| `.webhook(url, secret=None)` | Add webhook recipient with optional secret |
| `.msteams(workflow_url)` | Add MS Teams workflow recipient |
| `.recipient_id(id)` | Reference existing recipient by ID |

### Tag Methods (from TagsMixin)

| Method | Description |
|--------|-------------|
| `.tag(key, value)` | Add a single tag (max 10 tags total) |
| `.tags(dict)` | Add multiple tags from a dictionary |

**Tag Validation Rules:**
- Key: lowercase letters and underscores only, max 32 chars
- Value: must start with lowercase letter, can contain lowercase letters, numbers, `/` and `-`, max 128 chars

### Baseline Methods

| Method | Description |
|--------|-------------|
| `.baseline_1_hour_ago(type)` | Compare against results from 1 hour ago |
| `.baseline_1_day_ago(type)` | Compare against results from 1 day ago |
| `.baseline_1_week_ago(type)` | Compare against results from 1 week ago |
| `.baseline_4_weeks_ago(type)` | Compare against results from 4 weeks ago |
| `.baseline(offset_minutes, type)` | Custom baseline offset (60, 1440, 10080, or 40320) |

**Comparison types:**
- `"percentage"`: Compare percentage change `(current - baseline) / baseline`
- `"value"`: Compare absolute change `current - baseline`

## Important Constraints

TriggerBuilder automatically validates these constraints at build time:

### Frequency vs Duration (duration ≤ frequency × 4)

The query duration (time range) cannot exceed 4 times the check frequency:

```python
# Valid - 1 hour duration with 15 min frequency: 3600 <= 900 * 4 (OK)
trigger = TriggerBuilder("Test").last_1_hour().count().threshold_gt(100).every_15_minutes().build()

# Invalid - 30 min duration with 1 min frequency: 1800 > 60 * 4 = 240 (FAIL)
try:
    trigger = (
        TriggerBuilder("Test")
        .last_30_minutes()  # 1800s
        .count()
        .threshold_gt(100)
        .every_minute()  # 60s: 1800 > 240
        .build()
    )
except ValueError as e:
    print(f"Error: {e}")  # "Time range cannot be more than 4x frequency"
```

**Common valid combinations:**
- `.last_1_hour()` (3600s) + `.every_15_minutes()` (900s): 3600 ≤ 3600 ✓
- `.time_range(1200)` (20 min) + `.every_5_minutes()` (300s): 1200 ≤ 1200 ✓
- `.time_range(240)` (4 min) + `.every_minute()` (60s): 240 ≤ 240 ✓

### Time Range Limit (max 3600 seconds)

```python
# Valid
trigger = TriggerBuilder("Test").last_1_hour().count().threshold_gt(100).build()

# Invalid - raises ValueError
try:
    trigger = TriggerBuilder("Test").last_2_hours().count().threshold_gt(100).build()
except ValueError as e:
    print(f"Error: {e}")  # "Trigger time range must be <= 3600 seconds"
```

### Single Calculation Only

```python
# Valid
trigger = TriggerBuilder("Test").last_30_minutes().p99("duration_ms").threshold_gt(500).build()

# Invalid - raises ValueError
try:
    trigger = (
        TriggerBuilder("Test")
        .last_30_minutes()
        .count()
        .p99("duration_ms")  # Second calculation
        .threshold_gt(100)
        .build()
    )
except ValueError as e:
    print(f"Error: {e}")  # "Triggers can only have one calculation"
```

### No Absolute Time Ranges

```python
# Valid - relative time
trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_gt(100).build()

# Invalid - raises ValueError
try:
    trigger = (
        TriggerBuilder("Test")
        .absolute_time(1000000, 1003600)
        .count()
        .threshold_gt(100)
        .build()
    )
except ValueError as e:
    print(f"Error: {e}")  # "Triggers do not support absolute time ranges"
```

## Tags and Organization

Add tags to triggers for organization and filtering:

```python
from honeycomb import TriggerBuilder

trigger = (
    TriggerBuilder("API Error Spike")
    .dataset("api-logs")
    .last_1_hour()
    .count()
    .gte("status", 500)
    .threshold_gt(100)
    .tag("team", "backend")
    .tag("service", "api")
    .tag("severity", "high")
    .tags({"env": "production", "region": "us-east-1"})  # Bulk add
    .email("oncall@example.com")
    .build()
)
```

**Tag validation:**
- Keys: lowercase letters and underscores only, max 32 chars
- Values: start with lowercase letter, contain letters/numbers/`/`/`-` only, max 128 chars
- Maximum 10 tags per trigger

## Baseline Triggers

Compare current results against historical data to detect anomalies:

=== "Async"

    ```python
    from honeycomb import TriggerBuilder

    # Alert on percentage increase compared to 1 hour ago
    trigger = (
        TriggerBuilder("Traffic Spike vs 1h Ago")
        .dataset("api-logs")
        .last_30_minutes()
        .count()
        .threshold_gt(50)  # >50% increase
        .baseline_1_hour_ago("percentage")  # Compare to same time 1h ago
        .every_15_minutes()
        .slack("#alerts")
        .build()
    )

    created = await client.triggers.create_async(trigger.get_dataset(), trigger)
    ```

=== "Sync"

    ```python
    trigger = (
        TriggerBuilder("Traffic Spike vs 1h Ago")
        .dataset("api-logs")
        .last_30_minutes()
        .count()
        .threshold_gt(50)
        .baseline_1_hour_ago("percentage")
        .every_15_minutes()
        .slack("#alerts")
        .build()
    )

    created = client.triggers.create(trigger.get_dataset(), trigger)
    ```

**Baseline comparison types:**

- `"percentage"`: Alert when `(current - baseline) / baseline` exceeds threshold
  - Example: threshold 50 means alert on >50% increase
- `"value"`: Alert when `current - baseline` exceeds threshold
  - Example: threshold 100 means alert when current is >100 more than baseline

**Available baseline offsets:**

- `.baseline_1_hour_ago()` - Compare to 1 hour ago
- `.baseline_1_day_ago()` - Compare to 1 day ago (useful for daily patterns)
- `.baseline_1_week_ago()` - Compare to 1 week ago (useful for weekly patterns)
- `.baseline_4_weeks_ago()` - Compare to 4 weeks ago

## Advanced Usage

### Building Triggers Without TriggerBuilder

You can construct triggers manually by creating each component separately:

=== "Async"

    ```python
    from honeycomb import (
        HoneycombClient,
        TriggerCreate,
        TriggerThreshold,
        TriggerThresholdOp,
        TriggerAlertType,
        QueryBuilder,
    )

    async with HoneycombClient(api_key="...") as client:
        # Build query separately
        query = (
            QueryBuilder()
            .last_30_minutes()
            .count()
            .gte("status", 500)
            .build_for_trigger()
        )

        # Build threshold
        threshold = TriggerThreshold(
            op=TriggerThresholdOp.GREATER_THAN,
            value=100,
            exceeded_limit=3,
        )

        # Build recipients separately
        recipients = [
            {"type": "email", "target": "oncall@example.com"},
            {"type": "slack", "target": "#alerts"},
            {"id": "existing-recipient-id"},
        ]

        # Create trigger
        trigger = TriggerCreate(
            name="High Error Rate",
            description="Alert when errors exceed threshold",
            threshold=threshold,
            frequency=300,
            query=query,
            alert_type=TriggerAlertType.ON_CHANGE,
            disabled=False,
            recipients=recipients,
        )

        created = await client.triggers.create_async("my-dataset", trigger)
    ```

=== "Sync"

    ```python
    from honeycomb import (
        HoneycombClient,
        TriggerCreate,
        TriggerThreshold,
        TriggerThresholdOp,
        QueryBuilder,
    )

    with HoneycombClient(api_key="...", sync=True) as client:
        query = (
            QueryBuilder()
            .last_30_minutes()
            .count()
            .gte("status", 500)
            .build_for_trigger()
        )

        threshold = TriggerThreshold(
            op=TriggerThresholdOp.GREATER_THAN,
            value=100,
        )

        recipients = [
            {"type": "email", "target": "oncall@example.com"},
        ]

        trigger = TriggerCreate(
            name="High Error Rate",
            threshold=threshold,
            frequency=300,
            query=query,
            recipients=recipients,
        )

        created = client.triggers.create("my-dataset", trigger)
    ```

### Using Saved Queries

Reference an existing saved query instead of an inline query:

```python
from honeycomb import TriggerCreate, TriggerThreshold, TriggerThresholdOp, QueryBuilder

# First, create and save a query
query = await client.queries.create_async(
    "my-dataset",
    QueryBuilder().last_30_minutes().p99("duration_ms").build()
)

# Then reference it in the trigger
trigger = TriggerCreate(
    name="Latency Alert",
    threshold=TriggerThreshold(
        op=TriggerThresholdOp.GREATER_THAN,
        value=500,
    ),
    query_id=query.id,  # Reference saved query
)

created = await client.triggers.create_async("my-dataset", trigger)
```

### Using TriggerQuery Directly

```python
from honeycomb import TriggerCreate, TriggerThreshold, TriggerThresholdOp, TriggerQuery, CalcOp

trigger = TriggerCreate(
    name="Manual Trigger",
    threshold=TriggerThreshold(
        op=TriggerThresholdOp.GREATER_THAN,
        value=100,
    ),
    frequency=300,
    query=TriggerQuery(
        time_range=1800,
        calculations=[{"op": CalcOp.COUNT}],
        filters=[
            {"column": "status", "op": ">=", "value": 500},
        ],
        breakdowns=["service"],
    ),
)

created = await client.triggers.create_async("my-dataset", trigger)
```

## Updating Triggers

When updating a trigger, you must provide all fields:

=== "Async"

    ```python
    from honeycomb import TriggerCreate, TriggerThreshold, TriggerThresholdOp

    # Get the existing trigger first
    existing = await client.triggers.get_async("my-dataset", "trigger-id")

    # Update with all fields
    updated = await client.triggers.update_async(
        "my-dataset",
        "trigger-id",
        TriggerCreate(
            name="Updated Name",
            description=existing.description,
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN,
                value=0.10,  # Change threshold
            ),
            frequency=existing.frequency,
            query=existing.query,
        )
    )
    ```

=== "Sync"

    ```python
    from honeycomb import TriggerCreate, TriggerThreshold, TriggerThresholdOp

    existing = client.triggers.get("my-dataset", "trigger-id")

    updated = client.triggers.update(
        "my-dataset",
        "trigger-id",
        TriggerCreate(
            name="Updated Name",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN,
                value=0.10,
            ),
            frequency=existing.frequency,
            query=existing.query,
        )
    )
    ```

## See Also

- [Triggers API Reference](../api/resources.md#triggers) - Full API documentation
- [Trigger Models](../api/models.md#trigger-models) - All trigger model fields
- [Queries Guide](queries.md) - Query specifications for triggers
