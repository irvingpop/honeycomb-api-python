"""Markers resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING, List  # noqa: UP035

from ..models.markers import Marker, MarkerCreate, MarkerSetting, MarkerSettingCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class MarkersResource(BaseResource):
    """Resource for managing dataset markers.

    Markers allow you to annotate your data with events like deployments,
    configuration changes, or other significant occurrences.

    Note: The Markers API does not support GET for individual markers.
    Use list() to retrieve all markers and filter client-side if needed.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     markers = await client.markers.list_async(dataset="my-dataset")
        ...     marker = await client.markers.create_async(
        ...         dataset="my-dataset",
        ...         marker=MarkerCreate(
        ...             message="deploy #123",
        ...             type="deploy"
        ...         )
        ...     )

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     markers = client.markers.list(dataset="my-dataset")
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, marker_id: str | None = None) -> str:
        """Build API path for markers."""
        base = f"/1/markers/{dataset}"
        if marker_id:
            return f"{base}/{marker_id}"
        return base

    def _build_settings_path(self, dataset: str, setting_id: str | None = None) -> str:
        """Build API path for marker settings."""
        base = f"/1/marker_settings/{dataset}"
        if setting_id:
            return f"{base}/{setting_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods - Markers
    # -------------------------------------------------------------------------

    async def list_async(self, dataset: str) -> list[Marker]:
        """List all markers for a dataset (async).

        Args:
            dataset: Dataset slug.

        Returns:
            List of Marker objects.
        """
        data = await self._get_async(self._build_path(dataset))
        return self._parse_model_list(Marker, data)

    async def create_async(self, dataset: str, marker: MarkerCreate) -> Marker:
        """Create a new marker (async).

        Args:
            dataset: Dataset slug (use '__all__' for environment-wide markers).
            marker: Marker configuration.

        Returns:
            Created Marker object.
        """
        data = await self._post_async(self._build_path(dataset), json=marker.model_dump_for_api())
        return self._parse_model(Marker, data)

    async def update_async(self, dataset: str, marker_id: str, marker: MarkerCreate) -> Marker:
        """Update an existing marker (async).

        Args:
            dataset: Dataset slug.
            marker_id: Marker ID.
            marker: Updated marker configuration.

        Returns:
            Updated Marker object.
        """
        data = await self._put_async(
            self._build_path(dataset, marker_id), json=marker.model_dump_for_api()
        )
        return self._parse_model(Marker, data)

    async def delete_async(self, dataset: str, marker_id: str) -> None:
        """Delete a marker (async).

        Args:
            dataset: Dataset slug.
            marker_id: Marker ID.
        """
        await self._delete_async(self._build_path(dataset, marker_id))

    # -------------------------------------------------------------------------
    # Async methods - Marker Settings
    # -------------------------------------------------------------------------

    async def list_settings_async(self, dataset: str) -> list[MarkerSetting]:
        """List all marker settings for a dataset (async).

        Args:
            dataset: Dataset slug.

        Returns:
            List of MarkerSetting objects.
        """
        data = await self._get_async(self._build_settings_path(dataset))
        return self._parse_model_list(MarkerSetting, data)

    async def get_setting_async(self, dataset: str, setting_id: str) -> MarkerSetting:
        """Get a specific marker setting (async).

        Args:
            dataset: Dataset slug.
            setting_id: Marker setting ID.

        Returns:
            MarkerSetting object.
        """
        data = await self._get_async(self._build_settings_path(dataset, setting_id))
        return self._parse_model(MarkerSetting, data)

    async def create_setting_async(
        self, dataset: str, setting: MarkerSettingCreate
    ) -> MarkerSetting:
        """Create a new marker setting (async).

        Args:
            dataset: Dataset slug.
            setting: Marker setting configuration.

        Returns:
            Created MarkerSetting object.
        """
        data = await self._post_async(
            self._build_settings_path(dataset), json=setting.model_dump_for_api()
        )
        return self._parse_model(MarkerSetting, data)

    async def update_setting_async(
        self, dataset: str, setting_id: str, setting: MarkerSettingCreate
    ) -> MarkerSetting:
        """Update an existing marker setting (async).

        Args:
            dataset: Dataset slug.
            setting_id: Marker setting ID.
            setting: Updated marker setting configuration.

        Returns:
            Updated MarkerSetting object.
        """
        data = await self._put_async(
            self._build_settings_path(dataset, setting_id), json=setting.model_dump_for_api()
        )
        return self._parse_model(MarkerSetting, data)

    async def delete_setting_async(self, dataset: str, setting_id: str) -> None:
        """Delete a marker setting (async).

        Args:
            dataset: Dataset slug.
            setting_id: Marker setting ID.
        """
        await self._delete_async(self._build_settings_path(dataset, setting_id))

    # -------------------------------------------------------------------------
    # Sync methods - Markers
    # -------------------------------------------------------------------------

    def list(self, dataset: str) -> list[Marker]:
        """List all markers for a dataset.

        Args:
            dataset: Dataset slug.

        Returns:
            List of Marker objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset))
        return self._parse_model_list(Marker, data)

    def create(self, dataset: str, marker: MarkerCreate) -> Marker:
        """Create a new marker.

        Args:
            dataset: Dataset slug (use '__all__' for environment-wide markers).
            marker: Marker configuration.

        Returns:
            Created Marker object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(dataset), json=marker.model_dump_for_api())
        return self._parse_model(Marker, data)

    def update(self, dataset: str, marker_id: str, marker: MarkerCreate) -> Marker:
        """Update an existing marker.

        Args:
            dataset: Dataset slug.
            marker_id: Marker ID.
            marker: Updated marker configuration.

        Returns:
            Updated Marker object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(
            self._build_path(dataset, marker_id), json=marker.model_dump_for_api()
        )
        return self._parse_model(Marker, data)

    def delete(self, dataset: str, marker_id: str) -> None:
        """Delete a marker.

        Args:
            dataset: Dataset slug.
            marker_id: Marker ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(dataset, marker_id))

    # -------------------------------------------------------------------------
    # Sync methods - Marker Settings
    # -------------------------------------------------------------------------

    def list_settings(self, dataset: str) -> List[MarkerSetting]:  # noqa: UP006
        """List all marker settings for a dataset.

        Args:
            dataset: Dataset slug.

        Returns:
            List of MarkerSetting objects.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use list_settings_async() for async mode, or pass sync=True to client"
            )
        data = self._get_sync(self._build_settings_path(dataset))
        return self._parse_model_list(MarkerSetting, data)

    def get_setting(self, dataset: str, setting_id: str) -> MarkerSetting:
        """Get a specific marker setting.

        Args:
            dataset: Dataset slug.
            setting_id: Marker setting ID.

        Returns:
            MarkerSetting object.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use get_setting_async() for async mode, or pass sync=True to client"
            )
        data = self._get_sync(self._build_settings_path(dataset, setting_id))
        return self._parse_model(MarkerSetting, data)

    def create_setting(self, dataset: str, setting: MarkerSettingCreate) -> MarkerSetting:
        """Create a new marker setting.

        Args:
            dataset: Dataset slug.
            setting: Marker setting configuration.

        Returns:
            Created MarkerSetting object.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use create_setting_async() for async mode, or pass sync=True to client"
            )
        data = self._post_sync(
            self._build_settings_path(dataset), json=setting.model_dump_for_api()
        )
        return self._parse_model(MarkerSetting, data)

    def update_setting(
        self, dataset: str, setting_id: str, setting: MarkerSettingCreate
    ) -> MarkerSetting:
        """Update an existing marker setting.

        Args:
            dataset: Dataset slug.
            setting_id: Marker setting ID.
            setting: Updated marker setting configuration.

        Returns:
            Updated MarkerSetting object.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use update_setting_async() for async mode, or pass sync=True to client"
            )
        data = self._put_sync(
            self._build_settings_path(dataset, setting_id), json=setting.model_dump_for_api()
        )
        return self._parse_model(MarkerSetting, data)

    def delete_setting(self, dataset: str, setting_id: str) -> None:
        """Delete a marker setting.

        Args:
            dataset: Dataset slug.
            setting_id: Marker setting ID.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use delete_setting_async() for async mode, or pass sync=True to client"
            )
        self._delete_sync(self._build_settings_path(dataset, setting_id))
