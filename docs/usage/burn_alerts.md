# Working with Burn Alerts

Burn alerts notify you when you're consuming your SLO error budget too quickly. They help prevent budget exhaustion before it impacts your SLO compliance.

## Understanding Burn Alerts

Burn alerts work with SLOs to provide early warning when error budgets are depleting faster than expected. Two alert types are available:

- **Exhaustion Time**: Alerts when budget will be exhausted within X minutes
- **Budget Rate**: Alerts when budget drops by X% within a time window

## Basic Burn Alert Operations

### List Burn Alerts for an SLO

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    # Burn alerts are listed by SLO ID
    alerts = await client.burn_alerts.list_async(
        dataset="my-dataset",
        slo_id="slo-123"
    )

    for alert in alerts:
        print(f"{alert.alert_type}: {alert.description}")
        print(f"  Triggered: {alert.triggered}")
```

### Get a Specific Burn Alert

```python
alert = await client.burn_alerts.get_async("my-dataset", "alert-id")

print(f"Type: {alert.alert_type}")
print(f"SLO: {alert.slo_id}")
print(f"Triggered: {alert.triggered}")
```

### Delete a Burn Alert

```python
await client.burn_alerts.delete_async("my-dataset", "alert-id")
```

## Creating Burn Alerts

### Exhaustion Time Alert

Alert when budget will be exhausted within a specified time:

```python
from honeycomb import HoneycombClient, BurnAlertCreate, BurnAlertType

async with HoneycombClient(api_key="...") as client:
    alert = await client.burn_alerts.create_async(
        "my-dataset",
        BurnAlertCreate(
            alert_type=BurnAlertType.EXHAUSTION_TIME,
            slo_id="slo-123",
            description="Alert when budget depletes within 2 hours",
            exhaustion_minutes=120,  # Alert at 2 hours remaining
        )
    )
    print(f"Created exhaustion time alert: {alert.id}")
```

### Budget Rate Alert

Alert when budget drops by a percentage within a time window:

```python
alert = await client.burn_alerts.create_async(
    "my-dataset",
    BurnAlertCreate(
        alert_type=BurnAlertType.BUDGET_RATE,
        slo_id="slo-123",
        description="Alert on rapid budget consumption",
        budget_rate_window_minutes=60,  # 1-hour window
        budget_rate_decrease_threshold_per_million=10000,  # 1% drop (10000/1000000)
    )
)
```

## Updating Burn Alerts

```python
updated_alert = await client.burn_alerts.update_async(
    "my-dataset",
    "alert-id",
    BurnAlertCreate(
        alert_type=BurnAlertType.EXHAUSTION_TIME,
        slo_id="slo-123",
        description="Updated: Alert at 4 hours remaining",
        exhaustion_minutes=240,  # Changed to 4 hours
    )
)
```

## Burn Alert Strategies

### Layered Alerting

Create multiple burn alerts with different thresholds:

```python
# Critical: 2 hours until exhaustion
critical_alert = await client.burn_alerts.create_async(
    "my-dataset",
    BurnAlertCreate(
        alert_type=BurnAlertType.EXHAUSTION_TIME,
        slo_id="slo-123",
        description="CRITICAL: 2 hours until budget exhaustion",
        exhaustion_minutes=120,
    )
)

# Warning: 24 hours until exhaustion
warning_alert = await client.burn_alerts.create_async(
    "my-dataset",
    BurnAlertCreate(
        alert_type=BurnAlertType.EXHAUSTION_TIME,
        slo_id="slo-123",
        description="WARNING: 24 hours until budget exhaustion",
        exhaustion_minutes=1440,  # 24 hours
    )
)

# Rate-based: Rapid budget burn
rate_alert = await client.burn_alerts.create_async(
    "my-dataset",
    BurnAlertCreate(
        alert_type=BurnAlertType.BUDGET_RATE,
        slo_id="slo-123",
        description="Rapid budget consumption detected",
        budget_rate_window_minutes=60,
        budget_rate_decrease_threshold_per_million=5000,  # 0.5% in 1 hour
    )
)
```

### Per-Environment Burn Alerts

```python
# Production: Aggressive alerting
prod_alert = await client.burn_alerts.create_async(
    "production-dataset",
    BurnAlertCreate(
        alert_type=BurnAlertType.EXHAUSTION_TIME,
        slo_id="prod-slo-id",
        description="Production: 4 hours to exhaustion",
        exhaustion_minutes=240,
    )
)

# Staging: More lenient
staging_alert = await client.burn_alerts.create_async(
    "staging-dataset",
    BurnAlertCreate(
        alert_type=BurnAlertType.EXHAUSTION_TIME,
        slo_id="staging-slo-id",
        description="Staging: 1 hour to exhaustion",
        exhaustion_minutes=60,
    )
)
```

## Sync Usage

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List burn alerts for SLO
    alerts = client.burn_alerts.list("my-dataset", slo_id="slo-123")

    # Create burn alert
    alert = client.burn_alerts.create(
        "my-dataset",
        BurnAlertCreate(
            alert_type=BurnAlertType.EXHAUSTION_TIME,
            slo_id="slo-123",
            exhaustion_minutes=120
        )
    )

    # Delete burn alert
    client.burn_alerts.delete("my-dataset", "alert-id")
```

## Alert Type Comparison

| Alert Type | Use When | Configuration |
|------------|----------|---------------|
| **Exhaustion Time** | You want to know when budget will run out | `exhaustion_minutes` - time until budget exhaustion |
| **Budget Rate** | You want to catch sudden spikes in errors | `budget_rate_window_minutes` + `budget_rate_decrease_threshold_per_million` |

## Budget Rate Threshold Calculation

The `budget_rate_decrease_threshold_per_million` is expressed as parts per million:

```python
# Alert on 1% budget drop in 1 hour
# 1% = 10,000 / 1,000,000
threshold = 10000

# Alert on 0.5% budget drop in 30 minutes
# 0.5% = 5,000 / 1,000,000
threshold = 5000
window = 30

alert = BurnAlertCreate(
    alert_type=BurnAlertType.BUDGET_RATE,
    slo_id="slo-123",
    budget_rate_window_minutes=window,
    budget_rate_decrease_threshold_per_million=threshold
)
```

## Best Practices

1. **Layer Your Alerts**: Use multiple thresholds (critical, warning, info)
2. **Combine Alert Types**: Use both exhaustion time and budget rate for comprehensive coverage
3. **Test Thresholds**: Start conservative and adjust based on actual burn patterns
4. **Document Alerts**: Use clear descriptions for oncall context
5. **Per-SLO Strategy**: Different SLOs may need different alert strategies
6. **Connect to Runbooks**: Include runbook links in descriptions

## Example: Complete SLO + Burn Alert Setup

```python
from honeycomb import (
    HoneycombClient,
    SLOCreate,
    SLI,
    BurnAlertCreate,
    BurnAlertType
)

async with HoneycombClient(api_key="...") as client:
    # Create SLO
    slo = await client.slos.create_async(
        "my-dataset",
        SLOCreate(
            name="API Availability",
            description="99.9% of requests succeed",
            time_period_days=30,
            target_per_million=999000,  # 99.9%
            sli=SLI(alias="success_rate")
        )
    )

    # Critical burn alert
    await client.burn_alerts.create_async(
        "my-dataset",
        BurnAlertCreate(
            alert_type=BurnAlertType.EXHAUSTION_TIME,
            slo_id=slo.id,
            description="CRITICAL: Budget exhausts in 2 hours - page oncall",
            exhaustion_minutes=120
        )
    )

    # Warning burn alert
    await client.burn_alerts.create_async(
        "my-dataset",
        BurnAlertCreate(
            alert_type=BurnAlertType.EXHAUSTION_TIME,
            slo_id=slo.id,
            description="WARNING: Budget exhausts in 24 hours - investigate",
            exhaustion_minutes=1440
        )
    )

    # Rate-based alert for spikes
    await client.burn_alerts.create_async(
        "my-dataset",
        BurnAlertCreate(
            alert_type=BurnAlertType.BUDGET_RATE,
            slo_id=slo.id,
            description="Rapid budget burn detected - check for incidents",
            budget_rate_window_minutes=60,
            budget_rate_decrease_threshold_per_million=10000
        )
    )
```
