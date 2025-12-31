"""API Keys resource for Honeycomb API (v2 team-scoped)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

from ..models.api_keys import ApiKey, ApiKeyCreate, ApiKeyUpdate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient

# Default page size for pagination (API max is 100)
DEFAULT_PAGE_SIZE = 100


class ApiKeysResource(BaseResource):
    """Resource for managing API keys (v2 team-scoped).

    This resource requires Management Key authentication and operates
    on a specific team. API keys can be either ingest keys (for sending data)
    or configuration keys (for API access).

    Note:
        The list methods automatically paginate through all results. For teams
        with many API keys, this may result in multiple API requests. The default
        rate limit is 100 requests per minute per operation. If you need higher
        limits, contact Honeycomb support: https://www.honeycomb.io/support

    Example (async):
        >>> async with HoneycombClient(
        ...     management_key="hcamk_xxx",
        ...     management_secret="xxx"
        ... ) as client:
        ...     keys = await client.api_keys.list_async()
        ...     key = await client.api_keys.create_async(
        ...         api_key=ApiKeyCreate(
        ...             name="My Ingest Key",
        ...             key_type=ApiKeyType.INGEST,
        ...             environment_id="env-123"
        ...         )
        ...     )

    Example (sync):
        >>> with HoneycombClient(
        ...     management_key="hcamk_xxx",
        ...     management_secret="xxx",
        ...     sync=True
        ... ) as client:
        ...     keys = client.api_keys.list()
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)
        self._cached_team_slug: str | None = None

    async def _get_team_slug_async(self, team: str | None = None) -> str:
        """Get team slug, auto-detecting from auth if not provided."""
        if team:
            return team

        # Use cached value if available
        if self._cached_team_slug:
            return self._cached_team_slug

        # Auto-detect from auth endpoint
        auth_info = await self._client.auth.get_async()
        if not hasattr(auth_info, "team_slug") or not auth_info.team_slug:
            raise ValueError(
                "Cannot auto-detect team slug. Please provide team parameter explicitly."
            )

        self._cached_team_slug = auth_info.team_slug
        return self._cached_team_slug

    def _get_team_slug(self, team: str | None = None) -> str:
        """Get team slug (sync), auto-detecting from auth if not provided."""
        if team:
            return team

        # Use cached value if available
        if self._cached_team_slug:
            return self._cached_team_slug

        # Auto-detect from auth endpoint
        auth_info = self._client.auth.get()
        if not hasattr(auth_info, "team_slug") or not auth_info.team_slug:
            raise ValueError(
                "Cannot auto-detect team slug. Please provide team parameter explicitly."
            )

        self._cached_team_slug = auth_info.team_slug
        return self._cached_team_slug

    def _build_path(self, team: str, key_id: str | None = None) -> str:
        """Build API path for API keys."""
        base = f"/2/teams/{team}/api-keys"
        if key_id:
            return f"{base}/{key_id}"
        return base

    def _extract_cursor(self, next_link: str | None) -> str | None:
        """Extract cursor value from pagination next link."""
        if not next_link:
            return None
        parsed = urlparse(next_link)
        query_params = parse_qs(parsed.query)
        cursor_values = query_params.get("page[after]", [])
        return cursor_values[0] if cursor_values else None

    def _build_params(
        self,
        key_type: str | None = None,
        cursor: str | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        """Build query parameters for list requests."""
        params: dict[str, Any] = {"page[size]": page_size}
        if key_type:
            params["filter[type]"] = key_type
        if cursor:
            params["page[after]"] = cursor
        return params

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self, key_type: str | None = None) -> list[ApiKey]:
        """List all API keys for the authenticated team (async).

        Automatically paginates through all results. For teams with many API keys,
        this may result in multiple API requests.

        Args:
            key_type: Optional filter by key type ('ingest' or 'configuration').

        Returns:
            List of ApiKey objects.

        Note:
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        team = await self._get_team_slug_async()
        results: list[ApiKey] = []
        cursor: str | None = None
        path = self._build_path(team)

        while True:
            params = self._build_params(key_type=key_type, cursor=cursor)
            data = await self._get_async(path, params=params)

            # Parse JSON:API response
            if isinstance(data, dict) and "data" in data:
                items = data["data"]
                results.extend(ApiKey.from_jsonapi({"data": item}) for item in items)

                # Check for next page
                next_link = data.get("links", {}).get("next")
                cursor = self._extract_cursor(next_link)
                if not cursor:
                    break
            else:
                break

        return results

    async def get_async(self, key_id: str) -> ApiKey:
        """Get a specific API key (async).

        Args:
            key_id: API Key ID.

        Returns:
            ApiKey object.
        """
        team = await self._get_team_slug_async()
        data = await self._get_async(self._build_path(team, key_id))
        return ApiKey.from_jsonapi(data)

    async def create_async(self, api_key: ApiKeyCreate) -> ApiKey:
        """Create a new API key (async).

        Args:
            api_key: API key configuration.

        Returns:
            Created ApiKey object (includes secret, save it immediately!).
        """
        team = await self._get_team_slug_async()
        data = await self._post_async(
            self._build_path(team),
            json=api_key.to_jsonapi(),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return ApiKey.from_jsonapi(data)

    async def update_async(self, key_id: str, api_key: ApiKeyUpdate) -> ApiKey:
        """Update an existing API key (async).

        Args:
            key_id: API Key ID.
            api_key: Updated API key configuration.

        Returns:
            Updated ApiKey object.
        """
        team = await self._get_team_slug_async()
        payload = api_key.to_jsonapi(key_id)
        data = await self._patch_async(
            self._build_path(team, key_id),
            json=payload,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return ApiKey.from_jsonapi(data)

    async def delete_async(self, key_id: str) -> None:
        """Delete an API key (async).

        Args:
            key_id: API Key ID.
        """
        team = await self._get_team_slug_async()
        await self._delete_async(self._build_path(team, key_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self, key_type: str | None = None) -> list[ApiKey]:
        """List all API keys for the authenticated team.

        Automatically paginates through all results. For teams with many API keys,
        this may result in multiple API requests.

        Args:
            key_type: Optional filter by key type ('ingest' or 'configuration').

        Returns:
            List of ApiKey objects.

        Note:
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")

        team = self._get_team_slug()
        results: list[ApiKey] = []
        cursor: str | None = None
        path = self._build_path(team)

        while True:
            params = self._build_params(key_type=key_type, cursor=cursor)
            data = self._get_sync(path, params=params)

            # Parse JSON:API response
            if isinstance(data, dict) and "data" in data:
                items = data["data"]
                results.extend(ApiKey.from_jsonapi({"data": item}) for item in items)

                # Check for next page
                next_link = data.get("links", {}).get("next")
                cursor = self._extract_cursor(next_link)
                if not cursor:
                    break
            else:
                break

        return results

    def get(self, key_id: str) -> ApiKey:
        """Get a specific API key.

        Args:
            key_id: API Key ID.

        Returns:
            ApiKey object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        data = self._get_sync(self._build_path(team, key_id))
        return ApiKey.from_jsonapi(data)

    def create(self, api_key: ApiKeyCreate) -> ApiKey:
        """Create a new API key.

        Args:
            team: Team slug.
            api_key: API key configuration.

        Returns:
            Created ApiKey object (includes secret, save it immediately!).
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        data = self._post_sync(
            self._build_path(team),
            json=api_key.to_jsonapi(),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return ApiKey.from_jsonapi(data)

    def update(self, key_id: str, api_key: ApiKeyUpdate) -> ApiKey:
        """Update an existing API key.

        Args:
            key_id: API Key ID.
            api_key: Updated API key configuration.

        Returns:
            Updated ApiKey object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        payload = api_key.to_jsonapi(key_id)
        data = self._patch_sync(
            self._build_path(team, key_id),
            json=payload,
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return ApiKey.from_jsonapi(data)

    def delete(self, key_id: str) -> None:
        """Delete an API key.

        Args:
            key_id: API Key ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        self._delete_sync(self._build_path(team, key_id))
