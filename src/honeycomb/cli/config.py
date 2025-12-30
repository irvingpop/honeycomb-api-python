"""
Configuration management for the Honeycomb CLI.

Handles profiles, credentials, and client initialization.
"""

import os
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.table import Table

from honeycomb import HoneycombClient

app = typer.Typer(help="Manage CLI configuration and profiles")
console = Console()

CONFIG_DIR = Path.home() / ".honeycomb"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def _ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(exist_ok=True)


def _load_config() -> dict[str, Any]:
    """Load the config file, returning empty dict if it doesn't exist."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or {}


def _save_config(config: dict[str, Any]) -> None:
    """Save the config file."""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False)


def get_client(
    profile: str | None = None,
    api_key: str | None = None,
    management_key: str | None = None,
    management_secret: str | None = None,
    base_url: str | None = None,
) -> HoneycombClient:
    """
    Get a configured Honeycomb client.

    Priority order:
    1. Explicit parameters (api_key, management_key, etc.)
    2. Environment variables (HONEYCOMB_API_KEY, etc.)
    3. Profile from config file
    4. Default profile from config file
    """
    # If explicit credentials provided, use them
    if api_key or management_key:
        return HoneycombClient(
            api_key=api_key,
            management_key=management_key,
            management_secret=management_secret,
            base_url=base_url or "https://api.honeycomb.io",
            sync=True,
        )

    # Try environment variables
    env_api_key = os.environ.get("HONEYCOMB_API_KEY")
    env_mgmt_key = os.environ.get("HONEYCOMB_MANAGEMENT_KEY")
    env_mgmt_secret = os.environ.get("HONEYCOMB_MANAGEMENT_SECRET")

    if env_api_key or env_mgmt_key:
        return HoneycombClient(
            api_key=env_api_key,
            management_key=env_mgmt_key,
            management_secret=env_mgmt_secret,
            base_url=base_url or "https://api.honeycomb.io",
            sync=True,
        )

    # Try profile from config file
    config = _load_config()
    profiles = config.get("profiles", {})

    # Use specified profile or default
    profile_name = profile or config.get("default_profile")

    if not profile_name:
        console.print(
            "[red]Error:[/red] No credentials found. Provide --api-key or configure a profile.",
            style="bold",
        )
        raise typer.Exit(1)

    if profile_name not in profiles:
        console.print(
            f"[red]Error:[/red] Profile '{profile_name}' not found in {CONFIG_FILE}",
            style="bold",
        )
        raise typer.Exit(1)

    profile_config = profiles[profile_name]
    return HoneycombClient(
        api_key=profile_config.get("api_key"),
        management_key=profile_config.get("management_key"),
        management_secret=profile_config.get("management_secret"),
        base_url=profile_config.get("base_url", "https://api.honeycomb.io"),
        sync=True,
    )


@app.command("show")
def show_config() -> None:
    """Show current configuration."""
    if not CONFIG_FILE.exists():
        console.print(f"[yellow]No config file found at {CONFIG_FILE}[/yellow]")
        return

    config = _load_config()

    # Display default profile
    default_profile = config.get("default_profile")
    if default_profile:
        console.print(f"[bold]Default profile:[/bold] {default_profile}\n")
    else:
        console.print("[yellow]No default profile set[/yellow]\n")

    # Display profiles table
    profiles = config.get("profiles", {})
    if not profiles:
        console.print("[yellow]No profiles configured[/yellow]")
        return

    table = Table(title="Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("API Key", style="green")
    table.add_column("Management Key", style="green")
    table.add_column("Base URL", style="blue")

    for name, profile in profiles.items():
        api_key = profile.get("api_key", "")
        mgmt_key = profile.get("management_key", "")
        base_url = profile.get("base_url", "https://api.honeycomb.io")

        # Mask keys for security
        api_key_display = f"{api_key[:10]}..." if api_key else "-"
        mgmt_key_display = f"{mgmt_key[:10]}..." if mgmt_key else "-"

        table.add_row(name, api_key_display, mgmt_key_display, base_url)

    console.print(table)


@app.command("add-profile")
def add_profile(
    name: str = typer.Argument(..., help="Profile name"),
    api_key: str | None = typer.Option(None, "--api-key", help="API key"),
    management_key: str | None = typer.Option(None, "--management-key", help="Management key"),
    management_secret: str | None = typer.Option(
        None, "--management-secret", help="Management secret"
    ),
    base_url: str | None = typer.Option(
        None, "--base-url", help="Base URL (default: https://api.honeycomb.io)"
    ),
    set_default: bool = typer.Option(False, "--set-default", help="Set as default profile"),
) -> None:
    """Add or update a profile."""
    if not api_key and not management_key:
        console.print("[red]Error:[/red] Must provide --api-key or --management-key", style="bold")
        raise typer.Exit(1)

    if management_key and not management_secret:
        console.print(
            "[red]Error:[/red] --management-secret required when using --management-key",
            style="bold",
        )
        raise typer.Exit(1)

    config = _load_config()
    if "profiles" not in config:
        config["profiles"] = {}

    config["profiles"][name] = {}
    if api_key:
        config["profiles"][name]["api_key"] = api_key
    if management_key:
        config["profiles"][name]["management_key"] = management_key
        config["profiles"][name]["management_secret"] = management_secret
    if base_url:
        config["profiles"][name]["base_url"] = base_url

    if set_default:
        config["default_profile"] = name

    _save_config(config)
    console.print(f"[green]Profile '{name}' saved to {CONFIG_FILE}[/green]")


@app.command("remove-profile")
def remove_profile(name: str = typer.Argument(..., help="Profile name")) -> None:
    """Remove a profile."""
    config = _load_config()
    profiles = config.get("profiles", {})

    if name not in profiles:
        console.print(f"[red]Error:[/red] Profile '{name}' not found", style="bold")
        raise typer.Exit(1)

    del profiles[name]
    _save_config(config)
    console.print(f"[green]Profile '{name}' removed[/green]")


@app.command("set-default")
def set_default(name: str = typer.Argument(..., help="Profile name")) -> None:
    """Set the default profile."""
    config = _load_config()
    profiles = config.get("profiles", {})

    if name not in profiles:
        console.print(f"[red]Error:[/red] Profile '{name}' not found", style="bold")
        raise typer.Exit(1)

    config["default_profile"] = name
    _save_config(config)
    console.print(f"[green]Default profile set to '{name}'[/green]")
