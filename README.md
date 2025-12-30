# honeycomb-api-python

A modern, async-first Python client for the [Honeycomb.io](https://www.honeycomb.io/) API.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

📚 **[Read the full documentation](https://irvingpop.github.io/honeycomb-api-python/)**

## Features

- **Async-first design** with full sync support
- **Fluent builder pattern** for queries, triggers, SLOs, and boards
- **CLI tool** for porting objects between environments
- **Pydantic models** for type-safe request/response handling
- **Automatic retries** with exponential backoff for transient failures
- **Comprehensive error handling** with specific exception types
- **Dual authentication** support (API keys and Management keys)
- **Resource-oriented API** for intuitive usage

## Installation (coming soon)

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
from honeycomb import HoneycombClient, QueryBuilder

async def main():
    async with HoneycombClient(api_key="your-api-key") as client:
        # List all datasets
        datasets = await client.datasets.list_async()
        for ds in datasets:
            print(f"Dataset: {ds.name} ({ds.slug})")

        # Run a query using the fluent QueryBuilder
        query, result = await client.query_results.create_and_run_async(
            QueryBuilder("Error Analysis")  # Optional name for board integration
                .dataset("my-dataset")       # Dataset scope on builder
                .last_24_hours()             # Time preset matching Honeycomb UI
                .count()
                .p99("duration_ms")
                .avg("duration_ms")
                .gte("status_code", 500)     # Filter shortcuts: gte, eq, contains, etc.
                .group_by("service", "endpoint")
                .order_by_count()
                .limit(100)
        )

        for row in result.data.rows:
            print(f"Service: {row['service']}, Count: {row['COUNT']}, P99: {row['P99']}")

asyncio.run(main())
```

### Sync Usage

```python
from honeycomb import HoneycombClient, QueryBuilder

with HoneycombClient(api_key="your-api-key", sync=True) as client:
    datasets = client.datasets.list()

    # Run queries with the same fluent API
    query, result = client.query_results.create_and_run(
        QueryBuilder()
            .dataset("my-dataset")
            .last_1_hour()
            .count()
            .group_by("endpoint"),
    )
```

## Builders with resource mixins

### TriggerBuilder

```python
from honeycomb import TriggerBuilder

# Create sophisticated alert in one fluent call
trigger = await client.triggers.create_async(
    "api-logs",
    TriggerBuilder("High Error Rate")
        .dataset("api-logs")             # Or .environment_wide() for all datasets
        .last_15_minutes()                # Frequency presets
        .count()
        .gte("status_code", 500)
        .threshold_gt(100)                # Threshold shortcuts
        .email("oncall@example.com")      # Multiple recipients
        .pagerduty("critical")
        .slack("#incidents")
        .tag("team", "backend")           # Tag support with validation
        .build()
)
```

### SLOBuilder

```python
from honeycomb import SLOBuilder

# Create SLO with derived column and burn alerts automatically
slos = await client.slos.create_from_bundle_async(
    SLOBuilder("API Availability")
        .dataset("api-logs")
        .target_nines(3)                         # 99.9% = .target_percentage(99.9)
        .time_period_days(30)
        .sli(
            alias="success_rate",
            expression="IF(LT($status_code, 400), 1, 0)",
            description="Success indicator"
        )
        # Burn alerts with integrated recipients
        .exhaustion_alert(exhaustion_minutes=15)
        .budget_rate_alert(window_minutes=60, threshold_percentage=10)
        .email("sre@example.com")
        .pagerduty("critical")
        .build()
)
```

### BoardBuilder

```python
from honeycomb import BoardBuilder, QueryBuilder, SLOBuilder

# Create board with inline queries and SLOs - no pre-creation needed!
board = await client.boards.create_from_bundle_async(
    BoardBuilder("Production Dashboard")
        .description("Service health monitoring")
        .auto_layout()
        .tag("team", "platform")
        # Inline QueryBuilder - creates query automatically
        .query(
            QueryBuilder("Request Count")
                .dataset("api-logs")
                .last_24_hours()
                .count()
                .group_by("service"),
            style="graph"
        )
        # Inline SLOBuilder - creates SLO automatically
        .slo(
            SLOBuilder("API Availability")
                .dataset("api-logs")
                .target_nines(3)
                .sli(alias="sli_success")
        )
        # Environment-wide query
        .query(
            QueryBuilder("P99 Latency")
                .environment_wide()  # All datasets
                .last_1_hour()
                .p99("duration_ms")
                .group_by("endpoint"),
            style="table"
        )
        .build()
)
```

See [full documentation](https://irvingpop.github.io/honeycomb-api-python/) for more examples and advanced features.

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

## Usage Guide

For complete usage examples and guides, see the [full documentation](https://irvingpop.github.io/honeycomb-api-python/):

- [Quick Start Guide](https://irvingpop.github.io/honeycomb-api-python/getting-started/quickstart/) - Common operations with examples
- [Working with Queries](https://irvingpop.github.io/honeycomb-api-python/usage/queries/) - Saved, ephemeral, and combined query patterns
- [Working with Triggers](https://irvingpop.github.io/honeycomb-api-python/usage/triggers/) - Alert configuration
- [Working with SLOs](https://irvingpop.github.io/honeycomb-api-python/usage/slos/) - Service level objectives
- [API Reference](https://irvingpop.github.io/honeycomb-api-python/api/resources/) - Complete API documentation

## Error Handling

The client provides specific exception types for different error scenarios (authentication, rate limiting, validation, etc.). All exceptions include useful debugging information like HTTP status codes and request IDs for support tickets.

See the [Error Handling Guide](https://irvingpop.github.io/honeycomb-api-python/advanced/error-handling/) for complete documentation and best practices.

## Configuration

### Client Options

```python
from honeycomb import HoneycombClient, RetryConfig

client = HoneycombClient(
    api_key="...",                              # API key for single-environment access
    management_key="...",                       # Management key ID (alternative auth)
    management_secret="...",                    # Management key secret
    base_url="https://api.honeycomb.io",        # API base URL (default)
    timeout=30.0,                               # Request timeout in seconds (default: 30)
    max_retries=3,                              # Max retry attempts (default: 3)
    retry_config=None,                          # Custom retry configuration (optional)
    sync=False,                                 # Use sync mode (default: False)
)
```

### Retry Behavior

The client automatically retries requests on:
- HTTP 429 (Rate Limited) - respects `Retry-After` header
- HTTP 500, 502, 503, 504 (Server Errors)
- Connection timeouts

Retries use exponential backoff: 1s, 2s, 4s, ... up to 30s max.

#### Custom Retry Configuration

```python
from honeycomb import HoneycombClient, RetryConfig

# Customize retry behavior
retry_config = RetryConfig(
    max_retries=5,                # More retry attempts
    base_delay=2.0,               # Start with 2s delay
    max_delay=60.0,               # Cap at 60s
    exponential_base=2.0,         # Double each time
    retry_statuses={429, 503},    # Only retry these status codes
)

client = HoneycombClient(api_key="...", retry_config=retry_config)
```

## API Reference

The client provides resource-oriented access to the Honeycomb API:

**Core Resources:**
- `client.datasets` - Dataset management
- `client.triggers` - Alert triggers
- `client.slos` - Service level objectives
- `client.boards` - Dashboards
- `client.queries` - Saved queries
- `client.query_results` - Query execution

**Data Management:**
- `client.columns` - Column schema management
- `client.markers` - Event markers and annotations
- `client.recipients` - Notification recipients
- `client.burn_alerts` - SLO burn rate alerts
- `client.events` - Event ingestion (send data to Honeycomb)

**Team Management (v2 - requires Management Key):**
- `client.api_keys` - API key management (team-scoped)
- `client.environments` - Environment management (team-scoped)

All methods have both sync and async variants (`list()` / `list_async()`).

See the [API Reference](https://irvingpop.github.io/honeycomb-api-python/api/resources/) for complete documentation.

## Development

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management
- [direnv](https://direnv.net/) (optional, for environment management)
- Make

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
| `make install` | Install poetry production dependencies only |
| `make install-dev` | Install all poetry dependencies (including dev) |

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
