# Working with SLOs

Service Level Objectives (SLOs) help you track reliability targets for your services. An SLO defines a target success rate over a time period.

## Basic SLO Operations

### List SLOs

```python
{%
   include "../examples/slos/basic_slo.py"
   start="# start_example:list_slos"
   end="# end_example:list_slos"
%}
```

### Get a Specific SLO

```python
{%
   include "../examples/slos/basic_slo.py"
   start="# start_example:get_slo"
   end="# end_example:get_slo"
%}
```

### Update an SLO

```python
{%
   include "../examples/slos/basic_slo.py"
   start="# start_example:update_slo"
   end="# end_example:update_slo"
%}
```

### Delete an SLO

```python
{%
   include "../examples/slos/basic_slo.py"
   start="# start_example:delete"
   end="# end_example:delete"
%}
```

## Creating SLOs with SLOBuilder

`SLOBuilder` provides a fluent interface for creating SLOs with integrated burn alerts and automatic derived column management. It handles the complete orchestration of creating an SLO with all its dependencies.

### Simple Example - Using Existing Derived Column

```python
{%
   include "../examples/slos/builder_slo.py"
   start="# start_example:create_simple"
   end="# end_example:create_simple"
%}
```

### Moderate Complexity - Creating New Derived Column

When you need to create both a derived column and an SLO together:

```python
{%
   include "../examples/slos/builder_slo.py"
   start="# start_example:create_with_new_column"
   end="# end_example:create_with_new_column"
%}
```

### High Complexity - SLO with Burn Alerts

Create an SLO with both exhaustion time and budget rate burn alerts:

```python
{%
   include "../examples/slos/builder_slo.py"
   start="# start_example:create_with_burn_alerts"
   end="# end_example:create_with_burn_alerts"
%}
```

### SLOs with Tags

Organize and categorize SLOs using tags for team, service, environment, or criticality:

```python
{%
   include "../examples/slos/builder_slo.py"
   start="# start_example:create_with_tags"
   end="# end_example:create_with_tags"
%}
```

### Multi-Dataset SLOs

Create an SLO across multiple datasets with an environment-wide derived column:

```python
{%
   include "../examples/slos/builder_slo.py"
   start="# start_example:create_multi_dataset"
   end="# end_example:create_multi_dataset"
%}
```

## SLOBuilder Reference

### Target Configuration Methods

| Method | Description |
|--------|-------------|
| `.target_percentage(percent)` | Set target as percentage (e.g., 99.9 for 99.9%) |
| `.target_per_million(value)` | Set target directly as per-million value (e.g., 999000 for 99.9%) |

### Time Period Methods

| Method | Description |
|--------|-------------|
| `.time_period_days(days)` | Set time period in days (1-90) |
| `.time_period_weeks(weeks)` | Set time period in weeks |

### SLI Definition Methods

| Method | Description |
|--------|-------------|
| `.sli(alias)` | Use existing derived column |
| `.sli(alias, expression, description)` | Create new derived column |

### Dataset Scoping

| Method | Description |
|--------|-------------|
| `.dataset(slug)` | Scope SLO to single dataset |
| `.datasets([slug1, slug2])` | Scope SLO to multiple datasets (creates one SLO via __all__ endpoint) |

### Organization Methods

| Method | Description |
|--------|-------------|
| `.description(desc)` | Set SLO description |
| `.tag(key, value)` | Add a tag key-value pair for organizing/filtering SLOs (max 10 tags) |

### Burn Alert Methods

| Method | Description |
|--------|-------------|
| `.exhaustion_alert(builder)` | Add exhaustion time burn alert |
| `.budget_rate_alert(builder)` | Add budget rate burn alert |

## BurnAlertBuilder Reference

`BurnAlertBuilder` is used within `SLOBuilder` to configure burn alerts with recipients. It composes `RecipientMixin` for notification management.

### Alert Type Configuration

| Alert Type | Required Methods | Description |
|------------|------------------|-------------|
| `EXHAUSTION_TIME` | `.exhaustion_minutes(minutes)` | Alert when budget will be exhausted within timeframe |
| `BUDGET_RATE` | `.window_minutes(minutes)` + `.threshold_percent(percent)` | Alert when burn rate exceeds threshold |

### Recipient Methods (from RecipientMixin)

See [Recipients documentation](recipients.md) for full details on available recipient methods:
- `.email(address)` - Email notification
- `.slack(channel)` - Slack notification
- `.pagerduty(routing_key, severity)` - PagerDuty notification
- `.webhook(url, secret)` - Webhook notification
- `.msteams(workflow_url)` - MS Teams notification
- `.recipient_id(id)` - Reference existing recipient by ID

### Example: Exhaustion Time Alert

```python
from honeycomb import BurnAlertBuilder, BurnAlertType

alert = (
    BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
    .exhaustion_minutes(60)
    .description("Alert when budget exhausts in 1 hour")
    .recipient_id("recipient-id-123")  # Reference existing recipient
    .build()
)
```

### Example: Budget Rate Alert

```python
from honeycomb import BurnAlertBuilder, BurnAlertType

alert = (
    BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
    .window_minutes(60)
    .threshold_percent(2.0)
    .description("Alert when burn rate exceeds 2% per hour")
    .recipient_id("recipient-id-456")  # Reference existing recipient
    .build()
)
```

**Note**: For integration testing, use `.recipient_id()` to reference recipients configured in Honeycomb. Email, Slack, PagerDuty, and webhook recipients must be set up in Honeycomb first via the Recipients API or UI.

## Creating SLOs Manually

For simple cases or when you need fine-grained control, you can create SLOs directly:

```python
{%
   include "../examples/slos/basic_slo.py"
   start="# start_example:create_slo"
   end="# end_example:create_slo"
%}
```

### Understanding target_per_million

The `target_per_million` field represents your success rate as parts per million. Common values:

- `999000` = 99.9% (3 nines) - ~43 minutes downtime/month
- `999900` = 99.99% (4 nines) - ~4.3 minutes downtime/month
- `999990` = 99.999% (5 nines) - ~26 seconds downtime/month
- `990000` = 99.0% (2 nines) - ~7.2 hours downtime/month
- `950000` = 95.0% - ~36 hours downtime/month

To convert from percentage: `target_per_million = int(percentage * 10000)`

### SLI Configuration

The Service Level Indicator (SLI) is typically configured in the Honeycomb UI and referenced by alias:

```python
from honeycomb import SLI

sli = SLI(alias="my-service-availability")
```

### Time Period Options

SLOs support rolling windows between 1 and 90 days:
- **7 days**: Good for rapidly changing services
- **30 days**: Good for most services (recommended)
- **90 days**: Good for very stable, critical services

## Sync Usage

All SLO operations have sync equivalents:

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # List SLOs
    slos = client.slos.list("my-dataset")

    # Create SLO
    slo = client.slos.create("my-dataset", SLOCreate(...))

    # Get SLO
    slo = client.slos.get("my-dataset", slo_id)

    # Update SLO
    updated = client.slos.update("my-dataset", slo_id, SLOCreate(...))

    # Delete SLO
    client.slos.delete("my-dataset", slo_id)
```
