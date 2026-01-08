"""
Dataset management commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.datasets import DatasetCreate, DatasetUpdate

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
    delete_protected: bool | None = typer.Option(
        None, "--delete-protected/--no-delete-protected", help="Enable/disable delete protection"
    ),
    from_file: Path | None = typer.Option(
        None, "--from-file", "-f", help="JSON file with dataset config"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an existing dataset.

    Examples:
        hny datasets update my-dataset --description "Updated description"
        hny datasets update my-dataset --delete-protected
        hny datasets update my-dataset --no-delete-protected
    """
    try:
        client = get_client(profile=profile, api_key=api_key)

        update_payload: DatasetCreate | DatasetUpdate
        if from_file:
            # Load from JSON file
            data = json.loads(from_file.read_text())
            data.pop("slug", None)  # Can't change slug
            data.pop("created_at", None)
            data.pop("updated_at", None)
            update_payload = DatasetCreate.model_validate(data)
        elif name or description is not None or delete_protected is not None:
            # Use DatasetUpdate for partial updates
            update_payload = DatasetUpdate(
                name=name,
                description=description,
                delete_protected=delete_protected,
            )
        else:
            console.print(
                "[red]Error:[/red] Provide --name, --description, "
                "--delete-protected/--no-delete-protected, or --from-file",
                style="bold",
            )
            raise typer.Exit(1)

        dataset = client.datasets.update(slug=slug, dataset=update_payload)

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
    remove_delete_protection: bool = typer.Option(
        False, "--remove-delete-protection", help="Remove delete protection before deleting"
    ),
) -> None:
    """Delete a dataset.

    If the dataset has delete protection enabled, use --remove-delete-protection
    to disable it before deleting.
    """
    try:
        if not yes:
            confirm = typer.confirm(
                f"Delete dataset '{slug}' and ALL its data (triggers, SLOs, queries, events)?"
            )
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client = get_client(profile=profile, api_key=api_key)

        if remove_delete_protection:
            console.print(f"Removing delete protection from '{slug}'...")
            client.datasets.set_delete_protected(slug=slug, protected=False)

        client.datasets.delete(slug=slug)
        console.print(f"[green]Deleted dataset '{slug}'[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
