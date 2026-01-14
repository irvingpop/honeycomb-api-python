"""Tests for TriggersResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from tests.factories import (
    TriggerCreateFactory,
    TriggerFactory,
    mock_list_response,
    mock_response,
)

# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_triggers_async():
    """Test listing triggers (async)."""
    respx.get("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(200, json=mock_list_response(TriggerFactory, count=3))
    )

    async with HoneycombClient(api_key="test-key") as client:
        triggers = await client.triggers.list_async(dataset="test-dataset")
        assert len(triggers) == 3


@pytest.mark.asyncio
@respx.mock
async def test_list_triggers_empty_async():
    """Test listing triggers returns empty list (async)."""
    respx.get("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(200, json=[])
    )

    async with HoneycombClient(api_key="test-key") as client:
        triggers = await client.triggers.list_async(dataset="test-dataset")
        assert len(triggers) == 0


@pytest.mark.asyncio
@respx.mock
async def test_get_trigger_async():
    """Test getting a specific trigger (async)."""
    respx.get("https://api.honeycomb.io/1/triggers/test-dataset/trigger-123").mock(
        return_value=Response(
            200, json=mock_response(TriggerFactory, id="trigger-123", name="Error Rate Alert")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        trigger = await client.triggers.get_async(dataset="test-dataset", trigger_id="trigger-123")
        assert trigger.id == "trigger-123"
        assert trigger.name == "Error Rate Alert"


@pytest.mark.asyncio
@respx.mock
async def test_create_trigger_async():
    """Test creating a trigger (async)."""
    respx.post("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(
            201, json=mock_response(TriggerFactory, id="new-trigger", name="New Trigger")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = TriggerCreateFactory.build(name="New Trigger")
        trigger = await client.triggers.create_async(dataset="test-dataset", trigger=request)
        assert trigger.id == "new-trigger"
        assert trigger.name == "New Trigger"


@pytest.mark.asyncio
@respx.mock
async def test_update_trigger_async():
    """Test updating a trigger (async)."""
    respx.put("https://api.honeycomb.io/1/triggers/test-dataset/trigger-123").mock(
        return_value=Response(
            200, json=mock_response(TriggerFactory, id="trigger-123", name="Updated Trigger")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = TriggerCreateFactory.build(name="Updated Trigger")
        trigger = await client.triggers.update_async(
            dataset="test-dataset", trigger_id="trigger-123", trigger=request
        )
        assert trigger.id == "trigger-123"
        assert trigger.name == "Updated Trigger"


@pytest.mark.asyncio
@respx.mock
async def test_delete_trigger_async():
    """Test deleting a trigger (async)."""
    respx.delete("https://api.honeycomb.io/1/triggers/test-dataset/trigger-123").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.triggers.delete_async(dataset="test-dataset", trigger_id="trigger-123")


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_list_triggers_sync():
    """Test listing triggers (sync)."""
    respx.get("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(200, json=mock_list_response(TriggerFactory, count=2))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        triggers = client.triggers.list(dataset="test-dataset")
        assert len(triggers) == 2


@respx.mock
def test_list_triggers_empty_sync():
    """Test listing triggers returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(200, json=[])
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        triggers = client.triggers.list(dataset="test-dataset")
        assert len(triggers) == 0


@respx.mock
def test_get_trigger_sync():
    """Test getting a specific trigger (sync)."""
    respx.get("https://api.honeycomb.io/1/triggers/test-dataset/trigger-123").mock(
        return_value=Response(200, json=mock_response(TriggerFactory, id="trigger-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        trigger = client.triggers.get(dataset="test-dataset", trigger_id="trigger-123")
        assert trigger.id == "trigger-123"


@respx.mock
def test_create_trigger_sync():
    """Test creating a trigger (sync)."""
    respx.post("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(201, json=mock_response(TriggerFactory, id="new-trigger"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = TriggerCreateFactory.build(name="New Trigger")
        trigger = client.triggers.create(dataset="test-dataset", trigger=request)
        assert trigger.id == "new-trigger"


@respx.mock
def test_update_trigger_sync():
    """Test updating a trigger (sync)."""
    respx.put("https://api.honeycomb.io/1/triggers/test-dataset/trigger-123").mock(
        return_value=Response(200, json=mock_response(TriggerFactory, id="trigger-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = TriggerCreateFactory.build(name="Updated")
        trigger = client.triggers.update(
            dataset="test-dataset", trigger_id="trigger-123", trigger=request
        )
        assert trigger.id == "trigger-123"


@respx.mock
def test_delete_trigger_sync():
    """Test deleting a trigger (sync)."""
    respx.delete("https://api.honeycomb.io/1/triggers/test-dataset/trigger-123").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.triggers.delete(dataset="test-dataset", trigger_id="trigger-123")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.triggers.list(dataset="test-dataset")

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.triggers.get(dataset="test-dataset", trigger_id="trigger-123")

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = TriggerCreateFactory.build()
        client.triggers.create(dataset="test-dataset", trigger=request)

    with pytest.raises(RuntimeError, match="Use update_async"):
        request = TriggerCreateFactory.build()
        client.triggers.update(dataset="test-dataset", trigger_id="trigger-123", trigger=request)

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.triggers.delete(dataset="test-dataset", trigger_id="trigger-123")


# -------------------------------------------------------------------------
# Bundle tests
# -------------------------------------------------------------------------


@respx.mock
def test_create_from_bundle_sync():
    """Test creating trigger from bundle (sync)."""
    from honeycomb import TriggerBuilder

    respx.post("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(201, json=mock_response(TriggerFactory, id="bundle-trigger"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        bundle = (
            TriggerBuilder("High Error Rate")
            .dataset("test-dataset")
            .last_1_hour()
            .count()
            .threshold_gt(100)
            .build()
        )
        trigger = client.triggers.create_from_bundle(bundle)
        assert trigger.id == "bundle-trigger"
