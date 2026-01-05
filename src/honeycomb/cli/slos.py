"""
SLO management commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.slos import SLOCreate

app = typer.Typer(help="Manage SLOs (Service Level Objectives)")
console = Console()


@app.command("list")
def list_slos(
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__ for environment-wide)"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output SLO IDs"),
) -> None:
    """List all SLOs (environment-wide by default, or in a specific dataset)."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        slos = client.slos.list(dataset=dataset)

        # Add computed datasets column for table display
        slos_with_datasets = []
        for slo in slos:
            slo_dict = slo.model_dump(mode="json")
            # Show "environment-wide" or comma-separated dataset slugs
            if slo.dataset_slugs and len(slo.dataset_slugs) > 0:
                if slo.dataset_slugs == ["__all__"]:
                    slo_dict["datasets"] = "environment-wide"
                else:
                    slo_dict["datasets"] = ", ".join(slo.dataset_slugs)
            else:
                slo_dict["datasets"] = "environment-wide"
            slos_with_datasets.append(slo_dict)

        output_result(
            slos_with_datasets if output == OutputFormat.table else slos,
            output,
            columns=[
                "id",
                "name",
                "datasets",
                "target_per_million",
                "time_period_days",
                "created_at",
            ],
            quiet=quiet,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_slo(
    slo_id: str = typer.Argument(..., help="SLO ID"),
    dataset: str | None = typer.Option(
        None, "--dataset", "-d", help="Dataset slug (auto-detected if not provided)"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific SLO."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # If dataset not provided, find it by listing all SLOs
        if dataset is None:
            all_slos = client.slos.list(dataset="__all__")
            matching = [s for s in all_slos if s.id == slo_id]
            if not matching:
                console.print(f"[red]Error:[/red] SLO {slo_id} not found", style="bold")
                raise typer.Exit(1)

            slo = matching[0]
            # Check if SLO spans multiple datasets
            if slo.dataset_slugs and len(slo.dataset_slugs) > 1:
                datasets_str = ", ".join(slo.dataset_slugs)
                console.print(
                    f"[yellow]Note:[/yellow] SLO {slo_id} spans multiple datasets: {datasets_str}"
                )
                console.print(
                    "[yellow]Fetching from first dataset. Use --dataset to specify a different one.[/yellow]"
                )

            found_dataset = slo.dataset
            if not found_dataset:
                console.print(f"[red]Error:[/red] SLO {slo_id} has no dataset", style="bold")
                raise typer.Exit(1)
            dataset = found_dataset
            console.print(f"[dim]Found SLO in dataset: {dataset}[/dim]")
            # We already have the SLO from the list, just output it
            output_result(slo, output)
        else:
            # Dataset provided, fetch directly
            slo = client.slos.get(dataset=dataset, slo_id=slo_id)
            output_result(slo, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_slo(
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with SLO config"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create an SLO from a JSON file."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in create request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        slo_create = SLOCreate.model_validate(data)
        slo = client.slos.create(dataset=dataset, slo=slo_create)

        console.print(f"[green]Created SLO '{slo.name}' with ID: {slo.id}[/green]")
        output_result(slo, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_slo(
    slo_id: str = typer.Argument(..., help="SLO ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with SLO config"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an existing SLO."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in update request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        slo_update = SLOCreate.model_validate(data)
        slo = client.slos.update(dataset=dataset, slo_id=slo_id, slo=slo_update)

        console.print(f"[green]Updated SLO '{slo.name}'[/green]")
        output_result(slo, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_slo(
    slo_id: str = typer.Argument(..., help="SLO ID"),
    dataset: str | None = typer.Option(
        None, "--dataset", "-d", help="Dataset slug (auto-detected if not provided)"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete an SLO."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # If dataset not provided, find it by listing all SLOs
        if dataset is None:
            all_slos = client.slos.list(dataset="__all__")
            matching = [s for s in all_slos if s.id == slo_id]
            if not matching:
                console.print(f"[red]Error:[/red] SLO {slo_id} not found", style="bold")
                raise typer.Exit(1)

            slo = matching[0]
            # Check if SLO spans multiple datasets - must use __all__ to delete
            if slo.dataset_slugs and len(slo.dataset_slugs) > 1:
                datasets_str = ", ".join(slo.dataset_slugs)
                console.print(
                    f"[dim]SLO {slo_id} spans multiple datasets: {datasets_str}[/dim]"
                )
                dataset = "__all__"
                console.print("[dim]Using dataset=__all__ for deletion[/dim]")
            else:
                found_dataset = slo.dataset
                if not found_dataset:
                    console.print(f"[red]Error:[/red] SLO {slo_id} has no dataset", style="bold")
                    raise typer.Exit(1)
                dataset = found_dataset
                console.print(f"[dim]Found SLO in dataset: {dataset}[/dim]")
        else:
            # If dataset is explicitly provided for a multi-dataset SLO and it's not __all__, error
            all_slos = client.slos.list(dataset="__all__")
            matching = [s for s in all_slos if s.id == slo_id]
            if matching:
                slo = matching[0]
                if (
                    slo.dataset_slugs
                    and len(slo.dataset_slugs) > 1
                    and dataset != "__all__"
                ):
                    datasets_str = ", ".join(slo.dataset_slugs)
                    console.print(
                        f"[red]Error:[/red] SLO {slo_id} spans multiple datasets: {datasets_str}",
                        style="bold",
                    )
                    console.print(
                        "[yellow]Multi-dataset SLOs can only be deleted with --dataset __all__[/yellow]"
                    )
                    raise typer.Exit(1)

        if not yes:
            confirm = typer.confirm(f"Delete SLO {slo_id} from dataset {dataset}?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client.slos.delete(dataset=dataset, slo_id=slo_id)
        console.print(f"[green]Deleted SLO {slo_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export")
def export_slo(
    slo_id: str = typer.Argument(..., help="SLO ID"),
    dataset: str | None = typer.Option(
        None, "--dataset", "-d", help="Dataset slug (auto-detected if not provided)"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output_file: Path | None = typer.Option(
        None, "--output-file", "-o", help="Output file (default: stdout)"
    ),
) -> None:
    """
    Export an SLO as JSON.

    Output is suitable for importing to another environment via the 'create' command.
    """
    try:
        client = get_client(profile=profile, api_key=api_key)

        # If dataset not provided, find it by listing all SLOs
        if dataset is None:
            all_slos = client.slos.list(dataset="__all__")
            matching = [s for s in all_slos if s.id == slo_id]
            if not matching:
                console.print(f"[red]Error:[/red] SLO {slo_id} not found", style="bold")
                raise typer.Exit(1)

            slo = matching[0]
            # Check if SLO spans multiple datasets
            if slo.dataset_slugs and len(slo.dataset_slugs) > 1:
                datasets_str = ", ".join(slo.dataset_slugs)
                console.print(
                    f"[yellow]Warning:[/yellow] SLO {slo_id} spans multiple datasets: {datasets_str}"
                )
                console.print(
                    "[yellow]Exporting from first dataset. Use --dataset to specify a different one.[/yellow]"
                )

            found_dataset = slo.dataset
            if not found_dataset:
                console.print(f"[red]Error:[/red] SLO {slo_id} has no dataset", style="bold")
                raise typer.Exit(1)
            dataset = found_dataset
            console.print(f"[dim]Exporting SLO from dataset: {dataset}[/dim]")
        else:
            # Dataset provided, fetch directly
            slo = client.slos.get(dataset=dataset, slo_id=slo_id)

        # Export without IDs/timestamps for portability
        data = slo.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")
        json_str = json.dumps(data, indent=2, default=str)

        if output_file:
            output_file.write_text(json_str)
            console.print(f"[green]Exported SLO to {output_file}[/green]")
        else:
            console.print(json_str)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export-all")
def export_all_slos(
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    output_dir: Path = typer.Option(..., "--output-dir", help="Output directory"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
) -> None:
    """Export all SLOs from a dataset to individual JSON files."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        client = get_client(profile=profile, api_key=api_key)
        slos = client.slos.list(dataset=dataset)

        for slo in slos:
            # Export without IDs/timestamps
            data = slo.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")

            # Sanitize filename (replace special chars with dash)
            filename = f"{slo.name}.json".replace("/", "-").replace(" ", "-").lower()
            file_path = output_dir / filename

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            console.print(f"[green]Exported '{slo.name}' to {file_path}[/green]")

        console.print(f"\n[bold green]Exported {len(slos)} SLOs to {output_dir}[/bold green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
