# Honeycomb API Python Client

A modern, async-first Python client for the [Honeycomb.io](https://www.honeycomb.io/) API.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Features

- **Async-first design** with full sync support for maximum flexibility
- **Fluent QueryBuilder** for constructing queries with IDE autocomplete
- **Claude tool definitions** exposing the full Honeycomb API for Claude-based agents
- **Pydantic models** for type-safe request/response handling
- **Automatic retries** with exponential backoff for transient failures
- **Comprehensive error handling** with specific exception types
- **Dual authentication** support (API keys and Management keys)
- **Resource-oriented API** for intuitive, Pythonic usage

## Quick Example

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
            QueryBuilder()
                .dataset("my-dataset")
                .last_1_hour()
                .count()
                .p99("duration_ms")
                .gte("status", 500)
                .group_by("service")
                .order_by_count(),
        )
        for row in result.data.rows:
            print(f"Service: {row['service']}, Count: {row['COUNT']}, P99: {row['P99']}")

asyncio.run(main())
```

## Get Started

Check out the [Installation Guide](getting-started/installation.md) to get started, or jump straight to the [Quick Start](getting-started/quickstart.md) for code examples.

## CLI Tool

For quick operations without writing Python:

```bash
# Configure authentication
export HONEYCOMB_API_KEY=your_api_key_here

# Run without installing
uvx honeycomb-api triggers list
# or
pipx run honeycomb-api triggers list

# Or install and use the short alias
uv tool install honeycomb-api
# or
pipx install honeycomb-api

hny triggers list
```

See the [CLI Reference](cli.md) for full documentation.

## Resources Supported

| Resource | Description |
|----------|-------------|
| **Datasets** | Manage your data collections |
| **Triggers** | Alert on query thresholds |
| **SLOs** | Define and track Service Level Objectives |
| **Boards** | Visualization dashboards |
| **Queries** | Save and run queries |

## Project Status

This project is in **active development**. Core functionality for managing Triggers, SLOs, Datasets, Boards, and Queries is complete and tested.

See the [API Reference](api/resources.md) for detailed documentation of all available resources and methods.
