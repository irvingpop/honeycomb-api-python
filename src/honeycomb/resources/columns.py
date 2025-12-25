"""Columns resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.columns import Column, ColumnCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class ColumnsResource(BaseResource):
    """Resource for managing dataset columns.

    Columns define the schema of your datasets and control how fields
    are displayed and queried in the Honeycomb UI.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     columns = await client.columns.list(dataset="my-dataset")
        ...     column = await client.columns.get(
        ...         dataset="my-dataset",
        ...         column_id="abc123"
        ...     )

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     columns = client.columns.list(dataset="my-dataset")
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, column_id: str | None = None) -> str:
        """Build API path for columns."""
        base = f"/1/columns/{dataset}"
        if column_id:
            return f"{base}/{column_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self, dataset: str) -> list[Column]:
        """List all columns for a dataset (async).

        Args:
            dataset: Dataset slug.

        Returns:
            List of Column objects.
        """
        data = await self._get_async(self._build_path(dataset))
        return self._parse_model_list(Column, data)

    async def get_async(self, dataset: str, column_id: str) -> Column:
        """Get a specific column (async).

        Args:
            dataset: Dataset slug.
            column_id: Column ID.

        Returns:
            Column object.
        """
        data = await self._get_async(self._build_path(dataset, column_id))
        return self._parse_model(Column, data)

    async def create_async(self, dataset: str, column: ColumnCreate) -> Column:
        """Create a new column (async).

        Args:
            dataset: Dataset slug.
            column: Column configuration.

        Returns:
            Created Column object.
        """
        data = await self._post_async(self._build_path(dataset), json=column.model_dump_for_api())
        return self._parse_model(Column, data)

    async def update_async(self, dataset: str, column_id: str, column: ColumnCreate) -> Column:
        """Update an existing column (async).

        Args:
            dataset: Dataset slug.
            column_id: Column ID.
            column: Updated column configuration.

        Returns:
            Updated Column object.
        """
        data = await self._put_async(
            self._build_path(dataset, column_id), json=column.model_dump_for_api()
        )
        return self._parse_model(Column, data)

    async def delete_async(self, dataset: str, column_id: str) -> None:
        """Delete a column (async).

        Args:
            dataset: Dataset slug.
            column_id: Column ID.
        """
        await self._delete_async(self._build_path(dataset, column_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self, dataset: str) -> list[Column]:
        """List all columns for a dataset.

        Args:
            dataset: Dataset slug.

        Returns:
            List of Column objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset))
        return self._parse_model_list(Column, data)

    def get(self, dataset: str, column_id: str) -> Column:
        """Get a specific column.

        Args:
            dataset: Dataset slug.
            column_id: Column ID.

        Returns:
            Column object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, column_id))
        return self._parse_model(Column, data)

    def create(self, dataset: str, column: ColumnCreate) -> Column:
        """Create a new column.

        Args:
            dataset: Dataset slug.
            column: Column configuration.

        Returns:
            Created Column object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(dataset), json=column.model_dump_for_api())
        return self._parse_model(Column, data)

    def update(self, dataset: str, column_id: str, column: ColumnCreate) -> Column:
        """Update an existing column.

        Args:
            dataset: Dataset slug.
            column_id: Column ID.
            column: Updated column configuration.

        Returns:
            Updated Column object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(
            self._build_path(dataset, column_id), json=column.model_dump_for_api()
        )
        return self._parse_model(Column, data)

    def delete(self, dataset: str, column_id: str) -> None:
        """Delete a column.

        Args:
            dataset: Dataset slug.
            column_id: Column ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(dataset, column_id))
