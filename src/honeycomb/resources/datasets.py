"""Datasets resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.datasets import Dataset, DatasetCreate, DatasetUpdate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class DatasetsResource(BaseResource):
    """Resource for managing Honeycomb datasets.

    Datasets are containers for your telemetry data in Honeycomb.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     datasets = await client.datasets.list()
        ...     dataset = await client.datasets.get(slug="my-dataset")

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     datasets = client.datasets.list()
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, slug: str | None = None) -> str:
        """Build API path for datasets."""
        base = "/1/datasets"
        if slug:
            return f"{base}/{slug}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    def _parse_dataset(self, data: dict) -> Dataset:
        """Parse a dataset from API response, handling nested settings."""
        return Dataset.from_api_response(data)

    def _parse_dataset_list(self, data: list) -> list[Dataset]:
        """Parse a list of datasets from API response."""
        return [self._parse_dataset(item) for item in data]

    async def list_async(self) -> list[Dataset]:
        """List all datasets (async).

        Returns:
            List of Dataset objects.
        """
        data = await self._get_async(self._build_path())
        return self._parse_dataset_list(data)

    async def get_async(self, slug: str) -> Dataset:
        """Get a specific dataset (async).

        Args:
            slug: Dataset slug.

        Returns:
            Dataset object.
        """
        data = await self._get_async(self._build_path(slug))
        return self._parse_dataset(data)

    async def create_async(self, dataset: DatasetCreate) -> Dataset:
        """Create a new dataset (async).

        Args:
            dataset: Dataset configuration.

        Returns:
            Created Dataset object.
        """
        data = await self._post_async(self._build_path(), json=dataset.model_dump_for_api())
        return self._parse_dataset(data)

    async def update_async(self, slug: str, dataset: DatasetCreate | DatasetUpdate) -> Dataset:
        """Update an existing dataset (async).

        Args:
            slug: Dataset slug.
            dataset: Updated dataset configuration.

        Returns:
            Updated Dataset object.
        """
        data = await self._put_async(self._build_path(slug), json=dataset.model_dump_for_api())
        return self._parse_dataset(data)

    async def set_delete_protected_async(self, slug: str, protected: bool) -> Dataset:
        """Set delete protection on a dataset (async).

        Args:
            slug: Dataset slug.
            protected: True to enable delete protection, False to disable.

        Returns:
            Updated Dataset object.
        """
        update = DatasetUpdate(delete_protected=protected)
        return await self.update_async(slug=slug, dataset=update)

    async def delete_async(self, slug: str) -> None:
        """Delete a dataset (async).

        Args:
            slug: Dataset slug.
        """
        await self._delete_async(self._build_path(slug))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self) -> list[Dataset]:
        """List all datasets.

        Returns:
            List of Dataset objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path())
        return self._parse_dataset_list(data)

    def get(self, slug: str) -> Dataset:
        """Get a specific dataset.

        Args:
            slug: Dataset slug.

        Returns:
            Dataset object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(slug))
        return self._parse_dataset(data)

    def create(self, dataset: DatasetCreate) -> Dataset:
        """Create a new dataset.

        Args:
            dataset: Dataset configuration.

        Returns:
            Created Dataset object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(), json=dataset.model_dump_for_api())
        return self._parse_dataset(data)

    def update(self, slug: str, dataset: DatasetCreate | DatasetUpdate) -> Dataset:
        """Update an existing dataset.

        Args:
            slug: Dataset slug.
            dataset: Updated dataset configuration.

        Returns:
            Updated Dataset object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(self._build_path(slug), json=dataset.model_dump_for_api())
        return self._parse_dataset(data)

    def set_delete_protected(self, slug: str, protected: bool) -> Dataset:
        """Set delete protection on a dataset.

        Args:
            slug: Dataset slug.
            protected: True to enable delete protection, False to disable.

        Returns:
            Updated Dataset object.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use set_delete_protected_async() for async mode, or pass sync=True to client"
            )
        update = DatasetUpdate(delete_protected=protected)
        return self.update(slug=slug, dataset=update)

    def delete(self, slug: str) -> None:
        """Delete a dataset.

        Args:
            slug: Dataset slug.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(slug))
