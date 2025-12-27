"""List derived columns examples.

These examples demonstrate listing derived columns in a dataset.
"""

from __future__ import annotations

from honeycomb import DerivedColumn, HoneycombClient


# start_example:list_async
async def list_derived_columns(client: HoneycombClient, dataset: str) -> list[DerivedColumn]:
    """List all derived columns in a dataset.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list columns from

    Returns:
        List of derived columns
    """
    columns = await client.derived_columns.list_async(dataset)
    for col in columns:
        print(f"{col.alias}: {col.expression}")
    return columns


# end_example:list_async


# start_example:list_sync
def list_derived_columns_sync(client: HoneycombClient, dataset: str) -> list[DerivedColumn]:
    """List derived columns using sync client.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list columns from

    Returns:
        List of derived columns
    """
    columns = client.derived_columns.list(dataset)
    for col in columns:
        print(f"{col.alias}: {col.expression}")
    return columns


# end_example:list_sync


# TEST_ASSERTIONS
async def test_assertions(columns: list[DerivedColumn]) -> None:
    """Verify the example worked correctly."""
    assert isinstance(columns, list)
