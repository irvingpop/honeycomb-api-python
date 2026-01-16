"""Unit tests for analysis tool caching."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from honeycomb.tools.analysis.cache import (
    clear_all_caches,
    clear_cache_for_client,
    get_columns_cached,
    get_datasets_cached,
    get_derived_columns_cached,
)


@pytest.fixture
def client() -> HoneycombClient:
    """Create a test client."""
    return HoneycombClient(api_key="test-api-key")


@pytest.fixture(autouse=True)
def clear_cache_before_test():
    """Clear all caches before each test to ensure isolation."""
    clear_all_caches()
    yield
    clear_all_caches()


class TestDatasetsCaching:
    """Tests for datasets caching."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_cache_miss_fetches_from_api(self, client: HoneycombClient):
        """First call should fetch from API."""
        route = respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(
                200, json=[{"name": "Test", "slug": "test", "description": "Test dataset"}]
            )
        )

        async with client:
            datasets = await get_datasets_cached(client)

        assert len(datasets) == 1
        assert datasets[0].slug == "test"
        assert route.call_count == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_data(self, client: HoneycombClient):
        """Second call should return cached data without API call."""
        route = respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(
                200, json=[{"name": "Test", "slug": "test", "description": "Test dataset"}]
            )
        )

        async with client:
            # First call - cache miss
            datasets1 = await get_datasets_cached(client)
            # Second call - cache hit
            datasets2 = await get_datasets_cached(client)

        assert datasets1 == datasets2
        assert route.call_count == 1  # Only one API call

    @respx.mock
    @pytest.mark.asyncio
    async def test_different_clients_have_separate_caches(self):
        """Different client instances should have separate caches."""
        client1 = HoneycombClient(api_key="key1")
        client2 = HoneycombClient(api_key="key2")

        route = respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "Test", "slug": "test"}])
        )

        async with client1:
            await get_datasets_cached(client1)

        async with client2:
            await get_datasets_cached(client2)

        # Each client should make its own API call
        assert route.call_count == 2


class TestColumnsCaching:
    """Tests for columns caching."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_columns_cache_miss_fetches_from_api(self, client: HoneycombClient):
        """First call should fetch columns from API."""
        route = respx.get("https://api.honeycomb.io/1/columns/test-dataset").mock(
            return_value=Response(
                200,
                json=[
                    {"id": "c1", "key_name": "status_code", "type": "integer"},
                    {"id": "c2", "key_name": "duration_ms", "type": "float"},
                ],
            )
        )

        async with client:
            columns = await get_columns_cached(client, "test-dataset")

        assert len(columns) == 2
        assert columns[0].key_name == "status_code"
        assert route.call_count == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_columns_cache_hit_returns_cached_data(self, client: HoneycombClient):
        """Second call for same dataset should return cached data."""
        route = respx.get("https://api.honeycomb.io/1/columns/test-dataset").mock(
            return_value=Response(
                200, json=[{"id": "c1", "key_name": "status_code", "type": "integer"}]
            )
        )

        async with client:
            columns1 = await get_columns_cached(client, "test-dataset")
            columns2 = await get_columns_cached(client, "test-dataset")

        assert columns1 == columns2
        assert route.call_count == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_different_datasets_cached_separately(self, client: HoneycombClient):
        """Different datasets should have separate cache entries."""
        route1 = respx.get("https://api.honeycomb.io/1/columns/dataset1").mock(
            return_value=Response(200, json=[{"id": "c1", "key_name": "field1", "type": "string"}])
        )
        route2 = respx.get("https://api.honeycomb.io/1/columns/dataset2").mock(
            return_value=Response(200, json=[{"id": "c2", "key_name": "field2", "type": "string"}])
        )

        async with client:
            columns1 = await get_columns_cached(client, "dataset1")
            columns2 = await get_columns_cached(client, "dataset2")
            # Fetch again - should hit cache
            columns1_again = await get_columns_cached(client, "dataset1")
            columns2_again = await get_columns_cached(client, "dataset2")

        assert columns1[0].key_name == "field1"
        assert columns2[0].key_name == "field2"
        assert columns1 == columns1_again
        assert columns2 == columns2_again
        assert route1.call_count == 1
        assert route2.call_count == 1


class TestDerivedColumnsCaching:
    """Tests for derived columns caching."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_derived_columns_cache_miss_fetches_from_api(self, client: HoneycombClient):
        """First call should fetch derived columns from API."""
        route = respx.get("https://api.honeycomb.io/1/derived_columns/test-dataset").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": "dc1",
                        "alias": "is_error",
                        "expression": "GTE($status_code, 400)",
                        "description": "Error status",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
            )
        )

        async with client:
            derived = await get_derived_columns_cached(client, "test-dataset")

        assert len(derived) == 1
        assert derived[0].alias == "is_error"
        assert route.call_count == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_derived_columns_cache_hit_returns_cached_data(self, client: HoneycombClient):
        """Second call should return cached derived columns."""
        route = respx.get("https://api.honeycomb.io/1/derived_columns/test-dataset").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": "dc1",
                        "alias": "is_error",
                        "expression": "GTE($status_code, 400)",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
            )
        )

        async with client:
            derived1 = await get_derived_columns_cached(client, "test-dataset")
            derived2 = await get_derived_columns_cached(client, "test-dataset")

        assert derived1 == derived2
        assert route.call_count == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_environment_wide_derived_columns_cached(self, client: HoneycombClient):
        """Environment-wide derived columns (__all__) should be cached."""
        route = respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": "dc1",
                        "alias": "sli.availability",
                        "expression": "LT($status_code, 500)",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
            )
        )

        async with client:
            derived1 = await get_derived_columns_cached(client, "__all__")
            derived2 = await get_derived_columns_cached(client, "__all__")

        assert derived1 == derived2
        assert derived1[0].alias == "sli.availability"
        assert route.call_count == 1


class TestCacheClear:
    """Tests for cache clearing functionality."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_clear_cache_for_client(self, client: HoneycombClient):
        """clear_cache_for_client should clear only that client's cache."""
        route = respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "Test", "slug": "test"}])
        )

        async with client:
            # First fetch
            await get_datasets_cached(client)
            assert route.call_count == 1

            # Clear cache
            clear_cache_for_client(client)

            # Should fetch again
            await get_datasets_cached(client)
            assert route.call_count == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_clear_all_caches(self):
        """clear_all_caches should clear caches for all clients."""
        client1 = HoneycombClient(api_key="key1")
        client2 = HoneycombClient(api_key="key2")

        route = respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "Test", "slug": "test"}])
        )

        async with client1:
            await get_datasets_cached(client1)
        async with client2:
            await get_datasets_cached(client2)

        assert route.call_count == 2

        # Clear all caches
        clear_all_caches()

        # Both clients should need to fetch again
        async with client1:
            await get_datasets_cached(client1)
        async with client2:
            await get_datasets_cached(client2)

        assert route.call_count == 4


class TestCacheWarming:
    """Tests for cache warming behavior."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_environment_summary_warms_cache_for_column_search(self, client: HoneycombClient):
        """get_environment_summary should warm cache for honeycomb_search_columns."""
        from honeycomb.tools.executor import execute_tool

        # Mock all required endpoints
        respx.get("https://api.honeycomb.io/1/auth").mock(
            return_value=Response(
                200,
                json={
                    "id": "key123",
                    "type": "configuration",
                    "team": {"name": "Test", "slug": "test"},
                    "environment": {"name": "Prod", "slug": "prod"},
                    "api_key_access": {},
                },
            )
        )
        datasets_route = respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "Test", "slug": "test"}])
        )
        columns_route = respx.get("https://api.honeycomb.io/1/columns/test").mock(
            return_value=Response(
                200, json=[{"id": "c1", "key_name": "duration_ms", "type": "float"}]
            )
        )
        derived_route = respx.get("https://api.honeycomb.io/1/derived_columns/test").mock(
            return_value=Response(200, json=[])
        )
        env_derived_route = respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(200, json=[])
        )

        async with client:
            # First, get environment summary (warms the cache)
            await execute_tool(client, "honeycomb_get_environment_summary", {})

            # Record call counts after first tool
            datasets_after_summary = datasets_route.call_count
            columns_after_summary = columns_route.call_count
            derived_after_summary = derived_route.call_count
            env_derived_after_summary = env_derived_route.call_count

            # Now search columns - should use cache
            await execute_tool(client, "honeycomb_search_columns", {"query": "duration"})

            # Call counts should NOT have increased (cache hit)
            assert datasets_route.call_count == datasets_after_summary
            assert columns_route.call_count == columns_after_summary
            assert derived_route.call_count == derived_after_summary
            assert env_derived_route.call_count == env_derived_after_summary
