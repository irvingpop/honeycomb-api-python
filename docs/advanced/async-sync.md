# Async vs Sync

The Honeycomb API client is designed with an **async-first** architecture but provides full synchronous support for compatibility.

## When to Use Async

**Use async when:**

- Building web applications (FastAPI, aiohttp, etc.)
- Handling concurrent operations
- Maximum performance is needed
- You're already using async/await in your codebase

**Benefits:**
- Better performance through concurrency
- Non-blocking I/O
- Can handle multiple operations simultaneously

## When to Use Sync

**Use sync when:**

- Writing simple scripts or CLI tools
- Working in environments without async support
- Integrating with sync-only codebases
- Simplicity is more important than performance

**Benefits:**
- Simpler code (no async/await)
- Works in any Python environment
- Easier to debug for beginners

## Async Examples

### Basic Async Usage

```python
import asyncio
from honeycomb import HoneycombClient

async def main():
    async with HoneycombClient(api_key="...") as client:
        datasets = await client.datasets.list_async()
        for ds in datasets:
            print(ds.name)

asyncio.run(main())
```

### Concurrent Operations

```python
import asyncio
from honeycomb import HoneycombClient

async def main():
    async with HoneycombClient(api_key="...") as client:
        # Run multiple operations concurrently
        datasets_task = client.datasets.list_async()
        triggers_task = client.triggers.list_async("my-dataset")
        slos_task = client.slos.list_async("my-dataset")

        # Wait for all to complete
        datasets, triggers, slos = await asyncio.gather(
            datasets_task,
            triggers_task,
            slos_task,
        )

        print(f"Datasets: {len(datasets)}")
        print(f"Triggers: {len(triggers)}")
        print(f"SLOs: {len(slos)}")

asyncio.run(main())
```

### Integration with FastAPI

```python
from fastapi import FastAPI, Depends
from honeycomb import HoneycombClient

app = FastAPI()

async def get_client():
    """Dependency to provide Honeycomb client."""
    async with HoneycombClient(api_key="...") as client:
        yield client

@app.get("/datasets")
async def list_datasets(client: HoneycombClient = Depends(get_client)):
    datasets = await client.datasets.list_async()
    return [{"name": ds.name, "slug": ds.slug} for ds in datasets]

@app.get("/triggers/{dataset}")
async def list_triggers(dataset: str, client: HoneycombClient = Depends(get_client)):
    triggers = await client.triggers.list_async(dataset)
    return [{"id": t.id, "name": t.name} for t in triggers]
```

## Sync Examples

### Basic Sync Usage

```python
from honeycomb import HoneycombClient

# Enable sync mode
with HoneycombClient(api_key="...", sync=True) as client:
    datasets = client.datasets.list()
    for ds in datasets:
        print(ds.name)
```

### CLI Tool Example

```python
#!/usr/bin/env python3
"""CLI tool to list Honeycomb datasets."""

import argparse
import os
from honeycomb import HoneycombClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=os.environ.get("HONEYCOMB_API_KEY"))
    args = parser.parse_args()

    with HoneycombClient(api_key=args.api_key, sync=True) as client:
        datasets = client.datasets.list()

        print("Datasets:")
        for ds in datasets:
            print(f"  - {ds.name} ({ds.slug})")
            print(f"    Columns: {ds.regular_columns_count}")

if __name__ == "__main__":
    main()
```

### Sequential Operations

```python
from honeycomb import HoneycombClient, TriggerCreate, TriggerThreshold, TriggerThresholdOp

with HoneycombClient(api_key="...", sync=True) as client:
    # List all datasets
    datasets = client.datasets.list()

    # Create a trigger for each dataset
    for dataset in datasets:
        trigger = client.triggers.create(
            dataset.slug,
            TriggerCreate(
                name=f"Errors in {dataset.name}",
                threshold=TriggerThreshold(
                    op=TriggerThresholdOp.GREATER_THAN,
                    value=10,
                ),
                frequency=300,
            )
        )
        print(f"Created trigger {trigger.id} for {dataset.name}")
```

## Mixing Async and Sync

!!! warning "Choose One Mode"
    A single client instance is either async OR sync - you can't mix them:

```python
# ✗ WRONG - Don't do this
async def wrong_usage():
    client = HoneycombClient(api_key="...")
    await client.datasets.list_async()  # Won't work without async context
    client.datasets.list()               # Will fail - not in sync mode

# ✓ CORRECT - Choose one mode
async def correct_async():
    async with HoneycombClient(api_key="...") as client:
        await client.datasets.list_async()

# ✓ CORRECT - Or use sync mode
def correct_sync():
    with HoneycombClient(api_key="...", sync=True) as client:
        client.datasets.list()
```

## Context Managers

### Async Context Manager

```python
# Recommended: async context manager
async with HoneycombClient(api_key="...") as client:
    datasets = await client.datasets.list_async()
# Automatically closes connections

# Manual cleanup (not recommended)
client = HoneycombClient(api_key="...")
try:
    datasets = await client.datasets.list_async()
finally:
    await client.aclose()
```

### Sync Context Manager

```python
# Recommended: sync context manager
with HoneycombClient(api_key="...", sync=True) as client:
    datasets = client.datasets.list()
# Automatically closes connections

# Manual cleanup (not recommended)
client = HoneycombClient(api_key="...", sync=True)
try:
    datasets = client.datasets.list()
finally:
    client.close()
```

## Performance Comparison

### Async - Concurrent Operations

```python
import asyncio
import time

async def async_example():
    async with HoneycombClient(api_key="...") as client:
        start = time.time()

        # Run 10 operations concurrently
        tasks = [
            client.datasets.get_async(f"dataset-{i}")
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.time() - start
        print(f"Async: {elapsed:.2f}s")  # ~1-2 seconds

asyncio.run(async_example())
```

### Sync - Sequential Operations

```python
import time

def sync_example():
    with HoneycombClient(api_key="...", sync=True) as client:
        start = time.time()

        # Run 10 operations sequentially
        results = []
        for i in range(10):
            try:
                result = client.datasets.get(f"dataset-{i}")
                results.append(result)
            except Exception as e:
                results.append(e)

        elapsed = time.time() - start
        print(f"Sync: {elapsed:.2f}s")  # ~10-20 seconds

sync_example()
```

## Choosing the Right Mode

| Criteria | Use Async | Use Sync |
|----------|-----------|----------|
| Multiple concurrent operations | ✓ | |
| Web framework integration | ✓ | |
| Simple scripts | | ✓ |
| CLI tools | | ✓ |
| Learning curve | Higher | Lower |
| Performance | Better | Good enough |
| Code complexity | More | Less |

## See Also

- [Client API Reference](../api/client.md) - Full client documentation
- [Quick Start](../getting-started/quickstart.md) - Examples of both modes
