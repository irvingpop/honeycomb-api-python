# honeycomb-api-python

A modern, async-first Python client for the [Honeycomb.io](https://www.honeycomb.io/) API.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Features

- **Async-first design** with full sync support
- **Pydantic models** for type-safe request/response handling
- **Automatic retries** with exponential backoff for transient failures
- **Comprehensive error handling** with specific exception types
- **Dual authentication** support (API keys and Management keys)
- **Resource-oriented API** for intuitive usage

## Installation

```bash
pip install honeycomb-api-python
```

Or with Poetry:

```bash
poetry add honeycomb-api-python
```

## Quick Start

### Async Usage (Recommended)

```python
import asyncio
from honeycomb import HoneycombClient

async def main():
    async with HoneycombClient(api_key="your-api-key") as client:
        # List all datasets
        datasets = await client.datasets.list_async()
        for ds in datasets:
            print(f"Dataset: {ds.name} ({ds.slug})")

        # List triggers for a dataset
        triggers = await client.triggers.list_async("my-dataset")
        for trigger in triggers:
            print(f"Trigger: {trigger.name} (triggered: {trigger.triggered})")

asyncio.run(main())
```

### Sync Usage

```python
from honeycomb import HoneycombClient

with HoneycombClient(api_key="your-api-key", sync=True) as client:
    datasets = client.datasets.list()
    triggers = client.triggers.list("my-dataset")
```

## Authentication

The client supports two authentication methods:

### API Key (Single Environment)

For accessing a single Honeycomb environment:

```python
client = HoneycombClient(api_key="your-api-key")
```

The API key is sent via the `X-Honeycomb-Team` header.

### Management Key (Multi-Environment)

For management operations across multiple environments:

```python
client = HoneycombClient(
    management_key="your-key-id",
    management_secret="your-key-secret"
)
```

Management credentials are sent via the `Authorization: Bearer` header.

## Usage Examples

### Working with Datasets

```python
from honeycomb import HoneycombClient, DatasetCreate

async with HoneycombClient(api_key="...") as client:
    # List all datasets
    datasets = await client.datasets.list_async()

    # Get a specific dataset
    dataset = await client.datasets.get_async("my-dataset")
    print(f"Created: {dataset.created_at}")
    print(f"Columns: {dataset.regular_columns_count}")

    # Create a new dataset
    new_dataset = await client.datasets.create_async(
        DatasetCreate(
            name="My New Dataset",
            description="For testing purposes"
        )
    )
```

### Working with Triggers

```python
from honeycomb import (
    HoneycombClient,
    TriggerCreate,
    TriggerThreshold,
    TriggerThresholdOp,
    TriggerQuery,
    QueryCalculation,
)

async with HoneycombClient(api_key="...") as client:
    # List triggers
    triggers = await client.triggers.list_async("my-dataset")

    # Create a trigger with an inline query
    trigger = await client.triggers.create_async(
        "my-dataset",
        TriggerCreate(
            name="High Error Rate",
            description="Alert when error rate exceeds threshold",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN,
                value=0.05,  # 5%
            ),
            frequency=300,  # Check every 5 minutes
            query=TriggerQuery(
                time_range=900,  # 15-minute window (max 3600)
                calculations=[
                    QueryCalculation(op="AVG", column="error_rate")
                ],
            ),
        )
    )
    print(f"Created trigger: {trigger.id}")

    # Update a trigger
    updated = await client.triggers.update_async(
        "my-dataset",
        trigger.id,
        TriggerCreate(
            name="High Error Rate (Updated)",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN_OR_EQUAL,
                value=0.10,
            ),
            frequency=300,
            query=TriggerQuery(time_range=900),
        )
    )

    # Delete a trigger
    await client.triggers.delete_async("my-dataset", trigger.id)
```

### Working with SLOs

```python
from honeycomb import HoneycombClient, SLOCreate, SLI

async with HoneycombClient(api_key="...") as client:
    # List SLOs
    slos = await client.slos.list_async("my-dataset")

    # Create an SLO
    slo = await client.slos.create_async(
        "my-dataset",
        SLOCreate(
            name="API Availability",
            description="99.9% availability target",
            sli=SLI(alias="availability-sli"),
            time_period_days=30,
            target_per_million=999000,  # 99.9%
        )
    )
```

### Working with Boards

```python
from honeycomb import HoneycombClient, BoardCreate

async with HoneycombClient(api_key="...") as client:
    # List boards
    boards = await client.boards.list_async()

    # Create a board
    board = await client.boards.create_async(
        BoardCreate(
            name="Service Overview",
            description="Key metrics dashboard",
            column_layout="multi",
            style="visual",
        )
    )
```

## Error Handling

The client provides specific exception types for different error conditions:

```python
from honeycomb import (
    HoneycombClient,
    HoneycombAPIError,
    HoneycombAuthError,
    HoneycombForbiddenError,
    HoneycombNotFoundError,
    HoneycombValidationError,
    HoneycombRateLimitError,
    HoneycombServerError,
    HoneycombTimeoutError,
    HoneycombConnectionError,
)

async with HoneycombClient(api_key="...") as client:
    try:
        trigger = await client.triggers.get_async("dataset", "invalid-id")
    except HoneycombNotFoundError as e:
        print(f"Trigger not found: {e}")
        print(f"Request ID: {e.request_id}")  # Useful for support
    except HoneycombAuthError:
        print("Invalid API key")
    except HoneycombRateLimitError as e:
        print(f"Rate limited. Retry after: {e.retry_after} seconds")
    except HoneycombValidationError as e:
        print(f"Validation error: {e}")
        print(f"Details: {e.errors}")
    except HoneycombAPIError as e:
        print(f"API error [{e.status_code}]: {e}")
```

### Exception Hierarchy

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `HoneycombAPIError` | Any | Base exception for all API errors |
| `HoneycombAuthError` | 401 | Invalid or missing credentials |
| `HoneycombForbiddenError` | 403 | Insufficient permissions |
| `HoneycombNotFoundError` | 404 | Resource not found |
| `HoneycombValidationError` | 422 | Invalid request data |
| `HoneycombRateLimitError` | 429 | Rate limit exceeded |
| `HoneycombServerError` | 5xx | Honeycomb server error |
| `HoneycombTimeoutError` | - | Request timed out |
| `HoneycombConnectionError` | - | Connection failed |

## Configuration

### Client Options

```python
client = HoneycombClient(
    api_key="...",                              # API key for single-environment access
    management_key="...",                       # Management key ID (alternative auth)
    management_secret="...",                    # Management key secret
    base_url="https://api.honeycomb.io",       # API base URL (default)
    timeout=30.0,                               # Request timeout in seconds (default: 30)
    max_retries=3,                              # Max retry attempts (default: 3)
    sync=False,                                 # Use sync mode (default: False)
)
```

### Retry Behavior

The client automatically retries requests on:
- HTTP 429 (Rate Limited) - respects `Retry-After` header
- HTTP 500, 502, 503, 504 (Server Errors)
- Connection timeouts

Retries use exponential backoff: 1s, 2s, 4s, ... up to 30s max.

## API Reference

### Resources

| Resource | Methods |
|----------|---------|
| `client.datasets` | `list`, `get`, `create`, `update`, `delete` |
| `client.triggers` | `list`, `get`, `create`, `update`, `delete` |
| `client.slos` | `list`, `get`, `create`, `update`, `delete` |
| `client.boards` | `list`, `get`, `create`, `update`, `delete` |

All methods have both sync and async variants:
- Sync: `client.datasets.list()`
- Async: `await client.datasets.list_async()`

### Models

**Triggers:**
- `Trigger` - Response model
- `TriggerCreate` - Create/update model
- `TriggerThreshold` - Threshold configuration
- `TriggerThresholdOp` - Comparison operators (`>`, `>=`, `<`, `<=`)
- `TriggerQuery` - Inline query specification
- `QueryCalculation` - Query calculation (COUNT, AVG, P99, etc.)
- `QueryFilter` - Query filter

**SLOs:**
- `SLO` - Response model
- `SLOCreate` - Create/update model
- `SLI` - Service Level Indicator configuration

**Datasets:**
- `Dataset` - Response model
- `DatasetCreate` - Create/update model

**Boards:**
- `Board` - Response model
- `BoardCreate` - Create/update model

## Development

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management
- [direnv](https://direnv.net/) (optional, for environment management)
- Make (optional, for convenience commands)

### Setup

```bash
# Clone the repository
git clone https://github.com/irvingpop/honeycomb-api-python.git
cd honeycomb-api-python

# Install dependencies
make install-dev
# Or: poetry install

# Set up environment variables (for live API testing)
cp .envrc.example .envrc
# Edit .envrc with your API key
direnv allow
```

### Make Commands

All common development tasks are available via `make`. Run `make help` for a full list:

```bash
make help          # Show all available commands
```

#### Setup
| Command | Description |
|---------|-------------|
| `make install` | Install production dependencies only |
| `make install-dev` | Install all dependencies (including dev) |

#### Code Quality
| Command | Description |
|---------|-------------|
| `make lint` | Run linter (ruff check) |
| `make lint-fix` | Run linter and auto-fix issues |
| `make format` | Format code with ruff |
| `make typecheck` | Run type checker (mypy) |
| `make check` | Run all checks (lint + typecheck) |

#### Testing
| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-unit` | Run only unit tests |
| `make test-cov` | Run tests with coverage report |
| `make test-live` | Run live API tests (requires `HONEYCOMB_API_KEY`) |

#### Build & Publish
| Command | Description |
|---------|-------------|
| `make build` | Build distribution packages |
| `make publish` | Publish to PyPI |
| `make publish-test` | Publish to Test PyPI |

#### Maintenance
| Command | Description |
|---------|-------------|
| `make clean` | Remove build artifacts and cache files |
| `make update-deps` | Update dependencies to latest versions |
| `make ci` | Run full CI pipeline (install, check, test) |

### Running Tests (Manual)

```bash
# Run all tests
make test
# Or: poetry run pytest tests/ -v

# Run with coverage
make test-cov
# Or: poetry run pytest --cov=honeycomb --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_wrapper_client.py -v
```

### Code Quality (Manual)

```bash
# Run all checks
make check

# Or run individually:
poetry run ruff check src/ tests/    # Linting
poetry run ruff format src/ tests/   # Formatting
poetry run mypy src/                 # Type checking
```

### Live API Testing

```bash
# Requires HONEYCOMB_API_KEY environment variable
make test-live
# Or: poetry run python scripts/test_live_api.py
```

## Project Structure

```
honeycomb-api-python/
├── src/
│   └── honeycomb/
│       ├── __init__.py          # Package exports
│       ├── auth.py              # Authentication strategies
│       ├── client.py            # Main HoneycombClient
│       ├── exceptions.py        # Exception hierarchy
│       ├── models/              # Pydantic models
│       │   ├── datasets.py
│       │   ├── slos.py
│       │   └── triggers.py
│       └── resources/           # API resources
│           ├── base.py
│           ├── boards.py
│           ├── datasets.py
│           ├── slos.py
│           └── triggers.py
├── tests/
│   └── unit/
├── scripts/
│   └── test_live_api.py
├── Makefile                     # Development commands
├── pyproject.toml               # Project configuration
├── .envrc.example               # Environment template
└── README.md
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run checks and tests (`make check && make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Guidelines

- Follow the existing code style (enforced by Ruff)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic
- Run `make ci` before submitting to ensure all checks pass

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Links

- [Honeycomb Documentation](https://docs.honeycomb.io/)
- [Honeycomb API Reference](https://docs.honeycomb.io/api/)
- [Issue Tracker](https://github.com/irvingpop/honeycomb-api-python/issues)

## Acknowledgments

- Built with [httpx](https://www.python-httpx.org/) for async HTTP
- Models powered by [Pydantic](https://docs.pydantic.dev/)
- API spec from [Honeycomb OpenAPI](https://docs.honeycomb.io/api/)
