"""Basic column creation examples.

These examples demonstrate creating and managing columns.
"""

from __future__ import annotations

from honeycomb import Column, ColumnCreate, ColumnType, HoneycombClient


# start_example:create_column
async def create_basic_column(client: HoneycombClient, dataset: str) -> str:
    """Create a basic float column.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create column in

    Returns:
        The created column ID
    """
    column = await client.columns.create_async(
        dataset,
        ColumnCreate(
            key_name="response_time_ms",
            type=ColumnType.FLOAT,
            description="API response time in milliseconds",
        ),
    )
    return column.id


# end_example:create_column


# start_example:create_hidden_column
async def create_hidden_column(client: HoneycombClient, dataset: str) -> str:
    """Create a hidden column (excluded from autocomplete).

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create column in

    Returns:
        The created column ID
    """
    column = await client.columns.create_async(
        dataset,
        ColumnCreate(
            key_name="internal_trace_id",
            type=ColumnType.STRING,
            description="Internal tracing identifier",
            hidden=True,
        ),
    )
    return column.id


# end_example:create_hidden_column


# start_example:list_columns
async def list_columns(client: HoneycombClient, dataset: str) -> list[Column]:
    """List all columns in a dataset.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list columns from

    Returns:
        List of columns
    """
    columns = await client.columns.list_async(dataset)
    for column in columns:
        hidden = " (hidden)" if column.hidden else ""
        print(f"{column.key_name}: {column.type.value}{hidden}")
    return columns


# end_example:list_columns


# start_example:get
async def get_column(client: HoneycombClient, dataset: str, column_id: str) -> Column:
    """Get a specific column by ID.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the column
        column_id: ID of the column to retrieve

    Returns:
        The column object
    """
    column = await client.columns.get_async(dataset, column_id)
    print(f"Column: {column.key_name} ({column.type.value})")
    if column.description:
        print(f"Description: {column.description}")
    print(f"Hidden: {column.hidden}")
    return column


# end_example:get


# start_example:update
async def update_column(
    client: HoneycombClient, dataset: str, column_id: str
) -> Column:
    """Update a column's description and hidden status.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the column
        column_id: ID of the column to update

    Returns:
        The updated column object
    """
    # Get existing column first to preserve values
    existing = await client.columns.get_async(dataset, column_id)

    # Update with new values
    updated = await client.columns.update_async(
        dataset,
        column_id,
        ColumnCreate(
            key_name=existing.key_name,
            type=existing.type,
            description="Updated description for response time",
            hidden=False,  # Make visible in autocomplete
        ),
    )
    return updated


# end_example:update


# start_example:delete
async def delete_column(client: HoneycombClient, dataset: str, column_id: str) -> None:
    """Delete a column.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug containing the column
        column_id: ID of the column to delete
    """
    await client.columns.delete_async(dataset, column_id)


# end_example:delete


# start_example:list_sync
def list_columns_sync(client: HoneycombClient, dataset: str) -> list[Column]:
    """List columns using sync client.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to list columns from

    Returns:
        List of columns
    """
    columns = client.columns.list(dataset)
    for column in columns:
        print(f"{column.key_name}: {column.type.value}")
    return columns


# end_example:list_sync


# TEST_ASSERTIONS
async def test_create_column(client: HoneycombClient, dataset: str, column_id: str) -> None:
    """Verify the example worked correctly."""
    column = await client.columns.get_async(dataset, column_id)
    assert column.key_name == "response_time_ms"
    assert column.type == ColumnType.FLOAT


async def test_list_columns(columns: list[Column]) -> None:
    """Verify list example worked correctly."""
    assert isinstance(columns, list)


async def test_get_column(column: Column, expected_column_id: str) -> None:
    """Verify get example worked correctly."""
    assert column.id == expected_column_id
    assert column.key_name == "response_time_ms"


async def test_update_column(
    updated: Column, original_column_id: str
) -> None:
    """Verify update example worked correctly."""
    assert updated.id == original_column_id
    assert updated.description == "Updated description for response time"
    assert updated.hidden is False


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, column_id: str) -> None:
    """Clean up resources created by example."""
    await client.columns.delete_async(dataset, column_id)
