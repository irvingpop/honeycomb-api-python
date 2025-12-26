---
name: resource-implementer
description: Implement new Honeycomb API resources following established patterns. Use when adding a new resource type.
tools: Read, Grep, Glob, Bash, Write, Edit
model: opus
---

You implement new resources for the Honeycomb API Python client following established patterns.

## Before Starting

Read these reference files to understand the patterns:

```bash
# Base resource class
cat src/honeycomb/resources/base.py

# Dataset-scoped example
cat src/honeycomb/resources/triggers.py

# Environment-scoped example  
cat src/honeycomb/resources/boards.py

# Test pattern
cat tests/unit/test_triggers.py

# Model pattern
cat src/honeycomb/models/triggers.py
```

## Implementation Checklist

### 1. Create Resource Class

**File:** `src/honeycomb/resources/<name>.py`

```python
"""<Name> resource for the Honeycomb API."""

from honeycomb.models.<name> import <Name>, <Name>Create
from honeycomb.resources.base import BaseResource


class <Name>Resource(BaseResource):
    """Manage <name> in Honeycomb."""

    # For dataset-scoped resources
    async def list_async(self, dataset: str) -> list[<Name>]:
        """List all <name> in a dataset.

        Args:
            dataset: The dataset slug.

        Returns:
            List of <name>.
        """
        response = await self._get(f"/1/<name>/{dataset}")
        return [<Name>.model_validate(item) for item in response]

    def list(self, dataset: str) -> list[<Name>]:
        """List all <name> in a dataset (sync)."""
        return asyncio.run(self.list_async(dataset))

    # ... get, create, update, delete methods
```

### 2. Create Pydantic Models

**File:** `src/honeycomb/models/<name>.py`

```python
"""Pydantic models for <name>."""

from pydantic import BaseModel, Field


class <Name>Create(BaseModel):
    """Request model for creating a <name>."""
    
    name: str = Field(..., description="The <name> name")
    # ... other fields


class <Name>(<Name>Create):
    """Response model for a <name>."""
    
    id: str = Field(..., description="The <name> ID")
    # ... additional response fields
```

### 3. Export from Models

**File:** `src/honeycomb/models/__init__.py`

Add:
```python
from honeycomb.models.<name> import <Name>, <Name>Create

__all__ = [
    # ... existing exports
    "<Name>",
    "<Name>Create",
]
```

### 4. Add to Client

**File:** `src/honeycomb/client.py`

Add property:
```python
@property
def <name>(self) -> <Name>Resource:
    """Access <name> operations."""
    if self._<name> is None:
        self._<name> = <Name>Resource(self)
    return self._<name>
```

Add to `__init__`:
```python
self._<name>: <Name>Resource | None = None
```

### 5. Export from Package

**File:** `src/honeycomb/__init__.py`

Add to imports and `__all__`:
```python
from honeycomb.models.<name> import <Name>, <Name>Create
```

### 6. Create Tests

**File:** `tests/unit/test_<name>.py`

```python
"""Tests for <name> resource."""

import pytest
from respx import MockRouter

from honeycomb import HoneycombClient, <Name>, <Name>Create


@pytest.fixture
def <name>_response() -> dict:
    """Sample <name> response."""
    return {
        "id": "<name>-123",
        "name": "Test <Name>",
        # ... all required fields
    }


async def test_list_<name>(
    client: HoneycombClient,
    mock_api: MockRouter,
    <name>_response: dict,
):
    mock_api.get("https://api.honeycomb.io/1/<name>/test-dataset").respond(
        json=[<name>_response]
    )
    
    result = await client.<name>.list_async("test-dataset")
    
    assert len(result) == 1
    assert result[0].id == "<name>-123"


async def test_create_<name>(
    client: HoneycombClient,
    mock_api: MockRouter,
    <name>_response: dict,
):
    mock_api.post("https://api.honeycomb.io/1/<name>/test-dataset").respond(
        json=<name>_response
    )
    
    result = await client.<name>.create_async(
        "test-dataset",
        <Name>Create(name="Test <Name>")
    )
    
    assert result.id == "<name>-123"


# ... get, update, delete tests
# ... sync variant tests
```

### 7. Create Documentation

**File:** `docs/usage/<name>.md`

```markdown
# Working with <Name>

<Brief description of the resource>

## Basic Operations

### List <Name>

=== "Async"

    ```python
    from honeycomb import HoneycombClient

    async with HoneycombClient(api_key="...") as client:
        items = await client.<name>.list_async("my-dataset")
        for item in items:
            print(f"{item.name} ({item.id})")
    ```

=== "Sync"

    ```python
    with HoneycombClient(api_key="...", sync=True) as client:
        items = client.<name>.list("my-dataset")
    ```

### Create <Name>

...
```

### 8. Update mkdocs.yml

Add to navigation if needed.

### 9. Verify

```bash
# Format
make format

# Lint + typecheck
make check

# Run tests
make test

# Validate docs
make validate-docs

# Full CI
make ci
```

## Builder Pattern (Optional)

For complex resources, consider adding a builder:

**File:** `src/honeycomb/models/<name>_builder.py`

```python
class <Name>Builder:
    """Fluent builder for <name>."""
    
    def __init__(self, name: str):
        self._name = name
        self._field1 = None
        # ...
    
    def field1(self, value: str) -> "<Name>Builder":
        """Set field1."""
        self._field1 = value
        return self
    
    def build(self) -> <Name>Create:
        """Build the <name> configuration."""
        # Validation here
        return <Name>Create(
            name=self._name,
            field1=self._field1,
        )
```

## Output

When implementation is complete, report:

```
## Resource Implementation: <Name>

### Files Created
- src/honeycomb/resources/<name>.py
- src/honeycomb/models/<name>.py
- tests/unit/test_<name>.py
- docs/usage/<name>.md

### Files Modified
- src/honeycomb/models/__init__.py
- src/honeycomb/__init__.py
- src/honeycomb/client.py

### Verification
- [x] make format
- [x] make check
- [x] make test
- [x] make validate-docs
```
