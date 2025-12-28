# Honeycomb API Python Client - Implementation Plan

## Project Status

**Current Phase:** Production Ready - All core features complete

**Completed Phases:**
- ✅ Phase 1: Project Setup & Generation
- ✅ Phase 2: Authentication
- ✅ Phase 3: Client Design (Async-First)
- ✅ Phase 4: Exception Handling
- ✅ Phase 5: Rate Limiting & Retries
- ✅ Phase 6: Pydantic Models
- ✅ Phase 7.1: Priority Resources (Triggers, SLOs, Datasets, Boards, Queries, Query Results)
- ✅ Phase 7.2: Secondary Resources (Columns, Markers, Recipients, Burn Alerts, Events)
- ✅ Phase 7.3: v2 Team-Scoped Resources (API Keys, Environments)
- ✅ Phase 8: Pagination (API Keys, Environments, Service Map Dependencies)
- ✅ Documentation: MkDocs + Material with auto-generated API reference + 13 resource guides

**Test Coverage:** 159 tests passing | **Doc Validation:** 222 code examples validated

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

### 7.2 Secondary Resources ✓ COMPLETED

| Resource | Implementation | Notes |
|----------|----------------|-------|
| Columns | ✅ `resources/columns.py` | Dataset-scoped column management |
| Markers | ✅ `resources/markers.py` | Dataset-scoped event markers + settings |
| Recipients | ✅ `resources/recipients.py` | Notification targets (email, Slack, PagerDuty, etc.) |
| Burn Alerts | ✅ `resources/burn_alerts.py` | SLO burn rate alerts (exhaustion_time, budget_rate) |
| Events | ✅ `resources/events.py` | Data ingestion (batch/single) |

**Implementation Summary:**
- All 5 secondary resources fully implemented with async + sync variants
- Marker Settings included in Markers resource (list/create/update/delete)
- Events support both single and batch sending with result tracking
- JSON:API format handling for v2 endpoints
- Comprehensive documentation with usage examples
- Files: `src/honeycomb/resources/{columns,markers,recipients,burn_alerts,events}.py`

### 7.3 v2 Team-Scoped Resources ✓ COMPLETED

| Resource | Implementation | Notes |
|----------|----------------|-------|
| API Keys | ✅ `resources/api_keys.py` | Team-scoped key management (ingest & configuration) with auto-pagination |
| Environments | ✅ `resources/environments.py` | Team-scoped environment management with auto-pagination |
| Pipelines | ⏸️ Deferred | Team-scoped (internal, low priority) |

**Implementation Summary:**
- Full CRUD for API Keys and Environments
- JSON:API format support with proper parsing
- Management Key authentication required
- Transparent auto-pagination for list operations
- Delete protection for environments
- Key rotation and security best practices in docs
- Files: `src/honeycomb/resources/{api_keys,environments}.py`

### 7.4 Service Map Dependencies ✓ COMPLETED

| Resource | Implementation | Notes |
|----------|----------------|-------|
| Service Map Dependencies | ✅ `resources/service_map_dependencies.py` | Query service relationships with auto-pagination |

**Implementation Summary:**
- Create/Get/Poll pattern for async dependency queries
- Transparent auto-pagination (default max_pages=640 for safety)
- Time range filtering (absolute or relative timestamps)
- Service filtering by node name
- Polling convenience method (`get_async()`) that creates and waits
- Support for up to 64,000 dependencies (640 pages at 100/page)
- Comprehensive rate limiting documentation
- Files: `src/honeycomb/resources/service_map_dependencies.py`, `src/honeycomb/models/service_map_dependencies.py`

### 7.5 Base Resource Implementation (Reference Pattern)

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

### 7.6 Triggers Resource Example (Reference Pattern)

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

## Phase 8: Pagination ✓ COMPLETED

**Implementation Summary:**
Transparent auto-pagination for all endpoints that support it. Users call `list()` and get complete results automatically.

### 8.1 Paginated Endpoints

| Endpoint | Parameters | Implementation | Notes |
|----------|------------|----------------|-------|
| `/2/teams/{team}/api-keys` | `page[after]`, `page[size]` (max 100) | ✅ Transparent pagination | Small result sets (typically < 100 keys) |
| `/2/teams/{team}/environments` | `page[after]`, `page[size]` (max 100) | ✅ Transparent pagination | Small result sets (typically < 20 envs) |
| `/1/maps/dependencies/requests/{id}` | `page[after]`, `page[size]` (max 100) | ✅ Transparent pagination with `max_pages` | Can return up to 64,000 items (640 pages) |

### 8.2 Service Map Dependencies Resource (NEW)

New resource added for querying service dependencies:
- **Models**: `ServiceMapDependency`, `ServiceMapDependencyRequest`, `ServiceMapDependencyResult`, `ServiceMapNode`
- **Methods**: `create_async()`, `get_result_async()`, `get_async()` (convenience method with polling)
- **Features**:
  - Automatic pagination (default max_pages=640)
  - Polling support for async request processing
  - Time range filtering (absolute or relative)
  - Service filtering
- **Documentation**: Full usage guide with examples
- **Tests**: 9 new tests covering pagination, polling, and filtering

### 8.3 Design Decision: Transparent Pagination

All paginated `list()` methods automatically fetch all pages:

```python
# API Keys - automatically paginates
keys = await client.api_keys.list_async(team="my-team")  # Returns ALL keys

# Environments - automatically paginates
envs = await client.environments.list_async(team="my-team")  # Returns ALL environments

# Service Map Dependencies - transparent with max_pages safety valve
deps = await client.service_map_dependencies.get_async(
    request=ServiceMapDependencyRequestCreate(time_range=7200),
    max_pages=640  # Default, prevents runaway pagination
)
```

**Rationale:**
- Consistent DX with v1 endpoints (all return complete results)
- Small result sets for API Keys/Environments (typically < 100 items)
- `max_pages` parameter provides safety for large Service Map queries
- Rate limiting with exponential backoff prevents overwhelming the API

### 8.4 Rate Limiting Documentation

All paginated methods include documentation about:
- Default rate limit: 100 requests per minute per operation
- Link to Honeycomb support for higher limits: https://www.honeycomb.io/support
- Warning about potential number of requests for large result sets

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
12. ✅ **Secondary resources** - Columns, Markers, Recipients, Burn Alerts, Events (CRUD with tests)
13. ✅ **v2 resources** - API Keys, Environments (team-scoped with JSON:API support)
14. ✅ **Pagination** - Transparent auto-pagination for API Keys, Environments, Service Map Dependencies
15. ✅ **Service Map Dependencies** - Query service relationships with polling and pagination
16. ✅ **Documentation** - MkDocs + Material, auto-generated API reference, validated examples
17. ✅ **CI setup** - Makefile with format, lint, typecheck, test, validate-docs

## Completed Features

### Core Functionality (Production Ready)
- **Client**: Async-first with sync support, configurable retry logic, rate limit handling
- **Authentication**: API keys and Management keys with automatic header management
- **v1 Resources**: Datasets, Triggers, SLOs, Boards, Queries, Query Results, Columns, Markers, Recipients, Burn Alerts, Events, Service Map Dependencies
- **v2 Resources**: API Keys (team-scoped with pagination), Environments (team-scoped with pagination)
- **Models**: Pydantic models for all resources with validation and serialization
- **Error Handling**: 9 specific exception types with request ID tracking
- **Retry Logic**: Exponential backoff with Retry-After header support (RFC 7231 dates)
- **Rate Limiting**: Automatic handling with configurable retry behavior
- **HTTP Methods**: GET, POST, PUT, PATCH, DELETE with headers support
- **Pagination**: Transparent auto-pagination for API Keys, Environments, and Service Map Dependencies

### Developer Experience
- **Documentation**: 21-page MkDocs site with auto-generated API reference
- **Testing**: 159 unit tests (all passing)
- **Code Quality**: Ruff (format + lint), mypy (type checking), all integrated in CI
- **Validation**: 222 documentation code examples validated in CI
- **Live API Testing**: Rate limit test suite with automatic retry verification

### Advanced Features
- **create_and_run**: Convenience method that creates saved query + executes in one call
- **RetryConfig**: Fully customizable retry behavior (delays, statuses, limits)
- **RateLimitInfo**: Parse rate limit headers (multiple formats supported)
- **Multiple error formats**: RFC 7807, JSON:API, simple JSON
- **Batch Event Sending**: Efficient event ingestion with per-event status tracking
- **Marker Settings**: Color configuration for marker types
- **Delete Protection**: Environment safety with delete-protected flag
- **Transparent Pagination**: Automatic multi-page result fetching with max_pages safety valve
- **Service Map Queries**: Query service dependencies with polling and automatic pagination

## Key Metrics

| Metric | Count |
|--------|-------|
| **Test Coverage** | 159 tests passing |
| **Doc Examples** | 222 code blocks validated |
| **Resources Implemented** | 14 resources (12 v1 + 2 v2) |
| **Models** | 37+ Pydantic models |
| **Exceptions** | 9 specific types |
| **Doc Pages** | 21 pages |
| **Type Coverage** | 100% (mypy strict on src/) |

## Next Steps (Recommended Priority)

1. **GitHub Actions CI/CD** - Automate testing and docs deployment
2. **PyPI Publishing** - Make package publicly available
3. **Claude Tool Definitions** - Generate LLM tool definitions for agent workflows (Phase 11)
4. **CLI Tool** - Command-line interface for CRUD operations (Phase 12)

---

## Phase 11: Claude Tool Definition Generator

**Purpose:** Generate Claude-compatible tool definitions from the `honeycomb-api-python` library, enabling LLMs to create and manage Honeycomb resources (triggers, SLOs, boards, queries) via structured tool calls.

**Specification:** See [HONEYCOMB_API_TOOL_GENERATOR_SPEC.md](HONEYCOMB_API_TOOL_GENERATOR_SPEC.md) for detailed requirements.

### 11.1 Use Cases

- **LLM Tool Calls**: Enable Claude to create/manage Honeycomb resources via structured output
- **Datadog Migration**: Power automated translation of Datadog monitors to Honeycomb triggers
- **Agent Workflows**: Build autonomous agents that manage observability infrastructure
- **API Integration**: Direct usage with Anthropic SDK's `tools` parameter

### 11.2 Output Format (Claude Tool Schema)

```json
{
  "name": "honeycomb_create_trigger",
  "description": "Creates a new trigger (alert) in Honeycomb that fires when query results cross a threshold...",
  "input_schema": {
    "type": "object",
    "properties": { ... },
    "required": [ ... ]
  },
  "input_examples": [ ... ]
}
```

### 11.3 Tool Naming Convention

| Resource | Operation | Tool Name |
|----------|-----------|-----------|
| Trigger | Create | `honeycomb_create_trigger` |
| Trigger | List | `honeycomb_list_triggers` |
| Trigger | Get | `honeycomb_get_trigger` |
| Trigger | Update | `honeycomb_update_trigger` |
| Trigger | Delete | `honeycomb_delete_trigger` |
| SLO | Create | `honeycomb_create_slo` |
| SLO | List | `honeycomb_list_slos` |
| SLO | Get | `honeycomb_get_slo` |
| SLO | Update | `honeycomb_update_slo` |
| SLO | Delete | `honeycomb_delete_slo` |
| Burn Alert | Create | `honeycomb_create_burn_alert` |
| Burn Alert | List | `honeycomb_list_burn_alerts` |
| Burn Alert | Get | `honeycomb_get_burn_alert` |
| Burn Alert | Update | `honeycomb_update_burn_alert` |
| Burn Alert | Delete | `honeycomb_delete_burn_alert` |
| Board | Create | `honeycomb_create_board` |
| Board | List | `honeycomb_list_boards` |
| Board | Get | `honeycomb_get_board` |
| Board | Update | `honeycomb_update_board` |
| Board | Delete | `honeycomb_delete_board` |
| Query | Create | `honeycomb_create_query` |
| Query | Get | `honeycomb_get_query` |
| Query | Run | `honeycomb_run_query` |
| Query | Get Results | `honeycomb_get_query_results` |
| Dataset | Create | `honeycomb_create_dataset` |
| Dataset | List | `honeycomb_list_datasets` |
| Dataset | Get | `honeycomb_get_dataset` |
| Dataset | Update | `honeycomb_update_dataset` |
| Dataset | Delete | `honeycomb_delete_dataset` |
| Column | List | `honeycomb_list_columns` |
| Column | Get | `honeycomb_get_column` |
| Column | Create | `honeycomb_create_column` |
| Column | Update | `honeycomb_update_column` |
| Column | Delete | `honeycomb_delete_column` |
| Derived Column | Create | `honeycomb_create_derived_column` |
| Derived Column | List | `honeycomb_list_derived_columns` |
| Derived Column | Get | `honeycomb_get_derived_column` |
| Derived Column | Update | `honeycomb_update_derived_column` |
| Derived Column | Delete | `honeycomb_delete_derived_column` |
| Recipient | Create | `honeycomb_create_recipient` |
| Recipient | List | `honeycomb_list_recipients` |
| Recipient | Get | `honeycomb_get_recipient` |
| Recipient | Update | `honeycomb_update_recipient` |
| Recipient | Delete | `honeycomb_delete_recipient` |
| Marker | Create | `honeycomb_create_marker` |
| Marker | List | `honeycomb_list_markers` |
| Marker | Update | `honeycomb_update_marker` |
| Marker | Delete | `honeycomb_delete_marker` |
| Marker Setting | Create | `honeycomb_create_marker_setting` |
| Marker Setting | List | `honeycomb_list_marker_settings` |
| Marker Setting | Get | `honeycomb_get_marker_setting` |
| Marker Setting | Update | `honeycomb_update_marker_setting` |
| Marker Setting | Delete | `honeycomb_delete_marker_setting` |
| Query Annotation | Create | `honeycomb_create_query_annotation` |
| Query Annotation | List | `honeycomb_list_query_annotations` |
| Query Annotation | Get | `honeycomb_get_query_annotation` |
| Query Annotation | Update | `honeycomb_update_query_annotation` |
| Query Annotation | Delete | `honeycomb_delete_query_annotation` |
| Event | Send | `honeycomb_send_event` |
| Event | Send Batch | `honeycomb_send_events_batch` |

**Constraints:** Prefix `honeycomb_`, snake_case, max 64 chars, `[a-zA-Z0-9_-]` only

### 11.4 Description Quality Requirements

Each tool description MUST include:
1. **What it does** (1 sentence)
2. **When to use it** (1 sentence)
3. **Key parameters explained** (1-2 sentences)
4. **Important caveats/limitations** (if any)

**Good example:**
```
Creates a new trigger (alert) in Honeycomb that fires when query results cross a threshold.
Use this when migrating Datadog monitors or creating new alerting rules.
Requires a dataset, query specification with calculations/filters, threshold operator and value,
and frequency (how often to evaluate). Note: Recipients must already exist in Honeycomb.
```

### 11.5 Input Schema Generation

Generate JSON Schema from Pydantic models with:

| Python Type | JSON Schema |
|-------------|-------------|
| `str` | `{"type": "string"}` |
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `bool` | `{"type": "boolean"}` |
| `list[T]` | `{"type": "array", "items": {...}}` |
| `Optional[T]` | Include in properties, exclude from required |
| `Literal["a", "b"]` | `{"type": "string", "enum": ["a", "b"]}` |
| `Enum` | `{"type": "string", "enum": [...values...]}` |

**Every field MUST have a description** extracted from Pydantic `Field(description=...)` or docstrings.

### 11.6 Input Examples

Generate 2-3 examples per tool:
1. Minimal required fields only
2. Common use case with optional fields
3. Complex/advanced usage (if applicable)

```json
"input_examples": [
  {
    "dataset": "api-logs",
    "name": "High Error Rate",
    "query": {
      "calculations": [{"op": "COUNT"}],
      "filters": [{"column": "status_code", "op": ">=", "value": 500}],
      "time_range": 900
    },
    "threshold": {"op": ">", "value": 100},
    "frequency": 900
  }
]
```

### 11.7 Resources Priority

**Priority 1 (Migration Critical):**
- Triggers: create, list, get, update, delete
- SLOs: create, list, get, update, delete
- Burn Alerts: create, list, get, update, delete

**Priority 2 (Observability Infrastructure):**
- Boards: create, list, get, update, delete
- Queries: create, get, run, get_results
- Derived Columns: create, list, get, update, delete
- Recipients: create, list, get, update, delete

**Priority 3 (Full Coverage):**
- Datasets: create, list, get, update, delete
- Columns: list, get, create, update, delete
- Markers: create, list, update, delete
- Marker Settings: create, list, get, update, delete
- Query Annotations: create, list, get, update, delete
- Events: send, send_batch

### 11.8 Output Formats

**JSON File:**
```json
{
  "tools": [...],
  "version": "0.1.0",
  "generated_at": "2025-12-27T12:00:00Z"
}
```

**Python Module:**
```python
# src/honeycomb/tools/__init__.py
HONEYCOMB_TOOLS: list[dict[str, Any]] = [...]

def get_tool(name: str) -> dict[str, Any] | None: ...
def get_all_tools() -> list[dict[str, Any]]: ...
```

### 11.9 Generator CLI

```bash
# Generate all tools
poetry run python -m honeycomb.tools generate --output tools.json

# Generate specific resource
poetry run python -m honeycomb.tools generate --resource triggers --output triggers.json

# Validate existing definitions
poetry run python -m honeycomb.tools validate tools.json

# Generate Python module
poetry run python -m honeycomb.tools generate --format python --output src/honeycomb/tools/definitions.py
```

### 11.10 Implementation Approach

Use **Introspection from Pydantic Models + Manual Description Override**:

```python
# src/honeycomb/tools/generator.py

from pydantic import BaseModel
from typing import Callable, Any

def generate_tool_from_method(
    resource_name: str,
    method_name: str,
    method: Callable,
    input_model: type[BaseModel] | None = None,
    description_override: str | None = None,
) -> dict[str, Any]:
    """Generate a Claude tool definition from an API client method."""

    # Extract schema from Pydantic model
    if input_model:
        schema = input_model.model_json_schema()
    else:
        schema = _schema_from_signature(method)

    # Use override or build from docstring
    description = description_override or _build_description(
        method.__doc__, resource_name, method_name
    )

    return {
        "name": f"honeycomb_{method_name}_{resource_name}",
        "description": description,
        "input_schema": schema,
    }
```

### 11.11 Builder Integration Strategy

For complex resources (Boards, SLOs, Triggers, Queries), tool schemas accept nested structures that map directly to our Builder pattern. This enables **single-call creation** of resources that would otherwise require multiple sequential API calls.

**Builder-Enabled Resources:**

| Resource | Builder | Orchestration Method | Creates Automatically |
|----------|---------|---------------------|----------------------|
| Board | `BoardBuilder` | `boards.create_from_bundle_async()` | Queries, Annotations, SLOs, Derived Columns |
| SLO | `SLOBuilder` | `slos.create_from_bundle_async()` | Derived Columns, Burn Alerts |
| Trigger | `TriggerBuilder` | `triggers.create_async()` | Embedded Query Spec |
| Query | `QueryBuilder` | `queries.create_async()` | Query with dataset scope |

**Benefits:**
- **Single tool call** - LLM says "create board with these charts" not "create query, then board"
- **No ID management** - LLM doesn't track intermediate query/annotation IDs
- **Hidden complexity** - Derived columns, query annotations created automatically
- **Matches mental model** - LLMs think hierarchically, not in sequential API calls

**Example: Board with Inline Queries and SLOs**

Tool input from LLM:
```json
{
  "name": "Service Dashboard",
  "layout": "auto",
  "panels": [
    {
      "type": "query",
      "name": "Request Count",
      "dataset": "api-logs",
      "calculations": [{"op": "COUNT"}],
      "group_by": ["service"],
      "time_range": 3600
    },
    {
      "type": "slo",
      "name": "API Availability",
      "dataset": "api-logs",
      "target_percentage": 99.9,
      "sli": {"alias": "success", "expression": "IF(LT($status_code, 500), 1, 0)"}
    }
  ]
}
```

Executor converts to Builder pattern internally (see 11.12).

**Example: SLO with Burn Alerts**

Tool input from LLM:
```json
{
  "name": "API Availability",
  "dataset": "api-logs",
  "target_percentage": 99.9,
  "time_period_days": 30,
  "sli": {
    "alias": "success_rate",
    "expression": "IF(LT($status_code, 500), 1, 0)"
  },
  "burn_alerts": [
    {
      "type": "exhaustion_time",
      "threshold_minutes": 60,
      "recipients": [{"type": "email", "target": "oncall@example.com"}]
    }
  ]
}
```

**Example: Trigger with Inline Query**

Tool input from LLM:
```json
{
  "name": "High Error Rate",
  "dataset": "api-logs",
  "query": {
    "calculations": [{"op": "COUNT"}],
    "filters": [{"column": "status_code", "op": ">=", "value": 500}],
    "time_range": 900
  },
  "threshold": {"op": ">", "value": 100},
  "frequency": 900,
  "recipients": [{"type": "email", "target": "oncall@example.com"}]
}
```

### 11.12 Tool Execution Handler

```python
# src/honeycomb/tools/executor.py

from honeycomb import (
    HoneycombClient, QueryBuilder, BoardBuilder, SLOBuilder, TriggerBuilder
)

async def execute_tool(
    client: HoneycombClient,
    tool_name: str,
    tool_input: dict,
) -> str:
    """Execute a Honeycomb tool and return the result as JSON string."""

    # === BUILDER-ENABLED RESOURCES (single-call complex creation) ===

    if tool_name == "honeycomb_create_board":
        builder = BoardBuilder(tool_input["name"])
        if tool_input.get("layout") == "auto":
            builder.auto_layout()

        for panel in tool_input.get("panels", []):
            if panel["type"] == "query":
                qb = _build_query(panel)
                builder.query(qb, style=panel.get("style", "graph"))
            elif panel["type"] == "slo":
                sb = _build_slo(panel)
                builder.slo(sb)
            elif panel["type"] == "text":
                builder.text(panel["content"])

        result = await client.boards.create_from_bundle_async(builder.build())
        return json.dumps(result.model_dump())

    elif tool_name == "honeycomb_create_slo":
        builder = _build_slo(tool_input)
        result = await client.slos.create_from_bundle_async(builder.build())
        # Returns dict of created SLOs (main + any from burn alerts)
        return json.dumps({k: v.model_dump() for k, v in result.items()})

    elif tool_name == "honeycomb_create_trigger":
        builder = _build_trigger(tool_input)
        result = await client.triggers.create_async(
            dataset=tool_input["dataset"],
            trigger=builder.build()
        )
        return json.dumps(result.model_dump())

    elif tool_name == "honeycomb_run_query":
        builder = _build_query(tool_input)
        result = await client.query_results.create_and_run_async(builder)
        return json.dumps(result.model_dump())

    # === SIMPLE CRUD OPERATIONS ===

    elif tool_name == "honeycomb_list_triggers":
        result = await client.triggers.list_async(dataset=tool_input["dataset"])
        return json.dumps([t.model_dump() for t in result])

    elif tool_name == "honeycomb_get_trigger":
        result = await client.triggers.get_async(
            dataset=tool_input["dataset"],
            trigger_id=tool_input["trigger_id"]
        )
        return json.dumps(result.model_dump())

    # ... other tools

    raise ValueError(f"Unknown tool: {tool_name}")


def _build_query(data: dict) -> QueryBuilder:
    """Convert tool input to QueryBuilder."""
    qb = QueryBuilder(data.get("name", "Query"))
    qb.dataset(data["dataset"])

    if "time_range" in data:
        qb.time_range(data["time_range"])

    for calc in data.get("calculations", []):
        op = calc["op"].lower()
        col = calc.get("column")
        if op == "count":
            qb.count()
        elif op == "avg":
            qb.avg(col)
        elif op == "sum":
            qb.sum(col)
        elif op == "max":
            qb.max(col)
        elif op == "min":
            qb.min(col)
        elif op.startswith("p"):
            qb.percentile(col, int(op[1:]))
        # ... other ops

    for f in data.get("filters", []):
        qb.filter(f["column"], f["op"], f.get("value"))

    for col in data.get("group_by", []):
        qb.group_by(col)

    return qb


def _build_slo(data: dict) -> SLOBuilder:
    """Convert tool input to SLOBuilder."""
    builder = SLOBuilder(data["name"]).dataset(data["dataset"])

    if "target_percentage" in data:
        builder.target_percentage(data["target_percentage"])
    elif "target_per_million" in data:
        builder.target_per_million(data["target_per_million"])

    if "time_period_days" in data:
        builder.time_period(data["time_period_days"])

    sli = data["sli"]
    if "expression" in sli:
        builder.sli(sli["alias"], sli["expression"], sli.get("description"))
    else:
        builder.sli(sli["alias"])  # Existing derived column

    for ba in data.get("burn_alerts", []):
        if ba["type"] == "exhaustion_time":
            builder.exhaustion_time_alert(ba["threshold_minutes"])
        elif ba["type"] == "budget_rate":
            builder.budget_rate_alert(ba["threshold_percent"], ba["window_minutes"])
        # Add recipients to the burn alert
        for r in ba.get("recipients", []):
            if r["type"] == "email":
                builder.email(r["target"])
            elif r["type"] == "slack":
                builder.slack(r["target"])
            # ... other recipient types

    return builder


def _build_trigger(data: dict) -> TriggerBuilder:
    """Convert tool input to TriggerBuilder."""
    builder = TriggerBuilder(data["name"]).dataset(data["dataset"])

    query = data["query"]
    if "time_range" in query:
        builder.time_range(query["time_range"])

    for calc in query.get("calculations", []):
        op = calc["op"].lower()
        col = calc.get("column")
        if op == "count":
            builder.count()
        elif op == "avg":
            builder.avg(col)
        # ... single calculation only for triggers

    for f in query.get("filters", []):
        builder.filter(f["column"], f["op"], f.get("value"))

    threshold = data["threshold"]
    if threshold["op"] == ">":
        builder.threshold_gt(threshold["value"])
    elif threshold["op"] == ">=":
        builder.threshold_gte(threshold["value"])
    elif threshold["op"] == "<":
        builder.threshold_lt(threshold["value"])
    elif threshold["op"] == "<=":
        builder.threshold_lte(threshold["value"])

    if "frequency" in data:
        builder.frequency(data["frequency"])

    for r in data.get("recipients", []):
        if r["type"] == "email":
            builder.email(r["target"])
        elif r["type"] == "slack":
            builder.slack(r["target"])
        elif r["type"] == "pagerduty":
            builder.pagerduty(r["target"])
        # ... other recipient types

    return builder
```

### 11.13 Anthropic SDK Integration

```python
from anthropic import Anthropic
from honeycomb.tools import HONEYCOMB_TOOLS, execute_tool
from honeycomb import HoneycombClient

anthropic = Anthropic()
honeycomb = HoneycombClient(api_key="...")

response = anthropic.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    tools=HONEYCOMB_TOOLS,  # Direct usage
    messages=[
        {"role": "user", "content": "Create a trigger for high error rates in api-logs"}
    ]
)

# Execute tool calls
for block in response.content:
    if block.type == "tool_use":
        result = await execute_tool(honeycomb, block.name, block.input)
```

### 11.14 Package Structure

```
src/honeycomb/
├── tools/
│   ├── __init__.py           # Exports HONEYCOMB_TOOLS, get_tool(), get_all_tools()
│   ├── generator.py          # Tool definition generator
│   ├── executor.py           # Tool execution handler (with Builder integration)
│   ├── validator.py          # Schema validation
│   ├── descriptions.py       # Hand-crafted description overrides
│   ├── builders.py           # _build_query(), _build_slo(), _build_trigger() helpers
│   └── definitions/          # Generated tool definitions (optional)
│       ├── triggers.py
│       ├── slos.py
│       ├── boards.py
│       └── ...
```

### 11.15 Validation Requirements

The generator MUST validate:
1. Tool names match `^[a-zA-Z0-9_-]{1,64}$`
2. Descriptions are non-empty and >= 50 characters
3. Input schemas are valid JSON Schema draft-07
4. Required fields are listed in `required` array
5. Examples validate against the schema (if provided)

### 11.16 Claude API Integration Tests (Eval Suite with DeepEval)

Reference implementation using [DeepEval](https://github.com/confident-ai/deepeval) to validate tool definitions against the real Claude API. DeepEval runs fully standalone without any SaaS requirement.

**Why DeepEval:**
- Pytest-native integration (fits with our existing 481 tests)
- `ToolCorrectnessMetric` validates tool selection accuracy
- `ArgumentCorrectnessMetric` validates parameter quality
- Apache 2.0 open source, runs locally without cloud dependency
- Can use Claude or local LLMs (Ollama) as the evaluation judge

**Optional Dependencies:**

```toml
# pyproject.toml
[project.optional-dependencies]
evals = [
    "deepeval>=1.0",
    "anthropic>=0.40.0",
]
```

**Test Categories:**

| Category | DeepEval Metric | What It Validates |
|----------|-----------------|------------------|
| Tool Selection | `ToolCorrectnessMetric` | Claude picks the correct tool |
| Parameter Quality | `ArgumentCorrectnessMetric` | Claude generates valid parameters |
| Schema Acceptance | Manual assertion | Claude parses tool definitions |
| End-to-End | Custom + Honeycomb API | Full loop execution |

**Test Structure:**

```python
# tests/integration/test_claude_tools_eval.py

import os
import json
import pytest
from anthropic import Anthropic
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import ToolCorrectnessMetric, ArgumentCorrectnessMetric

from honeycomb import HoneycombClient
from honeycomb.tools import HONEYCOMB_TOOLS, execute_tool

pytestmark = [
    pytest.mark.evals,   # Requires ANTHROPIC_API_KEY
    pytest.mark.live,    # Requires HONEYCOMB_API_KEY (for E2E tests)
]


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def anthropic_client():
    return Anthropic()  # Uses ANTHROPIC_API_KEY env var


@pytest.fixture
async def honeycomb_client():
    async with HoneycombClient(api_key=os.environ["HONEYCOMB_API_KEY"]) as client:
        yield client


def call_claude_with_tools(client: Anthropic, prompt: str) -> dict:
    """Call Claude with Honeycomb tools, return parsed response."""
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        tools=HONEYCOMB_TOOLS,
        messages=[{"role": "user", "content": prompt}]
    )
    tool_calls = [b for b in response.content if b.type == "tool_use"]
    text_content = " ".join(b.text for b in response.content if hasattr(b, "text"))
    return {
        "tool_calls": tool_calls,
        "text": text_content,
        "stop_reason": response.stop_reason,
    }


# ============================================================================
# Schema Acceptance Tests
# ============================================================================

class TestToolSchemaAcceptance:
    """Verify Claude accepts our tool definitions without error."""

    def test_all_tools_accepted(self, anthropic_client):
        """Claude should parse all tool definitions successfully."""
        result = call_claude_with_tools(anthropic_client, "What tools do you have?")
        assert result["stop_reason"] in ("end_turn", "tool_use")


# ============================================================================
# Tool Selection Tests (DeepEval ToolCorrectnessMetric)
# ============================================================================

class TestToolSelection:
    """Verify Claude selects appropriate tools using DeepEval metrics."""

    @pytest.mark.parametrize("prompt,expected_tool", [
        ("Create a trigger for high error rates in api-logs", "honeycomb_create_trigger"),
        ("List all SLOs in the production dataset", "honeycomb_list_slos"),
        ("Create a dashboard showing request counts and latency", "honeycomb_create_board"),
        ("Run a query to count errors in the last hour", "honeycomb_run_query"),
        ("Delete the trigger with ID abc123 from my-dataset", "honeycomb_delete_trigger"),
        ("Get details about the SLO slo-456 in production", "honeycomb_get_slo"),
    ])
    def test_tool_selection(self, anthropic_client, prompt, expected_tool):
        """Claude should select the correct tool for each prompt."""
        result = call_claude_with_tools(anthropic_client, prompt)

        # Build DeepEval test case
        tools_called = [
            ToolCall(name=tc.name, input_parameters=tc.input)
            for tc in result["tool_calls"]
        ]

        test_case = LLMTestCase(
            input=prompt,
            actual_output=result["text"] or f"Tool call: {result['tool_calls'][0].name}",
            tools_called=tools_called,
            expected_tools=[ToolCall(name=expected_tool)],
        )

        # Evaluate with DeepEval
        metric = ToolCorrectnessMetric(threshold=0.9)
        assert_test(test_case, [metric])


# ============================================================================
# Parameter Quality Tests (DeepEval ArgumentCorrectnessMetric)
# ============================================================================

class TestParameterQuality:
    """Verify Claude generates valid parameters using DeepEval metrics."""

    def test_trigger_params_complete(self, anthropic_client):
        """Trigger parameters should include all required fields."""
        prompt = (
            "Create a trigger named 'High Errors' in dataset 'api-logs' "
            "that fires when error count > 100 in the last 15 minutes"
        )
        result = call_claude_with_tools(anthropic_client, prompt)
        tool_call = result["tool_calls"][0]

        # Build test case with expected parameter structure
        test_case = LLMTestCase(
            input=prompt,
            actual_output=json.dumps(tool_call.input),
            tools_called=[ToolCall(
                name=tool_call.name,
                input_parameters=tool_call.input,
            )],
            expected_tools=[ToolCall(
                name="honeycomb_create_trigger",
                input_parameters={
                    "name": "High Errors",
                    "dataset": "api-logs",
                    "query": {"calculations": [{"op": "COUNT"}], "time_range": 900},
                    "threshold": {"op": ">", "value": 100},
                },
            )],
        )

        # Use ArgumentCorrectnessMetric for parameter validation
        metric = ArgumentCorrectnessMetric(threshold=0.8)
        assert_test(test_case, [metric])

    def test_slo_params_complete(self, anthropic_client):
        """SLO parameters should include target and SLI."""
        prompt = (
            "Create an SLO named 'API Availability' in dataset 'api-logs' "
            "with 99.9% target over 30 days, using success_rate as the SLI"
        )
        result = call_claude_with_tools(anthropic_client, prompt)
        tool_call = result["tool_calls"][0]

        test_case = LLMTestCase(
            input=prompt,
            actual_output=json.dumps(tool_call.input),
            tools_called=[ToolCall(
                name=tool_call.name,
                input_parameters=tool_call.input,
            )],
            expected_tools=[ToolCall(
                name="honeycomb_create_slo",
                input_parameters={
                    "name": "API Availability",
                    "dataset": "api-logs",
                    "target_percentage": 99.9,
                    "time_period_days": 30,
                    "sli": {"alias": "success_rate"},
                },
            )],
        )

        metric = ArgumentCorrectnessMetric(threshold=0.8)
        assert_test(test_case, [metric])


# ============================================================================
# End-to-End Tests (Claude → Executor → Honeycomb API)
# ============================================================================

class TestEndToEnd:
    """Full integration: Claude → Executor → Honeycomb API."""

    @pytest.mark.live
    async def test_create_and_cleanup_trigger(self, anthropic_client, honeycomb_client):
        """Create a trigger via Claude, verify in Honeycomb, then clean up."""
        prompt = (
            "Create a trigger named 'DeepEval Test Trigger' in dataset "
            "'claude-tool-test' that alerts when COUNT > 50"
        )
        result = call_claude_with_tools(anthropic_client, prompt)
        tool_call = result["tool_calls"][0]

        # Verify correct tool selected
        assert tool_call.name == "honeycomb_create_trigger"

        # Execute via our handler
        result_json = await execute_tool(
            honeycomb_client,
            tool_call.name,
            tool_call.input
        )
        created = json.loads(result_json)

        try:
            # Verify trigger was created
            assert "id" in created
            assert created["name"] == "DeepEval Test Trigger"

            # Verify it exists in Honeycomb
            fetched = await honeycomb_client.triggers.get_async(
                dataset="claude-tool-test",
                trigger_id=created["id"]
            )
            assert fetched.name == "DeepEval Test Trigger"
        finally:
            # Clean up
            await honeycomb_client.triggers.delete_async(
                dataset="claude-tool-test",
                trigger_id=created["id"]
            )
```

**Running the Tests:**

```bash
# Install eval dependencies
poetry install --extras evals

# Run all eval tests (requires both API keys)
ANTHROPIC_API_KEY=sk-ant-... HONEYCOMB_API_KEY=... \
    poetry run pytest tests/integration/test_claude_tools_eval.py -v

# Run just tool selection tests (no Honeycomb needed)
ANTHROPIC_API_KEY=sk-ant-... \
    poetry run pytest tests/integration/test_claude_tools_eval.py -v -k "TestToolSelection"

# Run with DeepEval's enhanced output
ANTHROPIC_API_KEY=sk-ant-... \
    poetry run deepeval test run tests/integration/test_claude_tools_eval.py

# Skip eval tests in regular CI
poetry run pytest --ignore=tests/integration/test_claude_tools_eval.py
```

**Using Local LLM as Judge (Fully Offline):**

```python
# For air-gapped environments, use Ollama as the evaluation judge
from deepeval.models import OllamaModel

local_judge = OllamaModel(model="llama3.2")
metric = ToolCorrectnessMetric(model=local_judge, threshold=0.9)
```

**Credentials Management:**

```bash
# .envrc (gitignored)
export ANTHROPIC_API_KEY="sk-ant-..."
export HONEYCOMB_API_KEY="..."
```

### 11.17 Deliverables

- [ ] Tool definition generator (`src/honeycomb/tools/generator.py`)
- [ ] Tool execution handler with Builder integration (`src/honeycomb/tools/executor.py`)
- [ ] Builder helper functions (`_build_query`, `_build_slo`, `_build_trigger`)
- [ ] Hand-crafted descriptions for Priority 1 resources
- [ ] Generated tool definitions (JSON + Python module)
- [ ] Generator CLI (`python -m honeycomb.tools`)
- [ ] Makefile targets: `make generate-tools`, `make validate-tools`
- [ ] Unit tests for generator and executor
- [ ] DeepEval integration tests (`tests/integration/test_claude_tools_eval.py`)
  - [ ] Tool selection tests with `ToolCorrectnessMetric`
  - [ ] Parameter quality tests with `ArgumentCorrectnessMetric`
  - [ ] End-to-end tests with Honeycomb API
- [ ] Optional `evals` dependency group (deepeval, anthropic)
- [ ] Documentation page in MkDocs
- [ ] Example integration with Anthropic SDK

---

## Phase 12: CLI Tool

**Purpose:** Provide a `honeycomb` CLI for ergonomic CRUD operations, particularly useful for porting objects between Honeycomb teams/environments.

### 12.1 Framework Choice

**Typer** - Modern CLI framework using Python type hints
- Auto-generates help text and shell completion
- Rich integration for beautiful output
- Minimal boilerplate

### 12.2 Dependencies

```toml
# pyproject.toml additions
[project.optional-dependencies]
cli = [
    "typer[all]>=0.9.0",
    "rich>=13.0",
]

[project.scripts]
honeycomb = "honeycomb.cli:app"
```

### 12.3 Authentication

Support multiple auth mechanisms for team/environment porting:

```bash
# Environment variables (default)
export HONEYCOMB_API_KEY=hcaik_xxx
honeycomb triggers list --dataset my-dataset

# Explicit key override
honeycomb triggers list --dataset my-dataset --api-key hcaik_other

# Named profiles for multi-team workflows
honeycomb config add-profile production --api-key hcaik_prod
honeycomb config add-profile staging --api-key hcaik_staging
honeycomb triggers list --dataset my-dataset --profile production

# Config file location: ~/.honeycomb/config.yaml
```

**Config file format:**
```yaml
# ~/.honeycomb/config.yaml
default_profile: production
profiles:
  production:
    api_key: hcaik_prod_xxx
    base_url: https://api.honeycomb.io  # optional
  staging:
    api_key: hcaik_staging_xxx
  eu_production:
    api_key: hcaik_eu_xxx
    base_url: https://api.eu1.honeycomb.io
```

### 12.4 Command Structure

```bash
honeycomb <resource> <action> [options]
```

**Resources and actions:**
```bash
# Triggers
honeycomb triggers list --dataset my-dataset
honeycomb triggers get <id> --dataset my-dataset
honeycomb triggers create --dataset my-dataset --from-file trigger.json
honeycomb triggers update <id> --dataset my-dataset --from-file trigger.json
honeycomb triggers delete <id> --dataset my-dataset
honeycomb triggers export <id> --dataset my-dataset > trigger.json

# SLOs
honeycomb slos list --dataset my-dataset
honeycomb slos get <id> --dataset my-dataset
honeycomb slos create --dataset my-dataset --from-file slo.json
honeycomb slos export <id> --dataset my-dataset > slo.json

# Boards
honeycomb boards list
honeycomb boards get <id>
honeycomb boards create --from-file board.json
honeycomb boards export <id> > board.json

# Queries
honeycomb queries run --dataset my-dataset --spec '{"calculations": [{"op": "COUNT"}]}'
honeycomb queries run --dataset my-dataset --from-file query.json

# Datasets
honeycomb datasets list
honeycomb datasets get <slug>
honeycomb datasets create --name "My Dataset" --slug my-dataset

# Config management
honeycomb config show
honeycomb config add-profile <name> --api-key <key>
honeycomb config remove-profile <name>
honeycomb config set-default <name>
```

### 12.5 Output Formats

```bash
# Default: Rich table output
honeycomb triggers list --dataset my-dataset

# JSON output for piping/scripting
honeycomb triggers list --dataset my-dataset --output json

# YAML output
honeycomb triggers list --dataset my-dataset --output yaml

# Quiet mode (IDs only)
honeycomb triggers list --dataset my-dataset --quiet
```

### 12.6 Porting Workflow

Primary use case: copy objects between teams/environments

```bash
# Export from production
honeycomb triggers export trigger-123 \
    --dataset my-dataset \
    --profile production > trigger.json

# Import to staging (IDs are stripped/regenerated)
honeycomb triggers create \
    --dataset my-dataset \
    --profile staging \
    --from-file trigger.json

# Bulk export all triggers
honeycomb triggers list --dataset my-dataset --profile production --output json \
    | jq '.[]' > triggers/

# Or with built-in bulk export
honeycomb triggers export-all --dataset my-dataset --profile production --output-dir triggers/
```

### 12.7 Package Structure

```
src/honeycomb/
├── cli/
│   ├── __init__.py          # Main Typer app
│   ├── config.py            # Profile/config management
│   ├── formatters.py        # Output formatting (table, json, yaml)
│   ├── triggers.py          # honeycomb triggers <action>
│   ├── slos.py              # honeycomb slos <action>
│   ├── boards.py            # honeycomb boards <action>
│   ├── queries.py           # honeycomb queries <action>
│   ├── datasets.py          # honeycomb datasets <action>
│   └── schemas.py           # honeycomb export-schemas
```

### 12.8 Implementation Example

```python
# cli/__init__.py
import typer
from rich.console import Console

app = typer.Typer(
    name="honeycomb",
    help="CLI for Honeycomb.io API operations",
    no_args_is_help=True,
)
console = Console()

# Import and register subcommands
from honeycomb.cli import triggers, slos, boards, queries, datasets, config

app.add_typer(triggers.app, name="triggers")
app.add_typer(slos.app, name="slos")
app.add_typer(boards.app, name="boards")
app.add_typer(queries.app, name="queries")
app.add_typer(datasets.app, name="datasets")
app.add_typer(config.app, name="config")
```

```python
# cli/triggers.py
import typer
from typing import Optional
from pathlib import Path
from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import output_result, OutputFormat

app = typer.Typer(help="Manage triggers")

@app.command("list")
def list_triggers(
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(OutputFormat.table, "--output", "-o"),
):
    """List all triggers in a dataset."""
    client = get_client(profile=profile, api_key=api_key)
    triggers = client.triggers.list(dataset=dataset)
    output_result(triggers, output, columns=["id", "name", "disabled", "frequency"])

@app.command("get")
def get_trigger(
    trigger_id: str = typer.Argument(..., help="Trigger ID"),
    dataset: str = typer.Option(..., "--dataset", "-d"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(OutputFormat.json, "--output", "-o"),
):
    """Get a specific trigger."""
    client = get_client(profile=profile, api_key=api_key)
    trigger = client.triggers.get(dataset=dataset, trigger_id=trigger_id)
    output_result(trigger, output)

@app.command("create")
def create_trigger(
    dataset: str = typer.Option(..., "--dataset", "-d"),
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with trigger config"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(OutputFormat.json, "--output", "-o"),
):
    """Create a trigger from a JSON file."""
    import json
    from honeycomb.models import TriggerCreate

    client = get_client(profile=profile, api_key=api_key)
    data = json.loads(from_file.read_text())

    # Strip IDs and timestamps for import
    data.pop("id", None)
    data.pop("created_at", None)
    data.pop("updated_at", None)

    trigger_create = TriggerCreate.model_validate(data)
    trigger = client.triggers.create(dataset=dataset, trigger=trigger_create)
    output_result(trigger, output)

@app.command("export")
def export_trigger(
    trigger_id: str = typer.Argument(..., help="Trigger ID"),
    dataset: str = typer.Option(..., "--dataset", "-d"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
):
    """Export a trigger as JSON (suitable for import to another environment)."""
    import json
    client = get_client(profile=profile, api_key=api_key)
    trigger = client.triggers.get(dataset=dataset, trigger_id=trigger_id)

    # Export without IDs/timestamps for portability
    data = trigger.model_dump(exclude={"id", "created_at", "updated_at"})
    print(json.dumps(data, indent=2, default=str))
```

### 12.9 Deliverables

- [ ] CLI package structure (`src/honeycomb/cli/`)
- [ ] Config file management (profiles, credentials)
- [ ] Resource commands: triggers, slos, boards, queries, datasets
- [ ] Output formatters (table, json, yaml)
- [ ] Export/import workflow for porting
- [ ] Shell completion support
- [ ] CLI documentation page in MkDocs
- [ ] Tests for CLI commands

### 12.10 Future CLI Enhancements

- **Bulk operations**: `honeycomb triggers export-all`, `honeycomb triggers import-all`
- **Diff command**: `honeycomb triggers diff <id> --profile prod --compare-profile staging`
- **Watch mode**: `honeycomb query run --watch --interval 30`
- **Interactive mode**: `honeycomb shell` (REPL with autocomplete)

---

## Future Enhancements (Nice-to-Have)

- **Caching**: Optional response caching with TTL
- **OpenTelemetry**: Built-in tracing instrumentation
- **VCR-style recording**: Cassette recording for integration tests
- **Streaming Events**: Async event ingestion with batching

## References

- [Honeycomb API Docs](https://docs.honeycomb.io/api/)
- [OpenAPI Spec](https://api.honeycomb.io/api.yaml)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
