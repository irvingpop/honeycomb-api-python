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

## Creating SLOs

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
