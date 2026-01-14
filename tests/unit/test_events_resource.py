"""Tests for EventsResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from honeycomb.models.events import BatchEvent

# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_send_batch_async():
    """Test sending a batch of events (async)."""
    respx.post("https://api.honeycomb.io/1/batch/test-dataset").mock(
        return_value=Response(200, json=[{"status": 202}, {"status": 202}])
    )

    async with HoneycombClient(api_key="test-key") as client:
        events = [
            BatchEvent(data={"message": "Event 1", "severity": "info"}),
            BatchEvent(data={"message": "Event 2", "severity": "warn"}),
        ]
        results = await client.events.send_batch_async(dataset="test-dataset", events=events)
        assert len(results) == 2


@pytest.mark.asyncio
@respx.mock
async def test_send_async():
    """Test sending a single event (async)."""
    respx.post("https://api.honeycomb.io/1/events/test-dataset").mock(return_value=Response(200))

    async with HoneycombClient(api_key="test-key") as client:
        event = {"message": "Test event", "severity": "info"}
        # Should not raise
        await client.events.send_async(dataset="test-dataset", data=event)


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_send_batch_sync():
    """Test sending a batch of events (sync)."""
    respx.post("https://api.honeycomb.io/1/batch/test-dataset").mock(
        return_value=Response(200, json=[{"status": 202}, {"status": 202}])
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        events = [
            BatchEvent(data={"message": "Event 1", "severity": "info"}),
            BatchEvent(data={"message": "Event 2", "severity": "warn"}),
        ]
        results = client.events.send_batch(dataset="test-dataset", events=events)
        assert len(results) == 2


@respx.mock
def test_send_sync():
    """Test sending a single event (sync)."""
    respx.post("https://api.honeycomb.io/1/events/test-dataset").mock(return_value=Response(200))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        event = {"message": "Test event", "severity": "info"}
        # Should not raise
        client.events.send(dataset="test-dataset", data=event)


# -------------------------------------------------------------------------
# Validation tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_send_batch_empty_returns_empty_list():
    """Test that sending empty batch returns empty list."""
    respx.post("https://api.honeycomb.io/1/batch/test-dataset").mock(
        return_value=Response(200, json={})  # Not a list response
    )

    async with HoneycombClient(api_key="test-key") as client:
        events = [BatchEvent(data={"message": "test"})]
        results = await client.events.send_batch_async(dataset="test-dataset", events=events)
        # When API returns non-list, we return empty list
        assert results == []


@pytest.mark.asyncio
@respx.mock
async def test_send_with_timestamp_async():
    """Test sending single event with timestamp parameter (async)."""
    respx.post("https://api.honeycomb.io/1/events/test-dataset").mock(return_value=Response(200))

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.events.send_async(
            dataset="test-dataset", data={"message": "Event with time"}, timestamp=1640995200
        )


@respx.mock
def test_send_with_timestamp_sync():
    """Test sending single event with timestamp parameter (sync)."""
    respx.post("https://api.honeycomb.io/1/events/test-dataset").mock(return_value=Response(200))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.events.send(
            dataset="test-dataset", data={"message": "Event with time"}, timestamp=1640995200
        )


@pytest.mark.asyncio
@respx.mock
async def test_send_with_samplerate_async():
    """Test sending single event with samplerate parameter (async)."""
    respx.post("https://api.honeycomb.io/1/events/test-dataset").mock(return_value=Response(200))

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.events.send_async(
            dataset="test-dataset", data={"message": "Sampled event"}, samplerate=10
        )


@respx.mock
def test_send_with_samplerate_sync():
    """Test sending single event with samplerate parameter (sync)."""
    respx.post("https://api.honeycomb.io/1/events/test-dataset").mock(return_value=Response(200))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.events.send(dataset="test-dataset", data={"message": "Sampled event"}, samplerate=10)


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use send_batch_async"):
        client.events.send_batch(dataset="test-dataset", events=[{"msg": "test"}])

    with pytest.raises(RuntimeError, match="Use send_async"):
        client.events.send(dataset="test-dataset", data={"msg": "test"})
