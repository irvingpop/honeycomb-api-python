"""Tests for MCP server module."""

import os
from unittest.mock import patch

import pytest

from honeycomb.mcp.server import (
    TOOL_CATEGORIES,
    _get_category_from_tool_name,
    _get_meta_tools,
    _get_tool_catalog,
    _use_native_tools,
)
from honeycomb.tools import HONEYCOMB_TOOLS


class TestCategoryExtraction:
    """Tests for tool name to category extraction."""

    def test_trigger_tools(self):
        """Test trigger tool category extraction."""
        assert _get_category_from_tool_name("honeycomb_list_triggers") == "triggers"
        assert _get_category_from_tool_name("honeycomb_get_trigger") == "triggers"
        assert _get_category_from_tool_name("honeycomb_create_trigger") == "triggers"
        assert _get_category_from_tool_name("honeycomb_update_trigger") == "triggers"
        assert _get_category_from_tool_name("honeycomb_delete_trigger") == "triggers"

    def test_slo_tools(self):
        """Test SLO tool category extraction."""
        assert _get_category_from_tool_name("honeycomb_list_slos") == "slos"
        assert _get_category_from_tool_name("honeycomb_get_slo") == "slos"
        assert _get_category_from_tool_name("honeycomb_create_slo") == "slos"

    def test_burn_alert_tools(self):
        """Test burn alert tool category extraction."""
        assert _get_category_from_tool_name("honeycomb_list_burn_alerts") == "burn_alerts"
        assert _get_category_from_tool_name("honeycomb_create_burn_alert") == "burn_alerts"

    def test_dataset_tools(self):
        """Test dataset tool category extraction."""
        assert _get_category_from_tool_name("honeycomb_list_datasets") == "datasets"
        assert _get_category_from_tool_name("honeycomb_get_dataset") == "datasets"

    def test_discovery_tools(self):
        """Test discovery (analysis) tool category extraction."""
        assert _get_category_from_tool_name("honeycomb_search_columns") == "discovery"
        assert _get_category_from_tool_name("honeycomb_get_environment_summary") == "discovery"

    def test_query_tools(self):
        """Test query tool category extraction."""
        assert _get_category_from_tool_name("honeycomb_create_query") == "queries"
        assert _get_category_from_tool_name("honeycomb_run_query") == "queries"

    def test_auth_tools(self):
        """Test auth tool category extraction."""
        assert _get_category_from_tool_name("honeycomb_get_auth") == "auth"

    def test_recipient_tools(self):
        """Test recipient tool category extraction."""
        assert _get_category_from_tool_name("honeycomb_list_recipients") == "recipients"
        assert _get_category_from_tool_name("honeycomb_get_recipient_triggers") == "recipients"

    def test_all_tools_have_categories(self):
        """Ensure all 67 tools have valid categories."""
        for tool in HONEYCOMB_TOOLS:
            category = _get_category_from_tool_name(tool["name"])
            assert category != "unknown", f"Tool {tool['name']} has unknown category"
            assert category in TOOL_CATEGORIES, (
                f"Tool {tool['name']} category {category} not in TOOL_CATEGORIES"
            )


class TestMetaTools:
    """Tests for meta-tool definitions."""

    def test_meta_tools_count(self):
        """Test that we have exactly 2 meta-tools."""
        meta_tools = _get_meta_tools()
        assert len(meta_tools) == 2

    def test_discover_tools_schema(self):
        """Test honeycomb_discover_tools schema."""
        meta_tools = _get_meta_tools()
        discover_tool = next(t for t in meta_tools if t["name"] == "honeycomb_discover_tools")

        assert "input_schema" in discover_tool
        assert discover_tool["input_schema"]["type"] == "object"
        assert "category" in discover_tool["input_schema"]["properties"]
        assert "enum" in discover_tool["input_schema"]["properties"]["category"]

        # Verify all categories are in enum
        enum_categories = discover_tool["input_schema"]["properties"]["category"]["enum"]
        assert set(enum_categories) == set(TOOL_CATEGORIES)

    def test_call_tool_schema(self):
        """Test honeycomb_call_tool schema."""
        meta_tools = _get_meta_tools()
        call_tool = next(t for t in meta_tools if t["name"] == "honeycomb_call_tool")

        assert "input_schema" in call_tool
        assert call_tool["input_schema"]["type"] == "object"
        assert "tool_name" in call_tool["input_schema"]["properties"]
        assert "arguments" in call_tool["input_schema"]["properties"]
        assert call_tool["input_schema"]["required"] == ["tool_name", "arguments"]


class TestToolCatalog:
    """Tests for tool catalog generation."""

    def test_catalog_returns_all_tools(self):
        """Test that catalog returns all tools without filter."""
        # Without management credentials, should exclude 10 management tools
        with patch.dict(os.environ, {}, clear=True):
            catalog = _get_tool_catalog(HONEYCOMB_TOOLS)
            assert catalog["total"] == 59  # 69 - 10 management tools
            assert len(catalog["tools"]) == 59
            assert "hint" in catalog

    def test_catalog_with_management_credentials(self):
        """Test that catalog includes management tools when credentials available."""
        with patch.dict(
            os.environ,
            {"HONEYCOMB_MANAGEMENT_KEY": "test-key", "HONEYCOMB_MANAGEMENT_SECRET": "test-secret"},
        ):
            catalog = _get_tool_catalog(HONEYCOMB_TOOLS)
            assert catalog["total"] == 69  # All tools
            assert len(catalog["tools"]) == 69

    def test_catalog_filters_management_tools(self):
        """Test that management tools are filtered without credentials."""
        with patch.dict(os.environ, {}, clear=True):
            catalog = _get_tool_catalog(HONEYCOMB_TOOLS)
            tool_names = {t["name"] for t in catalog["tools"]}

            # Management tools should not be present
            assert "honeycomb_list_environments" not in tool_names
            assert "honeycomb_list_api_keys" not in tool_names

            # v1 tools should be present
            assert "honeycomb_list_datasets" in tool_names
            assert "honeycomb_list_triggers" in tool_names

    def test_catalog_filter_by_category(self):
        """Test filtering by category."""
        catalog = _get_tool_catalog(HONEYCOMB_TOOLS, category="triggers")
        assert catalog["total"] == 5
        for tool in catalog["tools"]:
            assert tool["category"] == "triggers"

    def test_catalog_filter_discovery(self):
        """Test filtering by discovery category (maps to analysis)."""
        catalog = _get_tool_catalog(HONEYCOMB_TOOLS, category="discovery")
        assert catalog["total"] == 2
        for tool in catalog["tools"]:
            assert tool["category"] == "discovery"

    def test_catalog_tool_structure(self):
        """Test that catalog tool entries have expected structure."""
        catalog = _get_tool_catalog(HONEYCOMB_TOOLS)
        tool = catalog["tools"][0]

        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert "category" in tool

        # Schema should have required fields
        assert "required" in tool["input_schema"]
        assert "properties" in tool["input_schema"]

    def test_catalog_required_params(self):
        """Test that required params are included in schema."""
        catalog = _get_tool_catalog(HONEYCOMB_TOOLS, category="triggers")

        # honeycomb_list_triggers requires dataset
        list_tool = next(t for t in catalog["tools"] if t["name"] == "honeycomb_list_triggers")
        assert "dataset" in list_tool["input_schema"]["required"]


class TestNativeToolsMode:
    """Tests for native tools mode switching."""

    def test_native_tools_disabled_by_default(self):
        """Test that native tools mode is disabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            assert _use_native_tools() is False

    def test_native_tools_enabled_with_1(self):
        """Test enabling native tools with '1'."""
        with patch.dict(os.environ, {"HONEYCOMB_MCP_NATIVE_TOOLS": "1"}):
            assert _use_native_tools() is True

    def test_native_tools_enabled_with_true(self):
        """Test enabling native tools with 'true'."""
        with patch.dict(os.environ, {"HONEYCOMB_MCP_NATIVE_TOOLS": "true"}):
            assert _use_native_tools() is True

    def test_native_tools_enabled_with_TRUE(self):
        """Test enabling native tools with 'TRUE'."""
        with patch.dict(os.environ, {"HONEYCOMB_MCP_NATIVE_TOOLS": "TRUE"}):
            assert _use_native_tools() is True

    def test_native_tools_disabled_with_0(self):
        """Test that '0' keeps native tools disabled."""
        with patch.dict(os.environ, {"HONEYCOMB_MCP_NATIVE_TOOLS": "0"}):
            assert _use_native_tools() is False

    def test_native_tools_disabled_with_false(self):
        """Test that 'false' keeps native tools disabled."""
        with patch.dict(os.environ, {"HONEYCOMB_MCP_NATIVE_TOOLS": "false"}):
            assert _use_native_tools() is False


class TestToolCategories:
    """Tests for tool category definitions."""

    def test_all_categories_present(self):
        """Test that all expected categories are defined."""
        expected_categories = {
            "auth",
            "api_keys",
            "environments",
            "datasets",
            "columns",
            "derived_columns",
            "triggers",
            "slos",
            "burn_alerts",
            "queries",
            "boards",
            "markers",
            "marker_settings",
            "recipients",
            "events",
            "service_map",
            "discovery",
        }
        assert set(TOOL_CATEGORIES) == expected_categories

    def test_discovery_replaces_analysis(self):
        """Test that 'discovery' is used instead of 'analysis'."""
        assert "discovery" in TOOL_CATEGORIES
        assert "analysis" not in TOOL_CATEGORIES


# Integration tests for MCP server (require mcp package)
@pytest.fixture
def mcp_available():
    """Check if MCP package is available."""
    try:
        import mcp  # noqa: F401

        return True
    except ImportError:
        return False


@pytest.mark.asyncio
async def test_server_import_without_mcp():
    """Test that server module can be imported without MCP package."""
    # This test verifies the lazy import pattern works
    from honeycomb.mcp import server

    assert hasattr(server, "run_server")
    assert hasattr(server, "main")


@pytest.mark.asyncio
async def test_meta_tool_call_discover(mcp_available):
    """Test honeycomb_discover_tools meta-tool execution."""
    if not mcp_available:
        pytest.skip("MCP package not installed")

    # Import after skip check

    from honeycomb.mcp.server import _get_tool_catalog

    # Simulate what call_tool does for honeycomb_discover_tools
    catalog = _get_tool_catalog(HONEYCOMB_TOOLS, category="triggers")

    # Verify response format
    assert isinstance(catalog, dict)
    assert "tools" in catalog
    assert "total" in catalog
    assert catalog["total"] == 5


@pytest.mark.asyncio
async def test_meta_tool_call_tool_validation():
    """Test that honeycomb_call_tool validates tool names."""
    from honeycomb.tools import HONEYCOMB_TOOLS

    tool_names = {tool["name"] for tool in HONEYCOMB_TOOLS}

    # Valid tool
    assert "honeycomb_list_triggers" in tool_names

    # Invalid tool
    assert "honeycomb_invalid_tool" not in tool_names
