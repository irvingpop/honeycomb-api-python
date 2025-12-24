"""Datasets resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.datasets import Dataset, DatasetCreate
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

    async def list_async(self) -> list[Dataset]:
        """List all datasets (async).

        Returns:
            List of Dataset objects.
        """
        data = await self._get_async(self._build_path())
        return self._parse_model_list(Dataset, data)

    async def get_async(self, slug: str) -> Dataset:
        """Get a specific dataset (async).

        Args:
            slug: Dataset slug.

        Returns:
            Dataset object.
        """
        data = await self._get_async(self._build_path(slug))
        return self._parse_model(Dataset, data)

    async def create_async(self, dataset: DatasetCreate) -> Dataset:
        """Create a new dataset (async).

        Args:
            dataset: Dataset configuration.

        Returns:
            Created Dataset object.
        """
        data = await self._post_async(self._build_path(), json=dataset.model_dump_for_api())
        return self._parse_model(Dataset, data)

    async def update_async(self, slug: str, dataset: DatasetCreate) -> Dataset:
        """Update an existing dataset (async).

        Args:
            slug: Dataset slug.
            dataset: Updated dataset configuration.

        Returns:
            Updated Dataset object.
        """
        data = await self._put_async(self._build_path(slug), json=dataset.model_dump_for_api())
        return self._parse_model(Dataset, data)

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
        return self._parse_model_list(Dataset, data)

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
        return self._parse_model(Dataset, data)

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
        return self._parse_model(Dataset, data)

    def update(self, slug: str, dataset: DatasetCreate) -> Dataset:
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
        return self._parse_model(Dataset, data)

    def delete(self, slug: str) -> None:
        """Delete a dataset.

        Args:
            slug: Dataset slug.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(slug))
