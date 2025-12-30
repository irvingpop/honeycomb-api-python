"""
Dataset management commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.datasets import DatasetCreate

app = typer.Typer(help="Manage datasets")
console = Console()


@app.command("list")
def list_datasets(
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output dataset slugs"),
) -> None:
    """List all datasets in the environment."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        datasets = client.datasets.list()
        output_result(
            datasets, output, columns=["slug", "name", "description", "created_at"], quiet=quiet
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_dataset(
    slug: str = typer.Argument(..., help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific dataset."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        dataset = client.datasets.get(slug=slug)
        output_result(dataset, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_dataset(
    name: str | None = typer.Option(None, "--name", "-n", help="Dataset name"),
    slug: str | None = typer.Option(None, "--slug", "-s", help="Dataset slug"),
    description: str | None = typer.Option(None, "--description", "-d", help="Dataset description"),
    from_file: Path | None = typer.Option(
        None, "--from-file", "-f", help="JSON file with dataset config"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create a new dataset."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        if from_file:
            # Load from JSON file
            data = json.loads(from_file.read_text())
            data.pop("created_at", None)
            data.pop("updated_at", None)
            dataset_create = DatasetCreate.model_validate(data)
        elif name and slug:
            # Create from CLI arguments
            dataset_create = DatasetCreate(name=name, slug=slug, description=description)
        else:
            console.print(
                "[red]Error:[/red] Provide --name and --slug, or --from-file", style="bold"
            )
            raise typer.Exit(1)

        dataset = client.datasets.create(dataset=dataset_create)

        console.print(f"[green]Created dataset '{dataset.name}' with slug: {dataset.slug}[/green]")
        output_result(dataset, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_dataset(
    slug: str = typer.Argument(..., help="Dataset slug"),
    name: str | None = typer.Option(None, "--name", "-n", help="New dataset name"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    from_file: Path | None = typer.Option(
        None, "--from-file", "-f", help="JSON file with dataset config"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an existing dataset."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        if from_file:
            # Load from JSON file
            data = json.loads(from_file.read_text())
            data.pop("slug", None)  # Can't change slug
            data.pop("created_at", None)
            data.pop("updated_at", None)
            dataset_update = DatasetCreate.model_validate(data)
        elif name or description:
            # Get current dataset to preserve existing fields
            current = client.datasets.get(slug=slug)
            dataset_update = DatasetCreate(
                name=name if name else current.name,
                description=description if description is not None else current.description,
                expand_json_depth=current.expand_json_depth,
            )
        else:
            console.print(
                "[red]Error:[/red] Provide --name and/or --description, or --from-file",
                style="bold",
            )
            raise typer.Exit(1)

        dataset = client.datasets.update(slug=slug, dataset=dataset_update)

        console.print(f"[green]Updated dataset '{dataset.name}'[/green]")
        output_result(dataset, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_dataset(
    slug: str = typer.Argument(..., help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a dataset."""
    try:
        if not yes:
            confirm = typer.confirm(
                f"Delete dataset '{slug}' and ALL its data (triggers, SLOs, queries, events)?"
            )
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client = get_client(profile=profile, api_key=api_key)
        client.datasets.delete(slug=slug)
        console.print(f"[green]Deleted dataset '{slug}'[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
