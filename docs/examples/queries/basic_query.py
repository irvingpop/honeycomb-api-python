"""Basic query examples.

These examples demonstrate building and running queries
using QueryBuilder and the query results API.
"""

from __future__ import annotations

from honeycomb import HoneycombClient, Query, QueryBuilder, QueryResult


# start_example:create_and_run
async def create_and_run_query(client: HoneycombClient, dataset: str) -> tuple[Query, QueryResult]:
    """Create a query and run it in one step.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to query

    Returns:
        Tuple of (saved query, query result)
    """
    query, result = await client.query_results.create_and_run_async(
        QueryBuilder()
        .dataset(dataset)
        .last_1_hour()
        .count()
        .avg("duration_ms")
        .group_by("service"),
    )
    print(f"Query {query.id} returned {len(result.data.rows)} rows")
    return query, result


# end_example:create_and_run


# start_example:save_then_run
async def save_then_run_query(client: HoneycombClient, dataset: str) -> tuple[Query, QueryResult]:
    """Create a saved query, then run it separately.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to query

    Returns:
        Tuple of (saved query, query result)
    """
    # Step 1: Create and save the query
    query = await client.queries.create_async(
        QueryBuilder()
        .dataset(dataset)
        .last_1_hour()
        .p99("duration_ms")
        .group_by("endpoint"),
    )
    print(f"Saved query: {query.id}")

    # Step 2: Run the saved query
    result = await client.query_results.run_async(dataset, query_id=query.id)
    return query, result


# end_example:save_then_run


# start_example:query_with_filters
async def query_with_filters(client: HoneycombClient, dataset: str) -> tuple[Query, QueryResult]:
    """Run a query with filter conditions.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to query

    Returns:
        Tuple of (saved query, query result)
    """
    query, result = await client.query_results.create_and_run_async(
        QueryBuilder()
        .dataset(dataset)
        .last_2_hours()
        .count()
        .gte("status_code", 400)
        .eq("service", "api")
        .filter_with("AND")
        .group_by("endpoint")
        .order_by_count()
        .limit(10),
    )
    return query, result


# end_example:query_with_filters


# start_example:query_with_orders_and_havings
async def query_with_orders_and_havings(
    client: HoneycombClient, dataset: str
) -> tuple[Query, QueryResult]:
    """Run a query with ordering and post-aggregation filtering (havings).

    This example finds the slowest endpoints by filtering for high-volume endpoints
    (>100 requests) and ordering by P99 latency.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to query

    Returns:
        Tuple of (saved query, query result)
    """
    query, result = await client.query_results.create_and_run_async(
        QueryBuilder()
        .dataset(dataset)
        .last_1_hour()
        .count()
        .p99("duration_ms")
        .avg("duration_ms")
        .group_by("endpoint")
        .order_by(op="P99", column="duration_ms", direction="descending")
        .having(calculate_op="COUNT", op=">", value=100.0)  # Only high-volume endpoints
        .limit(10)
    )
    print(f"Found {len(result.data.rows)} high-volume slow endpoints")
    return query, result


# end_example:query_with_orders_and_havings


# start_example:get
async def get_query(client: HoneycombClient, dataset: str, query_id: str) -> Query:
    """Get a saved query by ID.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the query
        query_id: ID of the query to retrieve

    Returns:
        The query object
    """
    query = await client.queries.get_async(dataset, query_id)
    print(f"Query ID: {query.id}")
    # Query spec fields are returned at top level (via model extra fields)
    query_data = query.model_dump()
    print(f"Time range: {query_data.get('time_range')}s")
    print(f"Calculations: {len(query_data.get('calculations', []))}")
    return query


# end_example:get


# TEST_ASSERTIONS
async def test_create_and_run(query: Query, result: QueryResult) -> None:
    """Verify create_and_run example worked."""
    assert query.id is not None
    assert result.data is not None


async def test_save_then_run(query: Query, result: QueryResult) -> None:
    """Verify save_then_run example worked."""
    assert query.id is not None
    assert result.data is not None


async def test_get_query(query: Query, expected_query_id: str) -> None:
    """Verify get example worked."""
    assert query.id == expected_query_id
    # Query spec fields are returned at top level via extra fields
    query_data = query.model_dump()
    assert "time_range" in query_data or "calculations" in query_data


async def test_query_with_filters(query: Query, result: QueryResult) -> None:
    """Verify filters example worked."""
    assert query.id is not None
    assert result.data is not None


async def test_query_with_orders_and_havings(query: Query, result: QueryResult) -> None:
    """Verify orders and havings example worked."""
    assert query.id is not None
    assert result.data is not None
    # Verify query has orders and havings
    query_data = query.model_dump()
    assert query_data.get("orders") is not None, "Query should have orders"
    assert len(query_data["orders"]) == 1, "Query should have 1 order"
    assert query_data["orders"][0]["op"] == "P99"
    assert query_data["orders"][0]["column"] == "duration_ms"
    assert query_data.get("havings") is not None, "Query should have havings"
    assert len(query_data["havings"]) == 1, "Query should have 1 having"
    assert query_data["havings"][0]["calculate_op"] == "COUNT"


# NOTE: The Honeycomb API does not support deleting saved queries.
# Once created, queries persist in the dataset. This is by design to maintain
# query history and references from triggers/SLOs.
