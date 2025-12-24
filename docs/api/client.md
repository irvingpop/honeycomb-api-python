# Client API Reference

The main entry point for interacting with the Honeycomb API.

## HoneycombClient

::: honeycomb.client.HoneycombClient
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Configuration Classes

### RetryConfig

::: honeycomb.client.RetryConfig
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### RateLimitInfo

::: honeycomb.client.RateLimitInfo
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

## Usage Examples

### Basic Async Client

```python
import asyncio
from honeycomb import HoneycombClient

async def main():
    async with HoneycombClient(api_key="your-key") as client:
        datasets = await client.datasets.list_async()
        print(f"Found {len(datasets)} datasets")

asyncio.run(main())
```

### Sync Client

```python
from honeycomb import HoneycombClient

with HoneycombClient(api_key="your-key", sync=True) as client:
    datasets = client.datasets.list()
```

### Custom Configuration

```python
from honeycomb import HoneycombClient, RetryConfig

retry_config = RetryConfig(
    max_retries=5,
    base_delay=2.0,
    max_delay=60.0,
    retry_statuses={429, 503},
)

async with HoneycombClient(
    api_key="your-key",
    base_url="https://api.honeycomb.io",
    timeout=30.0,
    retry_config=retry_config,
) as client:
    # Your code here
    pass
```

### Management Key Authentication

```python
from honeycomb import HoneycombClient

async with HoneycombClient(
    management_key="your-key-id",
    management_secret="your-secret"
) as client:
    # Management operations
    pass
```
