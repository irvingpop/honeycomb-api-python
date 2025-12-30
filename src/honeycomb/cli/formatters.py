"""
Output formatters for CLI commands.

Supports table, JSON, and YAML output formats.
"""

import json
from enum import Enum
from typing import Any

import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

console = Console()


class OutputFormat(str, Enum):
    """Output format for CLI commands."""

    table = "table"
    json = "json"
    yaml = "yaml"


# Default output format for CLI commands
DEFAULT_OUTPUT_FORMAT = OutputFormat.table


def output_result(
    data: Any,
    format: OutputFormat,
    columns: list[str] | None = None,
    quiet: bool = False,
) -> None:
    """
    Output data in the specified format.

    Args:
        data: Data to output (Pydantic model, list of models, or dict)
        format: Output format (table, json, yaml)
        columns: Column names for table output (only used if format is table)
        quiet: If True, only output IDs (one per line)
    """
    # Handle quiet mode
    if quiet:
        if isinstance(data, list):
            for item in data:
                if isinstance(item, BaseModel):
                    console.print(item.id if hasattr(item, "id") else str(item))
                elif isinstance(item, dict):
                    console.print(item.get("id", str(item)))
        elif isinstance(data, BaseModel):
            console.print(data.id if hasattr(data, "id") else str(data))
        elif isinstance(data, dict):
            console.print(data.get("id", str(data)))
        return

    # Special handling for QueryResult objects in table mode (duck typing check)
    if (
        format == OutputFormat.table
        and isinstance(data, BaseModel)
        and hasattr(data, "data")
        and data.data is not None
        and hasattr(data.data, "rows")
    ):
        _output_query_result(data)
        return

    # Convert Pydantic models to dicts for easier handling
    data_dict: Any
    if isinstance(data, BaseModel):
        data_dict = data.model_dump(mode="json")
    elif isinstance(data, list) and data and isinstance(data[0], BaseModel):
        data_dict = [item.model_dump(mode="json") for item in data]
    else:
        data_dict = data

    # Output in requested format
    if format == OutputFormat.json:
        console.print(json.dumps(data_dict, indent=2, default=str))
    elif format == OutputFormat.yaml:
        console.print(yaml.dump(data_dict, default_flow_style=False, sort_keys=False))
    elif format == OutputFormat.table:
        if isinstance(data_dict, list):
            _output_table(data_dict, columns)
        else:
            # Single item - output as key-value pairs
            _output_single_item(data_dict)
    else:
        console.print(f"[red]Unknown output format: {format}[/red]")


def _output_table(data: list[dict[str, Any]], columns: list[str] | None = None) -> None:
    """Output a list of items as a table."""
    if not data:
        console.print("[yellow]No results found[/yellow]")
        return

    # Determine columns to display
    if columns is None:
        # Use all keys from first item
        columns = list(data[0].keys())

    table = Table()
    for col in columns:
        table.add_column(col.replace("_", " ").title(), style="cyan")

    for item in data:
        row = [str(item.get(col, "-")) for col in columns]
        table.add_row(*row)

    console.print(table)


def _output_single_item(data: dict[str, Any]) -> None:
    """Output a single item as key-value pairs in a table."""
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan bold")
    table.add_column("Value", style="white")

    for key, value in data.items():
        # Format complex values
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, indent=2, default=str)
        else:
            value_str = str(value)

        table.add_row(key, value_str)

    console.print(table)


def _output_query_result(result: Any) -> None:
    """Output a QueryResult object with proper formatting.

    Displays query results as a table with breakdown columns and calculation results.
    Shows query URL and result count.
    """
    # Check if data is available
    if not result.data or not hasattr(result.data, "rows"):
        console.print("[yellow]No data available (query may still be processing)[/yellow]")
        return

    rows = result.data.rows

    if not rows:
        console.print("[yellow]Query returned no results[/yellow]")
        # Still show the query URL
        if result.links and "query_url" in result.links:
            console.print(f"\n[dim]View in UI: {result.links['query_url']}[/dim]")
        return

    # Create table with all columns from first row
    table = Table(title=f"Query Results ({len(rows)} rows)")

    # Get all column names from first row
    columns = list(rows[0].keys())

    for col in columns:
        # Style calculation columns differently
        if col.isupper() or col.startswith("P"):  # COUNT, AVG, P99, etc.
            table.add_column(col, style="green bold", justify="right")
        else:
            table.add_column(col, style="cyan")

    # Add rows
    for row in rows:
        formatted_row = []
        for col in columns:
            value = row.get(col, "-")
            # Format numbers nicely
            if isinstance(value, (int, float)):
                if isinstance(value, float):
                    formatted_row.append(f"{value:.2f}")
                else:
                    formatted_row.append(str(value))
            else:
                formatted_row.append(str(value))
        table.add_row(*formatted_row)

    console.print(table)

    # Show query metadata
    if result.links and "query_url" in result.links:
        console.print(f"\n[dim]View in UI: {result.links['query_url']}[/dim]")
