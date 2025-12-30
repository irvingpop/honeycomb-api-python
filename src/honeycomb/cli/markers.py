"""
Marker management commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.markers import MarkerCreate

app = typer.Typer(help="Manage markers (event annotations)")
console = Console()


@app.command("list")
def list_markers(
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output marker IDs"),
) -> None:
    """List all markers in a dataset."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        markers = client.markers.list(dataset=dataset)
        output_result(
            markers,
            output,
            columns=["id", "message", "type", "start_time", "created_at"],
            quiet=quiet,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_marker(
    marker_id: str = typer.Argument(..., help="Marker ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific marker by ID."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        # Markers API doesn't have a direct get, so list and filter
        markers = client.markers.list(dataset=dataset)
        marker = next((m for m in markers if m.id == marker_id), None)

        if marker is None:
            console.print(f"[red]Error:[/red] Marker {marker_id} not found", style="bold")
            raise typer.Exit(1)

        output_result(marker, output)
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_marker(
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with marker config"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create a marker from a JSON file."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in create request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        marker_create = MarkerCreate.model_validate(data)
        marker = client.markers.create(dataset=dataset, marker=marker_create)

        console.print(f"[green]Created marker with ID: {marker.id}[/green]")
        output_result(marker, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_marker(
    marker_id: str = typer.Argument(..., help="Marker ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with marker config"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an existing marker."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in update request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        marker_update = MarkerCreate.model_validate(data)
        marker = client.markers.update(dataset=dataset, marker_id=marker_id, marker=marker_update)

        console.print(f"[green]Updated marker {marker.id}[/green]")
        output_result(marker, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_marker(
    marker_id: str = typer.Argument(..., help="Marker ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a marker."""
    try:
        if not yes:
            confirm = typer.confirm(f"Delete marker {marker_id} from dataset {dataset}?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client = get_client(profile=profile, api_key=api_key)
        client.markers.delete(dataset=dataset, marker_id=marker_id)
        console.print(f"[green]Deleted marker {marker_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
