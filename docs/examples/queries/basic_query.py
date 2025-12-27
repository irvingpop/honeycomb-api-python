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
        dataset,
        QueryBuilder().last_1_hour().count().avg("duration_ms").group_by("service").build(),
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
        dataset,
        QueryBuilder().last_1_hour().p99("duration_ms").group_by("endpoint").build(),
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
        dataset,
        QueryBuilder()
        .last_2_hours()
        .count()
        .gte("status_code", 400)
        .eq("service", "api")
        .filter_with("AND")
        .group_by("endpoint")
        .order_by_count()
        .limit(10)
        .build(),
    )
    return query, result


# end_example:query_with_filters


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


# NOTE: The Honeycomb API does not support deleting saved queries.
# Once created, queries persist in the dataset. This is by design to maintain
# query history and references from triggers/SLOs.
