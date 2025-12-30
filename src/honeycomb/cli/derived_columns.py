"""
Derived column (calculated field) management commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.derived_columns import DerivedColumnCreate

app = typer.Typer(help="Manage derived columns (calculated fields)")
console = Console()


@app.command("list")
def list_derived_columns(
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__ for environment-wide)"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output column IDs"),
) -> None:
    """List all derived columns (environment-wide by default, or in a specific dataset)."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        columns = client.derived_columns.list(dataset=dataset)
        output_result(
            columns,
            output,
            columns=["id", "alias", "expression", "description", "created_at"],
            quiet=quiet,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_derived_column(
    column_id: str = typer.Argument(..., help="Derived column ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific derived column."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        column = client.derived_columns.get(dataset=dataset, column_id=column_id)
        output_result(column, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_derived_column(
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path = typer.Option(
        ..., "--from-file", "-f", help="JSON file with derived column config"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create a derived column from a JSON file."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in create request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        column_create = DerivedColumnCreate.model_validate(data)
        column = client.derived_columns.create(dataset=dataset, derived_column=column_create)

        console.print(
            f"[green]Created derived column '{column.alias}' with ID: {column.id}[/green]"
        )
        output_result(column, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_derived_column(
    column_id: str = typer.Argument(..., help="Derived column ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path = typer.Option(
        ..., "--from-file", "-f", help="JSON file with derived column config"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an existing derived column."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in update request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        column_update = DerivedColumnCreate.model_validate(data)
        column = client.derived_columns.update(
            dataset=dataset, column_id=column_id, derived_column=column_update
        )

        console.print(f"[green]Updated derived column '{column.alias}'[/green]")
        output_result(column, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_derived_column(
    column_id: str = typer.Argument(..., help="Derived column ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a derived column."""
    try:
        if not yes:
            confirm = typer.confirm(f"Delete derived column {column_id} from dataset {dataset}?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client = get_client(profile=profile, api_key=api_key)
        client.derived_columns.delete(dataset=dataset, column_id=column_id)
        console.print(f"[green]Deleted derived column {column_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export")
def export_derived_column(
    column_id: str = typer.Argument(..., help="Derived column ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output_file: Path | None = typer.Option(
        None, "--output-file", "-o", help="Output file (default: stdout)"
    ),
) -> None:
    """
    Export a derived column as JSON.

    Output is suitable for importing to another environment via the 'create' command.
    """
    try:
        client = get_client(profile=profile, api_key=api_key)
        column = client.derived_columns.get(dataset=dataset, column_id=column_id)

        # Export without IDs/timestamps for portability
        data = column.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")
        json_str = json.dumps(data, indent=2, default=str)

        if output_file:
            output_file.write_text(json_str)
            console.print(f"[green]Exported derived column to {output_file}[/green]")
        else:
            console.print(json_str)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export-all")
def export_all_derived_columns(
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__ for environment-wide)"
    ),
    output_dir: Path = typer.Option(..., "--output-dir", help="Output directory"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
) -> None:
    """Export all derived columns to individual JSON files."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        client = get_client(profile=profile, api_key=api_key)
        columns = client.derived_columns.list(dataset=dataset)

        for column in columns:
            # Export without IDs/timestamps
            data = column.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")

            # Sanitize filename (replace special chars with dash)
            filename = f"{column.alias}.json".replace("/", "-").replace(" ", "-").lower()
            file_path = output_dir / filename

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            console.print(f"[green]Exported '{column.alias}' to {file_path}[/green]")

        console.print(
            f"\n[bold green]Exported {len(columns)} derived columns to {output_dir}[/bold green]"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
