"""Claude tool definitions for Honeycomb API.

This module provides Claude-compatible tool definitions that enable LLMs to create
and manage Honeycomb resources (triggers, SLOs, burn alerts) via structured tool calls.

Usage with Anthropic SDK:
    >>> from anthropic import Anthropic
    >>> from honeycomb.tools import HONEYCOMB_TOOLS
    >>>
    >>> client = Anthropic()
    >>> response = client.messages.create(
    ...     model="claude-sonnet-4-5-20250929",
    ...     max_tokens=4096,
    ...     tools=HONEYCOMB_TOOLS,
    ...     messages=[{"role": "user", "content": "Create a high error rate trigger"}]
    ... )
"""

from typing import Any

from honeycomb.tools.executor import execute_tool
from honeycomb.tools.generator import generate_all_tools

# Generate all tool definitions (includes input_examples for documentation)
_ALL_TOOLS_WITH_EXAMPLES: list[dict[str, Any]] = generate_all_tools()

# Claude-compatible tools (without input_examples which Claude API rejects)
HONEYCOMB_TOOLS: list[dict[str, Any]] = [
    {k: v for k, v in tool.items() if k != "input_examples"} for tool in _ALL_TOOLS_WITH_EXAMPLES
]


def get_tool(name: str) -> dict[str, Any] | None:
    """Get a tool definition by name.

    Args:
        name: Tool name (e.g., "honeycomb_create_trigger")

    Returns:
        Tool definition dict or None if not found

    Example:
        >>> tool = get_tool("honeycomb_create_trigger")
        >>> print(tool["description"])
    """
    for tool in HONEYCOMB_TOOLS:
        if tool["name"] == name:
            return tool
    return None


def get_all_tools() -> list[dict[str, Any]]:
    """Get all tool definitions.

    Returns:
        List of all 15 Priority 1 tool definitions

    Example:
        >>> tools = get_all_tools()
        >>> print(f"Available tools: {len(tools)}")
    """
    return HONEYCOMB_TOOLS.copy()


def list_tool_names() -> list[str]:
    """Get list of all tool names.

    Returns:
        List of tool names sorted alphabetically

    Example:
        >>> names = list_tool_names()
        >>> for name in names:
        ...     print(name)
    """
    return sorted([tool["name"] for tool in HONEYCOMB_TOOLS])


__all__ = [
    "HONEYCOMB_TOOLS",
    "get_tool",
    "get_all_tools",
    "list_tool_names",
    "execute_tool",
]
