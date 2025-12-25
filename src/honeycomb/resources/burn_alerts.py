"""Burn Alerts resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.burn_alerts import BurnAlert, BurnAlertCreate
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
        ...         burn_alert=BurnAlertCreate(
        ...             alert_type=BurnAlertType.EXHAUSTION_TIME,
        ...             slo_id="abc123",
        ...             exhaustion_minutes=120
        ...         )
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

    async def list_async(self, dataset: str, slo_id: str) -> list[BurnAlert]:
        """List all burn alerts for an SLO (async).

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID to list burn alerts for.

        Returns:
            List of BurnAlert objects.
        """
        path = f"{self._build_path(dataset)}?slo_id={slo_id}"
        data = await self._get_async(path)
        return self._parse_model_list(BurnAlert, data)

    async def get_async(self, dataset: str, burn_alert_id: str) -> BurnAlert:
        """Get a specific burn alert (async).

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.

        Returns:
            BurnAlert object.
        """
        data = await self._get_async(self._build_path(dataset, burn_alert_id))
        return self._parse_model(BurnAlert, data)

    async def create_async(self, dataset: str, burn_alert: BurnAlertCreate) -> BurnAlert:
        """Create a new burn alert (async).

        Args:
            dataset: Dataset slug.
            burn_alert: Burn alert configuration.

        Returns:
            Created BurnAlert object.
        """
        data = await self._post_async(
            self._build_path(dataset), json=burn_alert.model_dump_for_api()
        )
        return self._parse_model(BurnAlert, data)

    async def update_async(
        self, dataset: str, burn_alert_id: str, burn_alert: BurnAlertCreate
    ) -> BurnAlert:
        """Update an existing burn alert (async).

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.
            burn_alert: Updated burn alert configuration.

        Returns:
            Updated BurnAlert object.
        """
        data = await self._put_async(
            self._build_path(dataset, burn_alert_id), json=burn_alert.model_dump_for_api()
        )
        return self._parse_model(BurnAlert, data)

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

    def list(self, dataset: str, slo_id: str) -> list[BurnAlert]:
        """List all burn alerts for an SLO.

        Args:
            dataset: Dataset slug.
            slo_id: SLO ID to list burn alerts for.

        Returns:
            List of BurnAlert objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        path = f"{self._build_path(dataset)}?slo_id={slo_id}"
        data = self._get_sync(path)
        return self._parse_model_list(BurnAlert, data)

    def get(self, dataset: str, burn_alert_id: str) -> BurnAlert:
        """Get a specific burn alert.

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.

        Returns:
            BurnAlert object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, burn_alert_id))
        return self._parse_model(BurnAlert, data)

    def create(self, dataset: str, burn_alert: BurnAlertCreate) -> BurnAlert:
        """Create a new burn alert.

        Args:
            dataset: Dataset slug.
            burn_alert: Burn alert configuration.

        Returns:
            Created BurnAlert object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(dataset), json=burn_alert.model_dump_for_api())
        return self._parse_model(BurnAlert, data)

    def update(self, dataset: str, burn_alert_id: str, burn_alert: BurnAlertCreate) -> BurnAlert:
        """Update an existing burn alert.

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.
            burn_alert: Updated burn alert configuration.

        Returns:
            Updated BurnAlert object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(
            self._build_path(dataset, burn_alert_id), json=burn_alert.model_dump_for_api()
        )
        return self._parse_model(BurnAlert, data)

    def delete(self, dataset: str, burn_alert_id: str) -> None:
        """Delete a burn alert.

        Args:
            dataset: Dataset slug.
            burn_alert_id: Burn Alert ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(dataset, burn_alert_id))
