# Honeycomb API Python Client - Implementation Plan

## Project Status

**Current Phase:** Phase 7 - Resource Implementation (Priority Resources Complete)

**Completed Phases:**
- ✅ Phase 1: Project Setup & Generation
- ✅ Phase 2: Authentication
- ✅ Phase 3: Client Design (Async-First)
- ✅ Phase 4: Exception Handling
- ✅ Phase 5: Rate Limiting & Retries
- ✅ Phase 6: Pydantic Models
- ✅ Phase 7.1: Priority Resources (Triggers, SLOs, Datasets, Boards, Queries, Query Results)
- ✅ Documentation: MkDocs + Material with auto-generated API reference

**Test Coverage:** 145 tests passing | **Doc Validation:** 75 code examples validated

---

## Overview

Build a clean, ergonomic, and maintainable Python client for the Honeycomb.io API using `openapi-python-client` as the generation foundation, with a hand-crafted ergonomic wrapper layer.

**API Scope:** 89 operations, ~70+ schemas across these resource groups:
- Auth, Boards, Burn Alerts, Calculated Fields, Columns
- Datasets, Dataset Definitions, Events (batch/single/kinesis)
- Markers, Marker Settings, Queries, Query Annotations, Query Results
- Recipients, SLOs, SLO History, Triggers
- API Keys, Environments, Pipelines (v2 team-scoped endpoints)

## Architecture

**Hybrid Approach:** Generate base client with `openapi-python-client`, then wrap with an ergonomic high-level API.

```
┌─────────────────────────────────────────────────┐
│  honeycomb (public interface)                   │
│  - HoneycombClient class (async-first)          │
│  - Resource-oriented methods                    │
│  - Pythonic naming (snake_case)                 │
│  - Sync wrapper option                          │
├─────────────────────────────────────────────────┤
│  honeycomb._generated (internal)                │
│  - openapi-python-client output                 │
│  - Raw API operations                           │
│  - Generated Pydantic models                    │
└─────────────────────────────────────────────────┘
```

**Rationale:**
- Generated layer handles HTTP, serialization, types
- Wrapper layer provides clean DX: resource grouping, convenience methods, better error handling
- Easy to regenerate when API spec updates (just re-run generator, wrapper stays stable)

## Package Structure

```
honeycomb-api-python/
├── src/
│   └── honeycomb/
│       ├── __init__.py          # Exports HoneycombClient, models, exceptions
│       ├── client.py            # Main client class (async + sync)
│       ├── auth.py              # Auth strategies (API key, Management key)
│       ├── exceptions.py        # Exception hierarchy
│       ├── models/              # Pydantic models (re-export/extend generated)
│       │   ├── __init__.py
│       │   ├── triggers.py
│       │   ├── slos.py
│       │   ├── boards.py
│       │   ├── queries.py
│       │   ├── datasets.py
│       │   └── ...
│       ├── resources/           # Resource-specific clients
│       │   ├── __init__.py
│       │   ├── base.py          # BaseResource with common HTTP logic
│       │   ├── triggers.py
│       │   ├── slos.py
│       │   ├── boards.py
│       │   ├── queries.py
│       │   ├── datasets.py
│       │   ├── columns.py
│       │   ├── markers.py
│       │   ├── recipients.py
│       │   ├── events.py
│       │   └── ...
│       └── _generated/          # openapi-python-client output
├── tests/
│   ├── conftest.py
│   ├── fixtures/                # Sample API responses
│   ├── unit/
│   └── integration/
├── api.yaml                     # OpenAPI spec
├── generator-config.yaml
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

## Phase 1: Project Setup & Generation ✓ COMPLETED

### 1.1 Initialize Python Project

**pyproject.toml:**
```toml
[project]
name = "honeycomb-api"
version = "0.1.0"
description = "Python client for the Honeycomb.io API"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "respx>=0.21",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/honeycomb"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.mypy]
python_version = "3.10"
strict = true
```

### 1.2 Generate Base Client

```bash
pipx install openapi-python-client --include-deps
openapi-python-client generate --path api.yaml --output-path src/honeycomb/_generated --config generator-config.yaml
```

### 1.3 Generator Configuration

**generator-config.yaml:**
```yaml
project_name_override: honeycomb-generated
package_name_override: _generated
use_path_prefixes_for_title_model_names: true
post_hooks: []
```

### 1.4 Evaluate Generation Output
- Check for generation errors/warnings
- Review generated models for completeness
- Identify any OpenAPI features not supported
- Document gaps to handle manually

## Phase 2: Authentication ✓ COMPLETED

### 2.1 Auth Strategies

Support both authentication methods:

| Type           | Header Format                        | Use Case           |
|----------------|--------------------------------------|--------------------|
| API Key        | `X-Honeycomb-Team: {key}`            | Single environment |
| Management Key | `Authorization: Bearer {key}:{secret}` | Multi-environment  |

**auth.py:**
```python
from abc import ABC, abstractmethod
import httpx

class AuthStrategy(ABC):
    @abstractmethod
    def apply(self, request: httpx.Request) -> httpx.Request: ...

class APIKeyAuth(AuthStrategy):
    """Single environment API key auth."""
    def __init__(self, api_key: str):
        self.api_key = api_key

    def apply(self, request: httpx.Request) -> httpx.Request:
        request.headers["X-Honeycomb-Team"] = self.api_key
        return request

class ManagementKeyAuth(AuthStrategy):
    """Multi-environment management key auth."""
    def __init__(self, key: str, secret: str):
        self.key = key
        self.secret = secret

    def apply(self, request: httpx.Request) -> httpx.Request:
        request.headers["Authorization"] = f"Bearer {self.key}:{self.secret}"
        return request
```

### 2.2 Client Initialization

```python
# API key auth (single environment)
client = HoneycombClient(api_key="hcaik_xxx")

# Management key auth (multi-environment)
client = HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx"
)
```

## Phase 3: Client Design (Async-First) ✓ COMPLETED

### 3.1 Primary Interface (Async)

```python
async with HoneycombClient(api_key="...") as client:
    # Datasets
    datasets = await client.datasets.list()
    dataset = await client.datasets.get("my-dataset")

    # Triggers (dataset-scoped)
    triggers = await client.triggers.list(dataset="my-dataset")
    trigger = await client.triggers.create(
        dataset="my-dataset",
        name="High Latency",
        query_id="query-123",
        threshold=TriggerThreshold(op=">=", value=1000),
        frequency=300,
    )

    # SLOs
    slos = await client.slos.list(dataset="my-dataset")
    slo = await client.slos.get(dataset="my-dataset", slo_id="slo-123")

    # Queries
    query = await client.queries.create(dataset="my-dataset", query_spec={...})
    result = await client.query_results.run(
        dataset="my-dataset",
        query_id=query.id,
        poll_interval=1.0,
        timeout=60.0,
    )

    # Boards (environment-scoped)
    boards = await client.boards.list()
    board = await client.boards.update(board_id="board-123", name="Updated")

    # Events (data ingestion)
    await client.events.send(dataset="my-dataset", data={"field": "value"})
    await client.events.send_batch(dataset="my-dataset", events=[...])
```

### 3.2 Sync Wrapper

```python
# Sync mode for scripts/CLI
with HoneycombClient(api_key="...", sync=True) as client:
    trigger = client.triggers.create(...)  # blocks
```

**Implementation approach:**
```python
class HoneycombClient:
    def __init__(
        self,
        api_key: str | None = None,
        management_key: str | None = None,
        management_secret: str | None = None,
        base_url: str = "https://api.honeycomb.io",
        timeout: float = 30.0,
        max_retries: int = 3,
        sync: bool = False,
        http_client: httpx.AsyncClient | None = None,
    ):
        self._sync = sync
        # ... setup auth, client, resources

    async def __aenter__(self) -> "HoneycombClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)

    def __enter__(self) -> "HoneycombClient":
        # For sync mode
        if not self._sync:
            raise RuntimeError("Use 'async with' for async mode")
        return self

    def __exit__(self, *args) -> None:
        self._client.close()
```

### 3.3 HTTP Client Injection (Testing Support)

```python
# Easy to mock in tests
mock_transport = respx.MockTransport(...)
mock_client = httpx.AsyncClient(transport=mock_transport)
client = HoneycombClient(api_key="test", http_client=mock_client)
```

## Phase 4: Exception Handling ✓ COMPLETED

### 4.1 Exception Hierarchy

```python
class HoneycombAPIError(Exception):
    """Base exception for Honeycomb API errors."""
    def __init__(
        self,
        message: str,
        status_code: int,
        request_id: str | None = None,
        response_body: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.response_body = response_body

class HoneycombAuthError(HoneycombAPIError):
    """401 Unauthorized - Invalid or missing API key."""
    pass

class HoneycombForbiddenError(HoneycombAPIError):
    """403 Forbidden - Insufficient permissions."""
    pass

class HoneycombNotFoundError(HoneycombAPIError):
    """404 Not Found - Resource doesn't exist."""
    pass

class HoneycombValidationError(HoneycombAPIError):
    """422 Validation Error - Invalid request data."""
    def __init__(self, *args, errors: list[dict] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = errors or []

class HoneycombRateLimitError(HoneycombAPIError):
    """429 Rate Limited - Too many requests."""
    def __init__(self, *args, retry_after: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry_after = retry_after

class HoneycombServerError(HoneycombAPIError):
    """5xx Server Error - Honeycomb service issue."""
    pass
```

### 4.2 Error Response Parsing

Parse Honeycomb's error formats:
- `application/json`: `{"error": "message"}`
- `application/problem+json`: RFC 7807 format
- `application/vnd.api+json`: JSON:API error format

## Phase 5: Rate Limiting & Retries ✓ COMPLETED

### 5.1 Rate Limit Detection

Parse rate limit headers:
- `RateLimit`: `limit=100, remaining=50, reset=60`
- `RateLimit-Policy`: `100;w=60`
- `Retry-After`: RFC 7231 date or seconds

### 5.2 Exponential Backoff

```python
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    retry_statuses: set[int] = {429, 500, 502, 503, 504}

async def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
    last_exception: Exception | None = None

    for attempt in range(self._retry_config.max_retries + 1):
        try:
            response = await self._client.request(method, url, **kwargs)

            if response.status_code not in self._retry_config.retry_statuses:
                return response

            if response.status_code == 429:
                retry_after = self._parse_retry_after(response)
                delay = retry_after or self._calculate_backoff(attempt)
            else:
                delay = self._calculate_backoff(attempt)

            await asyncio.sleep(delay)

        except httpx.TransportError as e:
            last_exception = e
            await asyncio.sleep(self._calculate_backoff(attempt))

    raise last_exception or HoneycombAPIError("Max retries exceeded", 0)
```

## Phase 6: Pydantic Models ✓ COMPLETED

### 6.1 Model Strategy

Re-export generated models where suitable, extend/customize where needed:

```python
# models/triggers.py
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TriggerOp(str, Enum):
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="

class TriggerThreshold(BaseModel):
    op: TriggerOp
    value: float

class TriggerRecipient(BaseModel):
    id: str
    type: str

class TriggerCreate(BaseModel):
    name: str
    description: str | None = None
    query_id: str
    threshold: TriggerThreshold
    frequency: int = Field(..., description="Trigger frequency in seconds")
    recipients: list[TriggerRecipient] = Field(default_factory=list)
    disabled: bool = False

class Trigger(TriggerCreate):
    id: str
    created_at: datetime
    updated_at: datetime
```

### 6.2 Model Organization

```python
# models/__init__.py
from .triggers import Trigger, TriggerCreate, TriggerThreshold, TriggerRecipient
from .slos import SLO, SLOCreate, SLI
from .boards import Board, BoardCreate, BoardPanel
from .queries import Query, QuerySpec, QueryResult
from .datasets import Dataset, DatasetCreate
# ... etc

__all__ = [
    "Trigger", "TriggerCreate", "TriggerThreshold", "TriggerRecipient",
    "SLO", "SLOCreate", "SLI",
    # ...
]
```

## Phase 7: Resource Implementation

### 7.1 Priority Resources ✓ COMPLETED

| Resource | Endpoints | Notes |
|----------|-----------|-------|
| **Triggers** | POST, GET, GET/{id}, PUT/{id}, DELETE/{id} | Dataset-scoped |
| **SLOs** | POST, GET, GET/{id}, PUT/{id}, DELETE/{id} | Dataset-scoped |
| **Boards** | POST, GET, GET/{id}, PUT/{id}, DELETE/{id} | Environment-scoped |
| **Datasets** | POST, GET, GET/{id}, PUT/{id}, DELETE/{id} | CRUD operations |
| **Queries** | POST, GET/{id} | For trigger/SLO validation |
| **Query Results** | POST, GET/{id}, run (polling), create_and_run | Run queries with automatic polling |

**Implementation Summary:**
- All 6 priority resources fully implemented with async + sync variants
- Comprehensive test coverage (17 query tests + integration with wrapper tests)
- Resource accessor properties on HoneycombClient (`client.queries`, `client.query_results`, etc.)
- Convenience methods: `run()` for automatic polling, `create_and_run()` for save+execute
- Full error handling and validation
- Files: `src/honeycomb/resources/{triggers,slos,boards,datasets,queries,query_results}.py`

### 7.2 Secondary Resources (Deferred)

| Resource | Notes |
|----------|-------|
| Columns | Dataset-scoped column management |
| Markers | Dataset-scoped event markers |
| Marker Settings | Marker configuration |
| Recipients | Notification targets |
| Burn Alerts | SLO burn rate alerts |
| Events | Data ingestion (batch/single/kinesis) |

### 7.3 v2 Team-Scoped Resources

| Resource | Notes |
|----------|-------|
| API Keys | Team-scoped management |
| Environments | Team-scoped management |
| Pipelines | Team-scoped (internal) |

### 7.4 Base Resource Implementation

```python
# resources/base.py
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)

class BaseResource(Generic[T, CreateT, UpdateT]):
    def __init__(self, client: "HoneycombClient"):
        self._client = client

    async def _get(self, path: str) -> dict:
        response = await self._client._request("GET", path)
        return response.json()

    async def _post(self, path: str, data: BaseModel) -> dict:
        response = await self._client._request(
            "POST", path, json=data.model_dump(exclude_none=True)
        )
        return response.json()

    # ... _put, _delete, etc.
```

### 7.5 Triggers Resource Example

```python
# resources/triggers.py
class TriggersResource(BaseResource[Trigger, TriggerCreate, TriggerUpdate]):

    async def list(self, dataset: str) -> list[Trigger]:
        """List all triggers in a dataset."""
        data = await self._get(f"/1/triggers/{dataset}")
        return [Trigger.model_validate(t) for t in data]

    async def get(self, dataset: str, trigger_id: str) -> Trigger:
        """Get a specific trigger."""
        data = await self._get(f"/1/triggers/{dataset}/{trigger_id}")
        return Trigger.model_validate(data)

    async def create(self, dataset: str, trigger: TriggerCreate) -> Trigger:
        """Create a new trigger."""
        data = await self._post(f"/1/triggers/{dataset}", trigger)
        return Trigger.model_validate(data)

    async def update(
        self, dataset: str, trigger_id: str, trigger: TriggerUpdate
    ) -> Trigger:
        """Update an existing trigger."""
        data = await self._put(f"/1/triggers/{dataset}/{trigger_id}", trigger)
        return Trigger.model_validate(data)

    async def delete(self, dataset: str, trigger_id: str) -> None:
        """Delete a trigger."""
        await self._delete(f"/1/triggers/{dataset}/{trigger_id}")
```

## Phase 8: Pagination

### 8.1 Pagination Response Model

```python
class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    links: PaginationLinks | None = None

class PaginationLinks(BaseModel):
    next: str | None = None
```

### 8.2 Pagination Helpers

```python
# Manual pagination
page = await client.boards.list(page_size=20)
while page.links and page.links.next:
    page = await client.boards.list(page_size=20, page_after=page.links.next)

# Auto-pagination async generator
async for board in client.boards.list_all():
    print(board.name)
```

## Phase 9: Testing

### 9.1 Test Configuration

```python
# conftest.py
import pytest
from respx import MockRouter
import httpx
from honeycomb import HoneycombClient

@pytest.fixture
def mock_api(respx_mock: MockRouter) -> MockRouter:
    return respx_mock

@pytest.fixture
async def client(mock_api: MockRouter) -> HoneycombClient:
    async with HoneycombClient(api_key="test-key") as client:
        yield client
```

### 9.2 Unit Test Example

```python
# tests/unit/test_triggers.py
import pytest
from respx import MockRouter

async def test_list_triggers(client: HoneycombClient, mock_api: MockRouter):
    mock_api.get("https://api.honeycomb.io/1/triggers/my-dataset").respond(
        json=[
            {"id": "trigger-1", "name": "High Latency", ...},
            {"id": "trigger-2", "name": "Error Rate", ...},
        ]
    )

    triggers = await client.triggers.list(dataset="my-dataset")

    assert len(triggers) == 2
    assert triggers[0].id == "trigger-1"
    assert triggers[0].name == "High Latency"

async def test_create_trigger(client: HoneycombClient, mock_api: MockRouter):
    mock_api.post("https://api.honeycomb.io/1/triggers/my-dataset").respond(
        json={"id": "new-trigger", "name": "New Trigger", ...}
    )

    trigger = await client.triggers.create(
        dataset="my-dataset",
        trigger=TriggerCreate(name="New Trigger", ...),
    )

    assert trigger.id == "new-trigger"
```

### 9.3 Integration Tests

```python
# tests/integration/test_live_api.py
import pytest
import os

pytestmark = pytest.mark.integration

@pytest.fixture
def live_client():
    api_key = os.environ.get("HONEYCOMB_API_KEY")
    if not api_key:
        pytest.skip("HONEYCOMB_API_KEY not set")
    return HoneycombClient(api_key=api_key, sync=True)

def test_list_datasets(live_client):
    datasets = live_client.datasets.list()
    assert isinstance(datasets, list)
```

### 9.4 Fixtures

Store sample API responses in `tests/fixtures/`:
- `triggers_list.json`
- `trigger_detail.json`
- `slos_list.json`
- `error_404.json`
- `error_429.json`

## Phase 10: Documentation

### 10.1 README.md

- Installation instructions
- Quick start examples (async + sync)
- Authentication guide
- Common operations
- Error handling
- Link to Honeycomb API docs

### 10.2 Docstrings

Google-style docstrings on all public methods:

```python
async def create(self, dataset: str, trigger: TriggerCreate) -> Trigger:
    """Create a new trigger in a dataset.

    Args:
        dataset: The dataset slug.
        trigger: The trigger configuration.

    Returns:
        The created trigger with ID and timestamps.

    Raises:
        HoneycombValidationError: If the trigger configuration is invalid.
        HoneycombNotFoundError: If the dataset doesn't exist.
    """
```

## Implementation Order

1. ✅ **Project setup** - pyproject.toml, directory structure, dependencies
2. ✅ **Run generator** - Generate base client, evaluate output quality
3. ✅ **Auth module** - APIKeyAuth, ManagementKeyAuth strategies
4. ✅ **Exceptions** - Full exception hierarchy with parsing
5. ✅ **Base client** - HoneycombClient with async/sync, retry logic
6. ✅ **Base resource** - Generic CRUD operations
7. ✅ **Triggers resource** - Full CRUD with tests
8. ✅ **SLOs resource** - Full CRUD with tests
9. ✅ **Boards resource** - Full CRUD with tests
10. ✅ **Queries + Query Results** - Create/run queries (with create_and_run convenience method)
11. ✅ **Datasets** - CRUD operations
12. ⏸️ **Remaining resources** - Columns, Markers, Recipients, etc. (deferred)
13. ⏸️ **v2 resources** - API Keys, Environments (team-scoped) (deferred)
14. ⏸️ **Events** - Data ingestion (deferred)
15. ⏸️ **Pagination helpers** - Auto-pagination iterators (deferred)
16. ✅ **Documentation** - MkDocs + Material, auto-generated API reference, validated examples
17. ✅ **CI setup** - Makefile with format, lint, typecheck, test, validate-docs

## Completed Features

### Core Functionality (Production Ready)
- **Client**: Async-first with sync support, configurable retry logic, rate limit handling
- **Authentication**: API keys and Management keys with automatic header management
- **Resources**: Datasets, Triggers, SLOs, Boards, Queries, Query Results
- **Models**: Pydantic models for all resources with validation and serialization
- **Error Handling**: 9 specific exception types with request ID tracking
- **Retry Logic**: Exponential backoff with Retry-After header support (RFC 7231 dates)
- **Rate Limiting**: Automatic handling with configurable retry behavior

### Developer Experience
- **Documentation**: 13-page MkDocs site with auto-generated API reference
- **Testing**: 145 unit tests (all passing), 5 doc example tests
- **Code Quality**: Ruff (format + lint), mypy (type checking), all integrated in CI
- **Validation**: 75 documentation code examples validated in CI
- **Live API Testing**: Rate limit test suite with automatic retry verification

### Advanced Features
- **create_and_run**: Convenience method that creates saved query + executes in one call
- **RetryConfig**: Fully customizable retry behavior (delays, statuses, limits)
- **RateLimitInfo**: Parse rate limit headers (multiple formats supported)
- **Multiple error formats**: RFC 7807, JSON:API, simple JSON

## Key Metrics

| Metric | Count |
|--------|-------|
| **Test Coverage** | 145 tests passing |
| **Doc Examples** | 75 code blocks validated |
| **Resources** | 6 fully implemented |
| **Models** | 15+ Pydantic models |
| **Exceptions** | 9 specific types |
| **Doc Pages** | 13 pages |
| **Type Coverage** | 100% (mypy strict on src/) |

## Next Steps (Recommended Priority)

1. **GitHub Actions CI/CD** - Automate testing and docs deployment
2. **PyPI Publishing** - Make package publicly available
3. **Secondary Resources** - Columns, Markers, Recipients (as needed)
4. **Pagination Helpers** - Auto-pagination for list operations
5. **Events API** - Data ingestion support

## Future Enhancements (Nice-to-Have)

- **Caching**: Optional response caching with TTL
- **OpenTelemetry**: Built-in tracing instrumentation
- **CLI**: `honeycomb triggers list --env production`
- **VCR-style recording**: Cassette recording for integration tests
- **Streaming Events**: Async event ingestion with batching

## References

- [Honeycomb API Docs](https://docs.honeycomb.io/api/)
- [OpenAPI Spec](https://api.honeycomb.io/api.yaml)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
