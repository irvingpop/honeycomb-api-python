"""MCP server for Honeycomb API tools.

This module provides an MCP (Model Context Protocol) server that exposes
Honeycomb API tools to Claude Desktop and other MCP clients.

By default, it exposes 2 meta-tools for token efficiency:
- honeycomb_discover_tools: Find available tools and their parameters
- honeycomb_call_tool: Execute any Honeycomb tool

Set HONEYCOMB_MCP_NATIVE_TOOLS=1 to expose all 67 tools directly.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

# Configure logging to stderr (never stdout for stdio servers)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("honeycomb.mcp")

# Category mapping: internal name -> display name
# "analysis" module contains discovery tools, so we rename it for clarity
CATEGORY_DISPLAY_NAMES = {
    "analysis": "discovery",
}

# Reverse mapping for lookup
CATEGORY_INTERNAL_NAMES = {v: k for k, v in CATEGORY_DISPLAY_NAMES.items()}

# All categories in logical order
# Tool categories
TOOL_CATEGORIES = [
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
    "discovery",  # Displayed as "discovery", internally "analysis"
]

# Tools that require management key (v2 API)
MANAGEMENT_KEY_TOOLS = {
    "honeycomb_list_api_keys",
    "honeycomb_get_api_key",
    "honeycomb_create_api_key",
    "honeycomb_update_api_key",
    "honeycomb_delete_api_key",
    "honeycomb_list_environments",
    "honeycomb_get_environment",
    "honeycomb_create_environment",
    "honeycomb_update_environment",
    "honeycomb_delete_environment",
}

# Destructive tools that permanently delete data (blocked by default)
DELETE_TOOLS = {
    "honeycomb_delete_dataset",
    "honeycomb_delete_trigger",
    "honeycomb_delete_slo",
    "honeycomb_delete_burn_alert",
    "honeycomb_delete_board",
    "honeycomb_delete_derived_column",
    "honeycomb_delete_column",
    "honeycomb_delete_marker",
    "honeycomb_delete_marker_setting",
    "honeycomb_delete_recipient",
    "honeycomb_delete_environment",  # v2 API - also in MANAGEMENT_KEY_TOOLS
    "honeycomb_delete_api_key",  # v2 API - also in MANAGEMENT_KEY_TOOLS
}


def _get_category_from_tool_name(tool_name: str) -> str:
    """Extract category from tool name.

    Tool names follow pattern: honeycomb_{action}_{resource}
    e.g., honeycomb_list_triggers -> triggers
          honeycomb_create_slo -> slos
          honeycomb_search_columns -> discovery (analysis tools)
          honeycomb_get_environment_summary -> discovery
    """
    # Special cases for analysis/discovery tools
    if tool_name in ("honeycomb_search_columns", "honeycomb_get_environment_summary"):
        return "discovery"

    # Standard pattern: honeycomb_{action}_{resource}
    parts = tool_name.replace("honeycomb_", "").split("_", 1)
    if len(parts) < 2:
        return "unknown"

    remainder = parts[1]

    # Handle plural/singular and special cases
    resource_map = {
        "triggers": "triggers",
        "trigger": "triggers",
        "slos": "slos",
        "slo": "slos",
        "burn_alerts": "burn_alerts",
        "burn_alert": "burn_alerts",
        "datasets": "datasets",
        "dataset": "datasets",
        "columns": "columns",
        "column": "columns",
        "derived_columns": "derived_columns",
        "derived_column": "derived_columns",
        "boards": "boards",
        "board": "boards",
        "queries": "queries",
        "query": "queries",
        "markers": "markers",
        "marker": "markers",
        "marker_settings": "marker_settings",
        "marker_setting": "marker_settings",
        "recipients": "recipients",
        "recipient": "recipients",
        "recipient_triggers": "recipients",
        "environments": "environments",
        "environment": "environments",
        "api_keys": "api_keys",
        "api_key": "api_keys",
        "events": "events",
        "event": "events",
        "batch_events": "events",
        "service_map": "service_map",
        "auth": "auth",
    }

    # Try direct match first
    if remainder in resource_map:
        return resource_map[remainder]

    # Try to find resource in remainder
    for key, category in resource_map.items():
        if remainder.endswith(key) or remainder.startswith(key):
            return category

    return "unknown"


def _get_meta_tools() -> list[dict[str, Any]]:
    """Return the meta-tool definitions."""
    return [
        {
            "name": "honeycomb_discover_tools",
            "description": (
                "Discover available Honeycomb API tools with complete schemas and examples. "
                "Returns tool names, full descriptions, complete input schemas, and usage examples. "
                "TIP: Start with honeycomb_get_environment_summary (discovery category) "
                "to see the current environment and available datasets. "
                "Then use this tool to find specific tools for your task. "
                "Optionally filter by category: " + ", ".join(TOOL_CATEGORIES) + "."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category (optional)",
                        "enum": TOOL_CATEGORIES,
                    }
                },
            },
        },
        {
            "name": "honeycomb_call_tool",
            "description": (
                "Call a Honeycomb API tool. Use honeycomb_discover_tools first "
                "to find tool names and required parameters."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "The tool to call (e.g., 'honeycomb_list_datasets')",
                    },
                    "arguments": {
                        "type": "object",
                        "description": "Arguments for the tool",
                    },
                },
                "required": ["tool_name", "arguments"],
            },
        },
    ]


def _get_tool_catalog(tools: list[dict[str, Any]], category: str | None = None) -> dict[str, Any]:
    """Return complete tool information for discovery.

    Args:
        tools: List of tool definitions
        category: Optional category filter (uses display names like "discovery")

    Returns:
        Dict with complete tool definitions including schemas and examples
    """
    # Check if management credentials are available
    has_mgmt_creds = bool(
        os.environ.get("HONEYCOMB_MANAGEMENT_KEY") and os.environ.get("HONEYCOMB_MANAGEMENT_SECRET")
    )

    # Convert display category to internal if needed
    internal_category = CATEGORY_INTERNAL_NAMES.get(category, category) if category else None

    tool_details = []
    for tool in tools:
        tool_name = tool["name"]

        # Skip management tools if credentials not available
        if tool_name in MANAGEMENT_KEY_TOOLS and not has_mgmt_creds:
            continue

        tool_category = _get_category_from_tool_name(tool_name)

        # Filter by category if specified (check both display and internal names)
        if category and tool_category != category and tool_category != internal_category:
            continue

        # Return complete tool definition with schema and examples
        tool_info = {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": tool["input_schema"],
            "category": tool_category,
        }

        # Include examples if present
        if "input_examples" in tool:
            tool_info["input_examples"] = tool["input_examples"]

        tool_details.append(tool_info)

    return {
        "tools": tool_details,
        "total": len(tool_details),
        "hint": "Use honeycomb_call_tool with tool_name and arguments to execute",
    }


def _use_native_tools() -> bool:
    """Check if native (all 67) tools mode is enabled."""
    return os.environ.get("HONEYCOMB_MCP_NATIVE_TOOLS", "").lower() in ("1", "true")


def _are_deletes_blocked() -> bool:
    """Check if delete operations are blocked (default: true).

    Set HONEYCOMB_ALLOW_DELETES=true to enable delete operations.
    This is a safety mechanism to prevent accidental data loss.
    """
    allow_deletes = os.environ.get("HONEYCOMB_ALLOW_DELETES", "").lower()
    return allow_deletes not in ("1", "true")


def _check_mcp_available() -> bool:
    """Check if MCP package is available."""
    try:
        import mcp  # noqa: F401

        return True
    except ImportError:
        return False


async def _run_server() -> None:
    """Run the MCP server with stdio transport."""
    # Check if running interactively (not invoked by MCP client)
    if sys.stdin.isatty():
        logger.error("MCP server must be invoked by an MCP client (Claude Desktop, Cursor, etc.)")
        print(
            "Error: MCP server cannot run in interactive mode.\n\n"
            "This server must be invoked by an MCP client:\n"
            "- Claude Desktop: Configure in claude_desktop_config.json\n"
            "- Claude Code: Use 'claude mcp add honeycomb --command hny-mcp'\n"
            "- Cursor: Configure in MCP settings\n\n"
            "See documentation: https://irvingpop.github.io/honeycomb-api-python/usage/mcp/",
            file=sys.stderr,
        )
        sys.exit(1)

    # Import MCP here to allow graceful failure if not installed
    try:
        import mcp.server.stdio
        import mcp.types as types
        from mcp.server.lowlevel import Server
    except ImportError as e:
        logger.error("MCP package not installed. Install with: pip install honeycomb-api[mcp]")
        raise ImportError(
            "MCP package not installed. Install with: pip install honeycomb-api[mcp]"
        ) from e

    # Import Honeycomb tools
    from honeycomb import HoneycombClient
    from honeycomb.tools import HONEYCOMB_TOOLS, execute_tool

    # Build tool name set for validation
    tool_names = {tool["name"] for tool in HONEYCOMB_TOOLS}

    server = Server("honeycomb")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available tools based on mode."""
        # Check if management credentials are available
        has_mgmt_creds = bool(
            os.environ.get("HONEYCOMB_MANAGEMENT_KEY")
            and os.environ.get("HONEYCOMB_MANAGEMENT_SECRET")
        )

        if _use_native_tools():
            # Native mode: expose tools directly (filter by available credentials)
            available_tools = [
                tool
                for tool in HONEYCOMB_TOOLS
                if tool["name"] not in MANAGEMENT_KEY_TOOLS or has_mgmt_creds
            ]
            logger.info("Native tools mode: exposing %d tools", len(available_tools))
            return [
                types.Tool(
                    name=tool["name"],
                    description=tool["description"],
                    inputSchema=tool["input_schema"],
                )
                for tool in available_tools
            ]

        # Default: meta-tools only
        meta_tools = _get_meta_tools()
        logger.info("Meta-tools mode: exposing %d meta-tools", len(meta_tools))
        return [
            types.Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool["input_schema"],
            )
            for tool in meta_tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[types.TextContent]:
        """Handle tool calls."""
        logger.info("Tool call: %s", name)

        # Meta-tool: discover
        if name == "honeycomb_discover_tools":
            catalog = _get_tool_catalog(HONEYCOMB_TOOLS, arguments.get("category"))
            return [types.TextContent(type="text", text=json.dumps(catalog, indent=2))]

        # Meta-tool: call (unwrap to actual tool)
        if name == "honeycomb_call_tool":
            name = arguments["tool_name"]
            arguments = arguments.get("arguments", {})
            logger.info("Meta-tool call_tool -> %s", name)

        # Validate tool exists
        if name not in tool_names:
            error_msg = (
                f"Unknown tool: {name}. Use honeycomb_discover_tools to see available tools."
            )
            logger.warning(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

        # Check if delete operations are blocked
        if name in DELETE_TOOLS and _are_deletes_blocked():
            error_msg = (
                f"DELETE OPERATION BLOCKED: {name}\n\n"
                f"Delete operations are disabled by default to prevent accidental data loss.\n"
                f"All Honeycomb delete operations are IRREVERSIBLE and PERMANENT.\n\n"
                f"To enable delete operations, set HONEYCOMB_ALLOW_DELETES=true in your MCP configuration.\n\n"
                f"Blocked operations:\n" + "\n".join(f"  - {tool}" for tool in sorted(DELETE_TOOLS))
            )
            logger.warning("Delete operation blocked: %s", name)
            return [types.TextContent(type="text", text=error_msg)]

        # Get credentials and determine which to use based on tool
        api_key = os.environ.get("HONEYCOMB_API_KEY")
        mgmt_key = os.environ.get("HONEYCOMB_MANAGEMENT_KEY")
        mgmt_secret = os.environ.get("HONEYCOMB_MANAGEMENT_SECRET")

        # Determine which credentials this tool needs and create client accordingly
        is_mgmt_tool = name in MANAGEMENT_KEY_TOOLS

        # Execute tool
        try:
            if is_mgmt_tool:
                # v2 API tools require management credentials
                if not mgmt_key or not mgmt_secret:
                    error_msg = (
                        f"Error: {name} requires HONEYCOMB_MANAGEMENT_KEY and "
                        "HONEYCOMB_MANAGEMENT_SECRET environment variables"
                    )
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

                # Use ONLY management credentials
                async with HoneycombClient(
                    management_key=mgmt_key, management_secret=mgmt_secret
                ) as client:
                    result = await execute_tool(client, name, arguments)
                    return [types.TextContent(type="text", text=result)]
            else:
                # v1 API tools require API key
                if not api_key:
                    error_msg = f"Error: {name} requires HONEYCOMB_API_KEY environment variable"
                    logger.error(error_msg)
                    return [types.TextContent(type="text", text=error_msg)]

                # Use ONLY api_key
                async with HoneycombClient(api_key=api_key) as client:
                    result = await execute_tool(client, name, arguments)
                    return [types.TextContent(type="text", text=result)]
        except Exception as e:
            logger.exception("Tool call failed: %s", name)
            error_msg = f"Error calling {name}: {e}"
            return [types.TextContent(type="text", text=error_msg)]

    # Run server with stdio transport
    logger.info("Starting Honeycomb MCP server...")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def run_server() -> None:
    """Entry point for running the MCP server (sync wrapper)."""
    asyncio.run(_run_server())


async def main() -> None:
    """Async entry point for running the MCP server."""
    await _run_server()
