"""
Trigger management commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.triggers import TriggerCreate

app = typer.Typer(help="Manage triggers (alerts)")
console = Console()


@app.command("list")
def list_triggers(
    dataset: str = typer.Option(
        "__all__", "--dataset", "-d", help="Dataset slug (default: __all__ for environment-wide)"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output trigger IDs"),
) -> None:
    """List all triggers (environment-wide by default, or in a specific dataset)."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        triggers = client.triggers.list(dataset=dataset)
        output_result(
            triggers,
            output,
            columns=["id", "name", "disabled", "frequency", "created_at"],
            quiet=quiet,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_trigger(
    trigger_id: str = typer.Argument(..., help="Trigger ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific trigger."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        trigger = client.triggers.get(dataset=dataset, trigger_id=trigger_id)
        output_result(trigger, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_trigger(
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with trigger config"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create a trigger from a JSON file."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in create request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        trigger_create = TriggerCreate.model_validate(data)
        trigger = client.triggers.create(dataset=dataset, trigger=trigger_create)

        console.print(f"[green]Created trigger '{trigger.name}' with ID: {trigger.id}[/green]")
        output_result(trigger, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_trigger(
    trigger_id: str = typer.Argument(..., help="Trigger ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with trigger config"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an existing trigger."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in update request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        trigger_update = TriggerCreate.model_validate(data)
        trigger = client.triggers.update(
            dataset=dataset, trigger_id=trigger_id, trigger=trigger_update
        )

        console.print(f"[green]Updated trigger '{trigger.name}'[/green]")
        output_result(trigger, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_trigger(
    trigger_id: str = typer.Argument(..., help="Trigger ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a trigger."""
    try:
        if not yes:
            confirm = typer.confirm(f"Delete trigger {trigger_id} from dataset {dataset}?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client = get_client(profile=profile, api_key=api_key)
        client.triggers.delete(dataset=dataset, trigger_id=trigger_id)
        console.print(f"[green]Deleted trigger {trigger_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export")
def export_trigger(
    trigger_id: str = typer.Argument(..., help="Trigger ID"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output_file: Path | None = typer.Option(
        None, "--output-file", "-o", help="Output file (default: stdout)"
    ),
) -> None:
    """
    Export a trigger as JSON.

    Output is suitable for importing to another environment via the 'create' command.
    """
    try:
        client = get_client(profile=profile, api_key=api_key)
        trigger = client.triggers.get(dataset=dataset, trigger_id=trigger_id)

        # Export without IDs/timestamps for portability
        data = trigger.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")
        json_str = json.dumps(data, indent=2, default=str)

        if output_file:
            output_file.write_text(json_str)
            console.print(f"[green]Exported trigger to {output_file}[/green]")
        else:
            console.print(json_str)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export-all")
def export_all_triggers(
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset slug"),
    output_dir: Path = typer.Option(..., "--output-dir", help="Output directory"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
) -> None:
    """Export all triggers from a dataset to individual JSON files."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        client = get_client(profile=profile, api_key=api_key)
        triggers = client.triggers.list(dataset=dataset)

        for trigger in triggers:
            # Export without IDs/timestamps
            data = trigger.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")

            # Sanitize filename (replace special chars with dash)
            filename = f"{trigger.name}.json".replace("/", "-").replace(" ", "-").lower()
            file_path = output_dir / filename

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            console.print(f"[green]Exported '{trigger.name}' to {file_path}[/green]")

        console.print(
            f"\n[bold green]Exported {len(triggers)} triggers to {output_dir}[/bold green]"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
