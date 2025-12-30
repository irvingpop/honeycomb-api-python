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
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
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
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
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
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path | None = typer.Option(
        None, "--from-file", "-f", help="JSON file with query spec"
    ),
    spec: str | None = typer.Option(None, "--spec", "-s", help="Inline JSON query spec"),
    query_id: str | None = typer.Option(None, "--query-id", help="Run an existing saved query"),
    poll_interval: float = typer.Option(1.0, "--poll-interval", help="Polling interval in seconds"),
    timeout: float = typer.Option(60.0, "--timeout", help="Timeout in seconds"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """
    Run a query and wait for results.

    Provide one of: --from-file, --spec, or --query-id
    """
    try:
        if sum([bool(from_file), bool(spec), bool(query_id)]) != 1:
            console.print(
                "[red]Error:[/red] Provide exactly one of: --from-file, --spec, or --query-id",
                style="bold",
            )
            raise typer.Exit(1)

        client = get_client(profile=profile, api_key=api_key)

        if query_id:
            # Run existing saved query
            result = client.query_results.run(
                dataset=dataset,
                query_id=query_id,
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
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get-result")
def get_query_result(
    query_result_id: str = typer.Argument(..., help="Query result ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
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
