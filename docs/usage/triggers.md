# Working with Triggers

Triggers alert you when query results cross a threshold. They continuously monitor your data and notify you when conditions are met.

## Basic Trigger Operations

### List Triggers

```python
{%
   include "../examples/triggers/basic_trigger.py"
   start="# start_example:list"
   end="# end_example:list"
%}
```

### Get a Specific Trigger

```python
{%
   include "../examples/triggers/basic_trigger.py"
   start="# start_example:get"
   end="# end_example:get"
%}
```

### Update a Trigger

```python
{%
   include "../examples/triggers/basic_trigger.py"
   start="# start_example:update"
   end="# end_example:update"
%}
```

### Delete a Trigger

```python
{%
   include "../examples/triggers/basic_trigger.py"
   start="# start_example:delete"
   end="# end_example:delete"
%}
```

## Creating Triggers

### Using TriggerBuilder (Recommended)

```python
{%
   include "../examples/triggers/basic_trigger.py"
   start="# start_example:simple_with_builder"
   end="# end_example:simple_with_builder"
%}
```

See also: [trigger with filters](../examples/triggers/basic_trigger.py#L48) and [manual construction](../examples/triggers/basic_trigger.py#L80)

### Manual Construction

```python
{%
   include "../examples/triggers/basic_trigger.py"
   start="# start_example:manual_construction"
   end="# end_example:manual_construction"
%}
```

## TriggerBuilder Features

`TriggerBuilder` provides a fluent interface that combines:
- **Query specification** (inherited from QueryBuilder)
- **Threshold configuration** (`.threshold_gt()`, `.threshold_lt()`, etc.)
- **Frequency settings** (`.every_5_minutes()`, `.every_15_minutes()`, etc.)
- **Recipients** (`.email()`, `.slack()`, `.pagerduty()`, `.webhook()`)
- **Tags** (`.tag(key, value)` - max 10 tags)
- **Baseline comparison** (`.baseline_1_hour_ago()`, `.baseline_1_day_ago()`, etc.)

See the [QueryBuilder documentation](queries.md#building-queries) for full query methods.

### Important Constraints

Triggers have API-enforced limits that TriggerBuilder validates at build time:

- **Time range**: Maximum 3600 seconds (1 hour)
- **Frequency vs duration**: `time_range ≤ frequency × 4`
- **Single calculation**: Only one calculation per trigger (e.g., COUNT, P99, AVG)
- **No absolute time**: Must use relative time ranges

## Sync Usage

All trigger operations have sync equivalents:

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List triggers
    triggers = client.triggers.list("my-dataset")

    # Create trigger
    trigger = TriggerBuilder("High Errors").dataset("my-dataset").count().threshold_gt(100).build()
    created = client.triggers.create("my-dataset", trigger)

    # Get trigger
    trigger = client.triggers.get("my-dataset", trigger_id)

    # Update trigger
    updated = client.triggers.update("my-dataset", trigger_id, TriggerCreate(...))

    # Delete trigger
    client.triggers.delete("my-dataset", trigger_id)
```
