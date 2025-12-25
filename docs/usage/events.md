# Working with Events

Events are the core telemetry data sent to Honeycomb. The Events API allows you to send data programmatically for ingestion.

!!! note
    For production workloads, batch sending is highly preferred over single events for better efficiency and throughput.

## Basic Event Operations

### Send a Single Event

For testing or low-volume use cases:

```python
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    await client.events.send_async(
        dataset="my-dataset",
        data={
            "endpoint": "/api/users",
            "method": "GET",
            "duration_ms": 42,
            "status_code": 200,
            "user_id": "user-123",
        }
    )
```

### Send Event with Timestamp

Specify when the event occurred:

```python
import time

await client.events.send_async(
    dataset="my-dataset",
    data={"field": "value"},
    timestamp=int(time.time()),  # Unix timestamp
)
```

### Send Event with Sample Rate

Control sampling for high-volume data:

```python
await client.events.send_async(
    dataset="my-dataset",
    data={"field": "value"},
    samplerate=10,  # 1 in 10 events
)
```

## Batch Event Sending

**Recommended for production**: Send multiple events in a single request:

### Basic Batch

```python
from honeycomb import BatchEvent

events = [
    BatchEvent(data={
        "endpoint": "/api/users",
        "duration_ms": 42,
        "status_code": 200
    }),
    BatchEvent(data={
        "endpoint": "/api/posts",
        "duration_ms": 18,
        "status_code": 200
    }),
    BatchEvent(data={
        "endpoint": "/api/comments",
        "duration_ms": 35,
        "status_code": 404
    }),
]

results = await client.events.send_batch_async("my-dataset", events)

# Check results
for i, result in enumerate(results):
    if result.status != 202:
        print(f"Event {i} failed: {result.error}")
```

### Batch with Timestamps and Sampling

```python
import time
from datetime import datetime, timedelta

now = datetime.now()

events = [
    BatchEvent(
        data={"event": "request", "duration_ms": 42},
        time=(now - timedelta(minutes=1)).isoformat() + "Z",
        samplerate=1
    ),
    BatchEvent(
        data={"event": "request", "duration_ms": 38},
        time=(now - timedelta(minutes=2)).isoformat() + "Z",
        samplerate=1
    ),
]

results = await client.events.send_batch_async("my-dataset", events)
```

## Handling Batch Results

Each event in a batch gets an individual result:

```python
results = await client.events.send_batch_async("my-dataset", events)

successful = [r for r in results if r.status == 202]
failed = [r for r in results if r.status != 202]

print(f"✓ {len(successful)} events accepted")
print(f"✗ {len(failed)} events failed")

for result in failed:
    print(f"  Error: {result.error}")
```

## Sync Usage

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # Send single event
    client.events.send(
        dataset="my-dataset",
        data={"field": "value"}
    )

    # Send batch
    events = [
        BatchEvent(data={"event": 1}),
        BatchEvent(data={"event": 2}),
    ]
    results = client.events.send_batch("my-dataset", events)
```

## Data Ingestion Patterns

### Structured Logging Integration

```python
import logging
import json
from honeycomb import HoneycombClient, BatchEvent

class HoneycombHandler(logging.Handler):
    def __init__(self, client: HoneycombClient, dataset: str):
        super().__init__()
        self.client = client
        self.dataset = dataset
        self.buffer = []
        self.buffer_size = 100

    def emit(self, record):
        event = BatchEvent(data={
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        })
        self.buffer.append(event)

        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        if self.buffer:
            # In real implementation, make this async-safe
            results = self.client.events.send_batch(
                self.dataset,
                self.buffer
            )
            self.buffer = []
```

### Application Instrumentation

```python
from honeycomb import BatchEvent
import time

class RequestTracer:
    def __init__(self, client, dataset):
        self.client = client
        self.dataset = dataset

    async def trace_request(self, handler_func, request):
        start = time.time()

        try:
            response = await handler_func(request)
            status = response.status_code
            error = None
        except Exception as e:
            status = 500
            error = str(e)
            raise
        finally:
            duration_ms = (time.time() - start) * 1000

            await self.client.events.send_async(
                dataset=self.dataset,
                data={
                    "endpoint": request.path,
                    "method": request.method,
                    "status_code": status,
                    "duration_ms": duration_ms,
                    "error": error,
                    "user_id": request.user.id if request.user else None,
                }
            )
```

### Periodic Batch Flush

```python
import asyncio
from honeycomb import HoneycombClient, BatchEvent

class EventBuffer:
    def __init__(self, client: HoneycombClient, dataset: str, flush_interval: int = 5):
        self.client = client
        self.dataset = dataset
        self.buffer = []
        self.flush_interval = flush_interval
        self.lock = asyncio.Lock()

    async def add_event(self, data: dict):
        async with self.lock:
            self.buffer.append(BatchEvent(data=data))

    async def auto_flush(self):
        while True:
            await asyncio.sleep(self.flush_interval)
            await self.flush()

    async def flush(self):
        async with self.lock:
            if self.buffer:
                await self.client.events.send_batch_async(
                    self.dataset,
                    self.buffer
                )
                self.buffer = []

# Usage
buffer = EventBuffer(client, "my-dataset", flush_interval=5)

# Start background flusher
asyncio.create_task(buffer.auto_flush())

# Add events from application
await buffer.add_event({"request": "data"})
```

## Event Size Limits

- **Single event body**: 1MB maximum (raw or compressed)
- **Maximum columns per event**: 2000 distinct fields
- **Batch size**: Limited by total request size (1MB compressed)

## Best Practices

1. **Use Batch Sending**: Always prefer `send_batch()` over `send()` for production
2. **Buffer Events**: Collect events and send in batches of 50-100
3. **Handle Failures**: Check batch results and retry failed events
4. **Sampling Strategy**: Use sampling for high-volume, low-value events
5. **Structured Data**: Send consistent field names across events
6. **Timestamps**: Include timestamps for historical data or delayed ingestion
7. **Compression**: For large batches, consider compressing before sending (done by httpx)
8. **Error Handling**: Implement exponential backoff for network failures

## Example: Production-Ready Event Sender

```python
from honeycomb import HoneycombClient, BatchEvent
import asyncio
from typing import Dict, List
import logging

class ProductionEventSender:
    def __init__(
        self,
        client: HoneycombClient,
        dataset: str,
        batch_size: int = 100,
        flush_interval: float = 5.0
    ):
        self.client = client
        self.dataset = dataset
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer: List[BatchEvent] = []
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)

    async def send(self, data: Dict):
        """Add event to buffer and flush if needed."""
        async with self.lock:
            self.buffer.append(BatchEvent(data=data))

            if len(self.buffer) >= self.batch_size:
                await self._flush_unsafe()

    async def start_auto_flush(self):
        """Background task to periodically flush buffer."""
        while True:
            await asyncio.sleep(self.flush_interval)
            async with self.lock:
                if self.buffer:
                    await self._flush_unsafe()

    async def _flush_unsafe(self):
        """Flush buffer (must be called with lock held)."""
        if not self.buffer:
            return

        events = self.buffer[:]
        self.buffer = []

        try:
            results = await self.client.events.send_batch_async(
                self.dataset,
                events
            )

            failed = [r for r in results if r.status != 202]
            if failed:
                self.logger.warning(f"{len(failed)} events failed to send")

        except Exception as e:
            self.logger.error(f"Failed to send batch: {e}")
            # Re-add to buffer for retry (implement max retries in production)
            self.buffer.extend(events)

    async def shutdown(self):
        """Flush remaining events on shutdown."""
        async with self.lock:
            await self._flush_unsafe()
```
