"""List queries examples.

IMPORTANT: The Honeycomb API does not currently support listing saved queries.
This file is kept for reference but the examples below will not work.

The Queries API only supports:
- POST /1/queries/{dataset} - Create a query
- GET /1/queries/{dataset}/{query_id} - Get a specific query by ID

There is no GET /1/queries/{dataset} endpoint to list all queries.
Once created, queries can only be retrieved by their specific ID.
"""

from __future__ import annotations

from honeycomb import HoneycombClient, Query


# NOTE: The following examples are NOT FUNCTIONAL because the API doesn't support listing.
# Kept for documentation purposes only.

# start_example:list_async
async def list_queries(client: HoneycombClient, dataset: str) -> list[Query]:
    """List all saved queries in a dataset.

    NOTE: This function will fail - the Honeycomb API does not support listing queries.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list queries from

    Returns:
        List of saved queries

    Raises:
        AttributeError: queries resource has no list_async method
    """
    # This will fail - method does not exist
    queries = await client.queries.list_async(dataset)
    for query in queries:
        print(f"Query {query.id}: {len(query.query_spec.calculations)} calculations")
    return queries


# end_example:list_async


# start_example:list_sync
def list_queries_sync(client: HoneycombClient, dataset: str) -> list[Query]:
    """List saved queries using sync client.

    NOTE: This function will fail - the Honeycomb API does not support listing queries.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list queries from

    Returns:
        List of saved queries

    Raises:
        AttributeError: queries resource has no list method
    """
    # This will fail - method does not exist
    queries = client.queries.list(dataset)
    for query in queries:
        print(f"Query {query.id}")
    return queries


# end_example:list_sync


# TEST_ASSERTIONS
async def test_assertions(queries: list[Query]) -> None:
    """Verify the example worked correctly."""
    assert isinstance(queries, list)
