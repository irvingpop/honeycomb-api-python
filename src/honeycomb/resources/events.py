"""Events resource for Honeycomb API (data ingestion)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.events import BatchEvent, BatchEventResult
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class EventsResource(BaseResource):
    """Resource for sending events (data ingestion).

    Events are the core telemetry data sent to Honeycomb. This resource
    provides methods to send single events or batches of events.

    Note: Batch sending is highly preferred over single events for efficiency.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     # Send single event
        ...     await client.events.send(
        ...         dataset="my-dataset",
        ...         data={"endpoint": "/api/users", "duration_ms": 42}
        ...     )
        ...     # Send batch of events
        ...     results = await client.events.send_batch(
        ...         dataset="my-dataset",
        ...         events=[
        ...             BatchEvent(data={"endpoint": "/api/users", "duration_ms": 42}),
        ...             BatchEvent(data={"endpoint": "/api/posts", "duration_ms": 18}),
        ...         ]
        ...     )

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     client.events.send(dataset="my-dataset", data={"key": "value"})
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def send_async(
        self,
        dataset: str,
        data: dict[str, Any],
        timestamp: int | None = None,
        samplerate: int | None = None,
    ) -> None:
        """Send a single event (async).

        Note: For production use, prefer send_batch() for better efficiency.

        Args:
            dataset: Dataset slug.
            data: Event payload (key-value pairs).
            timestamp: Unix timestamp for the event (optional).
            samplerate: Sample rate (optional, defaults to 1).
        """
        path = f"/1/events/{dataset}"
        headers = {}
        if timestamp is not None:
            headers["X-Honeycomb-Event-Time"] = str(timestamp)
        if samplerate is not None:
            headers["X-Honeycomb-Samplerate"] = str(samplerate)

        # Single event endpoint returns empty 200, don't try to parse JSON
        await self._client.post_async(path, json=data, headers=headers)

    async def send_batch_async(
        self, dataset: str, events: list[BatchEvent]
    ) -> list[BatchEventResult]:
        """Send a batch of events (async).

        This is the preferred method for sending events to Honeycomb.

        Args:
            dataset: Dataset slug.
            events: List of BatchEvent objects.

        Returns:
            List of BatchEventResult objects indicating status for each event.
        """
        path = f"/1/batch/{dataset}"
        payload = [event.model_dump_for_api() for event in events]
        data = await self._post_async(path, json=payload)  # type: ignore[arg-type]

        # Parse results
        if isinstance(data, list):
            return self._parse_model_list(BatchEventResult, data)
        return []

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def send(
        self,
        dataset: str,
        data: dict[str, Any],
        timestamp: int | None = None,
        samplerate: int | None = None,
    ) -> None:
        """Send a single event.

        Note: For production use, prefer send_batch() for better efficiency.

        Args:
            dataset: Dataset slug.
            data: Event payload (key-value pairs).
            timestamp: Unix timestamp for the event (optional).
            samplerate: Sample rate (optional, defaults to 1).
        """
        if not self._client.is_sync:
            raise RuntimeError("Use send_async() for async mode, or pass sync=True to client")

        path = f"/1/events/{dataset}"
        headers = {}
        if timestamp is not None:
            headers["X-Honeycomb-Event-Time"] = str(timestamp)
        if samplerate is not None:
            headers["X-Honeycomb-Samplerate"] = str(samplerate)

        # Single event endpoint returns empty 200, don't try to parse JSON
        self._client.post_sync(path, json=data, headers=headers)

    def send_batch(self, dataset: str, events: list[BatchEvent]) -> list[BatchEventResult]:
        """Send a batch of events.

        This is the preferred method for sending events to Honeycomb.

        Args:
            dataset: Dataset slug.
            events: List of BatchEvent objects.

        Returns:
            List of BatchEventResult objects indicating status for each event.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use send_batch_async() for async mode, or pass sync=True to client")

        path = f"/1/batch/{dataset}"
        payload = [event.model_dump_for_api() for event in events]
        data = self._post_sync(path, json=payload)  # type: ignore[arg-type]

        # Parse results
        if isinstance(data, list):
            return self._parse_model_list(BatchEventResult, data)
        return []
