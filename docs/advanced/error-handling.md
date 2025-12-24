# Error Handling

The Honeycomb API client provides a comprehensive exception hierarchy for handling different error scenarios.

## Exception Types

| Exception | HTTP Status | When It's Raised |
|-----------|-------------|------------------|
| `HoneycombAuthError` | 401 | Invalid or missing credentials |
| `HoneycombForbiddenError` | 403 | Insufficient permissions |
| `HoneycombNotFoundError` | 404 | Resource doesn't exist |
| `HoneycombValidationError` | 422 | Invalid request data |
| `HoneycombRateLimitError` | 429 | Too many requests |
| `HoneycombServerError` | 5xx | Server-side error |
| `HoneycombTimeoutError` | - | Request timed out |
| `HoneycombConnectionError` | - | Connection failed |

## Basic Error Handling

### Catch Specific Errors

```python
from honeycomb import (
    HoneycombClient,
    HoneycombNotFoundError,
    HoneycombValidationError,
)

async with HoneycombClient(api_key="...") as client:
    try:
        dataset = await client.datasets.get_async("nonexistent")
    except HoneycombNotFoundError as e:
        print(f"Dataset not found: {e.message}")
        # Handle gracefully - maybe create it?
```

### Catch All API Errors

```python
from honeycomb import HoneycombClient, HoneycombAPIError

async with HoneycombClient(api_key="...") as client:
    try:
        result = await client.some_operation()
    except HoneycombAPIError as e:
        print(f"API error [{e.status_code}]: {e.message}")
        if e.request_id:
            print(f"Report this Request ID to support: {e.request_id}")
```

## Advanced Error Handling

### Rate Limit Handling

When you hit rate limits, the client automatically retries, but you can also handle it manually:

```python
from honeycomb import HoneycombClient, HoneycombRateLimitError
import asyncio

async with HoneycombClient(api_key="...", max_retries=0) as client:
    try:
        datasets = await client.datasets.list_async()
    except HoneycombRateLimitError as e:
        if e.retry_after:
            print(f"Rate limited. Waiting {e.retry_after} seconds...")
            await asyncio.sleep(e.retry_after)
            # Retry the operation
            datasets = await client.datasets.list_async()
```

!!! tip "Automatic Retry"
    By default, the client automatically retries rate limit errors (429) using the `Retry-After` header. Set `max_retries=0` to disable this behavior.

### Validation Error Details

```python
from honeycomb import HoneycombClient, HoneycombValidationError, TriggerCreate

async with HoneycombClient(api_key="...") as client:
    try:
        trigger = await client.triggers.create_async(
            "my-dataset",
            TriggerCreate(name="")  # Invalid - name is required
        )
    except HoneycombValidationError as e:
        print(f"Validation failed: {e.message}")
        for error in e.errors:
            field = error.get("field", "unknown")
            msg = error.get("message", "invalid")
            print(f"  - {field}: {msg}")
```

### Timeout Handling

```python
from honeycomb import HoneycombClient, HoneycombTimeoutError

async with HoneycombClient(api_key="...", timeout=5.0) as client:
    try:
        result = await client.query_results.run_async(
            "my-dataset",
            spec=...,
            timeout=30.0  # Query execution timeout
        )
    except HoneycombTimeoutError as e:
        print(f"Operation timed out after {e.timeout}s")
        # Maybe increase timeout or simplify query?
```

### Connection Errors

```python
from honeycomb import HoneycombClient, HoneycombConnectionError

async with HoneycombClient(api_key="...") as client:
    try:
        datasets = await client.datasets.list_async()
    except HoneycombConnectionError as e:
        print(f"Connection failed: {e.message}")
        if e.original_error:
            print(f"Original error: {e.original_error}")
        # Maybe network is down?
```

## Error Response Information

All exceptions include useful debugging information:

```python
from honeycomb import HoneycombClient, HoneycombAPIError

async with HoneycombClient(api_key="...") as client:
    try:
        result = await client.some_operation()
    except HoneycombAPIError as e:
        print(f"Message: {e.message}")
        print(f"Status Code: {e.status_code}")
        print(f"Request ID: {e.request_id}")  # For support tickets
        print(f"Response Body: {e.response_body}")  # Raw API response
```

## Best Practices

### 1. Always Use Context Managers

```python
# ✓ Good - Resources are cleaned up
async with HoneycombClient(api_key="...") as client:
    await client.datasets.list_async()

# ✗ Bad - Manual cleanup required
client = HoneycombClient(api_key="...")
await client.datasets.list_async()
await client.aclose()  # Easy to forget!
```

### 2. Handle Expected Errors

```python
# If you're checking if a resource exists, expect 404
from honeycomb import HoneycombClient, HoneycombNotFoundError

async with HoneycombClient(api_key="...") as client:
    try:
        dataset = await client.datasets.get_async("maybe-exists")
        print("Dataset exists!")
    except HoneycombNotFoundError:
        print("Dataset doesn't exist - creating it...")
        dataset = await client.datasets.create_async(...)
```

### 3. Save Request IDs

Request IDs are crucial for debugging with Honeycomb support:

```python
import logging

from honeycomb import HoneycombClient, HoneycombAPIError

logger = logging.getLogger(__name__)

async with HoneycombClient(api_key="...") as client:
    try:
        result = await client.some_operation()
    except HoneycombAPIError as e:
        logger.error(
            "API error",
            extra={
                "status_code": e.status_code,
                "request_id": e.request_id,
                "message": e.message,
            }
        )
        raise
```

### 4. Different Strategies for Different Errors

```python
from honeycomb import (
    HoneycombClient,
    HoneycombAuthError,
    HoneycombNotFoundError,
    HoneycombRateLimitError,
    HoneycombServerError,
)

async with HoneycombClient(api_key="...") as client:
    try:
        result = await client.datasets.get_async("my-dataset")
    except HoneycombAuthError:
        # Auth errors are not retryable - fix credentials
        logger.error("Invalid API key - check credentials")
        raise
    except HoneycombNotFoundError:
        # Resource doesn't exist - maybe create it
        result = await client.datasets.create_async(...)
    except HoneycombRateLimitError as e:
        # Rate limit - automatic retry usually handles this
        logger.warning(f"Rate limited, retry after {e.retry_after}s")
        raise
    except HoneycombServerError:
        # Server error - might be transient
        logger.error("Server error - retrying automatically")
        raise  # Client will retry automatically
```

## See Also

- [Retry Configuration](retry-config.md) - Configure automatic retry behavior
- [Exceptions API Reference](../api/exceptions.md) - Full exception class documentation
