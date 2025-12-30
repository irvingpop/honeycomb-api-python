"""
Query management and execution commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.queries import QuerySpec
from honeycomb.models.query_builder import QueryBuilder

app = typer.Typer(help="Manage and run queries")
console = Console()


@app.command("list")
def list_queries(
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__ for environment-wide)"
    ),
    include_board_annotations: bool = typer.Option(
        False, "--include-boards", help="Include board queries"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output query IDs"),
) -> None:
    """List all query annotations (saved queries) in a dataset."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        annotations = client.query_annotations.list(
            dataset=dataset, include_board_annotations=include_board_annotations
        )
        output_result(
            annotations,
            output,
            columns=["id", "name", "description", "created_at"],
            quiet=quiet,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_query(
    query_id: str = typer.Argument(..., help="Query ID"),
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__)"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific query."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        query = client.queries.get(dataset=dataset, query_id=query_id)
        output_result(query, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_query(
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__)"
    ),
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with query spec"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create (save) a query from a JSON file."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        query_spec = QuerySpec.model_validate(data)
        query = client.queries.create(dataset=dataset, spec=query_spec)

        console.print(f"[green]Created query with ID: {query.id}[/green]")
        output_result(query, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("run")
def run_query(
    # Dataset
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__)"
    ),
    # Input methods (mutually exclusive with builder flags)
    from_file: Path | None = typer.Option(
        None, "--from-file", "-f", help="JSON file with query spec"
    ),
    spec: str | None = typer.Option(None, "--spec", "-s", help="Inline JSON query spec"),
    query_id: str | None = typer.Option(None, "--query-id", help="Run an existing saved query"),
    # QueryBuilder flags - Calculations
    count: bool = typer.Option(False, "--count", help="Add COUNT calculation"),
    avg: list[str] = typer.Option([], "--avg", help="Add AVG calculation for column (repeatable)"),
    sum_cols: list[str] = typer.Option(
        [], "--sum", help="Add SUM calculation for column (repeatable)"
    ),
    min_calc: list[str] = typer.Option(
        [], "--min", help="Add MIN calculation for column (repeatable)"
    ),
    max_calc: list[str] = typer.Option(
        [], "--max", help="Add MAX calculation for column (repeatable)"
    ),
    p50: list[str] = typer.Option([], "--p50", help="Add P50 calculation for column (repeatable)"),
    p90: list[str] = typer.Option([], "--p90", help="Add P90 calculation for column (repeatable)"),
    p95: list[str] = typer.Option([], "--p95", help="Add P95 calculation for column (repeatable)"),
    p99: list[str] = typer.Option([], "--p99", help="Add P99 calculation for column (repeatable)"),
    # Time ranges
    time_range: int | None = typer.Option(None, "--time-range", help="Time range in seconds"),
    last_10_minutes: bool = typer.Option(False, "--last-10-minutes", help="Last 10 minutes"),
    last_30_minutes: bool = typer.Option(False, "--last-30-minutes", help="Last 30 minutes"),
    last_1_hour: bool = typer.Option(False, "--last-1-hour", help="Last 1 hour"),
    last_2_hours: bool = typer.Option(False, "--last-2-hours", help="Last 2 hours"),
    last_8_hours: bool = typer.Option(False, "--last-8-hours", help="Last 8 hours"),
    last_24_hours: bool = typer.Option(False, "--last-24-hours", help="Last 24 hours"),
    last_7_days: bool = typer.Option(False, "--last-7-days", help="Last 7 days"),
    # Filters (comma-separated: column,value)
    where_equals: list[str] = typer.Option(
        [], "--where-equals", help="Filter: column=value (format: col,val)"
    ),
    where_ne: list[str] = typer.Option(
        [], "--where-ne", help="Filter: column!=value (format: col,val)"
    ),
    where_gt: list[str] = typer.Option(
        [], "--where-gt", help="Filter: column>value (format: col,val)"
    ),
    where_gte: list[str] = typer.Option(
        [], "--where-gte", help="Filter: column>=value (format: col,val)"
    ),
    where_lt: list[str] = typer.Option(
        [], "--where-lt", help="Filter: column<value (format: col,val)"
    ),
    where_lte: list[str] = typer.Option(
        [], "--where-lte", help="Filter: column<=value (format: col,val)"
    ),
    where_contains: list[str] = typer.Option(
        [], "--where-contains", help="Filter: column contains value (format: col,val)"
    ),
    where_exists: list[str] = typer.Option(
        [], "--where-exists", help="Filter: column exists (just column name)"
    ),
    # Grouping and ordering
    group_by: list[str] = typer.Option([], "--group-by", help="Group by column (repeatable)"),
    order_by: str | None = typer.Option(None, "--order-by", help="Order by field"),
    limit_rows: int | None = typer.Option(None, "--limit", help="Limit results"),
    # Query execution
    poll_interval: float = typer.Option(1.0, "--poll-interval", help="Polling interval in seconds"),
    timeout: float = typer.Option(60.0, "--timeout", help="Timeout in seconds"),
    # Auth and output
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """
    Run a query and wait for results.

    Three modes:
    1. Builder mode: Use flags like --count, --avg, --where-equals, etc.
    2. File mode: --from-file query.json
    3. Spec mode: --spec '{"calculations": [...]}'
    4. Saved query mode: --query-id query-123
    """
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Determine which mode we're in
        using_builder = any(
            [
                count,
                avg,
                sum_cols,
                min_calc,
                max_calc,
                p50,
                p90,
                p95,
                p99,
                time_range,
                last_10_minutes,
                last_30_minutes,
                last_1_hour,
                last_2_hours,
                last_8_hours,
                last_24_hours,
                last_7_days,
                where_equals,
                where_ne,
                where_gt,
                where_gte,
                where_lt,
                where_lte,
                where_contains,
                where_exists,
                group_by,
                order_by,
                limit_rows,
            ]
        )

        mode_count = sum([bool(from_file), bool(spec), bool(query_id), using_builder])
        if mode_count != 1:
            console.print(
                "[red]Error:[/red] Use exactly one mode: builder flags, --from-file, --spec, or --query-id",
                style="bold",
            )
            raise typer.Exit(1)

        if query_id:
            # Run existing saved query
            result = client.query_results.run(
                dataset=dataset,
                query_id=query_id,
                poll_interval=poll_interval,
                timeout=timeout,
            )
        elif using_builder:
            # Build query using flags
            builder = QueryBuilder().dataset(dataset)

            # Add calculations
            if count:
                builder.count()
            for col in avg:
                builder.avg(col)
            for col in sum_cols:
                builder.sum(col)
            for col in min_calc:
                builder.min(col)
            for col in max_calc:
                builder.max(col)
            for col in p50:
                builder.p50(col)
            for col in p90:
                builder.p90(col)
            for col in p95:
                builder.p95(col)
            for col in p99:
                builder.p99(col)

            # Add time range
            if time_range:
                builder.time_range(time_range)
            elif last_10_minutes:
                builder.last_10_minutes()
            elif last_30_minutes:
                builder.last_30_minutes()
            elif last_1_hour:
                builder.last_1_hour()
            elif last_2_hours:
                builder.last_2_hours()
            elif last_8_hours:
                builder.last_8_hours()
            elif last_24_hours:
                builder.last_24_hours()
            elif last_7_days:
                builder.last_7_days()

            # Add filters
            for filter_spec in where_equals:
                col, val = _parse_filter(filter_spec)
                builder.eq(col, val)
            for filter_spec in where_ne:
                col, val = _parse_filter(filter_spec)
                builder.ne(col, val)
            for filter_spec in where_gt:
                col, val = _parse_filter(filter_spec)
                builder.gt(col, _parse_number(val))
            for filter_spec in where_gte:
                col, val = _parse_filter(filter_spec)
                builder.gte(col, _parse_number(val))
            for filter_spec in where_lt:
                col, val = _parse_filter(filter_spec)
                builder.lt(col, _parse_number(val))
            for filter_spec in where_lte:
                col, val = _parse_filter(filter_spec)
                builder.lte(col, _parse_number(val))
            for filter_spec in where_contains:
                col, val = _parse_filter(filter_spec)
                builder.contains(col, val)
            for col in where_exists:
                builder.exists(col)

            # Add grouping
            if group_by:
                builder.group_by(*group_by)

            # Add ordering
            if order_by:
                builder.order_by(order_by)

            # Add limit
            if limit_rows:
                builder.limit(limit_rows)

            # Run the query
            _, result = client.query_results.create_and_run(
                spec=builder,
                poll_interval=poll_interval,
                timeout=timeout,
            )
        else:
            # Run ephemeral query from spec
            query_data = (
                json.loads(from_file.read_text()) if from_file else json.loads(spec)  # type: ignore
            )
            query_spec = QuerySpec.model_validate(query_data)
            # Use create_and_run for spec-based queries
            _, result = client.query_results.create_and_run(
                spec=query_spec,
                dataset=dataset,
                poll_interval=poll_interval,
                timeout=timeout,
            )

        console.print("[green]Query completed[/green]")
        output_result(result, output)
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get-result")
def get_query_result(
    query_result_id: str = typer.Argument(..., help="Query result ID"),
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__)"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get results for a specific query execution."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        result = client.query_results.get(dataset=dataset, query_result_id=query_result_id)
        output_result(result, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


def _parse_filter(filter_spec: str) -> tuple[str, str]:
    """Parse a filter specification like 'column,value' into (column, value)."""
    parts = filter_spec.split(",", 1)
    if len(parts) != 2:
        console.print(
            f"[red]Error:[/red] Invalid filter format: '{filter_spec}'. Expected: column,value",
            style="bold",
        )
        raise typer.Exit(1)
    return parts[0].strip(), parts[1].strip()


def _parse_number(value: str) -> int | float:
    """Parse a string as int or float."""
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value  # type: ignore  # Return as string if not a number
