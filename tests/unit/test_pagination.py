"""Tests for pagination support in resources."""

import respx
from httpx import Response

from honeycomb import HoneycombClient
from honeycomb.models import (
    ApiKeyType,
    ServiceMapDependencyRequestCreate,
    ServiceMapDependencyRequestStatus,
    ServiceMapNode,
)

# =============================================================================
# API Keys Pagination Tests
# =============================================================================


class TestApiKeysPagination:
    """Tests for API Keys pagination."""

    @respx.mock
    async def test_list_single_page(self):
        """Test listing API keys with a single page of results."""
        respx.get("https://api.honeycomb.io/2/teams/my-team/api-keys").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {
                            "id": "key-1",
                            "type": "api-keys",
                            "attributes": {
                                "name": "Key 1",
                                "type": "ingest",
                                "environment_id": "env-1",
                                "disabled": False,
                            },
                        },
                        {
                            "id": "key-2",
                            "type": "api-keys",
                            "attributes": {
                                "name": "Key 2",
                                "type": "configuration",
                                "environment_id": "env-1",
                                "disabled": False,
                            },
                        },
                    ],
                    "links": {"next": None},
                },
            )
        )

        async with HoneycombClient(
            management_key="hcamk_test", management_secret="test_secret"
        ) as client:
            keys = await client.api_keys.list_async(team="my-team")

        assert len(keys) == 2
        assert keys[0].id == "key-1"
        assert keys[1].id == "key-2"

    @respx.mock
    async def test_list_multiple_pages(self):
        """Test listing API keys with multiple pages of results."""
        call_count = {"value": 0}

        def api_keys_handler(_request):
            call_count["value"] += 1
            if call_count["value"] == 1:
                # First page
                return Response(
                    200,
                    json={
                        "data": [
                            {
                                "id": f"key-{i}",
                                "type": "api-keys",
                                "attributes": {
                                    "name": f"Key {i}",
                                    "type": "ingest",
                                    "environment_id": "env-1",
                                    "disabled": False,
                                },
                            }
                            for i in range(1, 4)
                        ],
                        "links": {
                            "next": "/2/teams/my-team/api-keys?page[after]=cursor1&page[size]=100"
                        },
                    },
                )
            else:
                # Second page
                return Response(
                    200,
                    json={
                        "data": [
                            {
                                "id": f"key-{i}",
                                "type": "api-keys",
                                "attributes": {
                                    "name": f"Key {i}",
                                    "type": "ingest",
                                    "environment_id": "env-1",
                                    "disabled": False,
                                },
                            }
                            for i in range(4, 6)
                        ],
                        "links": {"next": None},
                    },
                )

        respx.get("https://api.honeycomb.io/2/teams/my-team/api-keys").mock(
            side_effect=api_keys_handler
        )

        async with HoneycombClient(
            management_key="hcamk_test", management_secret="test_secret"
        ) as client:
            keys = await client.api_keys.list_async(team="my-team")

        assert len(keys) == 5
        assert keys[0].id == "key-1"
        assert keys[4].id == "key-5"
        assert call_count["value"] == 2

    @respx.mock
    async def test_list_with_key_type_filter(self):
        """Test listing API keys with key type filter."""
        route = respx.get("https://api.honeycomb.io/2/teams/my-team/api-keys").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {
                            "id": "key-1",
                            "type": "api-keys",
                            "attributes": {
                                "name": "Ingest Key",
                                "type": "ingest",
                                "environment_id": "env-1",
                                "disabled": False,
                            },
                        },
                    ],
                    "links": {"next": None},
                },
            )
        )

        async with HoneycombClient(
            management_key="hcamk_test", management_secret="test_secret"
        ) as client:
            keys = await client.api_keys.list_async(team="my-team", key_type="ingest")

        assert len(keys) == 1
        assert keys[0].key_type == ApiKeyType.INGEST
        # Verify filter was passed
        assert "filter%5Btype%5D=ingest" in str(route.calls[0].request.url)


# =============================================================================
# Environments Pagination Tests
# =============================================================================


class TestEnvironmentsPagination:
    """Tests for Environments pagination."""

    @respx.mock
    async def test_list_single_page(self):
        """Test listing environments with a single page of results."""
        respx.get("https://api.honeycomb.io/2/teams/my-team/environments").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {
                            "id": "env-1",
                            "type": "environments",
                            "attributes": {
                                "name": "Production",
                                "slug": "production",
                                "color": "red",
                                "description": "Prod environment",
                            },
                        },
                        {
                            "id": "env-2",
                            "type": "environments",
                            "attributes": {
                                "name": "Staging",
                                "slug": "staging",
                                "color": "gold",
                                "description": "Staging environment",
                            },
                        },
                    ],
                    "links": {"next": None},
                },
            )
        )

        async with HoneycombClient(
            management_key="hcamk_test", management_secret="test_secret"
        ) as client:
            envs = await client.environments.list_async(team="my-team")

        assert len(envs) == 2
        assert envs[0].id == "env-1"
        assert envs[0].name == "Production"
        assert envs[1].id == "env-2"
        assert envs[1].name == "Staging"

    @respx.mock
    async def test_list_multiple_pages(self):
        """Test listing environments with multiple pages of results."""
        call_count = {"value": 0}

        def envs_handler(_request):
            call_count["value"] += 1
            if call_count["value"] == 1:
                # First page
                return Response(
                    200,
                    json={
                        "data": [
                            {
                                "id": f"env-{i}",
                                "type": "environments",
                                "attributes": {
                                    "name": f"Environment {i}",
                                    "slug": f"environment-{i}",
                                    "color": "blue",
                                },
                            }
                            for i in range(1, 4)
                        ],
                        "links": {
                            "next": "/2/teams/my-team/environments?page[after]=cursor1&page[size]=100"
                        },
                    },
                )
            else:
                # Second page
                return Response(
                    200,
                    json={
                        "data": [
                            {
                                "id": f"env-{i}",
                                "type": "environments",
                                "attributes": {
                                    "name": f"Environment {i}",
                                    "slug": f"environment-{i}",
                                    "color": "blue",
                                },
                            }
                            for i in range(4, 6)
                        ],
                        "links": {"next": None},
                    },
                )

        respx.get("https://api.honeycomb.io/2/teams/my-team/environments").mock(
            side_effect=envs_handler
        )

        async with HoneycombClient(
            management_key="hcamk_test", management_secret="test_secret"
        ) as client:
            envs = await client.environments.list_async(team="my-team")

        assert len(envs) == 5
        assert envs[0].id == "env-1"
        assert envs[4].id == "env-5"
        assert call_count["value"] == 2


# =============================================================================
# Service Map Dependencies Tests
# =============================================================================


class TestServiceMapDependencies:
    """Tests for Service Map Dependencies resource."""

    @respx.mock
    async def test_create_request(self):
        """Test creating a map dependencies request."""
        respx.post("https://api.honeycomb.io/1/maps/dependencies/requests").mock(
            return_value=Response(
                200,
                json={
                    "request_id": "req-123",
                    "status": "pending",
                },
            )
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            req = await client.service_map_dependencies.create_async(
                request=ServiceMapDependencyRequestCreate(time_range=7200)
            )

        assert req.request_id == "req-123"
        assert req.status == ServiceMapDependencyRequestStatus.PENDING

    @respx.mock
    async def test_get_result_single_page(self):
        """Test getting map dependencies with a single page of results."""
        respx.get("https://api.honeycomb.io/1/maps/dependencies/requests/req-123").mock(
            return_value=Response(
                200,
                json={
                    "request_id": "req-123",
                    "status": "ready",
                    "dependencies": [
                        {
                            "parent_node": {"name": "service-a", "type": "service"},
                            "child_node": {"name": "service-b", "type": "service"},
                            "call_count": 100,
                        },
                        {
                            "parent_node": {"name": "service-b", "type": "service"},
                            "child_node": {"name": "service-c", "type": "service"},
                            "call_count": 50,
                        },
                    ],
                    "links": {"next": None},
                },
            )
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            result = await client.service_map_dependencies.get_result_async("req-123")

        assert result.request_id == "req-123"
        assert result.status == ServiceMapDependencyRequestStatus.READY
        assert len(result.dependencies) == 2
        assert result.dependencies[0].parent_node.name == "service-a"
        assert result.dependencies[0].child_node.name == "service-b"
        assert result.dependencies[0].call_count == 100

    @respx.mock
    async def test_get_result_multiple_pages(self):
        """Test getting map dependencies with multiple pages of results."""
        call_count = {"value": 0}

        def deps_handler(_request):
            call_count["value"] += 1
            if call_count["value"] == 1:
                # First page
                return Response(
                    200,
                    json={
                        "request_id": "req-123",
                        "status": "ready",
                        "dependencies": [
                            {
                                "parent_node": {"name": f"svc-{i}", "type": "service"},
                                "child_node": {"name": f"svc-{i + 1}", "type": "service"},
                                "call_count": i * 10,
                            }
                            for i in range(1, 4)
                        ],
                        "links": {
                            "next": "/1/maps/dependencies/requests/req-123?page[after]=cursor1&page[size]=100"
                        },
                    },
                )
            else:
                # Second page
                return Response(
                    200,
                    json={
                        "request_id": "req-123",
                        "status": "ready",
                        "dependencies": [
                            {
                                "parent_node": {"name": f"svc-{i}", "type": "service"},
                                "child_node": {"name": f"svc-{i + 1}", "type": "service"},
                                "call_count": i * 10,
                            }
                            for i in range(4, 6)
                        ],
                        "links": {"next": None},
                    },
                )

        respx.get("https://api.honeycomb.io/1/maps/dependencies/requests/req-123").mock(
            side_effect=deps_handler
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            result = await client.service_map_dependencies.get_result_async("req-123")

        assert len(result.dependencies) == 5
        assert result.dependencies[0].parent_node.name == "svc-1"
        assert result.dependencies[4].parent_node.name == "svc-5"
        assert call_count["value"] == 2

    @respx.mock
    async def test_get_result_max_pages_limit(self):
        """Test that max_pages parameter limits pagination."""
        # First page - has next link but we'll stop
        respx.get("https://api.honeycomb.io/1/maps/dependencies/requests/req-123").mock(
            return_value=Response(
                200,
                json={
                    "request_id": "req-123",
                    "status": "ready",
                    "dependencies": [
                        {
                            "parent_node": {"name": "svc-1", "type": "service"},
                            "child_node": {"name": "svc-2", "type": "service"},
                            "call_count": 10,
                        }
                    ],
                    "links": {
                        "next": "/1/maps/dependencies/requests/req-123?page[after]=cursor1&page[size]=100"
                    },
                },
            )
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            result = await client.service_map_dependencies.get_result_async("req-123", max_pages=1)

        # Should only get first page due to max_pages=1
        assert len(result.dependencies) == 1

    @respx.mock
    async def test_get_result_pending_status(self):
        """Test getting map dependencies when status is pending."""
        respx.get("https://api.honeycomb.io/1/maps/dependencies/requests/req-123").mock(
            return_value=Response(
                200,
                json={
                    "request_id": "req-123",
                    "status": "pending",
                    "dependencies": None,
                },
            )
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            result = await client.service_map_dependencies.get_result_async("req-123")

        assert result.status == ServiceMapDependencyRequestStatus.PENDING
        assert result.dependencies is None

    @respx.mock
    async def test_get_with_filters(self):
        """Test creating request with service filters."""
        route = respx.post("https://api.honeycomb.io/1/maps/dependencies/requests").mock(
            return_value=Response(
                200,
                json={
                    "request_id": "req-123",
                    "status": "pending",
                },
            )
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            req = await client.service_map_dependencies.create_async(
                request=ServiceMapDependencyRequestCreate(
                    time_range=7200,
                    filters=[
                        ServiceMapNode(name="user-service"),
                        ServiceMapNode(name="auth-service"),
                    ],
                )
            )

        assert req.request_id == "req-123"

        # Verify the request body
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["time_range"] == 7200
        assert len(body["filters"]) == 2
        assert body["filters"][0]["name"] == "user-service"


class TestServiceMapDependenciesModels:
    """Tests for Service Map Dependencies models."""

    def test_request_create_default_time_range(self):
        """Test ServiceMapDependencyRequestCreate default time range."""
        req = ServiceMapDependencyRequestCreate()
        assert req.time_range == 7200  # 2 hours default

    def test_request_create_model_dump(self):
        """Test ServiceMapDependencyRequestCreate serialization."""
        req = ServiceMapDependencyRequestCreate(
            start_time=1622548800,
            time_range=3600,
            filters=[ServiceMapNode(name="svc-a")],
        )
        data = req.model_dump_for_api()

        assert data["start_time"] == 1622548800
        assert data["time_range"] == 3600
        assert len(data["filters"]) == 1
        assert "end_time" not in data  # None values excluded

    def test_map_node_default_type(self):
        """Test ServiceMapNode default type."""
        from honeycomb.models import ServiceMapNodeType

        node = ServiceMapNode(name="my-service")
        assert node.type == ServiceMapNodeType.SERVICE


# =============================================================================
# Query Results Pagination Tests
# =============================================================================


class TestQueryResultsPagination:
    """Tests for Query Results pagination and disable_series."""

    @respx.mock
    async def test_run_with_disable_series_default(self):
        """Test that create_and_run_async defaults to disable_series=True."""
        from honeycomb.models import QueryBuilder

        # Mock create saved query
        respx.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(200, json={"id": "query-456", "query_json": {}})
        )

        # Mock create query result
        create_result_route = respx.post(
            "https://api.honeycomb.io/1/query_results/my-dataset"
        ).mock(return_value=Response(200, json={"id": "result-123"}))

        # Mock get query result (complete)
        respx.get("https://api.honeycomb.io/1/query_results/my-dataset/result-123").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "results": [{"count": 100}, {"count": 50}],
                        "series": [],
                    },
                },
            )
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            query, result = await client.query_results.create_and_run_async(
                QueryBuilder().dataset("my-dataset").time_range(3600).count().build(),
                dataset="my-dataset",
            )

        assert len(result.data.rows) == 2
        assert query.id == "query-456"

        # Verify disable_series=True was set on query result creation
        import json

        body = json.loads(create_result_route.calls[0].request.content)
        assert body["disable_series"] is True
        assert body["query_id"] == "query-456"

    @respx.mock
    async def test_run_with_disable_series_false(self):
        """Test that disable_series can be set to False."""
        from honeycomb.models import QueryBuilder

        # Mock create saved query
        respx.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(200, json={"id": "query-456", "query_json": {}})
        )

        # Mock create query result
        create_result_route = respx.post(
            "https://api.honeycomb.io/1/query_results/my-dataset"
        ).mock(return_value=Response(200, json={"id": "result-123"}))

        # Mock get query result
        respx.get("https://api.honeycomb.io/1/query_results/my-dataset/result-123").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "results": [{"count": 100}],
                        "series": [{"time": 123, "count": 100}],
                    }
                },
            )
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            await client.query_results.create_and_run_async(
                QueryBuilder().dataset("my-dataset").time_range(3600).count().build(),
                dataset="my-dataset",
                disable_series=False,
            )

        # Verify disable_series=False was set
        import json

        body = json.loads(create_result_route.calls[0].request.content)
        assert body["disable_series"] is False
        assert body["query_id"] == "query-456"


class TestQueryResultsPaginationHelpers:
    """Tests for query results pagination helper methods."""

    def test_normalize_time_range_relative(self):
        """Test normalizing relative time range."""
        from honeycomb.models import QuerySpec

        client = HoneycombClient(api_key="test", sync=True)
        resource = client.query_results

        spec = QuerySpec(time_range=3600)  # 1 hour ago
        start, end = resource._normalize_time_range(spec)

        assert end > start
        assert end - start == 3600  # 1 hour difference

    def test_normalize_time_range_absolute(self):
        """Test normalizing absolute time range."""
        from honeycomb.models import QuerySpec

        client = HoneycombClient(api_key="test", sync=True)
        resource = client.query_results

        spec = QuerySpec(start_time=1000000, end_time=1003600)
        start, end = resource._normalize_time_range(spec)

        assert start == 1000000
        assert end == 1003600

    def test_build_row_key_with_breakdowns(self):
        """Test building composite key from breakdowns."""
        from honeycomb.models import QuerySpec

        client = HoneycombClient(api_key="test", sync=True)
        resource = client.query_results

        spec = QuerySpec(
            time_range=3600,
            calculations=[{"op": "COUNT"}],
            breakdowns=["service", "endpoint"],
        )

        row = {"service": "api", "endpoint": "/users", "COUNT": 100}
        key = resource._build_row_key(row, spec)

        assert key == ("api", "/users", 100)

    def test_build_row_key_with_alias(self):
        """Test building composite key with calculation alias."""
        from honeycomb.models import QuerySpec

        client = HoneycombClient(api_key="test", sync=True)
        resource = client.query_results

        spec = QuerySpec(
            time_range=3600,
            calculations=[{"op": "AVG", "column": "duration_ms", "alias": "avg_duration"}],
            breakdowns=["service"],
        )

        row = {"service": "api", "avg_duration": 150.5}
        key = resource._build_row_key(row, spec)

        assert key == ("api", 150.5)


class TestRunAllAsync:
    """Tests for run_all_async method."""

    @respx.mock
    async def test_run_all_single_page(self):
        """Test run_all_async with single page of results."""
        from honeycomb.models import QuerySpec

        # Mock create saved query
        respx.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(200, json={"id": "query-456", "query_json": {}})
        )

        # Mock first (and only) query result
        respx.post("https://api.honeycomb.io/1/query_results/my-dataset").mock(
            return_value=Response(200, json={"id": "result-123"})
        )

        respx.get("https://api.honeycomb.io/1/query_results/my-dataset/result-123").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "results": [
                            {"service": "api", "count": 100},
                            {"service": "worker", "count": 50},
                        ],
                        "series": [],
                    }
                },
            )
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            rows = await client.query_results.run_all_async(
                dataset="my-dataset",
                spec=QuerySpec(
                    time_range=3600,
                    calculations=[{"op": "COUNT"}],
                    breakdowns=["service"],
                ),
            )

        assert len(rows) == 2
        assert rows[0]["service"] == "api"
        assert rows[1]["service"] == "worker"

    @respx.mock
    async def test_run_all_with_progress_callback(self):
        """Test run_all_async progress callback."""
        from honeycomb.models import QuerySpec

        progress_calls = []

        def track_progress(page, total):
            progress_calls.append((page, total))

        # Mock create saved query
        respx.post("https://api.honeycomb.io/1/queries/my-dataset").mock(
            return_value=Response(200, json={"id": "query-456", "query_json": {}})
        )

        # Mock single page
        respx.post("https://api.honeycomb.io/1/query_results/my-dataset").mock(
            return_value=Response(200, json={"id": "result-123"})
        )

        respx.get("https://api.honeycomb.io/1/query_results/my-dataset/result-123").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "results": [{"service": "api", "count": 100}],
                        "series": [],
                    }
                },
            )
        )

        async with HoneycombClient(api_key="test-api-key") as client:
            await client.query_results.run_all_async(
                dataset="my-dataset",
                spec=QuerySpec(
                    time_range=3600,
                    calculations=[{"op": "COUNT"}],
                    breakdowns=["service"],
                ),
                on_page=track_progress,
            )

        assert len(progress_calls) == 1
        assert progress_calls[0] == (1, 1)  # page 1, 1 total row

    @respx.mock
    async def test_run_all_validation_error_no_calculations(self):
        """Test run_all_async raises error if no calculations."""
        import pytest

        from honeycomb.models import QuerySpec

        async with HoneycombClient(api_key="test-api-key") as client:
            with pytest.raises(ValueError, match="calculations is required"):
                await client.query_results.run_all_async(
                    dataset="my-dataset",
                    spec=QuerySpec(time_range=3600),  # No calculations!
                )

    @respx.mock
    async def test_run_all_validation_error_conflicting_orders(self):
        """Test run_all_async raises error if spec has orders."""
        import pytest

        from honeycomb.models import QuerySpec

        async with HoneycombClient(api_key="test-api-key") as client:
            with pytest.raises(ValueError, match="orders must be None"):
                await client.query_results.run_all_async(
                    dataset="my-dataset",
                    spec=QuerySpec(
                        time_range=3600,
                        calculations=[{"op": "COUNT"}],
                        orders=[{"op": "COUNT", "order": "ascending"}],
                    ),
                )
