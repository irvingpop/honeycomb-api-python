"""Tests for MarkersResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from tests.factories import (
    MarkerCreateFactory,
    MarkerFactory,
    MarkerSettingCreateFactory,
    MarkerSettingFactory,
    mock_list_response,
    mock_response,
)

# -------------------------------------------------------------------------
# Async resource tests - Markers
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_markers_async():
    """Test listing markers (async)."""
    respx.get("https://api.honeycomb.io/1/markers/test-dataset").mock(
        return_value=Response(200, json=mock_list_response(MarkerFactory, count=3))
    )

    async with HoneycombClient(api_key="test-key") as client:
        markers = await client.markers.list_async(dataset="test-dataset")
        assert len(markers) == 3


@pytest.mark.asyncio
@respx.mock
async def test_list_markers_empty_async():
    """Test listing markers returns empty list (async)."""
    respx.get("https://api.honeycomb.io/1/markers/test-dataset").mock(
        return_value=Response(200, json=[])
    )

    async with HoneycombClient(api_key="test-key") as client:
        markers = await client.markers.list_async(dataset="test-dataset")
        assert len(markers) == 0


@pytest.mark.asyncio
@respx.mock
async def test_create_marker_async():
    """Test creating a marker (async)."""
    respx.post("https://api.honeycomb.io/1/markers/test-dataset").mock(
        return_value=Response(
            201,
            json=mock_response(MarkerFactory, id="new-marker", message="Deployment #123"),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = MarkerCreateFactory.build(message="Deployment #123", type="deploy")
        marker = await client.markers.create_async(dataset="test-dataset", marker=request)
        assert marker.id == "new-marker"
        assert marker.message == "Deployment #123"


@pytest.mark.asyncio
@respx.mock
async def test_create_environment_wide_marker_async():
    """Test creating environment-wide marker (async)."""
    respx.post("https://api.honeycomb.io/1/markers/__all__").mock(
        return_value=Response(
            201, json=mock_response(MarkerFactory, id="env-marker", message="System maintenance")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = MarkerCreateFactory.build(message="System maintenance")
        marker = await client.markers.create_async(dataset="__all__", marker=request)
        assert marker.id == "env-marker"


@pytest.mark.asyncio
@respx.mock
async def test_update_marker_async():
    """Test updating a marker (async)."""
    respx.put("https://api.honeycomb.io/1/markers/test-dataset/marker-123").mock(
        return_value=Response(
            200,
            json=mock_response(MarkerFactory, id="marker-123", message="Updated deployment"),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = MarkerCreateFactory.build(message="Updated deployment")
        marker = await client.markers.update_async(
            dataset="test-dataset", marker_id="marker-123", marker=request
        )
        assert marker.id == "marker-123"
        assert marker.message == "Updated deployment"


@pytest.mark.asyncio
@respx.mock
async def test_delete_marker_async():
    """Test deleting a marker (async)."""
    respx.delete("https://api.honeycomb.io/1/markers/test-dataset/marker-123").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.markers.delete_async(dataset="test-dataset", marker_id="marker-123")


# -------------------------------------------------------------------------
# Async resource tests - Marker Settings
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_marker_settings_async():
    """Test listing marker settings (async)."""
    respx.get("https://api.honeycomb.io/1/marker_settings/test-dataset").mock(
        return_value=Response(200, json=mock_list_response(MarkerSettingFactory, count=2))
    )

    async with HoneycombClient(api_key="test-key") as client:
        settings = await client.markers.list_settings_async(dataset="test-dataset")
        assert len(settings) == 2


@pytest.mark.asyncio
@respx.mock
async def test_get_marker_setting_async():
    """Test getting a specific marker setting (async)."""
    respx.get("https://api.honeycomb.io/1/marker_settings/test-dataset/setting-123").mock(
        return_value=Response(
            200, json=mock_response(MarkerSettingFactory, id="setting-123", type="deploy")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        setting = await client.markers.get_setting_async(
            dataset="test-dataset", setting_id="setting-123"
        )
        assert setting.id == "setting-123"
        assert setting.type == "deploy"


@pytest.mark.asyncio
@respx.mock
async def test_create_marker_setting_async():
    """Test creating a marker setting (async)."""
    respx.post("https://api.honeycomb.io/1/marker_settings/test-dataset").mock(
        return_value=Response(
            201, json=mock_response(MarkerSettingFactory, id="new-setting", type="release")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = MarkerSettingCreateFactory.build(type="release", color="blue")
        setting = await client.markers.create_setting_async(dataset="test-dataset", setting=request)
        assert setting.id == "new-setting"
        assert setting.type == "release"


@pytest.mark.asyncio
@respx.mock
async def test_update_marker_setting_async():
    """Test updating a marker setting (async)."""
    respx.put("https://api.honeycomb.io/1/marker_settings/test-dataset/setting-123").mock(
        return_value=Response(
            200,
            json=mock_response(MarkerSettingFactory, id="setting-123", color="red"),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = MarkerSettingCreateFactory.build(color="red")
        setting = await client.markers.update_setting_async(
            dataset="test-dataset", setting_id="setting-123", setting=request
        )
        assert setting.id == "setting-123"
        assert setting.color == "red"


@pytest.mark.asyncio
@respx.mock
async def test_delete_marker_setting_async():
    """Test deleting a marker setting (async)."""
    respx.delete("https://api.honeycomb.io/1/marker_settings/test-dataset/setting-123").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.markers.delete_setting_async(dataset="test-dataset", setting_id="setting-123")


# -------------------------------------------------------------------------
# Sync resource tests - Markers
# -------------------------------------------------------------------------


@respx.mock
def test_list_markers_sync():
    """Test listing markers (sync)."""
    respx.get("https://api.honeycomb.io/1/markers/test-dataset").mock(
        return_value=Response(200, json=mock_list_response(MarkerFactory, count=2))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        markers = client.markers.list(dataset="test-dataset")
        assert len(markers) == 2


@respx.mock
def test_list_markers_empty_sync():
    """Test listing markers returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/1/markers/test-dataset").mock(
        return_value=Response(200, json=[])
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        markers = client.markers.list(dataset="test-dataset")
        assert len(markers) == 0


@respx.mock
def test_create_marker_sync():
    """Test creating a marker (sync)."""
    respx.post("https://api.honeycomb.io/1/markers/test-dataset").mock(
        return_value=Response(201, json=mock_response(MarkerFactory, id="new-marker"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = MarkerCreateFactory.build(message="Deploy")
        marker = client.markers.create(dataset="test-dataset", marker=request)
        assert marker.id == "new-marker"


@respx.mock
def test_update_marker_sync():
    """Test updating a marker (sync)."""
    respx.put("https://api.honeycomb.io/1/markers/test-dataset/marker-123").mock(
        return_value=Response(200, json=mock_response(MarkerFactory, id="marker-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = MarkerCreateFactory.build(message="Updated")
        marker = client.markers.update(
            dataset="test-dataset", marker_id="marker-123", marker=request
        )
        assert marker.id == "marker-123"


@respx.mock
def test_delete_marker_sync():
    """Test deleting a marker (sync)."""
    respx.delete("https://api.honeycomb.io/1/markers/test-dataset/marker-123").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.markers.delete(dataset="test-dataset", marker_id="marker-123")


# -------------------------------------------------------------------------
# Sync resource tests - Marker Settings
# -------------------------------------------------------------------------


@respx.mock
def test_list_marker_settings_sync():
    """Test listing marker settings (sync)."""
    respx.get("https://api.honeycomb.io/1/marker_settings/test-dataset").mock(
        return_value=Response(200, json=mock_list_response(MarkerSettingFactory, count=1))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        settings = client.markers.list_settings(dataset="test-dataset")
        assert len(settings) == 1


@respx.mock
def test_get_marker_setting_sync():
    """Test getting a specific marker setting (sync)."""
    respx.get("https://api.honeycomb.io/1/marker_settings/test-dataset/setting-123").mock(
        return_value=Response(200, json=mock_response(MarkerSettingFactory, id="setting-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        setting = client.markers.get_setting(dataset="test-dataset", setting_id="setting-123")
        assert setting.id == "setting-123"


@respx.mock
def test_create_marker_setting_sync():
    """Test creating a marker setting (sync)."""
    respx.post("https://api.honeycomb.io/1/marker_settings/test-dataset").mock(
        return_value=Response(201, json=mock_response(MarkerSettingFactory, id="new-setting"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = MarkerSettingCreateFactory.build(type="deploy")
        setting = client.markers.create_setting(dataset="test-dataset", setting=request)
        assert setting.id == "new-setting"


@respx.mock
def test_update_marker_setting_sync():
    """Test updating a marker setting (sync)."""
    respx.put("https://api.honeycomb.io/1/marker_settings/test-dataset/setting-123").mock(
        return_value=Response(200, json=mock_response(MarkerSettingFactory, id="setting-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = MarkerSettingCreateFactory.build(color="green")
        setting = client.markers.update_setting(
            dataset="test-dataset", setting_id="setting-123", setting=request
        )
        assert setting.id == "setting-123"


@respx.mock
def test_delete_marker_setting_sync():
    """Test deleting a marker setting (sync)."""
    respx.delete("https://api.honeycomb.io/1/marker_settings/test-dataset/setting-123").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.markers.delete_setting(dataset="test-dataset", setting_id="setting-123")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    # Marker methods
    with pytest.raises(RuntimeError, match="Use list_async"):
        client.markers.list(dataset="test-dataset")

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = MarkerCreateFactory.build()
        client.markers.create(dataset="test-dataset", marker=request)

    with pytest.raises(RuntimeError, match="Use update_async"):
        request = MarkerCreateFactory.build()
        client.markers.update(dataset="test-dataset", marker_id="marker-123", marker=request)

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.markers.delete(dataset="test-dataset", marker_id="marker-123")

    # Marker settings methods
    with pytest.raises(RuntimeError, match="Use list_settings_async"):
        client.markers.list_settings(dataset="test-dataset")

    with pytest.raises(RuntimeError, match="Use get_setting_async"):
        client.markers.get_setting(dataset="test-dataset", setting_id="setting-123")

    with pytest.raises(RuntimeError, match="Use create_setting_async"):
        request = MarkerSettingCreateFactory.build()
        client.markers.create_setting(dataset="test-dataset", setting=request)

    with pytest.raises(RuntimeError, match="Use update_setting_async"):
        request = MarkerSettingCreateFactory.build()
        client.markers.update_setting(
            dataset="test-dataset", setting_id="setting-123", setting=request
        )

    with pytest.raises(RuntimeError, match="Use delete_setting_async"):
        client.markers.delete_setting(dataset="test-dataset", setting_id="setting-123")
