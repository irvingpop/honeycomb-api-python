"""Basic derived column creation examples.

These examples demonstrate creating derived columns using both
the DerivedColumnBuilder and manual construction patterns.
"""

from __future__ import annotations

from honeycomb import DerivedColumnBuilder, DerivedColumnCreate, HoneycombClient


# start_example:simple_with_builder
async def create_simple_derived_column(client: HoneycombClient, dataset: str) -> str:
    """Create a simple derived column using DerivedColumnBuilder.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create column in

    Returns:
        The created derived column ID
    """
    dc = (
        DerivedColumnBuilder("has_trace")
        .expression("EXISTS($trace.trace_id)")
        .description("True if trace ID exists")
        .build()
    )
    created = await client.derived_columns.create_async(dataset, dc)
    return created.id


# end_example:simple_with_builder


# start_example:if_expression_builder
async def create_if_expression_column(client: HoneycombClient, dataset: str) -> str:
    """Create a derived column with IF expression.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create column in

    Returns:
        The created derived column ID
    """
    dc = (
        DerivedColumnBuilder("request_success")
        .expression("IF(LT($status_code, 400), 1, 0)")
        .description("1 if request succeeded, 0 otherwise")
        .build()
    )
    created = await client.derived_columns.create_async(dataset, dc)
    return created.id


# end_example:if_expression_builder


# start_example:manual_construction
async def create_derived_column_manual(client: HoneycombClient, dataset: str) -> str:
    """Create a derived column using manual construction.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create column in

    Returns:
        The created derived column ID
    """
    dc = DerivedColumnCreate(
        alias="has_span",
        expression="EXISTS($trace.span_id)",
        description="True if span ID exists",
    )
    created = await client.derived_columns.create_async(dataset, dc)
    return created.id


# end_example:manual_construction


# TEST_ASSERTIONS
async def test_assertions(
    client: HoneycombClient, dataset: str, dc_id: str, expected_alias: str
) -> None:
    """Verify the example worked correctly."""
    dc = await client.derived_columns.get_async(dataset, dc_id)
    assert dc.alias == expected_alias
    assert dc.expression is not None


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, dc_id: str) -> None:
    """Clean up resources created by example."""
    await client.derived_columns.delete_async(dataset, dc_id)
