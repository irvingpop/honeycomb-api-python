"""
Column management commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.columns import ColumnCreate, ColumnType

app = typer.Typer(help="Manage dataset columns")
console = Console()


@app.command("list")
def list_columns(
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__ for environment-wide)"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output column IDs"),
) -> None:
    """List all columns (environment-wide by default, or in a specific dataset)."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        columns = client.columns.list(dataset=dataset)
        # Sort by key_name alphabetically
        columns = sorted(columns, key=lambda c: c.key_name.lower())
        output_result(
            columns,
            output,
            columns=["id", "key_name", "type", "description", "hidden", "last_written"],
            quiet=quiet,
            column_titles={"key_name": "Name"},
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_column(
    column_id: str = typer.Argument(..., help="Column ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific column."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        column = client.columns.get(dataset=dataset, column_id=column_id)
        output_result(column, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_column(
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path | None = typer.Option(
        None, "--from-file", "-f", help="JSON file with column config"
    ),
    key_name: str | None = typer.Option(None, "--key-name", "-k", help="Column name"),
    column_type: ColumnType = typer.Option(ColumnType.STRING, "--type", "-t", help="Column type"),
    description: str | None = typer.Option(None, "--description", help="Column description"),
    hidden: bool = typer.Option(False, "--hidden", help="Hide column from autocomplete"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create a column from a JSON file or command-line options."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        if from_file:
            # Load and parse JSON file
            data = json.loads(from_file.read_text())

            # Strip fields that shouldn't be in create request
            data.pop("id", None)
            data.pop("created_at", None)
            data.pop("updated_at", None)
            data.pop("last_written", None)

            column_create = ColumnCreate.model_validate(data)
        elif key_name:
            column_create = ColumnCreate(
                key_name=key_name,
                type=column_type,
                description=description,
                hidden=hidden,
            )
        else:
            console.print("[red]Error:[/red] Either --from-file or --key-name is required")
            raise typer.Exit(1)

        column = client.columns.create(dataset=dataset, column=column_create)

        console.print(f"[green]Created column '{column.key_name}' with ID: {column.id}[/green]")
        output_result(column, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_column(
    column_id: str = typer.Argument(..., help="Column ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path | None = typer.Option(
        None, "--from-file", "-f", help="JSON file with column config"
    ),
    key_name: str | None = typer.Option(None, "--key-name", "-k", help="Column name"),
    column_type: ColumnType | None = typer.Option(None, "--type", "-t", help="Column type"),
    description: str | None = typer.Option(None, "--description", help="Column description"),
    hidden: bool | None = typer.Option(None, "--hidden/--no-hidden", help="Hide column"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an existing column."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        if from_file:
            # Load and parse JSON file
            data = json.loads(from_file.read_text())

            # Strip fields that shouldn't be in update request
            data.pop("id", None)
            data.pop("created_at", None)
            data.pop("updated_at", None)
            data.pop("last_written", None)

            column_update = ColumnCreate.model_validate(data)
        else:
            # Get existing column to merge with updates
            existing = client.columns.get(dataset=dataset, column_id=column_id)
            column_update = ColumnCreate(
                key_name=key_name if key_name is not None else existing.key_name,
                type=column_type if column_type is not None else existing.type,
                description=description if description is not None else existing.description,
                hidden=hidden if hidden is not None else existing.hidden,
            )

        column = client.columns.update(dataset=dataset, column_id=column_id, column=column_update)

        console.print(f"[green]Updated column '{column.key_name}'[/green]")
        output_result(column, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_column(
    column_id: str = typer.Argument(..., help="Column ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a column."""
    try:
        if not yes:
            confirm = typer.confirm(f"Delete column {column_id} from dataset {dataset}?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client = get_client(profile=profile, api_key=api_key)
        client.columns.delete(dataset=dataset, column_id=column_id)
        console.print(f"[green]Deleted column {column_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export")
def export_column(
    column_id: str = typer.Argument(..., help="Column ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output_file: Path | None = typer.Option(
        None, "--output-file", "-o", help="Output file (default: stdout)"
    ),
) -> None:
    """
    Export a column as JSON.

    Output is suitable for importing to another environment via the 'create' command.
    """
    try:
        client = get_client(profile=profile, api_key=api_key)
        column = client.columns.get(dataset=dataset, column_id=column_id)

        # Export without IDs/timestamps for portability
        data = column.model_dump(
            exclude={"id", "created_at", "updated_at", "last_written"}, mode="json"
        )
        json_str = json.dumps(data, indent=2, default=str)

        if output_file:
            output_file.write_text(json_str)
            console.print(f"[green]Exported column to {output_file}[/green]")
        else:
            console.print(json_str)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export-all")
def export_all_columns(
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__ for environment-wide)"
    ),
    output_dir: Path = typer.Option(..., "--output-dir", help="Output directory"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
) -> None:
    """Export all columns to individual JSON files."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        client = get_client(profile=profile, api_key=api_key)
        columns = client.columns.list(dataset=dataset)

        for column in columns:
            # Export without IDs/timestamps
            data = column.model_dump(
                exclude={"id", "created_at", "updated_at", "last_written"}, mode="json"
            )

            # Sanitize filename (replace special chars with dash)
            filename = f"{column.key_name}.json".replace("/", "-").replace(" ", "-").lower()
            file_path = output_dir / filename

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            console.print(f"[green]Exported '{column.key_name}' to {file_path}[/green]")

        console.print(f"\n[bold green]Exported {len(columns)} columns to {output_dir}[/bold green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
