"""Auth resource for retrieving API key metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

from honeycomb.models.auth import Auth, AuthV2Response
from honeycomb.resources.base import BaseResource

if TYPE_CHECKING:
    from honeycomb.client import HoneycombClient


class AuthResource(BaseResource):
    """Access authentication metadata for the current API key.

    Example:
        >>> # Auto-detects endpoint based on credentials
        >>> auth_info = await client.auth.get_async()
        >>> print(f"Team: {auth_info.team.name}")

        >>> # Force v2 endpoint (requires management key)
        >>> auth_info = await client.auth.get_async(use_v2=True)
        >>> print(f"Scopes: {auth_info.data.attributes.scopes}")
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

    async def get_async(self, *, use_v2: bool | None = None) -> Auth | AuthV2Response:
        """Get metadata about the current API key.

        Args:
            use_v2: Force v2 endpoint. If None, auto-detects based on credentials.
                   If True with API key credentials, raises ValueError.

        Returns:
            Auth for v1 (API key) or AuthV2Response for v2 (management key).
        """
        if use_v2 is None:
            use_v2 = self._is_management_auth()

        if use_v2:
            self._require_management_auth()
            data = await self._get_async("/2/auth")
            return self._parse_model(AuthV2Response, data)

        data = await self._get_async("/1/auth")
        return self._parse_model(Auth, data)

    def get(self, *, use_v2: bool | None = None) -> Auth | AuthV2Response:
        """Get metadata about the current API key (sync version)."""
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")

        if use_v2 is None:
            use_v2 = self._is_management_auth()

        if use_v2:
            self._require_management_auth()
            data = self._get_sync("/2/auth")
            return self._parse_model(AuthV2Response, data)

        data = self._get_sync("/1/auth")
        return self._parse_model(Auth, data)
