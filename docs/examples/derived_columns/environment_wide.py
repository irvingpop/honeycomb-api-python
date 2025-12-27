"""Environment-wide derived column examples.

These examples demonstrate creating derived columns that apply
across all datasets in an environment.
"""

from __future__ import annotations

from honeycomb import DerivedColumnBuilder, HoneycombClient


# start_example:env_wide_create
async def create_environment_wide_column(client: HoneycombClient) -> str:
    """Create an environment-wide derived column.

    Environment-wide columns are available in all datasets.
    Use "__all__" as the dataset slug.

    Returns:
        The created derived column ID
    """
    dc = (
        DerivedColumnBuilder("global_has_trace")
        .expression("EXISTS($trace.trace_id)")
        .description("Environment-wide trace indicator")
        .build()
    )
    # Use "__all__" for environment-wide columns
    created = await client.derived_columns.create_async("__all__", dc)
    return created.id


# end_example:env_wide_create


# start_example:env_wide_list
async def list_environment_wide_columns(client: HoneycombClient) -> list:
    """List all environment-wide derived columns.

    Returns:
        List of environment-wide derived columns
    """
    columns = await client.derived_columns.list_async("__all__")
    for col in columns:
        print(f"{col.alias}: {col.expression}")
    return columns


# end_example:env_wide_list


# TEST_ASSERTIONS
async def test_assertions(client: HoneycombClient, dc_id: str) -> None:
    """Verify the example worked correctly."""
    dc = await client.derived_columns.get_async("__all__", dc_id)
    assert dc.alias == "global_has_trace"


# CLEANUP
async def cleanup(client: HoneycombClient, dc_id: str) -> None:
    """Clean up resources created by example."""
    await client.derived_columns.delete_async("__all__", dc_id)
