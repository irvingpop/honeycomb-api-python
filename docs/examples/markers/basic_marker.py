"""Basic marker creation examples.

These examples demonstrate creating deployment and event markers.
"""

from __future__ import annotations

import time

from honeycomb import HoneycombClient, Marker, MarkerCreate


# start_example:create_marker
async def create_deploy_marker(client: HoneycombClient, dataset: str) -> str:
    """Create a deployment marker.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create marker in

    Returns:
        The created marker ID
    """
    marker = await client.markers.create_async(
        dataset,
        MarkerCreate(
            message="Backend deploy v2.5.0",
            type="deploy",
            start_time=int(time.time()),
        ),
    )
    return marker.id


# end_example:create_marker


# start_example:create_marker_with_url
async def create_marker_with_url(client: HoneycombClient, dataset: str) -> str:
    """Create a marker with a link to the PR.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create marker in

    Returns:
        The created marker ID
    """
    marker = await client.markers.create_async(
        dataset,
        MarkerCreate(
            message="Hotfix: Fix memory leak",
            type="deploy",
            url="https://github.com/myorg/myrepo/pull/1234",
            start_time=int(time.time()),
        ),
    )
    return marker.id


# end_example:create_marker_with_url


# start_example:list_markers
async def list_markers(client: HoneycombClient, dataset: str) -> list[Marker]:
    """List all markers in a dataset.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list markers from

    Returns:
        List of markers
    """
    markers = await client.markers.list_async(dataset)
    for marker in markers:
        print(f"{marker.type}: {marker.message}")
        if marker.url:
            print(f"  URL: {marker.url}")
    return markers


# end_example:list_markers


# start_example:update
async def update_marker(client: HoneycombClient, dataset: str, marker_id: str) -> Marker:
    """Update a marker's message.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the marker
        marker_id: ID of the marker to update

    Returns:
        The updated marker
    """
    # For markers, you typically need the start_time from the original
    # In practice, you'd retrieve this or keep it from creation
    marker = await client.markers.update_async(
        dataset,
        marker_id,
        MarkerCreate(
            message="Updated: Backend deploy v2.5.0 - success",
            type="deploy",
            start_time=int(time.time()),  # Note: should use original start_time
        ),
    )
    return marker


# end_example:update


# start_example:delete
async def delete_marker(client: HoneycombClient, dataset: str, marker_id: str) -> None:
    """Delete a marker.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the marker
        marker_id: ID of the marker to delete
    """
    await client.markers.delete_async(dataset, marker_id)


# end_example:delete


# start_example:list_sync
def list_markers_sync(client: HoneycombClient, dataset: str) -> list[Marker]:
    """List markers using sync client.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list markers from

    Returns:
        List of markers
    """
    markers = client.markers.list(dataset)
    for marker in markers:
        print(f"{marker.type}: {marker.message}")
    return markers


# end_example:list_sync


# TEST_ASSERTIONS
async def test_create_marker(client: HoneycombClient, dataset: str, marker_id: str) -> None:
    """Verify the example worked correctly."""
    # Markers don't have a get endpoint, so we verify by listing
    markers = await client.markers.list_async(dataset)
    marker_ids = [m.id for m in markers]
    assert marker_id in marker_ids


async def test_list_markers(markers: list[Marker]) -> None:
    """Verify list example worked correctly."""
    assert isinstance(markers, list)


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, marker_id: str) -> None:
    """Clean up resources created by example."""
    await delete_marker(client, dataset, marker_id)
