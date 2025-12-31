"""
Board management commands.
"""

import json
from pathlib import Path

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.boards import BoardCreate

app = typer.Typer(help="Manage boards (dashboards)")
console = Console()


@app.command("list")
def list_boards(
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output board IDs"),
) -> None:
    """List all boards in the environment."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        boards = client.boards.list()
        output_result(boards, output, columns=["id", "name", "description"], quiet=quiet)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_board(
    board_id: str = typer.Argument(..., help="Board ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific board."""
    try:
        client = get_client(profile=profile, api_key=api_key)
        board = client.boards.get(board_id=board_id)
        output_result(board, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_board(
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with board config"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create a board from a JSON file."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in create request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        board_create = BoardCreate.model_validate(data)
        board = client.boards.create(board=board_create)

        console.print(f"[green]Created board '{board.name}' with ID: {board.id}[/green]")
        output_result(board, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_board(
    board_id: str = typer.Argument(..., help="Board ID"),
    from_file: Path = typer.Option(..., "--from-file", "-f", help="JSON file with board config"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an existing board."""
    try:
        client = get_client(profile=profile, api_key=api_key)

        # Load and parse JSON file
        data = json.loads(from_file.read_text())

        # Strip fields that shouldn't be in update request
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        board_update = BoardCreate.model_validate(data)
        board = client.boards.update(board_id=board_id, board=board_update)

        console.print(f"[green]Updated board '{board.name}'[/green]")
        output_result(board, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_board(
    board_id: str = typer.Argument(..., help="Board ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete a board."""
    try:
        if not yes:
            confirm = typer.confirm(f"Delete board {board_id}?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        client = get_client(profile=profile, api_key=api_key)
        client.boards.delete(board_id=board_id)
        console.print(f"[green]Deleted board {board_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export")
def export_board(
    board_id: str = typer.Argument(..., help="Board ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    output_file: Path | None = typer.Option(
        None, "--output-file", "-o", help="Output file (default: stdout)"
    ),
) -> None:
    """
    Export a board as JSON.

    Output is suitable for importing to another environment via the 'create' command.
    """
    try:
        client = get_client(profile=profile, api_key=api_key)
        board = client.boards.get(board_id=board_id)

        # Export without IDs/timestamps for portability
        data = board.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")
        json_str = json.dumps(data, indent=2, default=str)

        if output_file:
            output_file.write_text(json_str)
            console.print(f"[green]Exported board to {output_file}[/green]")
        else:
            console.print(json_str)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("export-all")
def export_all_boards(
    output_dir: Path = typer.Option(..., "--output-dir", help="Output directory"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
) -> None:
    """Export all boards to individual JSON files."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        client = get_client(profile=profile, api_key=api_key)
        boards = client.boards.list()

        for board in boards:
            # Export without IDs/timestamps
            data = board.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")

            # Sanitize filename (replace special chars with dash)
            filename = f"{board.name}.json".replace("/", "-").replace(" ", "-").lower()
            file_path = output_dir / filename

            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            console.print(f"[green]Exported '{board.name}' to {file_path}[/green]")

        console.print(f"\n[bold green]Exported {len(boards)} boards to {output_dir}[/bold green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
