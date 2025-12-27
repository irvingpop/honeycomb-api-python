# Working with Burn Alerts

Burn alerts notify you when you're consuming your SLO error budget too quickly. They help prevent budget exhaustion before it impacts your SLO compliance.

## Understanding Burn Alerts

Burn alerts work with SLOs to provide early warning when error budgets are depleting faster than expected. Two alert types are available:

- **Exhaustion Time**: Alerts when budget will be exhausted within X minutes
- **Budget Rate**: Alerts when budget drops by X% within a time window

## Basic Burn Alert Operations

### List Burn Alerts for an SLO

```python
{%
   include "../examples/burn_alerts/basic_burn_alert.py"
   start="# start_example:list_burn_alerts"
   end="# end_example:list_burn_alerts"
%}
```

### Get a Specific Burn Alert

```python
{%
   include "../examples/burn_alerts/basic_burn_alert.py"
   start="# start_example:get_burn_alert"
   end="# end_example:get_burn_alert"
%}
```

### Update a Burn Alert

```python
{%
   include "../examples/burn_alerts/basic_burn_alert.py"
   start="# start_example:update"
   end="# end_example:update"
%}
```

### Delete a Burn Alert

```python
{%
   include "../examples/burn_alerts/basic_burn_alert.py"
   start="# start_example:delete"
   end="# end_example:delete"
%}
```

## Creating Burn Alerts

### Exhaustion Time Alert

Alert when budget will be exhausted within a specified time:

```python
{%
   include "../examples/burn_alerts/basic_burn_alert.py"
   start="# start_example:exhaustion_time_alert"
   end="# end_example:exhaustion_time_alert"
%}
```

### Budget Rate Alert

Alert when budget drops by a percentage within a time window:

```python
{%
   include "../examples/burn_alerts/basic_burn_alert.py"
   start="# start_example:budget_rate_alert"
   end="# end_example:budget_rate_alert"
%}
```

## Alert Type Comparison

| Alert Type | Use When | Configuration |
|------------|----------|---------------|
| **Exhaustion Time** | You want to know when budget will run out | `exhaustion_minutes` - time until budget exhaustion |
| **Budget Rate** | You want to catch sudden spikes in errors | `budget_rate_window_minutes` + `budget_rate_decrease_threshold_per_million` |

### Understanding Budget Rate Thresholds

The `budget_rate_decrease_threshold_per_million` is expressed as parts per million:

- `10000` = 1% budget drop (10,000 / 1,000,000)
- `5000` = 0.5% budget drop (5,000 / 1,000,000)

**Best Practice**: Layer alerts with multiple thresholds (critical at 2 hours, warning at 24 hours). Combine both exhaustion time and budget rate alerts for comprehensive coverage.

## Sync Usage

All burn alert operations have sync equivalents:

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List burn alerts for SLO
    alerts = client.burn_alerts.list("my-dataset", slo_id="slo-123")

    # Create burn alert (requires recipient_id)
    alert = client.burn_alerts.create(
        "my-dataset",
        BurnAlertCreate(
            alert_type=BurnAlertType.EXHAUSTION_TIME,
            slo_id="slo-123",
            exhaustion_minutes=120,
            recipients=[BurnAlertRecipient(id=recipient_id)]
        )
    )

    # Get, update, delete burn alert
    alert = client.burn_alerts.get("my-dataset", alert_id)
    updated = client.burn_alerts.update("my-dataset", alert_id, BurnAlertCreate(...))
    client.burn_alerts.delete("my-dataset", alert_id)
```
