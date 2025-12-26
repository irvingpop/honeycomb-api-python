# Working with Triggers

Triggers alert you when query results cross a threshold. They continuously monitor your data and notify you when conditions are met.

## Basic Trigger Operations

### List Triggers

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    triggers = await client.triggers.list_async("my-dataset")

    for trigger in triggers:
        print(f"{trigger.name}: {trigger.threshold.op} {trigger.threshold.value}")
        print(f"  Frequency: every {trigger.frequency}s")
        print(f"  State: {'triggered' if trigger.triggered else 'ok'}")
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

## Creating Triggers

### Using the Builder (Recommended)

The fluent `QueryBuilder` makes trigger creation concise and readable:

```python
from honeycomb import (
    HoneycombClient,
    TriggerCreate,
    TriggerThreshold,
    TriggerThresholdOp,
    QueryBuilder,
)

async with HoneycombClient(api_key="...") as client:
    trigger = await client.triggers.create_async(
        "my-dataset",
        TriggerCreate(
            name="High Error Rate",
            description="Alert when error rate exceeds 5%",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN,
                value=0.05,
            ),
            frequency=300,  # Check every 5 minutes
            query=QueryBuilder()
                .last_30_minutes()
                .avg("error_rate")
                .build_for_trigger(),
        )
    )
    print(f"Created trigger: {trigger.id}")
```

### Trigger with Query Filters

```python
from honeycomb import (
    TriggerCreate,
    TriggerThreshold,
    TriggerThresholdOp,
    QueryBuilder,
)

trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="API 500 Errors",
        description="Alert on server errors in API service",
        threshold=TriggerThreshold(
            op=TriggerThresholdOp.GREATER_THAN,
            value=10,  # More than 10 errors
        ),
        frequency=300,
        query=QueryBuilder()
            .last_10_minutes()
            .count()
            .eq("service", "api")
            .gte("status", 500)
            .filter_with("AND")
            .build_for_trigger(),
    )
)
```

### Trigger with Grouping

```python
trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="Slow Endpoints",
        threshold=TriggerThreshold(
            op=TriggerThresholdOp.GREATER_THAN,
            value=1000,  # P99 > 1000ms
        ),
        frequency=300,
        query=QueryBuilder()
            .last_30_minutes()
            .p99("duration_ms")
            .group_by("endpoint")  # Alert per endpoint
            .build_for_trigger(),
    )
)
```

## Threshold Configuration

### Comparison Operators

```python
from honeycomb import TriggerThresholdOp

# Available operators:
TriggerThresholdOp.GREATER_THAN           # >
TriggerThresholdOp.GREATER_THAN_OR_EQUAL  # >=
TriggerThresholdOp.LESS_THAN              # <
TriggerThresholdOp.LESS_THAN_OR_EQUAL     # <=
```

### Exceeded Limit

Require the threshold to be exceeded multiple times before alerting:

```python
from honeycomb import TriggerThreshold, TriggerThresholdOp

threshold = TriggerThreshold(
    op=TriggerThresholdOp.GREATER_THAN,
    value=100,
    exceeded_limit=3,  # Must exceed 3 times before alerting
)
```

## Alert Behavior

### Alert Types

```python
from honeycomb import TriggerCreate, TriggerAlertType

# Alert on every evaluation where threshold is exceeded
trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="Continuous Alert",
        alert_type=TriggerAlertType.ON_TRUE,  # Alert every time
        # ... rest of config
    )
)

# Alert only when state changes (exceeded -> ok or ok -> exceeded)
trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="State Change Alert",
        alert_type=TriggerAlertType.ON_CHANGE,  # Alert on change only
        # ... rest of config
    )
)
```

### Disabling Triggers

```python
# Disable a trigger without deleting it
updated = await client.triggers.update_async(
    "my-dataset",
    trigger.id,
    TriggerCreate(
        name=trigger.name,
        disabled=True,  # Pause the trigger
        # ... rest of config (must provide all fields)
    )
)
```

## Updating Triggers

When updating a trigger, you must provide all fields:

```python
# Get the existing trigger first
existing = await client.triggers.get_async("my-dataset", "trigger-id")

# Update with all fields
updated = await client.triggers.update_async(
    "my-dataset",
    "trigger-id",
    TriggerCreate(
        name="Updated Name",
        description=existing.description,  # Keep existing
        threshold=TriggerThreshold(
            op=TriggerThresholdOp.GREATER_THAN,
            value=0.10,  # Change threshold
        ),
        frequency=existing.frequency,  # Keep existing
        query=existing.query,  # Keep existing query
    )
)
```

## Important Constraints

### Time Range Limit

Trigger queries have a maximum time range of 1 hour (3600 seconds):

```python
# Valid - using builder (recommended)
query=QueryBuilder().last_1_hour().count().build_for_trigger()

# Valid - using TriggerQuery directly
from honeycomb import TriggerQuery
query=TriggerQuery(time_range=3600)  # OK: 1 hour

# Invalid - exceeds max
query=TriggerQuery(time_range=7200)  # ERROR: exceeds max
```

**Note:** `build_for_trigger()` validates time range and raises `ValueError` if it exceeds 3600 seconds.

### Frequency

The `frequency` field controls how often the trigger evaluates:

```python
frequency=60    # Every minute
frequency=300   # Every 5 minutes
frequency=3600  # Every hour
```

## Common Trigger Patterns

### Error Rate Monitoring

```python
from honeycomb import TriggerCreate, TriggerThreshold, TriggerThresholdOp, QueryBuilder

trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="Error Rate Spike",
        threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=0.01),
        frequency=300,
        query=QueryBuilder()
            .last_30_minutes()
            .avg("error_rate")
            .build_for_trigger(),
    )
)
```

### Latency Alerts

```python
trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="High P99 Latency",
        threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=500),
        frequency=300,
        query=QueryBuilder()
            .last_30_minutes()
            .p99("duration_ms")
            .group_by("service")
            .build_for_trigger(),
    )
)
```

### Volume Alerts

```python
trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="Low Traffic Warning",
        threshold=TriggerThreshold(op=TriggerThresholdOp.LESS_THAN, value=100),
        frequency=300,
        query=QueryBuilder()
            .last_10_minutes()
            .count()
            .build_for_trigger(),
    )
)
```

## See Also

- [Triggers API Reference](../api/resources.md#triggers) - Full API documentation
- [Trigger Models](../api/models.md#trigger-models) - All trigger model fields
- [Queries Guide](queries.md) - Query specifications for triggers
