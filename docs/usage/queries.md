# Working with Queries

Queries allow you to analyze your data in Honeycomb. All queries must first be saved, then executed to get results.

**Note:** Query Results API requires Enterprise plan.

## Building Queries

The recommended way to build queries is using the fluent `QueryBuilder`:

```python
from honeycomb import HoneycombClient, QueryBuilder

async with HoneycombClient(api_key="...") as client:
    # Standalone query - no name needed
    query, result = await client.query_results.create_and_run_async(
        "my-dataset",
        QueryBuilder()  # No name for standalone queries
            .last_1_hour()
            .count()
            .p99("duration_ms")
            .gte("status", 500)
            .group_by("service", "endpoint")
            .order_by_count()
            .build(),
    )

    for row in result.data.rows:
        print(row)
```

The builder provides:

- **IDE autocomplete** for all operations
- **Time presets** matching the Honeycomb UI (`last_10_minutes()`, `last_1_hour()`, etc.)
- **Chainable methods** for calculations, filters, grouping, and ordering
- **Filter shortcuts** like `.gte()`, `.eq()`, `.contains()` for cleaner syntax
- **Type safety** with enums for operators

### When to Use Query Names

Query names are **optional** for standalone queries but **required** for board integration:

```python
from honeycomb import QueryBuilder

# Standalone query - no name needed
spec1 = QueryBuilder().last_1_hour().count().build()

# For boards - name required (becomes the panel annotation)
spec2 = QueryBuilder("Request Count").dataset("api-logs").last_1_hour().count().build()

# With description (optional)
spec3 = (
    QueryBuilder("Request Count")
    .dataset("api-logs")
    .last_1_hour()
    .count()
    .description("Total requests over time")
    .build()
)
```

You can also use `QuerySpec.builder()` as an entry point:

```python
spec = QuerySpec.builder().last_24_hours().count().avg("duration_ms").build()
```

## Two Ways to Run Queries

### 1. Saved Queries (Two Steps)

Create a saved query, then run it:

```python
{%
   include "../examples/queries/basic_query.py"
   start="# start_example:save_then_run"
   end="# end_example:save_then_run"
%}
```

**Use when:** You want to keep the query for future reuse

### 2. Create and Run Together (Convenience)

Save a query AND get immediate results in one call:

```python
{%
   include "../examples/queries/basic_query.py"
   start="# start_example:create_and_run"
   end="# end_example:create_and_run"
%}
```

**Use when:** You want results now AND want to reuse the query later

### 3. Get a Saved Query

Retrieve a previously saved query by its ID:

```python
{%
   include "../examples/queries/basic_query.py"
   start="# start_example:get"
   end="# end_example:get"
%}
```

**Note:** The Honeycomb API does not support listing or deleting saved queries. Once created, queries persist in the dataset to maintain query history and references from triggers/SLOs.

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

## QueryBuilder

`QueryBuilder` provides a fluent interface for building query specifications. See tested examples in [basic_query.py](../examples/queries/basic_query.py).

**Key features:**
- Time presets (`.last_1_hour()`, `.last_24_hours()`, etc.)
- Calculations (`.count()`, `.avg()`, `.p99()`, etc.)
- Filters (`.eq()`, `.gte()`, `.contains()`, etc.)
- Grouping (`.group_by()`)
- Ordering (`.order_by_count()`, `.order_by()`)

Alternative approaches: dict syntax (`{"op": "COUNT"}`) or typed models (`Calculation(op=CalcOp.COUNT)`).

## Polling for Results

Query execution is async on Honeycomb's servers. The client handles polling automatically with configurable `poll_interval` and `timeout` parameters on `run_async()` and `create_and_run_async()`.

## Working with Query Results

Results are returned as `QueryResult` objects:

```python
query, result = await client.query_results.create_and_run_async("my-dataset", spec)

# Each row is a dict with calculated values (uppercase) and breakdown values
for row in result.data.rows:
    count = row.get("COUNT", 0)
    avg = row.get("AVG", 0)
    endpoint = row.get("endpoint", "unknown")
    print(f"{endpoint}: {count} requests, avg {avg}ms")
```

## Sync Usage

All query operations have sync equivalents:

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # Create and run query
    query, result = client.query_results.create_and_run(
        "my-dataset",
        QueryBuilder().last_1_hour().count().build()
    )

    # Create saved query
    query = client.queries.create("my-dataset", spec)

    # Run saved query
    result = client.query_results.run("my-dataset", query_id=query.id)

    # Get saved query
    query = client.queries.get("my-dataset", query_id)
```
