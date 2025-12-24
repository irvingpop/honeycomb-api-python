# Honeycomb API Python Client

A modern, async-first Python client for the [Honeycomb.io](https://www.honeycomb.io/) API.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Features

- **Async-first design** with full sync support for maximum flexibility
- **Pydantic models** for type-safe request/response handling
- **Automatic retries** with exponential backoff for transient failures
- **Comprehensive error handling** with specific exception types
- **Dual authentication** support (API keys and Management keys)
- **Resource-oriented API** for intuitive, Pythonic usage

## Quick Example

```python
import asyncio
from honeycomb import HoneycombClient, TriggerCreate, TriggerThreshold, TriggerThresholdOp

async def main():
    async with HoneycombClient(api_key="your-api-key") as client:
        # List all datasets
        datasets = await client.datasets.list_async()
        print(f"Found {len(datasets)} datasets")

        # Create a trigger
        trigger = await client.triggers.create_async(
            "my-dataset",
            TriggerCreate(
                name="High Error Rate",
                threshold=TriggerThreshold(
                    op=TriggerThresholdOp.GREATER_THAN,
                    value=0.05,
                ),
                frequency=300,
            )
        )
        print(f"Created trigger: {trigger.id}")

asyncio.run(main())
```

## Why This Client?

- **Modern Python**: Built for Python 3.10+ with type hints throughout
- **Async Native**: First-class async support using httpx
- **Developer Friendly**: Intuitive API that matches how you think about Honeycomb resources
- **Production Ready**: Comprehensive error handling, retries, and timeouts
- **Well Tested**: 140+ unit tests with high coverage
- **Actively Maintained**: Built on the official Honeycomb OpenAPI spec

## Get Started

Check out the [Installation Guide](getting-started/installation.md) to get started, or jump straight to the [Quick Start](getting-started/quickstart.md) for code examples.

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
