"""Basic event sending examples.

These examples demonstrate sending events to Honeycomb.
Events cannot be deleted, but can be verified by querying the dataset.
"""

from __future__ import annotations

import asyncio
import time

from honeycomb import BatchEvent, HoneycombClient, QueryBuilder


# start_example:send_single
async def send_event(client: HoneycombClient, dataset: str) -> None:
    """Send a single event.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to send event to

    Note: For production use, prefer send_batch() for better efficiency.
    """
    await client.events.send_async(
        dataset,
        data={
            "service": "api",
            "endpoint": "/users",
            "duration_ms": 45,
            "status_code": 200,
        },
    )


# end_example:send_single


# start_example:send_with_timestamp
async def send_event_with_timestamp(client: HoneycombClient, dataset: str) -> None:
    """Send an event with a custom timestamp.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to send event to
    """
    await client.events.send_async(
        dataset,
        data={
            "service": "api",
            "endpoint": "/posts",
            "duration_ms": 120,
            "status_code": 201,
        },
        timestamp=int(time.time()),  # Unix timestamp
    )


# end_example:send_with_timestamp


# start_example:send_batch
async def send_batch(client: HoneycombClient, dataset: str) -> None:
    """Send multiple events in a batch.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to send events to

    Note: This is the recommended way to send events for production use.
    """
    events = [
        BatchEvent(
            data={
                "service": "api",
                "endpoint": "/users",
                "duration_ms": 45,
                "status_code": 200,
            }
        ),
        BatchEvent(
            data={
                "service": "api",
                "endpoint": "/orders",
                "duration_ms": 120,
                "status_code": 200,
            }
        ),
        BatchEvent(
            data={
                "service": "api",
                "endpoint": "/products",
                "duration_ms": 85,
                "status_code": 200,
            }
        ),
    ]
    results = await client.events.send_batch_async(dataset, events)

    # Check for any failures
    for i, result in enumerate(results):
        if result.status != 202:
            print(f"Event {i} failed: {result.error}")


# end_example:send_batch


# start_example:verify_via_query
async def verify_events(client: HoneycombClient, dataset: str) -> int:
    """Verify events were ingested by running a query.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to query

    Returns:
        The count of events found

    Note: Events take ~30 seconds to become queryable after sending.
    """
    # Wait for events to be queryable
    await asyncio.sleep(30)

    # Query to count recent events
    query, result = await client.query_results.create_and_run_async(
        QueryBuilder().dataset(dataset).last_10_minutes().count(),
    )

    # Get the count from the result
    if result.data and result.data.rows:
        count = result.data.rows[0].get("COUNT", 0)
        print(f"Found {count} events in the last 10 minutes")
        return int(count)

    return 0


# end_example:verify_via_query


# TEST_ASSERTIONS
async def test_send_event(client: HoneycombClient, dataset: str) -> None:
    """Verify send_event worked by querying."""
    # Events are sent asynchronously, verify via query in verify_events
    pass


async def test_send_batch(client: HoneycombClient, dataset: str) -> None:
    """Verify send_batch worked by querying."""
    # Events are sent asynchronously, verify via query in verify_events
    pass


async def test_verify_events(count: int) -> None:
    """Verify we found events in the query."""
    assert count > 0, "Expected to find events in the dataset"


# NOTE: Events cannot be deleted. They persist in the dataset.
# Cleanup is not needed for events - they are part of your data.
