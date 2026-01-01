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
        api_keys,
        auth,
        boards,
        columns,
        config,
        datasets,
        derived_columns,
        environments,
        markers,
        queries,
        recipients,
        slos,
        triggers,
    )

    # we can't do real aliases because Typer doesn't support them
    # but watch this PR: https://github.com/fastapi/typer/pull/1422
    app.add_typer(triggers.app, name="triggers")
    app.add_typer(triggers.app, name="triggers", hidden=True)
    app.add_typer(triggers.app, name="t", hidden=True)
    app.add_typer(slos.app, name="slos")
    app.add_typer(slos.app, name="slo", hidden=True)
    app.add_typer(slos.app, name="s", hidden=True)
    app.add_typer(boards.app, name="boards")
    app.add_typer(boards.app, name="board", hidden=True)
    app.add_typer(boards.app, name="b", hidden=True)
    app.add_typer(columns.app, name="columns")
    app.add_typer(columns.app, name="column", hidden=True)
    app.add_typer(columns.app, name="c", hidden=True)
    app.add_typer(queries.app, name="query")
    app.add_typer(queries.app, name="queries", hidden=True)
    app.add_typer(queries.app, name="q", hidden=True)
    app.add_typer(datasets.app, name="datasets")
    app.add_typer(datasets.app, name="dataset", hidden=True)
    app.add_typer(datasets.app, name="d", hidden=True)
    app.add_typer(markers.app, name="markers")
    app.add_typer(markers.app, name="marker", hidden=True)
    app.add_typer(markers.app, name="m", hidden=True)
    app.add_typer(recipients.app, name="recipients")
    app.add_typer(recipients.app, name="recipient", hidden=True)
    app.add_typer(recipients.app, name="r", hidden=True)
    app.add_typer(derived_columns.app, name="derived-columns")
    app.add_typer(derived_columns.app, name="derived-column", hidden=True)
    app.add_typer(derived_columns.app, name="dc", hidden=True)
    app.add_typer(derived_columns.app, name="calculated-fields", hidden=True)
    app.add_typer(derived_columns.app, name="calculated-field", hidden=True)
    app.add_typer(derived_columns.app, name="cf", hidden=True)
    app.add_typer(auth.app, name="auth")
    app.add_typer(api_keys.app, name="api-keys")
    app.add_typer(api_keys.app, name="api-key", hidden=True)
    app.add_typer(api_keys.app, name="a", hidden=True)
    app.add_typer(environments.app, name="environments")
    app.add_typer(environments.app, name="environment", hidden=True)
    app.add_typer(environments.app, name="e", hidden=True)
    app.add_typer(config.app, name="config")
    app.add_typer(config.app, name="conf", hidden=True)


_register_commands()

if __name__ == "__main__":
    app()
