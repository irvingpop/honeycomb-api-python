"""Tests for Queries and Query Results resources."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient, QueryBuilder, QuerySpec


@pytest.mark.asyncio
class TestQueriesResourceAsync:
    """Tests for QueriesResource async methods."""

    @respx.mock
    async def test_create_query(self, respx_mock):
        """Test creating a query."""
        client = HoneycombClient(api_key="test-key")

        respx_mock.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(
                200,
                json={
                    "id": "query-123",
                    "query_json": {"time_range": 3600},
                    "created_at": "2024-01-01T00:00:00Z",
                },
            )
        )

        async with client:
            builder = QueryBuilder().dataset("my-dataset").time_range(3600).count()
            query = await client.queries.create_async(builder)

            assert query.id == "query-123"
            assert query.query_json["time_range"] == 3600

    @respx.mock
    async def test_get_query(self, respx_mock):
        """Test getting a query by ID."""
        client = HoneycombClient(api_key="test-key")

        respx_mock.get("https://api.honeycomb.io/1/queries/my-dataset/query-123").mock(
            return_value=Response(
                200,
                json={
                    "id": "query-123",
                    "query_json": {"time_range": 3600},
                },
            )
        )

        async with client:
            query = await client.queries.get_async("my-dataset", "query-123")
            assert query.id == "query-123"


class TestQueriesResourceSync:
    """Tests for QueriesResource sync methods."""

    @respx.mock
    def test_create_query_sync(self, respx_mock):
        """Test creating a query in sync mode."""
        client = HoneycombClient(api_key="test-key", sync=True)

        respx_mock.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(
                200,
                json={
                    "id": "query-456",
                    "query_json": {"time_range": 1800},
                },
            )
        )

        with client:
            builder = QueryBuilder().dataset("my-dataset").time_range(1800)
            query = client.queries.create(builder)
            assert query.id == "query-456"

    @respx.mock
    def test_get_query_sync(self, respx_mock):
        """Test getting a query in sync mode."""
        client = HoneycombClient(api_key="test-key", sync=True)

        respx_mock.get("https://api.honeycomb.io/1/queries/my-dataset/query-456").mock(
            return_value=Response(200, json={"id": "query-456", "query_json": {}})
        )

        with client:
            query = client.queries.get("my-dataset", "query-456")
            assert query.id == "query-456"

    def test_sync_method_guard_create(self):
        """Test that sync methods raise in async mode."""
        client = HoneycombClient(api_key="test-key", sync=False)

        with pytest.raises(RuntimeError, match="async mode"), client:
            builder = QueryBuilder().dataset("my-dataset").time_range(3600)
            client.queries.create(builder)

    def test_sync_method_guard_get(self):
        """Test that sync methods raise in async mode."""
        client = HoneycombClient(api_key="test-key", sync=False)

        with pytest.raises(RuntimeError, match="async mode"), client:
            client.queries.get("my-dataset", "query-123")


@pytest.mark.asyncio
class TestQueryResultsResourceAsync:
    """Tests for QueryResultsResource async methods."""

    @respx.mock
    async def test_create_query_result(self, respx_mock):
        """Test creating a query result from saved query."""
        client = HoneycombClient(api_key="test-key")

        respx_mock.post("https://api.honeycomb.io/1/query_results/my-dataset").mock(
            return_value=Response(200, json={"id": "qr-123"})
        )

        async with client:
            result_id = await client.query_results.create_async(
                "my-dataset", query_id="saved-query-id"
            )
            assert result_id == "qr-123"

    @respx.mock
    async def test_get_query_result(self, respx_mock):
        """Test getting query result."""
        client = HoneycombClient(api_key="test-key")

        respx_mock.get("https://api.honeycomb.io/1/query_results/my-dataset/qr-123").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "results": [{"count": 100}],
                        "series": [],
                    },
                    "links": None,
                },
            )
        )

        async with client:
            result = await client.query_results.get_async("my-dataset", "qr-123")
            assert len(result.data.rows) == 1
            assert result.data.rows[0]["count"] == 100

    @respx.mock
    async def test_run_query_with_polling(self, respx_mock):
        """Test running a query with automatic polling."""
        client = HoneycombClient(api_key="test-key")

        # Mock create saved query
        respx_mock.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(200, json={"id": "saved-query-789", "query_json": {}})
        )

        # Mock create query result
        respx_mock.post("https://api.honeycomb.io/1/query_results/my-dataset").mock(
            return_value=Response(200, json={"id": "qr-789"})
        )

        # Mock polling - first call returns None (not ready), second returns data
        respx_mock.get("https://api.honeycomb.io/1/query_results/my-dataset/qr-789").mock(
            side_effect=[
                Response(200, json={"data": None}),
                Response(
                    200,
                    json={
                        "data": {
                            "results": [{"count": 42}],
                            "series": [],
                        }
                    },
                ),
            ]
        )

        async with client:
            builder = QueryBuilder().dataset("my-dataset").time_range(3600)
            query, result = await client.query_results.create_and_run_async(
                builder.build(), dataset="my-dataset", poll_interval=0.1, timeout=5.0
            )

            assert result.data is not None
            assert result.data.rows is not None
            assert len(result.data.rows) == 1
            assert result.data.rows[0]["count"] == 42

    @respx.mock
    async def test_run_query_timeout(self, respx_mock):
        """Test query run timeout."""
        from honeycomb.exceptions import HoneycombTimeoutError

        client = HoneycombClient(api_key="test-key")

        # Mock create saved query
        respx_mock.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(200, json={"id": "saved-query-slow", "query_json": {}})
        )

        # Mock create query result
        respx_mock.post("https://api.honeycomb.io/1/query_results/my-dataset").mock(
            return_value=Response(200, json={"id": "qr-slow"})
        )

        # Always return None (never completes)
        respx_mock.get("https://api.honeycomb.io/1/query_results/my-dataset/qr-slow").mock(
            return_value=Response(200, json={"data": None})
        )

        async with client:
            builder = QueryBuilder().dataset("my-dataset").time_range(3600)
            with pytest.raises(HoneycombTimeoutError) as exc_info:
                await client.query_results.create_and_run_async(
                    builder.build(), dataset="my-dataset", poll_interval=0.1, timeout=0.3
                )

            assert exc_info.value.timeout == 0.3

    @respx.mock
    async def test_create_and_run(self, respx_mock):
        """Test create_and_run convenience method."""
        client = HoneycombClient(api_key="test-key")

        # Mock query creation
        respx_mock.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(
                200,
                json={"id": "saved-query-123", "query_json": {"time_range": 3600}},
            )
        )

        # Mock query result creation
        respx_mock.post("https://api.honeycomb.io/1/query_results/my-dataset").mock(
            return_value=Response(200, json={"id": "qr-combo-1"})
        )

        # Mock query result polling
        respx_mock.get("https://api.honeycomb.io/1/query_results/my-dataset/qr-combo-1").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "results": [{"count": 999}],
                        "series": [],
                    }
                },
            )
        )

        async with client:
            builder = QueryBuilder().dataset("my-dataset").time_range(3600)
            query, result = await client.query_results.create_and_run_async(
                builder.build(), dataset="my-dataset", poll_interval=0.1, timeout=5.0
            )

            # Verify we got both the saved query and results
            assert query.id == "saved-query-123"
            assert result.data is not None
            assert result.data.rows is not None
            assert len(result.data.rows) == 1
            assert result.data.rows[0]["count"] == 999


class TestQueryResultsResourceSync:
    """Tests for QueryResultsResource sync methods."""

    @respx.mock
    def test_create_query_result_sync(self, respx_mock):
        """Test creating a query result in sync mode from saved query."""
        client = HoneycombClient(api_key="test-key", sync=True)

        respx_mock.post("https://api.honeycomb.io/1/query_results/my-dataset").mock(
            return_value=Response(200, json={"id": "qr-sync-1"})
        )

        with client:
            result_id = client.query_results.create("my-dataset", query_id="saved-query-id")
            assert result_id == "qr-sync-1"

    @respx.mock
    def test_get_query_result_sync(self, respx_mock):
        """Test getting query result in sync mode."""
        client = HoneycombClient(api_key="test-key", sync=True)

        respx_mock.get("https://api.honeycomb.io/1/query_results/my-dataset/qr-sync-1").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "results": [{"metric": "value"}],
                        "series": [],
                    }
                },
            )
        )

        with client:
            result = client.query_results.get("my-dataset", "qr-sync-1")
            assert result.data.rows[0]["metric"] == "value"

    def test_create_requires_query_id(self):
        """Test that create requires query_id parameter."""
        client = HoneycombClient(api_key="test-key", sync=True)

        # query_id is now a required parameter - Python will raise TypeError if missing
        with (
            client,
            pytest.raises(TypeError, match="missing 1 required positional argument: 'query_id'"),
        ):
            client.query_results.create("my-dataset")

    @respx.mock
    def test_create_and_run_sync(self, respx_mock):
        """Test create_and_run in sync mode."""
        client = HoneycombClient(api_key="test-key", sync=True)

        # Mock query creation
        respx_mock.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(
                200, json={"id": "saved-sync-query", "query_json": {"time_range": 1800}}
            )
        )

        # Mock query result creation
        respx_mock.post("https://api.honeycomb.io/1/query_results/my-dataset").mock(
            return_value=Response(200, json={"id": "qr-sync-combo"})
        )

        # Mock query result polling
        respx_mock.get("https://api.honeycomb.io/1/query_results/my-dataset/qr-sync-combo").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "results": [{"total": 555}],
                        "series": [],
                    }
                },
            )
        )

        with client:
            spec = QuerySpec(time_range=1800)
            query, result = client.query_results.create_and_run(
                spec, dataset="my-dataset", poll_interval=0.1, timeout=5.0
            )

            assert query.id == "saved-sync-query"
            assert result.data.rows[0]["total"] == 555


class TestQuerySpec:
    """Tests for QuerySpec model."""

    def test_model_dump_for_api(self):
        """Test serialization for API."""
        spec = QuerySpec(
            time_range=3600,
            granularity=60,
            calculations=[{"op": "COUNT"}],
            filters=[{"column": "status", "op": "=", "value": "200"}],
            breakdowns=["endpoint"],
        )

        data = spec.model_dump_for_api()

        assert data["time_range"] == 3600
        assert data["granularity"] == 60
        assert data["calculations"] == [{"op": "COUNT"}]
        assert data["filters"] == [{"column": "status", "op": "=", "value": "200"}]
        assert data["breakdowns"] == ["endpoint"]

    def test_model_dump_excludes_none(self):
        """Test that None values are excluded."""
        spec = QuerySpec(time_range=1800)
        data = spec.model_dump_for_api()

        assert "time_range" in data
        assert "granularity" not in data
        assert "calculations" not in data

    def test_model_dump_includes_calculated_fields(self):
        """Test that calculated_fields are included in model_dump_for_api."""
        spec = QuerySpec(
            time_range=3600,
            calculations=[{"op": "COUNT"}],
            calculated_fields=[
                {"name": "is_error", "expression": "IF(GTE($status_code, 500), 1, 0)"}
            ],
        )
        data = spec.model_dump_for_api()

        assert "calculated_fields" in data
        assert len(data["calculated_fields"]) == 1
        assert data["calculated_fields"][0]["name"] == "is_error"
        assert "status_code" in data["calculated_fields"][0]["expression"]

    def test_model_dump_includes_compare_time_offset(self):
        """Test that compare_time_offset_seconds is included in model_dump_for_api."""
        spec = QuerySpec(
            time_range=3600,
            calculations=[{"op": "COUNT"}],
            compare_time_offset_seconds=3600,
        )
        data = spec.model_dump_for_api()

        assert "compare_time_offset_seconds" in data
        assert data["compare_time_offset_seconds"] == 3600

    def test_limit_validation_max_1000(self):
        """Test that limit > 1000 raises validation error."""
        with pytest.raises(ValueError, match="limit cannot exceed 1000"):
            QuerySpec(
                time_range=3600,
                calculations=[{"op": "COUNT"}],
                limit=10000,  # Too high!
            )

    def test_limit_validation_allows_1000(self):
        """Test that limit = 1000 is allowed."""
        spec = QuerySpec(
            time_range=3600,
            calculations=[{"op": "COUNT"}],
            limit=1000,  # Maximum allowed
        )
        assert spec.limit == 1000

    def test_limit_validation_allows_none(self):
        """Test that limit = None is allowed."""
        spec = QuerySpec(
            time_range=3600,
            calculations=[{"op": "COUNT"}],
        )
        assert spec.limit is None

    def test_compare_time_offset_validation_valid_values(self):
        """Test that valid compare_time_offset_seconds values are accepted."""
        valid_offsets = [1800, 3600, 7200, 28800, 86400, 604800, 2419200, 15724800]
        for offset in valid_offsets:
            spec = QuerySpec(
                time_range=3600,
                calculations=[{"op": "COUNT"}],
                compare_time_offset_seconds=offset,
            )
            assert spec.compare_time_offset_seconds == offset

    def test_compare_time_offset_validation_invalid_values(self):
        """Test that invalid compare_time_offset_seconds values raise error."""
        invalid_offsets = [0, 100, 1799, 1801, 3601, 99999, -3600]
        for offset in invalid_offsets:
            with pytest.raises(ValueError, match="Invalid compare_time_offset_seconds"):
                QuerySpec(
                    time_range=3600,
                    calculations=[{"op": "COUNT"}],
                    compare_time_offset_seconds=offset,
                )

    def test_compare_time_offset_validation_allows_none(self):
        """Test that compare_time_offset_seconds = None is allowed."""
        spec = QuerySpec(
            time_range=3600,
            calculations=[{"op": "COUNT"}],
            compare_time_offset_seconds=None,
        )
        assert spec.compare_time_offset_seconds is None
