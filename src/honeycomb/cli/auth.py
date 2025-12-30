"""Authentication information commands."""

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result

app = typer.Typer(help="Authentication and API key information")
console = Console()


@app.command("get")
def get_auth(
    v2: bool = typer.Option(False, "--v2", help="Use v2 endpoint (management key)"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get metadata about the current API key.

    Shows information about the API key being used, including:
    - Team and environment details
    - Key type and permissions
    - Expiration (if applicable)

    By default, uses v1 endpoint (API key). Use --v2 to query management key info.

    Examples:
        # Use v1 endpoint (default)
        hny auth get

        # Use v2 endpoint (management key)
        hny auth get --v2

        # Output as JSON
        hny auth get --output json
    """
    try:
        # Based on the flag, only pass relevant credentials to client
        if v2:
            # Use v2: only pass management credentials
            client = get_client(
                profile=profile,
                management_key=management_key,
                management_secret=management_secret,
            )
            auth_info = client.auth.get(use_v2=True)
        else:
            # Use v1 (default): only pass API key
            client = get_client(
                profile=profile,
                api_key=api_key,
            )
            auth_info = client.auth.get(use_v2=False)

        output_result(auth_info, output)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
