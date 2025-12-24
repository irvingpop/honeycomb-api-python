# Retry Configuration

The client includes automatic retry logic with exponential backoff for handling transient failures.

## Default Behavior

By default, the client automatically retries:

- **429 (Rate Limit)** - Respects `Retry-After` header
- **500, 502, 503, 504** - Server errors
- **Connection timeouts**
- **Connection errors**

With these defaults:
- **Max retries**: 3
- **Base delay**: 1.0 seconds
- **Max delay**: 30.0 seconds
- **Exponential base**: 2.0 (doubles each time)

This results in retry delays of: 1s → 2s → 4s

## Custom Retry Configuration

### Using RetryConfig

```python
from honeycomb import HoneycombClient, RetryConfig

# Create custom retry configuration
retry_config = RetryConfig(
    max_retries=5,                      # More attempts
    base_delay=2.0,                     # Start with 2 seconds
    max_delay=60.0,                     # Cap at 60 seconds
    exponential_base=2.0,               # Double each time
    retry_statuses={429, 503},          # Only retry these codes
)

async with HoneycombClient(api_key="...", retry_config=retry_config) as client:
    # Client will use your custom retry logic
    datasets = await client.datasets.list_async()
```

### Quick Configuration (max_retries only)

```python
from honeycomb import HoneycombClient

# Simple: just change max_retries
async with HoneycombClient(api_key="...", max_retries=5) as client:
    datasets = await client.datasets.list_async()
```

## Retry Scenarios

### Disable Retries

```python
from honeycomb import HoneycombClient

# No automatic retries
async with HoneycombClient(api_key="...", max_retries=0) as client:
    # Any error will be raised immediately
    datasets = await client.datasets.list_async()
```

### Aggressive Retries

```python
from honeycomb import HoneycombClient, RetryConfig

# Retry more aggressively for critical operations
retry_config = RetryConfig(
    max_retries=10,
    base_delay=0.5,       # Start faster
    max_delay=120.0,      # Wait longer if needed
)

async with HoneycombClient(api_key="...", retry_config=retry_config) as client:
    # Critical operation that must succeed
    result = await client.some_critical_operation()
```

### Retry Only Rate Limits

```python
from honeycomb import HoneycombClient, RetryConfig

# Only retry rate limits, fail fast on other errors
retry_config = RetryConfig(
    max_retries=3,
    retry_statuses={429},  # Only 429
)

async with HoneycombClient(api_key="...", retry_config=retry_config) as client:
    datasets = await client.datasets.list_async()
```

## How Retry Logic Works

### Exponential Backoff Calculation

The delay between retries is calculated as:

```
delay = min(base_delay * (exponential_base ** attempt), max_delay)
```

**Example with defaults** (base_delay=1.0, exponential_base=2.0, max_delay=30.0):

| Attempt | Calculation | Delay |
|---------|-------------|-------|
| 0 | 1.0 × 2^0 | 1.0s |
| 1 | 1.0 × 2^1 | 2.0s |
| 2 | 1.0 × 2^2 | 4.0s |
| 3 | 1.0 × 2^3 | 8.0s |
| 4 | 1.0 × 2^4 | 16.0s |
| 5 | 1.0 × 2^5 | 30.0s (capped) |

### Retry-After Header

When the API returns a 429 with a `Retry-After` header, the client:

1. Parses the header (supports both seconds and HTTP dates)
2. Uses that value instead of exponential backoff
3. Waits the specified time before retrying

```python
# Automatic handling - nothing special required
async with HoneycombClient(api_key="...") as client:
    # If API returns 429 with Retry-After: 60
    # Client will wait 60 seconds, then retry automatically
    datasets = await client.datasets.list_async()
```

## Monitoring Retries

Want to see when retries happen? Add logging:

```python
import logging

# Enable httpx logging to see retry attempts
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)

from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    datasets = await client.datasets.list_async()
```

## Best Practices

### 1. Use Defaults for Most Cases

The default retry configuration works well for most scenarios:

```python
# ✓ Good - use defaults
async with HoneycombClient(api_key="...") as client:
    await client.datasets.list_async()
```

### 2. Disable Retries for Idempotency Tests

When testing idempotency or error handling:

```python
# For testing - fail fast
async with HoneycombClient(api_key="...", max_retries=0) as client:
    try:
        await client.datasets.get_async("test")
    except HoneycombNotFoundError:
        # Test your error handling
        pass
```

### 3. Increase Retries for Critical Operations

```python
from honeycomb import HoneycombClient, RetryConfig

# Critical operation - try harder
retry_config = RetryConfig(max_retries=10, max_delay=120.0)

async with HoneycombClient(api_key="...", retry_config=retry_config) as client:
    # This will retry up to 10 times
    await client.critical_operation()
```

### 4. Respect Rate Limits

The client automatically respects rate limits, but you can also implement your own backoff:

```python
from honeycomb import HoneycombClient, HoneycombRateLimitError
import asyncio

async def safe_list_datasets(client):
    """List datasets with extra rate limit protection."""
    while True:
        try:
            return await client.datasets.list_async()
        except HoneycombRateLimitError as e:
            if e.retry_after:
                await asyncio.sleep(e.retry_after)
                continue
            raise

async with HoneycombClient(api_key="...") as client:
    datasets = await safe_list_datasets(client)
```

## Timeout Configuration

Separate from retries, you can configure request timeouts:

```python
from honeycomb import HoneycombClient

async with HoneycombClient(
    api_key="...",
    timeout=60.0,      # 60 second timeout per request
    max_retries=3,     # Up to 3 retries
) as client:
    # Each request can take up to 60s
    # With retries, total time could be up to 240s
    datasets = await client.datasets.list_async()
```

## See Also

- [Client API Reference](../api/client.md#retryconfig) - Full RetryConfig documentation
- [Error Handling](error-handling.md) - Exception handling guide
