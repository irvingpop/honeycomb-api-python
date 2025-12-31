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


def _output_table(data: list[dict[str, Any]], columns: list[str] | None = None) -> None:
    """Output a list of items as a table."""
    if not data:
        console.print("[yellow]No results found[/yellow]")
        return

    # Determine columns to display
    if columns is None:
        # Use all keys from first item, excluding timestamp fields
        all_columns = list(data[0].keys())
        # Filter out timestamp fields (can be added back with explicit columns parameter)
        columns = [
            col for col in all_columns if col not in ("created_at", "updated_at", "timestamps")
        ]

    table = Table()
    for col in columns:
        # ID columns should never truncate
        if col == "id" or col.endswith("_id"):
            table.add_column(col.replace("_", " ").title(), style="cyan", no_wrap=True)
        else:
            table.add_column(col.replace("_", " ").title(), style="cyan")

    for item in data:
        row = []
        for col in columns:
            value = item.get(col)
            # Display "-" for missing or None values
            row.append(str(value) if value is not None else "-")
        table.add_row(*row)

    console.print(table)


def _output_single_item(data: dict[str, Any]) -> None:
    """Output a single item as key-value pairs in a table."""
    from rich import box

    table = Table(show_header=True, box=box.ROUNDED, padding=(0, 1))
    table.add_column("Field", style="cyan bold", no_wrap=True)
    table.add_column("Value", style="white")

    for key, value in data.items():
        # Format complex values with nested tables/panels for clarity
        value_display: Any
        if isinstance(value, dict):
            if value:
                # Create a mini-table for dict values
                nested_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
                nested_table.add_column("Key", style="cyan")
                nested_table.add_column("Value", style="white")
                for k, v in value.items():
                    nested_table.add_row(str(k), str(v))
                value_display = nested_table
            else:
                value_display = "{}"
        elif isinstance(value, list):
            if value:
                # Special handling for scopes - split on ':' to show resource:permission
                if key == "scopes" and value and isinstance(value[0], str) and ":" in value[0]:
                    nested_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
                    nested_table.add_column("Resource", style="cyan")
                    nested_table.add_column("Permission", style="white")
                    for item in value:
                        parts = str(item).split(":", 1)
                        if len(parts) == 2:
                            nested_table.add_row(parts[0], parts[1])
                        else:
                            nested_table.add_row(str(item), "")
                    value_display = nested_table
                else:
                    # Regular list - single column
                    nested_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
                    nested_table.add_column("Value", style="white")
                    for item in value:
                        nested_table.add_row(str(item))
                    value_display = nested_table
            else:
                value_display = "[]"
        else:
            value_display = str(value)

        table.add_row(key, value_display)

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
