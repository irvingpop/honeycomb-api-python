"""Burn Alerts resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.burn_alerts import (
    BurnAlertDetailResponse,
    BurnAlertListResponse,
    CreateBurnAlertRequest,
    UpdateBurnAlertRequest,
)
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class BurnAlertsResource(BaseResource):
    """Resource for managing SLO burn alerts.

    Burn alerts notify you when you're consuming your SLO error budget too quickly.
    Two alert types are supported:
    - exhaustion_time: Alerts when budget will be exhausted within X minutes
    - budget_rate: Alerts when budget drops by X% within a time window

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     alerts = await client.burn_alerts.list(
        ...         dataset="my-dataset",
        ...         slo_id="abc123"
        ...     )
        ...     alert = await client.burn_alerts.create(
        ...         dataset="my-dataset",
        ...         burn_alert=request  # See BurnAlertBuilder
        ...     )

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     alerts = client.burn_alerts.list(
        ...         dataset="my-dataset",
        ...         slo_id="abc123"
        ...     )
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, burn_alert_id: str | None = None) -> str:
        """Build API path for burn alerts."""
        base = f"/1/burn_alerts/{dataset}"
        if burn_alert_id:
            return f"{base}/{burn_alert_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self, dataset: str, slo_id: str) -> list[BurnAlertListResponse]:
        """List all burn alerts for an SLO (async).

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID to list burn alerts for.

        Returns:
            List of BurnAlertListResponse objects (discriminated union).
        """
        path = f"{self._build_path(dataset)}?slo_id={slo_id}"
        data = await self._get_async(path)
        return self._parse_model_list(BurnAlertListResponse, data)

    async def get_async(self, dataset: str, burn_alert_id: str) -> BurnAlertDetailResponse:
        """Get a specific burn alert (async).

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.

        Returns:
            BurnAlertDetailResponse (discriminated union).
        """
        data = await self._get_async(self._build_path(dataset, burn_alert_id))
        return self._parse_model(BurnAlertDetailResponse, data)

    async def create_async(
        self, dataset: str, burn_alert: CreateBurnAlertRequest
    ) -> BurnAlertDetailResponse:
        """Create a new burn alert (async).

        Args:
            dataset: Dataset slug.
            burn_alert: Burn alert creation request (discriminated union).

        Returns:
            Created BurnAlertDetailResponse.
        """
        data = await self._post_async(
            self._build_path(dataset),
            json=burn_alert.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return self._parse_model(BurnAlertDetailResponse, data)

    async def update_async(
        self, dataset: str, burn_alert_id: str, burn_alert: UpdateBurnAlertRequest
    ) -> BurnAlertDetailResponse:
        """Update an existing burn alert (async).

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.
            burn_alert: Updated burn alert request (discriminated union).

        Returns:
            Updated BurnAlertDetailResponse.
        """
        data = await self._put_async(
            self._build_path(dataset, burn_alert_id),
            json=burn_alert.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return self._parse_model(BurnAlertDetailResponse, data)

    async def delete_async(self, dataset: str, burn_alert_id: str) -> None:
        """Delete a burn alert (async).

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.
        """
        await self._delete_async(self._build_path(dataset, burn_alert_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self, dataset: str, slo_id: str) -> list[BurnAlertListResponse]:
        """List all burn alerts for an SLO.

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID to list burn alerts for.

        Returns:
            List of BurnAlertListResponse objects (discriminated union).
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        path = f"{self._build_path(dataset)}?slo_id={slo_id}"
        data = self._get_sync(path)
        return self._parse_model_list(BurnAlertListResponse, data)

    def get(self, dataset: str, burn_alert_id: str) -> BurnAlertDetailResponse:
        """Get a specific burn alert.

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.

        Returns:
            BurnAlertDetailResponse (discriminated union).
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, burn_alert_id))
        return self._parse_model(BurnAlertDetailResponse, data)

    def create(self, dataset: str, burn_alert: CreateBurnAlertRequest) -> BurnAlertDetailResponse:
        """Create a new burn alert.

        Args:
            dataset: Dataset slug.
            burn_alert: Burn alert creation request (discriminated union).

        Returns:
            Created BurnAlertDetailResponse.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(
            self._build_path(dataset),
            json=burn_alert.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return self._parse_model(BurnAlertDetailResponse, data)

    def update(
        self, dataset: str, burn_alert_id: str, burn_alert: UpdateBurnAlertRequest
    ) -> BurnAlertDetailResponse:
        """Update an existing burn alert.

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.
            burn_alert: Updated burn alert request (discriminated union).

        Returns:
            Updated BurnAlertDetailResponse.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(
            self._build_path(dataset, burn_alert_id),
            json=burn_alert.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return self._parse_model(BurnAlertDetailResponse, data)

    def delete(self, dataset: str, burn_alert_id: str) -> None:
        """Delete a burn alert.

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(dataset, burn_alert_id))
