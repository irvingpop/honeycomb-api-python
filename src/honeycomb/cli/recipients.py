"""
Recipient management commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.recipients import RecipientCreate

app = typer.Typer(help="Manage recipients (notification targets)")
console = Console()


@app.command("list")
def list_recipients(
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output recipient IDs"),
) -> None:
    """List all recipients in the environment."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        recipients = client.recipients.list()
        output_result(
            recipients,
            output,
            columns=["id", "type", "created_at"],
            quiet=quiet,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_recipient(
    recipient_id: str = typer.Argument(..., help="Recipient ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific recipient."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        recipient = client.recipients.get(recipient_id=recipient_id)
        output_result(recipient, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_recipient(
    from_file: Path = typer.Option(
        ..., "--from-file", "-f", help="JSON file with recipient config"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create a recipient from a JSON file."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in create request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        recipient_create = RecipientCreate.model_validate(data)
        recipient = client.recipients.create(recipient=recipient_create)

        console.print(
            f"[green]Created recipient ({recipient.type}) with ID: {recipient.id}[/green]"
        )
        output_result(recipient, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_recipient(
    recipient_id: str = typer.Argument(..., help="Recipient ID"),
    from_file: Path = typer.Option(
        ..., "--from-file", "-f", help="JSON file with recipient config"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an existing recipient."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in update request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        recipient_update = RecipientCreate.model_validate(data)
        recipient = client.recipients.update(recipient_id=recipient_id, recipient=recipient_update)

        console.print(f"[green]Updated recipient {recipient.id}[/green]")
        output_result(recipient, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_recipient(
    recipient_id: str = typer.Argument(..., help="Recipient ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a recipient."""
    try:
        if not yes:
            confirm = typer.confirm(f"Delete recipient {recipient_id}?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client = get_client(profile=profile, api_key=api_key)
        client.recipients.delete(recipient_id=recipient_id)
        console.print(f"[green]Deleted recipient {recipient_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export")
def export_recipient(
    recipient_id: str = typer.Argument(..., help="Recipient ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output_file: Path | None = typer.Option(
        None, "--output-file", "-o", help="Output file (default: stdout)"
    ),
) -> None:
    """
    Export a recipient as JSON.

    Output is suitable for importing to another environment via the 'create' command.
    """
    try:
        client = get_client(profile=profile, api_key=api_key)
        recipient = client.recipients.get(recipient_id=recipient_id)

        # Export without IDs/timestamps for portability
        data = recipient.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")
        json_str = json.dumps(data, indent=2, default=str)

        if output_file:
            output_file.write_text(json_str)
            console.print(f"[green]Exported recipient to {output_file}[/green]")
        else:
            console.print(json_str)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export-all")
def export_all_recipients(
    output_dir: Path = typer.Option(..., "--output-dir", help="Output directory"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
) -> None:
    """Export all recipients to individual JSON files."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        client = get_client(profile=profile, api_key=api_key)
        recipients = client.recipients.list()

        for recipient in recipients:
            # Export without IDs/timestamps
            data = recipient.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")

            # Use recipient ID and type for filename
            filename = f"{recipient.type.value}_{recipient.id}.json"
            file_path = output_dir / filename

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            console.print(
                f"[green]Exported {recipient.type.value} recipient to {file_path}[/green]"
            )

        console.print(
            f"\n[bold green]Exported {len(recipients)} recipients to {output_dir}[/bold green]"
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
