"""Environments resource for Honeycomb API (v2 team-scoped)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

from ..models.environments import Environment, EnvironmentCreate, EnvironmentUpdate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient

# Default page size for pagination (API max is 100)
DEFAULT_PAGE_SIZE = 100


class EnvironmentsResource(BaseResource):
    """Resource for managing environments (v2 team-scoped).

    This resource requires Management Key authentication and operates
    on a specific team. Environments help organize your data and API keys.
    The team slug is automatically detected from the management key.

    Note:
        The list methods automatically paginate through all results. For teams
        with many environments, this may result in multiple API requests. The default
        rate limit is 100 requests per minute per operation. If you need higher
        limits, contact Honeycomb support: https://www.honeycomb.io/support

    Example (async):
        >>> async with HoneycombClient(
        ...     management_key="hcamk_xxx",
        ...     management_secret="xxx"
        ... ) as client:
        ...     envs = await client.environments.list_async()
        ...     env = await client.environments.create_async(
        ...         environment=EnvironmentCreate(
        ...             name="Production",
        ...             description="Production environment",
        ...             color=EnvironmentColor.RED
        ...         )
        ...     )

    Example (sync):
        >>> with HoneycombClient(
        ...     management_key="hcamk_xxx",
        ...     management_secret="xxx",
        ...     sync=True
        ... ) as client:
        ...     envs = client.environments.list()
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)
        self._cached_team_slug: str | None = None

    async def _get_team_slug_async(self) -> str:
        """Get team slug, auto-detecting from auth."""
        # Use cached value if available
        if self._cached_team_slug:
            return self._cached_team_slug

        # Auto-detect from auth endpoint
        auth_info = await self._client.auth.get_async()
        if not hasattr(auth_info, "team_slug") or not auth_info.team_slug:
            raise ValueError("Cannot auto-detect team slug from management key credentials.")

        self._cached_team_slug = auth_info.team_slug
        return self._cached_team_slug

    def _get_team_slug(self) -> str:
        """Get team slug (sync), auto-detecting from auth."""
        # Use cached value if available
        if self._cached_team_slug:
            return self._cached_team_slug

        # Auto-detect from auth endpoint
        auth_info = self._client.auth.get()
        if not hasattr(auth_info, "team_slug") or not auth_info.team_slug:
            raise ValueError("Cannot auto-detect team slug from management key credentials.")

        self._cached_team_slug = auth_info.team_slug
        return self._cached_team_slug

    def _build_path(self, team: str, env_id: str | None = None) -> str:
        """Build API path for environments."""
        base = f"/2/teams/{team}/environments"
        if env_id:
            return f"{base}/{env_id}"
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
        cursor: str | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        """Build query parameters for list requests."""
        params: dict[str, Any] = {"page[size]": page_size}
        if cursor:
            params["page[after]"] = cursor
        return params

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self) -> list[Environment]:
        """List all environments for the authenticated team (async).

        Automatically paginates through all results. For teams with many environments,
        this may result in multiple API requests.

        Returns:
            List of Environment objects.

        Note:
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        team = await self._get_team_slug_async()
        results: list[Environment] = []
        cursor: str | None = None
        path = self._build_path(team)

        while True:
            params = self._build_params(cursor=cursor)
            data = await self._get_async(path, params=params)

            # Parse JSON:API response
            if isinstance(data, dict) and "data" in data:
                items = data["data"]
                results.extend(Environment.from_jsonapi({"data": item}) for item in items)

                # Check for next page
                next_link = data.get("links", {}).get("next")
                cursor = self._extract_cursor(next_link)
                if not cursor:
                    break
            else:
                break

        return results

    async def get_async(self, env_id: str) -> Environment:
        """Get a specific environment (async).

        Args:
            env_id: Environment ID.

        Returns:
            Environment object.
        """
        team = await self._get_team_slug_async()
        data = await self._get_async(self._build_path(team, env_id))
        return Environment.from_jsonapi(data)

    async def create_async(self, environment: EnvironmentCreate) -> Environment:
        """Create a new environment (async).

        Args:
            environment: Environment configuration.

        Returns:
            Created Environment object.
        """
        team = await self._get_team_slug_async()
        data = await self._post_async(
            self._build_path(team),
            json=environment.to_jsonapi(),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return Environment.from_jsonapi(data)

    async def update_async(self, env_id: str, environment: EnvironmentUpdate) -> Environment:
        """Update an existing environment (async).

        Args:
            env_id: Environment ID.
            environment: Updated environment configuration.

        Returns:
            Updated Environment object.
        """
        team = await self._get_team_slug_async()
        data = await self._patch_async(
            self._build_path(team, env_id),
            json=environment.to_jsonapi(env_id),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return Environment.from_jsonapi(data)

    async def delete_async(self, env_id: str) -> None:
        """Delete an environment (async).

        Args:
            env_id: Environment ID.
        """
        team = await self._get_team_slug_async()
        await self._delete_async(self._build_path(team, env_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self) -> list[Environment]:
        """List all environments for the authenticated team.

        Automatically paginates through all results. For teams with many environments,
        this may result in multiple API requests.

        Returns:
            List of Environment objects.

        Note:
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")

        team = self._get_team_slug()
        results: list[Environment] = []
        cursor: str | None = None
        path = self._build_path(team)

        while True:
            params = self._build_params(cursor=cursor)
            data = self._get_sync(path, params=params)

            # Parse JSON:API response
            if isinstance(data, dict) and "data" in data:
                items = data["data"]
                results.extend(Environment.from_jsonapi({"data": item}) for item in items)

                # Check for next page
                next_link = data.get("links", {}).get("next")
                cursor = self._extract_cursor(next_link)
                if not cursor:
                    break
            else:
                break

        return results

    def get(self, env_id: str) -> Environment:
        """Get a specific environment.

        Args:
            env_id: Environment ID.

        Returns:
            Environment object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        data = self._get_sync(self._build_path(team, env_id))
        return Environment.from_jsonapi(data)

    def create(self, environment: EnvironmentCreate) -> Environment:
        """Create a new environment.

        Args:
            environment: Environment configuration.

        Returns:
            Created Environment object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        data = self._post_sync(
            self._build_path(team),
            json=environment.to_jsonapi(),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return Environment.from_jsonapi(data)

    def update(self, env_id: str, environment: EnvironmentUpdate) -> Environment:
        """Update an existing environment.

        Args:
            env_id: Environment ID.
            environment: Updated environment configuration.

        Returns:
            Updated Environment object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        data = self._patch_sync(
            self._build_path(team, env_id),
            json=environment.to_jsonapi(env_id),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return Environment.from_jsonapi(data)

    def delete(self, env_id: str) -> None:
        """Delete an environment.

        Args:
            env_id: Environment ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        self._delete_sync(self._build_path(team, env_id))
