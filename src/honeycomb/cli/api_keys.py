"""API Keys management commands (v2 team-scoped)."""

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.api_keys import ApiKeyCreate, ApiKeyType

app = typer.Typer(help="Manage API keys (requires management key)")
console = Console()


@app.command("list")
def list_api_keys(
    key_type: str | None = typer.Option(
        None, "--type", help="Filter by type: ingest or configuration"
    ),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """List all API keys for your authenticated team.

    Examples:
        # List all API keys
        hny api-keys list

        # Filter by type
        hny api-keys list --type ingest
    """
    try:
        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        keys = client.api_keys.list(key_type=key_type)
        output_result(keys, output)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_api_key(
    key_id: str = typer.Argument(..., help="API key ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get a specific API key by ID for your authenticated team.

    Examples:
        hny api-keys get hcaik_123
    """
    try:
        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        key = client.api_keys.get(key_id=key_id)
        output_result(key, output)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_api_key(
    name: str = typer.Option(..., "--name", help="API key name"),
    key_type: ApiKeyType = typer.Option(..., "--type", help="Key type: ingest or configuration"),
    environment_id: str = typer.Option(..., "--environment", "-e", help="Environment ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create a new API key for your authenticated team.

    Examples:
        hny api-keys create --name "My Key" --type ingest --environment env-123
    """
    try:
        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        api_key = ApiKeyCreate(
            name=name,
            key_type=key_type,
            environment_id=environment_id,
        )

        created = client.api_keys.create(api_key=api_key)
        output_result(created, output)

        # Warn about secret
        if created.secret and output == OutputFormat.table:
            console.print(
                "\n[yellow]Warning:[/yellow] The secret is only shown once. Save it securely!",
                style="bold",
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_api_key(
    key_id: str = typer.Argument(..., help="API key ID"),
    name: str | None = typer.Option(None, "--name", help="New name"),
    disabled: bool | None = typer.Option(None, "--disabled", help="Disable the key"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Update an API key for your authenticated team.

    Examples:
        hny api-keys update hcaik_123 --name "New Name"
        hny api-keys update hcaik_123 --disabled
    """
    try:
        from honeycomb.models.api_keys import ApiKeyUpdate

        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        update = ApiKeyUpdate(name=name, disabled=disabled)
        updated = client.api_keys.update(key_id=key_id, api_key=update)
        output_result(updated, output)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_api_key(
    key_id: str = typer.Argument(..., help="API key ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete an API key for your authenticated team.

    Examples:
        hny api-keys delete hcaik_123
        hny api-keys delete hcaik_123 --yes
    """
    try:
        if not yes:
            confirm = typer.confirm(f"Delete API key {key_id}?")
            if not confirm:
                console.print("Cancelled")
                raise typer.Exit(0)

        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        client.api_keys.delete(key_id=key_id)
        console.print(f"[green]Deleted API key:[/green] {key_id}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
