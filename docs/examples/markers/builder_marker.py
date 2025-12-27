"""Marker Builder CRUD examples - using MarkerBuilder for marker creation."""

from __future__ import annotations

from honeycomb import HoneycombClient, Marker, MarkerBuilder


# start_example:create_with_builder
async def create_marker_with_builder(client: HoneycombClient, dataset: str) -> str:
    """Create a marker using MarkerBuilder.

    This example shows a marker for a past incident that started 3 hours ago
    and lasted for 2 hours, with a link to the incident report.
    """
    import time

    # Calculate timestamp 3 hours ago
    three_hours_ago = int(time.time()) - (3 * 60 * 60)
    two_hours_duration = 2 * 60 * 60

    marker = (
        MarkerBuilder("Production outage - Database connection timeout")
        .type("incident")
        .start_time(three_hours_ago)
        .end_time(three_hours_ago + two_hours_duration)
        .url("https://status.example.com/incidents/2024-001")
        .build()
    )

    created = await client.markers.create_async(dataset, marker)
    return created.id
# end_example:create_with_builder


# start_example:list
async def list_markers(client: HoneycombClient, dataset: str) -> list[Marker]:
    """List all markers in a dataset."""
    return await client.markers.list_async(dataset)
# end_example:list


# start_example:update
async def update_marker(client: HoneycombClient, dataset: str, marker_id: str) -> Marker:
    """Update a marker's message."""
    import time

    # Note: Updates require specifying start_time again
    marker = (
        MarkerBuilder("Updated: Deployed v1.2.3 - rollback completed")
        .type("deploy")
        .start_time(int(time.time()))
        .build()
    )

    return await client.markers.update_async(dataset, marker_id, marker)
# end_example:update


# start_example:delete
async def delete_marker(client: HoneycombClient, dataset: str, marker_id: str) -> None:
    """Delete a marker."""
    await client.markers.delete_async(dataset, marker_id)
# end_example:delete


# TEST_ASSERTIONS
async def test_lifecycle(client: HoneycombClient, dataset: str, marker_id: str) -> None:
    """Verify the full lifecycle worked."""
    # Markers don't have a get endpoint, verify by listing
    markers = await client.markers.list_async(dataset)
    marker_ids = [m.id for m in markers]
    assert marker_id in marker_ids


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, marker_id: str) -> None:
    """Clean up resources (called even on test failure)."""
    try:
        await client.markers.delete_async(dataset, marker_id)
    except Exception:
        pass  # Already deleted or doesn't exist
