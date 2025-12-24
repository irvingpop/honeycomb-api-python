# Working with SLOs

Service Level Objectives (SLOs) help you track reliability targets for your services. An SLO defines a target success rate over a time period.

## Basic SLO Operations

### List SLOs

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    slos = await client.slos.list_async("my-dataset")

    for slo in slos:
        target_pct = slo.target_per_million / 10000  # Convert to percentage
        print(f"{slo.name}: {target_pct}% over {slo.time_period_days} days")
        print(f"  SLI: {slo.sli}")
```

### Get a Specific SLO

```python
slo = await client.slos.get_async("my-dataset", "slo-id")

print(f"Name: {slo.name}")
print(f"Target: {slo.target_per_million / 10000}%")
print(f"Time Period: {slo.time_period_days} days")
print(f"Description: {slo.description}")
```

### Delete an SLO

```python
await client.slos.delete_async("my-dataset", "slo-id")
```

## Creating SLOs

### Basic SLO

```python
from honeycomb import HoneycombClient, SLOCreate, SLI

async with HoneycombClient(api_key="...") as client:
    slo = await client.slos.create_async(
        "my-dataset",
        SLOCreate(
            name="API Availability",
            description="99.9% uptime target for API service",
            sli=SLI(alias="api-availability"),
            time_period_days=30,
            target_per_million=999000,  # 99.9%
        )
    )
    print(f"Created SLO: {slo.id}")
```

### Understanding target_per_million

The `target_per_million` field represents your success rate as parts per million:

```python
# Common SLO targets:
target_per_million=999000   # 99.9% (3 nines)
target_per_million=999900   # 99.99% (4 nines)
target_per_million=999990   # 99.999% (5 nines)
target_per_million=990000    # 99.0% (2 nines)
target_per_million=950000    # 95.0%

# To convert from percentage:
percentage = 99.5
target_per_million = int(percentage * 10000)  # 995000
```

### SLI Configuration

The Service Level Indicator (SLI) defines what you're measuring:

```python
from honeycomb import SLI

# Reference an SLI by alias
sli = SLI(alias="my-service-availability")
```

The SLI itself is typically configured in the Honeycomb UI and defines:
- What constitutes a successful request
- How to calculate the success rate
- Which data to include

## Time Period Options

SLOs can be configured for time periods between 1 and 90 days:

```python
# 7-day rolling window
time_period_days=7

# 30-day rolling window (common)
time_period_days=30

# 90-day rolling window (maximum)
time_period_days=90
```

## Updating SLOs

When updating an SLO, you must provide all fields:

```python
# Get the existing SLO first
existing = await client.slos.get_async("my-dataset", "slo-id")

# Update with all fields
updated = await client.slos.update_async(
    "my-dataset",
    "slo-id",
    SLOCreate(
        name="Updated API Availability",  # New name
        description=existing.description,  # Keep existing
        sli=existing.sli,                  # Keep existing
        time_period_days=30,               # Keep existing
        target_per_million=999900,         # Change target to 99.99%
    )
)
```

## Common SLO Patterns

### High Availability Services

```python
# 99.99% availability (4 nines)
slo = await client.slos.create_async(
    "my-dataset",
    SLOCreate(
        name="Critical API Availability",
        description="High availability SLO for critical services",
        sli=SLI(alias="critical-api-availability"),
        time_period_days=30,
        target_per_million=999900,  # 99.99%
    )
)
```

### Request Success Rate

```python
# 99.5% success rate
slo = await client.slos.create_async(
    "my-dataset",
    SLOCreate(
        name="API Request Success",
        description="Non-5xx responses",
        sli=SLI(alias="api-success-rate"),
        time_period_days=7,
        target_per_million=995000,  # 99.5%
    )
)
```

### Latency SLO

```python
# 99% of requests under threshold
slo = await client.slos.create_async(
    "my-dataset",
    SLOCreate(
        name="API Latency",
        description="99% of requests under 500ms",
        sli=SLI(alias="api-p99-latency"),
        time_period_days=30,
        target_per_million=990000,  # 99.0%
    )
)
```

### Batch Job Success

```python
# 95% batch job success
slo = await client.slos.create_async(
    "my-dataset",
    SLOCreate(
        name="ETL Job Success",
        description="Batch job completion rate",
        sli=SLI(alias="etl-success-rate"),
        time_period_days=7,
        target_per_million=950000,  # 95.0%
    )
)
```

## Error Budget Tracking

SLOs automatically track your error budget. The error budget is the amount of unreliability you can tolerate while still meeting your SLO:

```python
# For a 99.9% SLO over 30 days:
# - You have 0.1% error budget
# - That's ~43 minutes of downtime
# - Or 0.1% of requests can fail

# For a 99.99% SLO over 30 days:
# - You have 0.01% error budget
# - That's ~4.3 minutes of downtime
# - Or 0.01% of requests can fail
```

When you fetch an SLO, you can see the current burn rate and remaining budget (fields returned by the API).

## Best Practices

### Start Conservative

Begin with achievable targets and tighten them over time:

```python
# Start here
target_per_million=990000   # 99.0%

# After consistently meeting it, increase to
target_per_million=995000   # 99.5%

# Then eventually
target_per_million=999000   # 99.9%
```

### Choose Appropriate Time Windows

```python
# Short windows (7 days): Good for rapidly changing services
time_period_days=7

# Medium windows (30 days): Good for most services
time_period_days=30

# Long windows (90 days): Good for very stable, critical services
time_period_days=90
```

### Use Descriptive Names

```python
# Good: Specific and clear
name="Auth Service Availability - 99.9%"
name="Payment API Latency P99 < 200ms"
name="User Signup Success Rate"

# Less helpful: Too vague
name="Service SLO"
name="API Monitoring"
```

## Multiple SLOs per Service

You can create multiple SLOs for different aspects of the same service:

```python
# Availability SLO
await client.slos.create_async(
    "my-dataset",
    SLOCreate(
        name="API Availability",
        sli=SLI(alias="api-availability"),
        time_period_days=30,
        target_per_million=999000,
    )
)

# Latency SLO
await client.slos.create_async(
    "my-dataset",
    SLOCreate(
        name="API Latency",
        sli=SLI(alias="api-latency"),
        time_period_days=30,
        target_per_million=990000,
    )
)

# Error rate SLO
await client.slos.create_async(
    "my-dataset",
    SLOCreate(
        name="API Error Rate",
        sli=SLI(alias="api-errors"),
        time_period_days=30,
        target_per_million=999500,
    )
)
```

## See Also

- [SLOs API Reference](../api/resources.md#slos) - Full API documentation
- [SLO Models](../api/models.md#slo-models) - All SLO model fields
- [Google SRE Book: SLIs, SLOs, and SLAs](https://sre.google/sre-book/service-level-objectives/) - Comprehensive guide to SLOs
