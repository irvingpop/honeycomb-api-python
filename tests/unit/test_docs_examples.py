"""Test that documentation examples actually work."""

import pytest
import respx
from httpx import Response

from honeycomb import (
    SLI,
    HoneycombClient,
    QueryCalculation,
    QuerySpec,
    SLOCreate,
    TriggerCreate,
    TriggerQuery,
    TriggerThreshold,
    TriggerThresholdOp,
)


class TestQuickstartExamples:
    """Validate examples from quickstart.md work correctly."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_first_request_async(self, respx_mock):
        """Test the 'Your First Request' async example."""
        respx_mock.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "name": "Production",
                        "slug": "production",
                        "regular_columns_count": 42,
                        "last_written_at": "2024-01-01T00:00:00Z",
                    }
                ],
            )
        )

        # This is the exact code from quickstart.md
        async with HoneycombClient(api_key="your-api-key") as client:
            datasets = await client.datasets.list_async()

            for dataset in datasets:
                assert dataset.name == "Production"
                assert dataset.slug == "production"
                assert dataset.regular_columns_count == 42

    @respx.mock
    def test_first_request_sync(self, respx_mock):
        """Test the sync example from quickstart.md."""
        respx_mock.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "Test", "slug": "test"}])
        )

        # This is the exact code from quickstart.md
        with HoneycombClient(api_key="your-api-key", sync=True) as client:
            datasets = client.datasets.list()
            assert len(datasets) == 1

    @respx.mock
    async def test_trigger_example(self, respx_mock):
        """Test the trigger creation example from quickstart.md."""
        # Mock list triggers
        respx_mock.get("https://api.honeycomb.io/1/triggers/my-dataset").mock(
            return_value=Response(200, json=[])
        )

        # Mock create trigger
        respx_mock.post("https://api.honeycomb.io/1/triggers/my-dataset").mock(
            return_value=Response(
                200,
                json={
                    "id": "trigger-123",
                    "name": "High Error Rate",
                    "dataset_slug": "my-dataset",
                    "threshold": {"op": ">", "value": 0.05},
                    "frequency": 300,
                    "disabled": False,
                    "triggered": False,
                },
            )
        )

        # This is adapted from quickstart.md
        async with HoneycombClient(api_key="...") as client:
            triggers = await client.triggers.list_async("my-dataset")
            assert len(triggers) == 0

            trigger = await client.triggers.create_async(
                "my-dataset",
                TriggerCreate(
                    name="High Error Rate",
                    description="Alert when error rate exceeds 5%",
                    threshold=TriggerThreshold(
                        op=TriggerThresholdOp.GREATER_THAN,
                        value=0.05,
                    ),
                    frequency=300,
                    query=TriggerQuery(
                        time_range=900,
                        calculations=[QueryCalculation(op="AVG", column="error_rate")],
                    ),
                ),
            )
            assert trigger.id == "trigger-123"

    @respx.mock
    @pytest.mark.asyncio
    async def test_query_example(self, respx_mock):
        """Test the query example from quickstart.md."""
        # Mock create query (saved query)
        respx_mock.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(
                200,
                json={
                    "id": "query-456",
                    "query_json": {"time_range": 3600},
                },
            )
        )

        # Mock create query result
        respx_mock.post("https://api.honeycomb.io/1/query_results/my-dataset").mock(
            return_value=Response(200, json={"id": "qr-123"})
        )

        # Mock get query result (completed)
        respx_mock.get("https://api.honeycomb.io/1/query_results/my-dataset/qr-123").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "results": [
                            {"endpoint": "/api/users", "duration_ms": 125.5},
                            {"endpoint": "/api/orders", "duration_ms": 89.3},
                        ],
                        "series": [],
                    }
                },
            )
        )

        # This is the exact code from quickstart.md (updated to create_and_run)
        async with HoneycombClient(api_key="...") as client:
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

            assert query.id == "query-456"

            # Process results
            assert result.data is not None
            assert result.data.rows is not None
            assert len(result.data.rows) == 2
            for row in result.data.rows:
                endpoint = row.get("endpoint")
                duration = row.get("duration_ms")
                assert endpoint is not None
                assert duration is not None

    @respx.mock
    async def test_slo_example(self, respx_mock):
        """Test the SLO creation example from quickstart.md."""
        respx_mock.post("https://api.honeycomb.io/1/slos/my-dataset").mock(
            return_value=Response(
                200,
                json={
                    "id": "slo-123",
                    "name": "API Availability",
                    "description": "99.9% uptime target",
                    "sli": {"alias": "api-availability"},
                    "time_period_days": 30,
                    "target_per_million": 999000,
                },
            )
        )

        # This is the exact code from quickstart.md
        async with HoneycombClient(api_key="...") as client:
            slo = await client.slos.create_async(
                "my-dataset",
                SLOCreate(
                    name="API Availability",
                    description="99.9% uptime target",
                    sli=SLI(alias="api-availability"),
                    time_period_days=30,
                    target_per_million=999000,
                ),
            )
            assert slo.id == "slo-123"
