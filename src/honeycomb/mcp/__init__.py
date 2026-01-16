"""MCP (Model Context Protocol) server for Honeycomb API tools.

This module provides an MCP server that exposes Honeycomb API tools to
Claude Desktop and other MCP clients.

Usage:
    # Run via Python module
    python -m honeycomb.mcp

    # Or via console script (after installing with mcp extra)
    hny-mcp

Configuration:
    Set environment variables before running:
    - HONEYCOMB_API_KEY: Your Honeycomb environment API key
    - HONEYCOMB_MANAGEMENT_KEY: Your Honeycomb management key (optional)
    - HONEYCOMB_MCP_NATIVE_TOOLS: Set to "1" to expose all 67 tools directly

Claude Desktop configuration (macOS):
    ~/Library/Application Support/Claude/claude_desktop_config.json:
    {
        "mcpServers": {
            "honeycomb": {
                "command": "hny-mcp",
                "env": {
                    "HONEYCOMB_API_KEY": "your-api-key"
                }
            }
        }
    }
"""

from honeycomb.mcp.server import main, run_server

__all__ = ["main", "run_server"]
