"""Auth resource for retrieving API key metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

from honeycomb.models.auth import AuthInfo, AuthInfoV2
from honeycomb.resources.base import BaseResource

if TYPE_CHECKING:
    from honeycomb.client import HoneycombClient


class AuthResource(BaseResource):
    """Access authentication metadata for the current API key.

    Example:
        >>> # Auto-detects endpoint based on credentials
        >>> auth_info = await client.auth.get_async()
        >>> print(f"Team: {auth_info.team_name}")

        >>> # Force v2 endpoint (requires management key)
        >>> auth_info = await client.auth.get_async(use_v2=True)
        >>> print(f"Scopes: {auth_info.scopes}")
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _is_management_auth(self) -> bool:
        """Check if client is using management key authentication."""
        from honeycomb.auth import ManagementKeyAuth

        return isinstance(self._client._auth, ManagementKeyAuth)

    def _require_management_auth(self) -> None:
        """Raise error if not using management key authentication."""
        if not self._is_management_auth():
            raise ValueError(
                "v2 auth endpoint requires management key authentication. "
                "Initialize client with management_key and management_secret."
            )

    async def get_async(self, *, use_v2: bool | None = None) -> AuthInfo | AuthInfoV2:
        """Get metadata about the current API key.

        Args:
            use_v2: Force v2 endpoint. If None, auto-detects based on credentials.
                   If True with API key credentials, raises ValueError.

        Returns:
            AuthInfo for v1 (API key) or AuthInfoV2 for v2 (management key).
        """
        if use_v2 is None:
            use_v2 = self._is_management_auth()

        if use_v2:
            self._require_management_auth()
            data = await self._get_async("/2/auth")
            return AuthInfoV2.from_jsonapi(data)

        data = await self._get_async("/1/auth")
        return AuthInfo(
            id=data.get("id", ""),
            type=data.get("type", ""),
            team_name=data.get("team", {}).get("name", ""),
            team_slug=data.get("team", {}).get("slug", ""),
            environment_name=data.get("environment", {}).get("name", ""),
            environment_slug=data.get("environment", {}).get("slug", ""),
            api_key_access=data.get("api_key_access", {}),
            time_to_live=data.get("time_to_live"),
        )

    def get(self, *, use_v2: bool | None = None) -> AuthInfo | AuthInfoV2:
        """Get metadata about the current API key (sync version)."""
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")

        if use_v2 is None:
            use_v2 = self._is_management_auth()

        if use_v2:
            self._require_management_auth()
            data = self._get_sync("/2/auth")
            return AuthInfoV2.from_jsonapi(data)

        data = self._get_sync("/1/auth")
        return AuthInfo(
            id=data.get("id", ""),
            type=data.get("type", ""),
            team_name=data.get("team", {}).get("name", ""),
            team_slug=data.get("team", {}).get("slug", ""),
            environment_name=data.get("environment", {}).get("name", ""),
            environment_slug=data.get("environment", {}).get("slug", ""),
            api_key_access=data.get("api_key_access", {}),
            time_to_live=data.get("time_to_live"),
        )
