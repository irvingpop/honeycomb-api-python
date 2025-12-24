# Working with Queries

Queries allow you to analyze your data in Honeycomb. The API supports both saved queries (for reuse) and ephemeral queries (one-time execution).

## Three Ways to Run Queries

### 1. Ephemeral Queries (Quick Analysis)

Run a query once without saving it:

```python
from honeycomb import HoneycombClient, QuerySpec

async with HoneycombClient(api_key="...") as client:
    result = await client.query_results.run_async(
        "my-dataset",
        spec=QuerySpec(
            time_range=3600,  # Last hour
            calculations=[{"op": "COUNT"}],
            breakdowns=["endpoint"],
        ),
        poll_interval=1.0,
        timeout=60.0,
    )

    # Process results
    for row in result.data:
        endpoint = row.get("endpoint", "unknown")
        count = row.get("COUNT", 0)
        print(f"{endpoint}: {count} requests")
```

**Use when:** One-off analysis, ad-hoc exploration

### 2. Saved Queries (Reusable)

Create a saved query for later reuse:

```python
from honeycomb import HoneycombClient, QuerySpec

async with HoneycombClient(api_key="...") as client:
    # Create and save the query
    query = await client.queries.create_async(
        "my-dataset",
        QuerySpec(
            time_range=3600,
            calculations=[{"op": "P99", "column": "duration_ms"}],
            breakdowns=["service"],
        )
    )
    print(f"Saved query: {query.id}")

    # Later, run the saved query
    result = await client.query_results.run_async(
        "my-dataset",
        query_id=query.id,
    )

    for row in result.data:
        print(row)
```

**Use when:** Queries you'll run repeatedly (monitoring, dashboards)

### 3. Create and Run Together (Best of Both!)

Save a query AND get immediate results:

```python
from honeycomb import HoneycombClient, QuerySpec

async with HoneycombClient(api_key="...") as client:
    # One call does both!
    query, result = await client.query_results.create_and_run_async(
        "my-dataset",
        QuerySpec(
            time_range=7200,
            calculations=[
                {"op": "AVG", "column": "duration_ms"},
                {"op": "COUNT"},
            ],
            filters=[
                {"column": "status", "op": ">=", "value": 500}
            ],
        ),
        poll_interval=1.0,
        timeout=60.0,
    )

    print(f"Saved as query {query.id}")
    print(f"Found {len(result.data)} rows")
```

**Use when:** You want results now AND want to reuse the query later

## Query Specifications

### Basic Query

```python
from honeycomb import QuerySpec

spec = QuerySpec(
    time_range=3600,  # Required: time range in seconds
)
```

### With Calculations

```python
spec = QuerySpec(
    time_range=3600,
    calculations=[
        {"op": "COUNT"},                           # Count all rows
        {"op": "AVG", "column": "duration_ms"},    # Average duration
        {"op": "P99", "column": "duration_ms"},    # 99th percentile
        {"op": "SUM", "column": "bytes_sent"},     # Sum of bytes
    ],
)
```

### With Filters

```python
spec = QuerySpec(
    time_range=3600,
    calculations=[{"op": "COUNT"}],
    filters=[
        {"column": "status", "op": "=", "value": "500"},
        {"column": "service", "op": "=", "value": "api"},
    ],
    filter_combination="AND",  # or "OR"
)
```

### With Breakdowns (GROUP BY)

```python
spec = QuerySpec(
    time_range=3600,
    calculations=[{"op": "COUNT"}],
    breakdowns=["endpoint", "status"],  # Group by these columns
)
```

### Complete Example

```python
from honeycomb import QuerySpec

spec = QuerySpec(
    time_range=7200,                              # Last 2 hours
    granularity=300,                              # 5-minute buckets
    calculations=[
        {"op": "COUNT"},
        {"op": "AVG", "column": "duration_ms"},
        {"op": "P99", "column": "duration_ms"},
    ],
    filters=[
        {"column": "service", "op": "=", "value": "api"},
        {"column": "status", "op": ">=", "value": 400},
    ],
    filter_combination="AND",
    breakdowns=["endpoint"],
    orders=[{"op": "COUNT", "order": "descending"}],
    limit=100,
)
```

## Polling for Results

When you run a query, it executes asynchronously on Honeycomb's servers. The client handles polling automatically:

### Automatic Polling (Recommended)

```python
# run_async() polls automatically until complete or timeout
result = await client.query_results.run_async(
    "my-dataset",
    spec=spec,
    poll_interval=1.0,  # Check every second
    timeout=60.0,       # Give up after 60 seconds
)
```

### Manual Polling (Advanced)

```python
import asyncio

# Start query execution
result_id = await client.query_results.create_async("my-dataset", spec=spec)

# Poll manually
while True:
    result = await client.query_results.get_async("my-dataset", result_id)

    if result.data is not None:
        # Query complete!
        break

    # Wait before polling again
    await asyncio.sleep(1.0)

print(f"Got {len(result.data)} rows")
```

## Working with Query Results

### Processing Results

```python
result = await client.query_results.run_async("my-dataset", spec=spec)

# Result is a QueryResult object
print(f"Rows: {len(result.data)}")

# Each row is a dict
for row in result.data:
    # Access calculated values
    count = row.get("COUNT", 0)
    avg_duration = row.get("duration_ms", 0)

    # Access breakdown values
    endpoint = row.get("endpoint", "unknown")

    print(f"{endpoint}: {count} requests, avg {avg_duration}ms")
```

### Pagination

```python
# First page
result = await client.query_results.run_async("my-dataset", spec=spec)

# Check for more pages
if result.links and result.links.get("next"):
    # Pagination handling (if needed)
    pass
```

## Common Query Patterns

### Error Rate by Endpoint

```python
spec = QuerySpec(
    time_range=3600,
    calculations=[
        {"op": "COUNT"},
    ],
    filters=[
        {"column": "status", "op": ">=", "value": 500}
    ],
    breakdowns=["endpoint"],
    orders=[{"op": "COUNT", "order": "descending"}],
    limit=10,
)
```

### Latency Percentiles

```python
spec = QuerySpec(
    time_range=3600,
    calculations=[
        {"op": "P50", "column": "duration_ms"},
        {"op": "P95", "column": "duration_ms"},
        {"op": "P99", "column": "duration_ms"},
    ],
    breakdowns=["service"],
)
```

### Time Series Data

```python
spec = QuerySpec(
    time_range=86400,      # Last 24 hours
    granularity=3600,      # 1-hour buckets
    calculations=[
        {"op": "COUNT"},
        {"op": "AVG", "column": "duration_ms"},
    ],
)
```

## See Also

- [Queries API Reference](../api/resources.md#queries) - Full API documentation
- [QuerySpec Model](../api/models.md#query-models) - All query options
- [Triggers Guide](triggers.md) - Queries are used in triggers
