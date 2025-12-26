"""Integration tests for Derived Columns (Calculated Fields).

Tests the DerivedColumns resource and DerivedColumnBuilder against the live API.
"""

from __future__ import annotations

import pytest

from honeycomb import (
    DerivedColumnBuilder,
    DerivedColumnCreate,
    HoneycombClient,
    HoneycombNotFoundError,
)


class TestDerivedColumnBuilder:
    """Test DerivedColumnBuilder against live API."""

    @pytest.mark.asyncio
    async def test_simple_derived_column(
        self, client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test creating a simple derived column with builder."""
        dataset = ensure_dataset

        # Use expression that doesn't depend on existing columns
        dc = (
            DerivedColumnBuilder("test_has_trace")
            .expression("EXISTS($trace.trace_id)")
            .description("True if trace ID exists")
            .build()
        )

        created = await client.derived_columns.create_async(dataset, dc)
        try:
            assert created.alias == "test_has_trace"
            assert created.expression == "EXISTS($trace.trace_id)"
            assert created.description == "True if trace ID exists"
        finally:
            await client.derived_columns.delete_async(dataset, created.id)

    @pytest.mark.asyncio
    async def test_derived_column_with_if_expression(
        self, client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test derived column with IF expression."""
        dataset = ensure_dataset

        # Use IF with EXISTS which doesn't require pre-existing columns
        dc = (
            DerivedColumnBuilder("test_trace_indicator")
            .expression("IF(EXISTS($trace.trace_id), 1, 0)")
            .description("1 if traced, 0 otherwise")
            .build()
        )

        created = await client.derived_columns.create_async(dataset, dc)
        try:
            assert created.alias == "test_trace_indicator"
            assert "IF(" in created.expression
        finally:
            await client.derived_columns.delete_async(dataset, created.id)

    @pytest.mark.asyncio
    async def test_derived_column_crud_cycle(
        self, client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test full CRUD cycle for derived columns."""
        dataset = ensure_dataset

        # CREATE - use simple expression that doesn't require existing columns
        dc = (
            DerivedColumnBuilder("test_crud_column")
            .expression("EXISTS($trace.span_id)")
            .description("Test CRUD column")
            .build()
        )

        created = await client.derived_columns.create_async(dataset, dc)
        dc_id = created.id

        # READ
        fetched = await client.derived_columns.get_async(dataset, dc_id)
        assert fetched.id == dc_id
        assert fetched.alias == "test_crud_column"

        # UPDATE
        updated_dc = DerivedColumnCreate(
            alias="test_crud_column_updated",
            expression="EXISTS($trace.parent_id)",
            description="Updated test column",
        )
        updated = await client.derived_columns.update_async(dataset, dc_id, updated_dc)
        assert updated.alias == "test_crud_column_updated"

        # DELETE
        await client.derived_columns.delete_async(dataset, dc_id)

        # Verify deletion
        with pytest.raises(HoneycombNotFoundError):
            await client.derived_columns.get_async(dataset, dc_id)


class TestDerivedColumnManualConstruction:
    """Test derived columns created without builder."""

    @pytest.mark.asyncio
    async def test_manual_derived_column_create(
        self, client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test creating derived column with manual construction."""
        dataset = ensure_dataset

        # Use expression that doesn't require existing columns
        dc = DerivedColumnCreate(
            alias="test_manual_column",
            expression="EXISTS($trace.trace_id)",
            description="Created without builder",
        )

        created = await client.derived_columns.create_async(dataset, dc)
        try:
            assert created.alias == "test_manual_column"
        finally:
            await client.derived_columns.delete_async(dataset, created.id)


class TestDerivedColumnList:
    """Test listing derived columns."""

    @pytest.mark.asyncio
    async def test_list_derived_columns(
        self, client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test listing derived columns in a dataset."""
        dataset = ensure_dataset
        columns = await client.derived_columns.list_async(dataset)
        assert isinstance(columns, list)

    def test_list_derived_columns_sync(
        self, sync_client: HoneycombClient, ensure_dataset: str
    ) -> None:
        """Test listing derived columns with sync client."""
        dataset = ensure_dataset
        columns = sync_client.derived_columns.list(dataset)
        assert isinstance(columns, list)


class TestEnvironmentWideDerivedColumns:
    """Test environment-wide derived columns."""

    @pytest.mark.asyncio
    async def test_list_environment_wide_columns(
        self, client: HoneycombClient
    ) -> None:
        """Test listing environment-wide derived columns."""
        # Use __all__ for environment-wide
        columns = await client.derived_columns.list_async("__all__")
        assert isinstance(columns, list)

    @pytest.mark.asyncio
    async def test_create_environment_wide_column(
        self, client: HoneycombClient
    ) -> None:
        """Test creating an environment-wide derived column."""
        dc = (
            DerivedColumnBuilder("test_env_wide_column")
            .expression("EXISTS($trace.trace_id)")
            .description("Environment-wide test column")
            .build()
        )

        created = await client.derived_columns.create_async("__all__", dc)
        try:
            assert created.alias == "test_env_wide_column"
        finally:
            await client.derived_columns.delete_async("__all__", created.id)
