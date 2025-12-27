"""Service map dependency examples.

These examples demonstrate querying service dependencies from trace data.
Service maps show how services communicate in your distributed system.
"""

from __future__ import annotations

import asyncio

from honeycomb import (
    HoneycombClient,
    ServiceMapDependencyRequestCreate,
    ServiceMapDependencyResult,
)


# start_example:create_request
async def create_service_map_request(client: HoneycombClient) -> str:
    """Create a service map dependency request.

    Args:
        client: Authenticated HoneycombClient

    Returns:
        The request ID for polling

    Note: Service map requires trace data to exist in your environment.
    """
    request = await client.service_map_dependencies.create_async(
        ServiceMapDependencyRequestCreate(
            time_range=3600,  # Last 1 hour
        ),
        limit=1000,
    )
    return request.request_id


# end_example:create_request


# start_example:poll_result
async def poll_service_map_result(
    client: HoneycombClient, request_id: str
) -> ServiceMapDependencyResult:
    """Poll for service map result until ready.

    Args:
        client: Authenticated HoneycombClient
        request_id: Request ID from create_service_map_request

    Returns:
        ServiceMapDependencyResult when ready

    Raises:
        TimeoutError: If result not ready within 30 seconds
    """
    for _ in range(30):  # Poll for up to 30 seconds
        result = await client.service_map_dependencies.get_result_async(request_id)

        if result.status.value == "ready":
            print(f"Found {len(result.dependencies or [])} service dependencies")
            return result

        if result.status.value == "error":
            raise RuntimeError(f"Service map request failed: {result.status}")

        await asyncio.sleep(1)

    raise TimeoutError("Service map request did not complete within 30 seconds")


# end_example:poll_result


# start_example:create_and_poll
async def get_service_map(client: HoneycombClient) -> ServiceMapDependencyResult:
    """Create and poll for service map in one step (convenience method).

    Args:
        client: Authenticated HoneycombClient

    Returns:
        ServiceMapDependencyResult with all dependencies

    Note: This is equivalent to create_request + poll_result but in one call.
    """
    result = await client.service_map_dependencies.get_async(
        ServiceMapDependencyRequestCreate(
            time_range=3600,  # Last 1 hour
        ),
        limit=1000,
        poll_interval=1.0,
        timeout=30.0,
    )

    if result.dependencies:
        print(f"Found {len(result.dependencies)} service dependencies")
        for dep in result.dependencies[:5]:  # Show first 5
            print(f"  {dep.parent_name} -> {dep.child_name}: {dep.request_count} requests")

    return result


# end_example:create_and_poll


# TEST_ASSERTIONS
async def test_create_request(request_id: str) -> None:
    """Verify create_request worked."""
    assert request_id is not None
    assert isinstance(request_id, str)


async def test_poll_result(result: ServiceMapDependencyResult) -> None:
    """Verify poll_result worked."""
    assert result is not None
    assert result.status.value == "ready"
    # Dependencies may be None or empty list if no trace data exists
    assert result.dependencies is not None or result.status.value == "ready"


async def test_get_service_map(result: ServiceMapDependencyResult) -> None:
    """Verify get_service_map worked."""
    assert result is not None
    assert result.status.value == "ready"


# NOTE: Service map dependencies are read-only queries - no cleanup needed.
# The request itself is ephemeral and doesn't persist.
