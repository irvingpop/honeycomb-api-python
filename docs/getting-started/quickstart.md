# Quick Start

This guide will help you get up and running with the Honeycomb API Python client in minutes.

## Your First Request

=== "Async (Recommended)"

    ```python
    import asyncio
    from honeycomb import HoneycombClient

    async def main():
        async with HoneycombClient(api_key="your-api-key") as client:
            # List all datasets
            datasets = await client.datasets.list_async()

            for dataset in datasets:
                print(f"Dataset: {dataset.name} ({dataset.slug})")
                print(f"  Columns: {dataset.regular_columns_count}")
                print(f"  Last written: {dataset.last_written_at}")

    asyncio.run(main())
    ```

=== "Sync"

    For scripts and CLI tools, you can use the synchronous mode:

    ```python
    from honeycomb import HoneycombClient

    with HoneycombClient(api_key="your-api-key", sync=True) as client:
        datasets = client.datasets.list()

        for dataset in datasets:
            print(f"Dataset: {dataset.name}")
    ```

## Common Operations

### Working with Triggers

=== "Async"

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
        # List existing triggers
        triggers = await client.triggers.list_async("my-dataset")
        print(f"Found {len(triggers)} triggers")

        # Create a new trigger
        trigger = await client.triggers.create_async(
            "my-dataset",
            TriggerCreate(
                name="High Error Rate",
                description="Alert when error rate exceeds 5%",
                threshold=TriggerThreshold(
                    op=TriggerThresholdOp.GREATER_THAN,
                    value=0.05,
                ),
                frequency=300,  # Check every 5 minutes
                query=TriggerQuery(
                    time_range=900,  # 15-minute window
                    calculations=[
                        QueryCalculation(op="AVG", column="error_rate")
                    ],
                ),
            )
        )
        print(f"Created trigger: {trigger.id}")

        # Update the trigger
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

        # Delete the trigger
        await client.triggers.delete_async("my-dataset", trigger.id)
    ```

=== "Sync"

    ```python
    from honeycomb import (
        HoneycombClient,
        TriggerCreate,
        TriggerThreshold,
        TriggerThresholdOp,
        TriggerQuery,
        QueryCalculation,
    )

    with HoneycombClient(api_key="...", sync=True) as client:
        # List existing triggers
        triggers = client.triggers.list("my-dataset")
        print(f"Found {len(triggers)} triggers")

        # Create a new trigger
        trigger = client.triggers.create(
            "my-dataset",
            TriggerCreate(
                name="High Error Rate",
                description="Alert when error rate exceeds 5%",
                threshold=TriggerThreshold(
                    op=TriggerThresholdOp.GREATER_THAN,
                    value=0.05,
                ),
                frequency=300,  # Check every 5 minutes
                query=TriggerQuery(
                    time_range=900,  # 15-minute window
                    calculations=[
                        QueryCalculation(op="AVG", column="error_rate")
                    ],
                ),
            )
        )
        print(f"Created trigger: {trigger.id}")

        # Update the trigger
        updated = client.triggers.update(
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

        # Delete the trigger
        client.triggers.delete("my-dataset", trigger.id)
    ```

### Running Queries

=== "Async"

    ```python
    from honeycomb import HoneycombClient, QuerySpec

    async with HoneycombClient(api_key="...") as client:
        # Create a saved query and run it (returns both!)
        query, result = await client.query_results.create_and_run_async(
            "my-dataset",
            QuerySpec(
                time_range=3600,
                calculations=[{"op": "P99", "column": "duration_ms"}],
                breakdowns=["endpoint"],
            ),
            poll_interval=1.0,
            timeout=60.0,
        )

        print(f"Saved as query: {query.id}")

        # Process results
        for row in result.data:
            print(f"Endpoint: {row.get('endpoint')}, P99: {row.get('duration_ms')}")
    ```

=== "Sync"

    ```python
    from honeycomb import HoneycombClient, QuerySpec

    with HoneycombClient(api_key="...", sync=True) as client:
        # Create a saved query and run it (returns both!)
        query, result = client.query_results.create_and_run(
            "my-dataset",
            QuerySpec(
                time_range=3600,
                calculations=[{"op": "P99", "column": "duration_ms"}],
                breakdowns=["endpoint"],
            ),
            poll_interval=1.0,
            timeout=60.0,
        )

        print(f"Saved as query: {query.id}")

        # Process results
        for row in result.data:
            print(f"Endpoint: {row.get('endpoint')}, P99: {row.get('duration_ms')}")
    ```

!!! tip "Query Execution Options"
    See the [Queries Guide](../usage/queries.md) for three different ways to run queries:

    - **Ephemeral** (`run`) - One-time execution, not saved
    - **Saved** (`create` + `run`) - Save for reuse
    - **Both** (`create_and_run`) - Save AND execute in one call

### Creating SLOs

=== "Async"

    ```python
    from honeycomb import HoneycombClient, SLOCreate, SLI

    async with HoneycombClient(api_key="...") as client:
        slo = await client.slos.create_async(
            "my-dataset",
            SLOCreate(
                name="API Availability",
                description="99.9% uptime target",
                sli=SLI(alias="api-availability"),
                time_period_days=30,
                target_per_million=999000,  # 99.9%
            )
        )
        print(f"Created SLO: {slo.id}")
    ```

=== "Sync"

    ```python
    from honeycomb import HoneycombClient, SLOCreate, SLI

    with HoneycombClient(api_key="...", sync=True) as client:
        slo = client.slos.create(
            "my-dataset",
            SLOCreate(
                name="API Availability",
                description="99.9% uptime target",
                sli=SLI(alias="api-availability"),
                time_period_days=30,
                target_per_million=999000,  # 99.9%
            )
        )
        print(f"Created SLO: {slo.id}")
    ```

## Error Handling

The client provides specific exception types for different error scenarios:

```python
from honeycomb import (
    HoneycombClient,
    HoneycombNotFoundError,
    HoneycombRateLimitError,
    HoneycombAuthError,
)

async with HoneycombClient(api_key="...") as client:
    try:
        trigger = await client.triggers.get_async("dataset", "invalid-id")
    except HoneycombNotFoundError as e:
        print(f"Not found: {e.message}")
        print(f"Request ID: {e.request_id}")
    except HoneycombRateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
    except HoneycombAuthError:
        print("Invalid API key")
```

See the [Error Handling guide](../advanced/error-handling.md) for more details.

## Next Steps

- **Dive deeper**: Check out the [Usage Guides](../usage/datasets.md) for detailed examples
- **Learn about auth**: See [Authentication](authentication.md) for API key and management key setup
- **Advanced features**: Explore [Retry Configuration](../advanced/retry-config.md) and [Async vs Sync](../advanced/async-sync.md)
- **API Reference**: Browse the complete [API Reference](../api/client.md)
