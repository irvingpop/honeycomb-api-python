"""
CLI for Honeycomb API operations.

Provides commands for managing triggers, SLOs, boards, queries, datasets,
markers, recipients, and derived columns.
"""

import typer
from rich.console import Console

app = typer.Typer(
    name="honeycomb",
    help="CLI for Honeycomb.io API operations",
    no_args_is_help=True,
)
console = Console()


# Import and register subcommands
# These imports are deferred to avoid circular dependencies
def _register_commands() -> None:
    """Register all CLI subcommands."""
    from honeycomb.cli import (
        boards,
        config,
        datasets,
        derived_columns,
        markers,
        queries,
        recipients,
        slos,
        triggers,
    )

    app.add_typer(triggers.app, name="triggers")
    app.add_typer(slos.app, name="slos")
    app.add_typer(boards.app, name="boards")
    app.add_typer(queries.app, name="queries")
    app.add_typer(datasets.app, name="datasets")
    app.add_typer(markers.app, name="markers")
    app.add_typer(recipients.app, name="recipients")
    app.add_typer(derived_columns.app, name="derived-columns")
    app.add_typer(config.app, name="config")


_register_commands()

if __name__ == "__main__":
    app()
