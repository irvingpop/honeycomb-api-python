"""Derived Columns (Calculated Fields) resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.derived_columns import DerivedColumn, DerivedColumnCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class DerivedColumnsResource(BaseResource):
    """Resource for managing derived columns (calculated fields).

    Derived columns (also called Calculated Fields) allow you to run queries
    based on the value of an expression that is calculated from the fields in an event.

    Can be scoped to a specific dataset or environment-wide (use dataset="__all__").

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     # List derived columns in a dataset
        ...     columns = await client.derived_columns.list_async(dataset="my-dataset")
        ...
        ...     # Create a derived column
        ...     dc = await client.derived_columns.create_async(
        ...         dataset="my-dataset",
        ...         derived_column=DerivedColumnCreate(
        ...             alias="request_success",
        ...             expression="IF(LT($status_code, 400), 1, 0)",
        ...             description="1 if request succeeded, 0 otherwise"
        ...         )
        ...     )
        ...
        ...     # Create environment-wide derived column
        ...     dc = await client.derived_columns.create_async(
        ...         dataset="__all__",
        ...         derived_column=DerivedColumnCreate(
        ...             alias="error_flag",
        ...             expression="IF(EQUALS($level, 'error'), 1, 0)"
        ...         )
        ...     )

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     columns = client.derived_columns.list(dataset="my-dataset")
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, column_id: str | None = None) -> str:
        """Build API path for derived columns.

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            column_id: Optional derived column ID.

        Returns:
            API path string.
        """
        base = f"/1/derived_columns/{dataset}"
        if column_id:
            return f"{base}/{column_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self, dataset: str, *, alias: str | None = None) -> list[DerivedColumn]:
        """List all derived columns for a dataset or environment (async).

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            alias: Optional alias to filter by (returns single column if found).

        Returns:
            List of DerivedColumn objects (or single-item list if alias provided).
        """
        params = {"alias": alias} if alias else None
        data = await self._get_async(self._build_path(dataset), params=params)

        # API returns either a list or a single object when alias is used
        if isinstance(data, list):
            return self._parse_model_list(DerivedColumn, data)
        else:
            return [self._parse_model(DerivedColumn, data)]

    async def get_async(self, dataset: str, column_id: str) -> DerivedColumn:
        """Get a specific derived column (async).

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            column_id: Derived column ID.

        Returns:
            DerivedColumn object.
        """
        data = await self._get_async(self._build_path(dataset, column_id))
        return self._parse_model(DerivedColumn, data)

    async def create_async(
        self, dataset: str, derived_column: DerivedColumnCreate
    ) -> DerivedColumn:
        """Create a new derived column (async).

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            derived_column: Derived column configuration.

        Returns:
            Created DerivedColumn object.
        """
        data = await self._post_async(
            self._build_path(dataset), json=derived_column.model_dump_for_api()
        )
        return self._parse_model(DerivedColumn, data)

    async def update_async(
        self, dataset: str, column_id: str, derived_column: DerivedColumnCreate
    ) -> DerivedColumn:
        """Update an existing derived column (async).

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            column_id: Derived column ID.
            derived_column: Updated derived column configuration.

        Returns:
            Updated DerivedColumn object.
        """
        data = await self._put_async(
            self._build_path(dataset, column_id), json=derived_column.model_dump_for_api()
        )
        return self._parse_model(DerivedColumn, data)

    async def delete_async(self, dataset: str, column_id: str) -> None:
        """Delete a derived column (async).

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            column_id: Derived column ID.
        """
        await self._delete_async(self._build_path(dataset, column_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self, dataset: str, *, alias: str | None = None) -> list[DerivedColumn]:
        """List all derived columns for a dataset or environment.

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            alias: Optional alias to filter by (returns single column if found).

        Returns:
            List of DerivedColumn objects (or single-item list if alias provided).
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        params = {"alias": alias} if alias else None
        data = self._get_sync(self._build_path(dataset), params=params)

        # API returns either a list or a single object when alias is used
        if isinstance(data, list):
            return self._parse_model_list(DerivedColumn, data)
        else:
            return [self._parse_model(DerivedColumn, data)]

    def get(self, dataset: str, column_id: str) -> DerivedColumn:
        """Get a specific derived column.

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            column_id: Derived column ID.

        Returns:
            DerivedColumn object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, column_id))
        return self._parse_model(DerivedColumn, data)

    def create(self, dataset: str, derived_column: DerivedColumnCreate) -> DerivedColumn:
        """Create a new derived column.

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            derived_column: Derived column configuration.

        Returns:
            Created DerivedColumn object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(dataset), json=derived_column.model_dump_for_api())
        return self._parse_model(DerivedColumn, data)

    def update(
        self, dataset: str, column_id: str, derived_column: DerivedColumnCreate
    ) -> DerivedColumn:
        """Update an existing derived column.

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            column_id: Derived column ID.
            derived_column: Updated derived column configuration.

        Returns:
            Updated DerivedColumn object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(
            self._build_path(dataset, column_id), json=derived_column.model_dump_for_api()
        )
        return self._parse_model(DerivedColumn, data)

    def delete(self, dataset: str, column_id: str) -> None:
        """Delete a derived column.

        Args:
            dataset: Dataset slug or "__all__" for environment-wide.
            column_id: Derived column ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(dataset, column_id))
