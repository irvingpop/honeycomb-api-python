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

### Basic Trigger with Inline Query

```python
from honeycomb import (
    HoneycombClient,
    TriggerCreate,
    TriggerThreshold,
    TriggerThresholdOp,
    TriggerQuery,
    QueryCalculation,
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
            query=TriggerQuery(
                time_range=900,  # 15-minute window
                calculations=[
                    QueryCalculation(op="AVG", column="error_rate")
                ],
            ),
        )
    )
    print(f"Created trigger: {trigger.id}")
```

### Trigger with Query Filters

```python
from honeycomb import TriggerCreate, TriggerThreshold, TriggerThresholdOp, TriggerQuery, QueryFilter

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
        query=TriggerQuery(
            time_range=600,  # 10-minute window
            calculations=[QueryCalculation(op="COUNT")],
            filters=[
                QueryFilter(column="service", op="=", value="api"),
                QueryFilter(column="status", op=">=", value=500),
            ],
            filter_combination="AND",
        ),
    )
)
```

### Trigger with Breakdowns

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
        query=TriggerQuery(
            time_range=1800,
            calculations=[QueryCalculation(op="P99", column="duration_ms")],
            breakdowns=["endpoint"],  # Alert per endpoint
        ),
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
# Valid
query=TriggerQuery(time_range=3600)  # OK: 1 hour

# Invalid
query=TriggerQuery(time_range=7200)  # ERROR: exceeds max
```

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
trigger = await client.triggers.create_async(
    "my-dataset",
    TriggerCreate(
        name="Error Rate Spike",
        threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=0.01),
        frequency=300,
        query=TriggerQuery(
            time_range=900,
            calculations=[QueryCalculation(op="AVG", column="error_rate")],
        ),
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
        query=TriggerQuery(
            time_range=1800,
            calculations=[QueryCalculation(op="P99", column="duration_ms")],
            breakdowns=["service"],
        ),
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
        query=TriggerQuery(
            time_range=600,
            calculations=[QueryCalculation(op="COUNT")],
        ),
    )
)
```

## See Also

- [Triggers API Reference](../api/resources.md#triggers) - Full API documentation
- [Trigger Models](../api/models.md#trigger-models) - All trigger model fields
- [Queries Guide](queries.md) - Query specifications for triggers
