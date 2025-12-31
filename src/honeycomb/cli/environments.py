"""Environments management commands (v2 team-scoped)."""

import typer
from rich.console import Console

from honeycomb.cli.config import get_api_key_from_config, get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result
from honeycomb.models.environments import EnvironmentColor, EnvironmentCreate

app = typer.Typer(help="Manage environments (requires management key)")
console = Console()


@app.command("list")
def list_environments(
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """List all environments for your authenticated team.

    Examples:
        hny environments list
    """
    try:
        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        envs = client.environments.list()
        output_result(envs, output)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("get")
def get_environment(
    env_id: str = typer.Argument(..., help="Environment ID"),
    with_datasets: bool = typer.Option(
        False, "--with-datasets", help="Also list datasets in this environment"
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
    """Get a specific environment by ID for your authenticated team.

    Examples:
        hny environments get env-123
        hny environments get env-123 --with-datasets
    """
    try:
        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        env = client.environments.get(env_id=env_id)
        output_result(env, output)

        # Optionally list datasets
        if with_datasets:
            api_key = get_api_key_from_config(profile)
            if not api_key:
                console.print(
                    "\n[yellow]Cannot list datasets:[/yellow] No HONEYCOMB_API_KEY found. "
                    "Set HONEYCOMB_API_KEY environment variable or add api_key to your profile.",
                    style="bold",
                )
                return

            # Create temporary client with API key to verify environment match
            from honeycomb import HoneycombClient

            with HoneycombClient(api_key=api_key, sync=True) as api_key_client:
                # Verify the API key is for this environment (force v1 for environment_slug)
                from honeycomb.models.auth import AuthInfo

                auth_info = api_key_client.auth.get(use_v2=False)
                assert isinstance(auth_info, AuthInfo)  # use_v2=False always returns AuthInfo
                if auth_info.environment_slug != env.slug:
                    console.print(
                        f"\n[yellow]Cannot list datasets:[/yellow] HONEYCOMB_API_KEY is for environment "
                        f"'{auth_info.environment_slug}' but you requested '{env.slug}'. "
                        "Provide an API key for the correct environment.",
                        style="bold",
                    )
                    return

                # Environment matches - list datasets
                console.print("\n[cyan]Datasets in this environment:[/cyan]")
                datasets = api_key_client.datasets.list()
                output_result(datasets, output)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("create")
def create_environment(
    name: str = typer.Option(..., "--name", help="Environment name"),
    description: str | None = typer.Option(None, "--description", "-d", help="Description"),
    color: EnvironmentColor | None = typer.Option(None, "--color", help="Display color"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Create a new environment for your authenticated team.

    Examples:
        hny environments create --name "Production"
        hny environments create --name "Staging" --color blue --description "Staging env"
    """
    try:
        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        environment = EnvironmentCreate(
            name=name,
            description=description,
            color=color,
        )

        created = client.environments.create(environment=environment)
        output_result(created, output)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("update")
def update_environment(
    env_id: str = typer.Argument(..., help="Environment ID"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    color: EnvironmentColor | None = typer.Option(None, "--color", help="New color"),
    delete_protected: bool | None = typer.Option(
        None, "--delete-protected/--no-delete-protected", help="Enable/disable delete protection"
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
    """Update an environment for your authenticated team.

    Examples:
        hny environments update env-123 --description "Updated"
        hny environments update env-123 --no-delete-protected
    """
    try:
        from honeycomb.models.environments import EnvironmentUpdate

        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        update = EnvironmentUpdate(
            description=description,
            color=color,
            delete_protected=delete_protected,
        )

        updated = client.environments.update(env_id=env_id, environment=update)
        output_result(updated, output)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command("delete")
def delete_environment(
    env_id: str = typer.Argument(..., help="Environment ID"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Delete an environment for your authenticated team.

    Note: Environment must not be delete-protected.

    Examples:
        hny environments delete env-123
        hny environments delete env-123 --yes
    """
    try:
        if not yes:
            confirm = typer.confirm(f"Delete environment {env_id}?")
            if not confirm:
                console.print("Cancelled")
                raise typer.Exit(0)

        client = get_client(
            profile=profile,
            management_key=management_key,
            management_secret=management_secret,
        )

        client.environments.delete(env_id=env_id)
        console.print(f"[green]Deleted environment:[/green] {env_id}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
