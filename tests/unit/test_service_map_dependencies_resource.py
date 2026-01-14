"""Tests for ServiceMapDependenciesResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from honeycomb.models.service_map_dependencies import ServiceMapDependencyRequestCreate

# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_create_request_async():
    """Test creating a service map dependencies request (async)."""
    respx.post("https://api.honeycomb.io/1/maps/dependencies/requests").mock(
        return_value=Response(201, json={"request_id": "req-123", "status": "pending"})
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = ServiceMapDependencyRequestCreate(time_range=7200)
        result = await client.service_map_dependencies.create_async(request=request)
        assert result.request_id == "req-123"
        assert result.status.value == "pending"


@pytest.mark.asyncio
@respx.mock
async def test_get_result_async():
    """Test getting result of a service map request (async)."""
    respx.get("https://api.honeycomb.io/1/maps/dependencies/requests/req-123").mock(
        return_value=Response(
            200,
            json={
                "request_id": "req-123",
                "status": "ready",
                "dependencies": [
                    {
                        "parent_node": {"name": "api-service", "type": "service"},
                        "child_node": {"name": "db-service", "type": "service"},
                        "call_count": 100,
                    }
                ],
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        result = await client.service_map_dependencies.get_result_async(request_id="req-123")
        assert result.request_id == "req-123"
        assert result.status.value == "ready"
        assert len(result.dependencies) == 1


@pytest.mark.asyncio
@respx.mock
async def test_get_with_polling_async():
    """Test get with automatic polling until ready (async)."""
    # First poll: pending
    respx.post("https://api.honeycomb.io/1/maps/dependencies/requests").mock(
        return_value=Response(201, json={"request_id": "req-poll", "status": "pending"})
    )

    # Second poll: ready with results
    respx.get("https://api.honeycomb.io/1/maps/dependencies/requests/req-poll").mock(
        return_value=Response(
            200,
            json={
                "request_id": "req-poll",
                "status": "ready",
                "dependencies": [],
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = ServiceMapDependencyRequestCreate(time_range=3600)
        result = await client.service_map_dependencies.get_async(
            request=request, poll_interval=0.01, timeout=5.0
        )
        assert result.status.value == "ready"


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_create_request_sync():
    """Test creating a service map dependencies request (sync)."""
    respx.post("https://api.honeycomb.io/1/maps/dependencies/requests").mock(
        return_value=Response(201, json={"request_id": "req-456", "status": "pending"})
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = ServiceMapDependencyRequestCreate(time_range=7200)
        result = client.service_map_dependencies.create(request=request)
        assert result.request_id == "req-456"


@respx.mock
def test_get_result_sync():
    """Test getting result of a service map request (sync)."""
    respx.get("https://api.honeycomb.io/1/maps/dependencies/requests/req-123").mock(
        return_value=Response(
            200,
            json={
                "request_id": "req-123",
                "status": "ready",
                "dependencies": [],
            },
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        result = client.service_map_dependencies.get_result(request_id="req-123")
        assert result.request_id == "req-123"
        assert result.status.value == "ready"


@respx.mock
def test_get_with_polling_sync():
    """Test get with automatic polling until ready (sync)."""
    respx.post("https://api.honeycomb.io/1/maps/dependencies/requests").mock(
        return_value=Response(201, json={"request_id": "req-sync", "status": "pending"})
    )

    respx.get("https://api.honeycomb.io/1/maps/dependencies/requests/req-sync").mock(
        return_value=Response(
            200,
            json={
                "request_id": "req-sync",
                "status": "ready",
                "dependencies": [],
            },
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = ServiceMapDependencyRequestCreate(time_range=3600)
        result = client.service_map_dependencies.get(
            request=request, poll_interval=0.01, timeout=5.0
        )
        assert result.status.value == "ready"


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = ServiceMapDependencyRequestCreate(time_range=3600)
        client.service_map_dependencies.create(request=request)

    with pytest.raises(RuntimeError, match="Use get_result_async"):
        client.service_map_dependencies.get_result(request_id="req-123")

    with pytest.raises(RuntimeError, match="Use get_async"):
        request = ServiceMapDependencyRequestCreate(time_range=3600)
        client.service_map_dependencies.get(request=request)
