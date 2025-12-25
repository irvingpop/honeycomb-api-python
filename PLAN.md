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
3. **Optional Enhancements** - CLI tool (Phase 12), JSON schema export (Phase 11)

---

## Phase 11: JSON Schema Export

**Purpose:** Export Pydantic model schemas as JSON Schema files for validation in external tools and improved AI understanding of the API structure.

### 11.1 Use Cases

- **External validation**: Use JSON Schema validators in other languages/tools
- **AI context**: Provide schema files to Claude/other LLMs for better API understanding
- **Documentation**: Machine-readable API contract documentation
- **Code generation**: Enable client generation in other languages

### 11.2 Implementation

```python
# scripts/export_schemas.py
from honeycomb.models import (
    Trigger, TriggerCreate, SLO, SLOCreate, Board, BoardCreate,
    Query, QuerySpec, Dataset, DatasetCreate, # ... all models
)
import json
from pathlib import Path

MODELS = [
    Trigger, TriggerCreate, TriggerUpdate,
    SLO, SLOCreate, SLOUpdate,
    Board, BoardCreate, BoardUpdate,
    Query, QuerySpec, QueryResult,
    Dataset, DatasetCreate, DatasetUpdate,
    # ... all public models
]

def export_schemas(output_dir: Path):
    """Export all model schemas to JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Individual model schemas
    for model in MODELS:
        schema = model.model_json_schema()
        schema_file = output_dir / f"{model.__name__}.json"
        schema_file.write_text(json.dumps(schema, indent=2))

    # Combined schema with all models
    combined = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Honeycomb API Models",
        "definitions": {
            model.__name__: model.model_json_schema()
            for model in MODELS
        }
    }
    (output_dir / "honeycomb-models.json").write_text(
        json.dumps(combined, indent=2)
    )

if __name__ == "__main__":
    export_schemas(Path("schemas"))
```

### 11.3 Package Integration

```toml
# pyproject.toml addition
[project.scripts]
honeycomb-export-schemas = "honeycomb.cli.schemas:main"
```

### 11.4 Makefile Target

```makefile
export-schemas:
    poetry run python scripts/export_schemas.py
    @echo "Schemas exported to schemas/"
```

### 11.5 Output Structure

```
schemas/
├── honeycomb-models.json     # Combined schema with all models
├── Trigger.json
├── TriggerCreate.json
├── SLO.json
├── SLOCreate.json
├── Board.json
├── Query.json
├── QuerySpec.json
├── QueryResult.json
└── ...
```

### 11.6 Deliverables

- [ ] Schema export script
- [ ] Makefile target `make export-schemas`
- [ ] CI step to regenerate schemas on model changes (optional)
- [ ] Include schemas in package distribution (optional)

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
