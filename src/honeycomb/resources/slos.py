"""SLOs resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.slos import SLO, SLOCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class SLOsResource(BaseResource):
    """Resource for managing Honeycomb SLOs (Service Level Objectives).

    SLOs allow you to define and track service level objectives
    based on your data.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     slos = await client.slos.list(dataset="my-dataset")
        ...     slo = await client.slos.get(dataset="my-dataset", slo_id="abc123")

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     slos = client.slos.list(dataset="my-dataset")
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, slo_id: str | None = None) -> str:
        """Build API path for SLOs."""
        base = f"/1/slos/{dataset}"
        if slo_id:
            return f"{base}/{slo_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self, dataset: str) -> list[SLO]:
        """List all SLOs for a dataset (async).

        Args:
            dataset: Dataset slug.

        Returns:
            List of SLO objects.
        """
        data = await self._get_async(self._build_path(dataset))
        return self._parse_model_list(SLO, data)

    async def get_async(self, dataset: str, slo_id: str) -> SLO:
        """Get a specific SLO (async).

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.

        Returns:
            SLO object.
        """
        data = await self._get_async(self._build_path(dataset, slo_id))
        return self._parse_model(SLO, data)

    async def create_async(self, dataset: str, slo: SLOCreate) -> SLO:
        """Create a new SLO (async).

        Args:
            dataset: Dataset slug.
            slo: SLO configuration.

        Returns:
            Created SLO object.
        """
        data = await self._post_async(self._build_path(dataset), json=slo.model_dump_for_api())
        return self._parse_model(SLO, data)

    async def update_async(self, dataset: str, slo_id: str, slo: SLOCreate) -> SLO:
        """Update an existing SLO (async).

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.
            slo: Updated SLO configuration.

        Returns:
            Updated SLO object.
        """
        data = await self._put_async(
            self._build_path(dataset, slo_id), json=slo.model_dump_for_api()
        )
        return self._parse_model(SLO, data)

    async def delete_async(self, dataset: str, slo_id: str) -> None:
        """Delete an SLO (async).

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.
        """
        await self._delete_async(self._build_path(dataset, slo_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self, dataset: str) -> list[SLO]:
        """List all SLOs for a dataset.

        Args:
            dataset: Dataset slug.

        Returns:
            List of SLO objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset))
        return self._parse_model_list(SLO, data)

    def get(self, dataset: str, slo_id: str) -> SLO:
        """Get a specific SLO.

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.

        Returns:
            SLO object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, slo_id))
        return self._parse_model(SLO, data)

    def create(self, dataset: str, slo: SLOCreate) -> SLO:
        """Create a new SLO.

        Args:
            dataset: Dataset slug.
            slo: SLO configuration.

        Returns:
            Created SLO object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(dataset), json=slo.model_dump_for_api())
        return self._parse_model(SLO, data)

    def update(self, dataset: str, slo_id: str, slo: SLOCreate) -> SLO:
        """Update an existing SLO.

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.
            slo: Updated SLO configuration.

        Returns:
            Updated SLO object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(self._build_path(dataset, slo_id), json=slo.model_dump_for_api())
        return self._parse_model(SLO, data)

    def delete(self, dataset: str, slo_id: str) -> None:
        """Delete an SLO.

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(dataset, slo_id))
