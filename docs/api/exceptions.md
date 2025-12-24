# Exceptions API Reference

Exception hierarchy for handling Honeycomb API errors.

## Exception Hierarchy

All exceptions inherit from `HoneycombAPIError`, allowing you to catch all API errors with a single except clause.

```
HoneycombAPIError (base)
├── HoneycombAuthError (401)
├── HoneycombForbiddenError (403)
├── HoneycombNotFoundError (404)
├── HoneycombValidationError (422)
├── HoneycombRateLimitError (429)
├── HoneycombServerError (5xx)
├── HoneycombTimeoutError
└── HoneycombConnectionError
```

## Base Exception

::: honeycomb.exceptions.HoneycombAPIError
    options:
      show_root_heading: true
      show_source: false

## HTTP Status Exceptions

::: honeycomb.exceptions.HoneycombAuthError
    options:
      show_root_heading: true
      show_source: false

::: honeycomb.exceptions.HoneycombForbiddenError
    options:
      show_root_heading: true
      show_source: false

::: honeycomb.exceptions.HoneycombNotFoundError
    options:
      show_root_heading: true
      show_source: false

::: honeycomb.exceptions.HoneycombValidationError
    options:
      show_root_heading: true
      show_source: false

::: honeycomb.exceptions.HoneycombRateLimitError
    options:
      show_root_heading: true
      show_source: false

::: honeycomb.exceptions.HoneycombServerError
    options:
      show_root_heading: true
      show_source: false

## Transport Exceptions

::: honeycomb.exceptions.HoneycombTimeoutError
    options:
      show_root_heading: true
      show_source: false

::: honeycomb.exceptions.HoneycombConnectionError
    options:
      show_root_heading: true
      show_source: false

## Helper Functions

::: honeycomb.exceptions.raise_for_status
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Specific Exception Handling

```python
from honeycomb import (
    HoneycombClient,
    HoneycombNotFoundError,
    HoneycombRateLimitError,
    HoneycombValidationError,
)

async with HoneycombClient(api_key="...") as client:
    try:
        trigger = await client.triggers.get_async("dataset", "trigger-id")
    except HoneycombNotFoundError as e:
        print(f"Trigger not found: {e.message}")
        print(f"Status: {e.status_code}")
        print(f"Request ID: {e.request_id}")
    except HoneycombRateLimitError as e:
        print(f"Rate limited! Retry after {e.retry_after} seconds")
    except HoneycombValidationError as e:
        print(f"Validation failed: {e.message}")
        for error in e.errors:
            print(f"  - {error}")
```

### Catch-All Error Handling

```python
from honeycomb import HoneycombClient, HoneycombAPIError

async with HoneycombClient(api_key="...") as client:
    try:
        result = await client.datasets.get_async("my-dataset")
    except HoneycombAPIError as e:
        print(f"API Error [{e.status_code}]: {e.message}")
        if e.request_id:
            print(f"Request ID for support: {e.request_id}")
```

See the [Error Handling guide](../advanced/error-handling.md) for more examples and best practices.
