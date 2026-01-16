"""CLI entry point for Honeycomb MCP server.

Usage:
    python -m honeycomb.mcp

Configure in Claude Desktop:
    ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
    %APPDATA%/Claude/claude_desktop_config.json (Windows)
"""

import asyncio

from honeycomb.mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())
