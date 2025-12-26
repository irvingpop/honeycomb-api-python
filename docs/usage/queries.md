# Working with Queries

Queries allow you to analyze your data in Honeycomb. All queries must first be saved, then executed to get results.

**Note:** Query Results API requires Enterprise plan.

## Two Ways to Run Queries

### 1. Saved Queries (Two Steps)

Create a saved query, then run it:

```python
from honeycomb import HoneycombClient, QuerySpec

async with HoneycombClient(api_key="...") as client:
    # Step 1: Create and save the query
    query = await client.queries.create_async(
        "my-dataset",
        QuerySpec(
            time_range=3600,  # Last hour
            calculations=[{"op": "P99", "column": "duration_ms"}],
            breakdowns=["service"],
        )
    )
    print(f"Saved query: {query.id}")

    # Step 2: Run the saved query
    result = await client.query_results.run_async(
        "my-dataset",
        query_id=query.id,
    )

    for row in result.data.rows:
        print(row)
```

**Use when:** You want to keep the query for future reuse

### 2. Create and Run Together (Convenience)

Save a query AND get immediate results in one call:

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
    print(f"Found {len(result.data.rows)} rows")
```

**Use when:** You want results now AND want to reuse the query later

## Result Limits and Pagination

### Understanding Query Limits

There are two different places where limits are applied:

1. **Saved query limit** (`spec.limit`): Maximum 1,000 rows
   - Set in QuerySpec when creating a saved query
   - Enforced by client (raises `ValueError` if `> 1000`)
   - Optional - leave it unset for maximum results

2. **Query result execution limit**: Up to 10,000 rows when `disable_series=True`
   - Set when executing the query result (not in the saved query)
   - Passed as `limit` parameter to `run_async()` or `create_and_run_async()`
   - Defaults to 10,000 when `disable_series=True`, 1,000 when `False`
   - Maximum: 10,000 with `disable_series=True`, 1,000 otherwise

### Default Behavior: Up to 10K Results

By default, `run_async()` and `create_and_run_async()`:
- Set `disable_series=True` (disables timeseries data)
- Set `limit=10000` automatically (maximum allowed with disable_series)
- Return up to **10,000 results** (vs 1,000 when `disable_series=False`)
- Improves query performance

```python
# Automatically gets up to 10K results
query, result = await client.query_results.create_and_run_async(
    "my-dataset",
    QuerySpec(
        time_range=86400,
        calculations=[{"op": "COUNT"}],
        breakdowns=["trace.trace_id"],
    ),
)
print(f"Got {len(result.data.rows)} traces (up to 10,000)")
```

### For > 10K Results: Advanced Pagination

Use `run_all_async()` for > 10,000 results with automatic pagination:

```python
# Get up to 100K results with smart pagination
rows = await client.query_results.run_all_async(
    "my-dataset",
    spec=QuerySpec(
        time_range=86400,  # Last 24 hours
        calculations=[{"op": "AVG", "column": "duration_ms"}],
        breakdowns=["trace.trace_id", "name"],
    ),
    sort_order="descending",  # Highest averages first
    max_results=100_000,      # Stop after 100K rows
    on_page=lambda page, total: print(f"Page {page}: {total} rows"),
)
print(f"Total: {len(rows)} traces")
```

**How it works:**
1. Converts time_range to absolute timestamps (for consistency across pages)
2. Creates saved queries sorted by first calculation (descending by default)
3. Executes each query with `limit=10000` to get maximum results per page
4. Captures last value from sort field (calculation or breakdown)
5. Re-runs with HAVING clause (for calculations) or filter (for breakdowns) to get next page
6. Deduplicates by composite key (breakdowns + calculation values)
7. **Smart stopping:** Stops if > 50% duplicates detected (long tail)
8. Rate limited: 10 queries/minute (be patient with large result sets)

**Important:**
- Don't set `spec.orders` (managed automatically)
- Don't set `spec.limit` (max 1000 for saved queries, limit is set at execution time)
- Default sort field is first calculation
- Default max_results = 100,000
- Each page returns up to 10,000 rows
- Can take several minutes for very large result sets
- **Each page creates a new saved query** (they accumulate)

### When to Use Each

| Results Needed | Method | Limit | Notes |
|----------------|--------|-------|-------|
| < 1,000 | `run_async(disable_series=False)` | 1,000 | Get timeseries data |
| 1,000 - 10,000 | `run_async()` or `create_and_run_async()` | 10,000 | Fastest, no pagination (disable_series=True) |
| > 10,000 | `run_all_async()` | 100,000 default | Automatic pagination, be patient |

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
    query_id=saved_query_id,
    poll_interval=1.0,  # Check every second
    timeout=60.0,       # Give up after 60 seconds
)
```

### Manual Polling (Advanced)

```python
import asyncio

# Start query execution
result_id = await client.query_results.create_async(
    "my-dataset",
    query_id=saved_query_id
)

# Poll manually
while True:
    result = await client.query_results.get_async("my-dataset", result_id)

    if result.data is not None:
        # Query complete!
        break

    # Wait before polling again
    await asyncio.sleep(1.0)

print(f"Got {len(result.data.results)} rows")
```

## Working with Query Results

### Processing Results

```python
query, result = await client.query_results.create_and_run_async(
    "my-dataset",
    spec=spec
)

# Result is a QueryResult object
print(f"Rows: {len(result.data.rows)}")

# Each row is a dict
for row in result.data.rows:
    # Access calculated values (uppercase: COUNT, AVG, P99, etc.)
    count = row.get("COUNT", 0)
    avg = row.get("AVG", 0)  # or use alias if you set one

    # Access breakdown values (as specified in breakdowns)
    endpoint = row.get("endpoint", "unknown")

    print(f"{endpoint}: {count} requests, avg {avg}ms")
```

### Advanced: Paginating Large Result Sets (> 10K rows)

For queries returning > 10,000 rows, use `run_all_async()`:

```python
# Example: Get all slow traces in last 24 hours
rows = await client.query_results.run_all_async(
    "my-dataset",
    spec=QuerySpec(
        time_range=86400,
        calculations=[{"op": "AVG", "column": "duration_ms", "alias": "avg_duration"}],
        filters=[
            {"column": "duration_ms", "op": ">", "value": 1000}  # > 1 second
        ],
        breakdowns=["trace.trace_id", "name"],
    ),
    sort_field="avg_duration",  # Sort by average duration (auto-default)
    sort_order="descending",     # Slowest first (default)
    max_results=50_000,          # Limit to 50K rows
    on_page=lambda page, total: print(f"Fetched page {page}: {total} rows total"),
)

# Process all results
slow_traces = [
    (row["trace.trace_id"], row["name"], row["avg_duration"])
    for row in rows
]
print(f"Found {len(slow_traces)} slow traces")
```

**Important Notes:**
- Rate limit: 10 queries/minute (50K rows = ~5 queries = ~30 seconds)
- Smart stopping: Stops if > 50% duplicate rows detected (long tail)
- Automatic deduplication by composite key (breakdowns + calculations)
- Don't set `spec.orders` - managed automatically
- Progress callback recommended for visibility
- **Each page creates a new saved query** that persists in Honeycomb

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
