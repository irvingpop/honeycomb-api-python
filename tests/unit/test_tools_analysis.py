"""Unit tests for analysis tool execution."""

import json

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from honeycomb.tools.executor import execute_tool


@pytest.fixture
def client() -> HoneycombClient:
    """Create a test client."""
    return HoneycombClient(api_key="test-api-key")


class TestSearchColumnsExecution:
    """Tests for honeycomb_search_columns tool execution."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_columns_basic(self, client: HoneycombClient):
        """Basic column search should work."""
        # Mock datasets list
        respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "API Logs", "slug": "api-logs"}])
        )
        # Mock columns
        respx.get("https://api.honeycomb.io/1/columns/api-logs").mock(
            return_value=Response(
                200,
                json=[
                    {"id": "c1", "key_name": "status_code", "type": "integer"},
                    {"id": "c2", "key_name": "error_message", "type": "string"},
                    {"id": "c3", "key_name": "duration_ms", "type": "float"},
                ],
            )
        )
        # Mock derived columns (per dataset)
        respx.get("https://api.honeycomb.io/1/derived_columns/api-logs").mock(
            return_value=Response(200, json=[])
        )
        # Mock environment-wide derived columns
        respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(200, json=[])
        )

        async with client:
            result = await execute_tool(client, "honeycomb_search_columns", {"query": "error"})

        data = json.loads(result)
        assert data["total_matches"] >= 1
        assert data["datasets_searched"] == 1
        assert any(r["column"] == "error_message" for r in data["results"])

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_columns_specific_dataset(self, client: HoneycombClient):
        """Search in specific dataset should not call /datasets."""
        # Should NOT call /datasets when dataset is specified
        # Mock columns
        respx.get("https://api.honeycomb.io/1/columns/api-logs").mock(
            return_value=Response(
                200,
                json=[
                    {"id": "c1", "key_name": "http.status_code", "type": "integer"},
                ],
            )
        )
        # Mock derived columns
        respx.get("https://api.honeycomb.io/1/derived_columns/api-logs").mock(
            return_value=Response(200, json=[])
        )
        # Mock environment-wide derived columns
        respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(200, json=[])
        )

        async with client:
            result = await execute_tool(
                client,
                "honeycomb_search_columns",
                {"query": "status", "dataset": "api-logs"},
            )

        data = json.loads(result)
        assert data["total_matches"] >= 1
        assert any(r["column"] == "http.status_code" for r in data["results"])

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_columns_with_pagination(self, client: HoneycombClient):
        """Pagination parameters should be respected."""
        # Mock datasets
        respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "Test", "slug": "test"}])
        )
        # Create many columns
        columns = [{"id": f"c{i}", "key_name": f"error_{i}", "type": "string"} for i in range(100)]
        respx.get("https://api.honeycomb.io/1/columns/test").mock(
            return_value=Response(200, json=columns)
        )
        respx.get("https://api.honeycomb.io/1/derived_columns/test").mock(
            return_value=Response(200, json=[])
        )
        respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(200, json=[])
        )

        async with client:
            result = await execute_tool(
                client,
                "honeycomb_search_columns",
                {"query": "error", "limit": 10, "offset": 5},
            )

        data = json.loads(result)
        assert len(data["results"]) == 10
        assert data["total_matches"] == 100
        assert data["has_more"] is True

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_columns_includes_derived(self, client: HoneycombClient):
        """Derived columns should be included in results."""
        respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "Test", "slug": "test"}])
        )
        respx.get("https://api.honeycomb.io/1/columns/test").mock(
            return_value=Response(
                200,
                json=[{"id": "c1", "key_name": "status_code", "type": "integer"}],
            )
        )
        respx.get("https://api.honeycomb.io/1/derived_columns/test").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": "dc1",
                        "alias": "is_error",
                        "expression": "GTE($status_code, 400)",
                        "description": "Request had error status",
                    }
                ],
            )
        )
        respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(200, json=[])
        )

        async with client:
            result = await execute_tool(client, "honeycomb_search_columns", {"query": "error"})

        data = json.loads(result)
        # Should find the derived column
        assert any(r["column"] == "is_error" and r["is_derived"] for r in data["results"])

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_columns_related_derived(self, client: HoneycombClient):
        """Related derived columns should be found."""
        respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "Test", "slug": "test"}])
        )
        respx.get("https://api.honeycomb.io/1/columns/test").mock(
            return_value=Response(
                200,
                json=[{"id": "c1", "key_name": "duration_ms", "type": "float"}],
            )
        )
        respx.get("https://api.honeycomb.io/1/derived_columns/test").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": "dc1",
                        "alias": "is_slow",
                        "expression": "GT($duration_ms, 1000)",
                        "description": "Request took >1s",
                    }
                ],
            )
        )
        respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(200, json=[])
        )

        async with client:
            result = await execute_tool(client, "honeycomb_search_columns", {"query": "duration"})

        data = json.loads(result)
        # Should find duration_ms as a direct match
        assert any(r["column"] == "duration_ms" for r in data["results"])
        # Should find is_slow as a related derived column (references duration_ms)
        assert any(r["column"] == "is_slow" for r in data["related_derived_columns"])


class TestEnvironmentSummaryExecution:
    """Tests for honeycomb_get_environment_summary tool execution."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_environment_summary_basic(self, client: HoneycombClient):
        """Basic environment summary should work."""
        # Mock auth
        respx.get("https://api.honeycomb.io/1/auth").mock(
            return_value=Response(
                200,
                json={
                    "id": "key123",
                    "type": "configuration",
                    "team": {"name": "Test Team", "slug": "test-team"},
                    "environment": {"name": "Production", "slug": "production"},
                    "api_key_access": {},
                },
            )
        )
        # Mock datasets
        respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "name": "API",
                        "slug": "api",
                        "description": "API logs",
                        "last_written_at": "2024-01-10T00:00:00Z",
                    }
                ],
            )
        )
        # Mock columns
        respx.get("https://api.honeycomb.io/1/columns/api").mock(
            return_value=Response(
                200,
                json=[
                    {"id": "c1", "key_name": "http.method", "type": "string"},
                    {"id": "c2", "key_name": "custom_field", "type": "string"},
                ],
            )
        )
        # Mock derived columns (per dataset)
        respx.get("https://api.honeycomb.io/1/derived_columns/api").mock(
            return_value=Response(200, json=[])
        )
        # Mock environment-wide derived columns
        respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(200, json=[])
        )

        async with client:
            result = await execute_tool(client, "honeycomb_get_environment_summary", {})

        data = json.loads(result)
        assert data["dataset_count"] == 1
        assert data["datasets"][0]["name"] == "api"
        assert data["datasets"][0]["semantic_groups"]["has_http"] is True
        assert "custom_field" in data["datasets"][0]["custom_columns"]

    @respx.mock
    @pytest.mark.asyncio
    async def test_environment_summary_without_columns(self, client: HoneycombClient):
        """Environment summary can exclude sample columns."""
        # Mock auth
        respx.get("https://api.honeycomb.io/1/auth").mock(
            return_value=Response(
                200,
                json={
                    "id": "key123",
                    "type": "configuration",
                    "team": {"name": "Test Team", "slug": "test-team"},
                    "environment": {"name": "Production", "slug": "production"},
                    "api_key_access": {},
                },
            )
        )
        # Mock datasets
        respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "API", "slug": "api", "description": None}])
        )
        # Mock columns
        respx.get("https://api.honeycomb.io/1/columns/api").mock(
            return_value=Response(
                200,
                json=[{"id": "c1", "key_name": "custom_field", "type": "string"}],
            )
        )
        # Mock derived columns
        respx.get("https://api.honeycomb.io/1/derived_columns/api").mock(
            return_value=Response(200, json=[])
        )
        respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(200, json=[])
        )

        async with client:
            result = await execute_tool(
                client,
                "honeycomb_get_environment_summary",
                {"include_sample_columns": False},
            )

        data = json.loads(result)
        assert data["datasets"][0]["custom_columns"] == []

    @respx.mock
    @pytest.mark.asyncio
    async def test_environment_summary_detects_semantic_groups(self, client: HoneycombClient):
        """Semantic groups should be detected correctly."""
        # Mock auth
        respx.get("https://api.honeycomb.io/1/auth").mock(
            return_value=Response(
                200,
                json={
                    "id": "key123",
                    "type": "configuration",
                    "team": {"name": "Test Team", "slug": "test-team"},
                    "environment": {"name": "Production", "slug": "production"},
                    "api_key_access": {},
                },
            )
        )
        # Mock datasets
        respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "API", "slug": "api", "description": None}])
        )
        # Mock columns with various OTel patterns
        respx.get("https://api.honeycomb.io/1/columns/api").mock(
            return_value=Response(
                200,
                json=[
                    {"id": "c1", "key_name": "http.method", "type": "string"},
                    {"id": "c2", "key_name": "db.system", "type": "string"},
                    {"id": "c3", "key_name": "trace.trace_id", "type": "string"},
                    {"id": "c4", "key_name": "k8s.pod.name", "type": "string"},
                ],
            )
        )
        # Mock derived columns
        respx.get("https://api.honeycomb.io/1/derived_columns/api").mock(
            return_value=Response(200, json=[])
        )
        respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(200, json=[])
        )

        async with client:
            result = await execute_tool(client, "honeycomb_get_environment_summary", {})

        data = json.loads(result)
        groups = data["datasets"][0]["semantic_groups"]
        assert groups["has_http"] is True
        assert groups["has_db"] is True
        assert groups["has_otel_traces"] is True
        assert groups["has_k8s"] is True

    @respx.mock
    @pytest.mark.asyncio
    async def test_environment_summary_includes_env_derived_columns(self, client: HoneycombClient):
        """Environment-wide derived columns should be included."""
        # Mock auth
        respx.get("https://api.honeycomb.io/1/auth").mock(
            return_value=Response(
                200,
                json={
                    "id": "key123",
                    "type": "configuration",
                    "team": {"name": "Test Team", "slug": "test-team"},
                    "environment": {"name": "Production", "slug": "production"},
                    "api_key_access": {},
                },
            )
        )
        # Mock datasets
        respx.get("https://api.honeycomb.io/1/datasets").mock(
            return_value=Response(200, json=[{"name": "API", "slug": "api", "description": None}])
        )
        # Mock columns
        respx.get("https://api.honeycomb.io/1/columns/api").mock(
            return_value=Response(200, json=[])
        )
        # Mock per-dataset derived columns
        respx.get("https://api.honeycomb.io/1/derived_columns/api").mock(
            return_value=Response(200, json=[])
        )
        # Mock environment-wide derived columns
        respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
            return_value=Response(
                200,
                json=[
                    {
                        "id": "dc1",
                        "alias": "sli.availability",
                        "expression": "LT($http.status_code, 500)",
                        "description": "Request succeeded",
                    }
                ],
            )
        )

        async with client:
            result = await execute_tool(client, "honeycomb_get_environment_summary", {})

        data = json.loads(result)
        assert data["environment_derived_columns"] is not None
        assert len(data["environment_derived_columns"]) == 1
        assert data["environment_derived_columns"][0]["alias"] == "sli.availability"


class TestToolDefinitions:
    """Tests for analysis tool definitions."""

    def test_search_columns_tool_definition(self):
        """Search columns tool definition should be valid."""
        from honeycomb.tools.resources.analysis import generate_search_columns_tool

        tool = generate_search_columns_tool()
        assert tool["name"] == "honeycomb_search_columns"
        assert "query" in tool["input_schema"]["required"]
        assert len(tool["description"]) >= 50

    def test_environment_summary_tool_definition(self):
        """Environment summary tool definition should be valid."""
        from honeycomb.tools.resources.analysis import generate_get_environment_summary_tool

        tool = generate_get_environment_summary_tool()
        assert tool["name"] == "honeycomb_get_environment_summary"
        assert tool["input_schema"]["required"] == []  # No required params
        assert len(tool["description"]) >= 50

    def test_get_tools_returns_both(self):
        """get_tools should return both analysis tools."""
        from honeycomb.tools.resources.analysis import get_tools

        tools = get_tools()
        assert len(tools) == 2
        names = {t["name"] for t in tools}
        assert "honeycomb_search_columns" in names
        assert "honeycomb_get_environment_summary" in names


class TestToolCount:
    """Test that tool count is correct after adding analysis tools."""

    def test_total_tool_count(self):
        """Total tool count should be 69 (67 existing + 2 analysis)."""
        from honeycomb.tools.generator import generate_all_tools

        tools = generate_all_tools()
        # Previously 67 tools, now 69 with analysis tools
        assert len(tools) == 69

    def test_analysis_tools_in_all_tools(self):
        """Analysis tools should be in the full tool list."""
        from honeycomb.tools.generator import generate_all_tools

        tools = generate_all_tools()
        names = {t["name"] for t in tools}
        assert "honeycomb_search_columns" in names
        assert "honeycomb_get_environment_summary" in names
