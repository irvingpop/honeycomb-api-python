"""Environments resource for Honeycomb API (v2 team-scoped)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.environments import Environment, EnvironmentCreate, EnvironmentUpdate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class EnvironmentsResource(BaseResource):
    """Resource for managing environments (v2 team-scoped).

    This resource requires Management Key authentication and operates
    on a specific team. Environments help organize your data and API keys.

    Example (async):
        >>> async with HoneycombClient(
        ...     management_key="hcamk_xxx",
        ...     management_secret="xxx"
        ... ) as client:
        ...     envs = await client.environments.list(team="my-team")
        ...     env = await client.environments.create(
        ...         team="my-team",
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
        ...     envs = client.environments.list(team="my-team")
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, team: str, env_id: str | None = None) -> str:
        """Build API path for environments."""
        base = f"/2/teams/{team}/environments"
        if env_id:
            return f"{base}/{env_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self, team: str) -> list[Environment]:
        """List all environments for a team (async).

        Args:
            team: Team slug.

        Returns:
            List of Environment objects.
        """
        data = await self._get_async(self._build_path(team))

        # Parse JSON:API response
        if isinstance(data, dict) and "data" in data:
            items = data["data"]
            return [Environment.from_jsonapi({"data": item}) for item in items]
        return []

    async def get_async(self, team: str, env_id: str) -> Environment:
        """Get a specific environment (async).

        Args:
            team: Team slug.
            env_id: Environment ID.

        Returns:
            Environment object.
        """
        data = await self._get_async(self._build_path(team, env_id))
        return Environment.from_jsonapi(data)

    async def create_async(self, team: str, environment: EnvironmentCreate) -> Environment:
        """Create a new environment (async).

        Args:
            team: Team slug.
            environment: Environment configuration.

        Returns:
            Created Environment object.
        """
        data = await self._post_async(
            self._build_path(team),
            json=environment.to_jsonapi(),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return Environment.from_jsonapi(data)

    async def update_async(
        self, team: str, env_id: str, environment: EnvironmentUpdate
    ) -> Environment:
        """Update an existing environment (async).

        Args:
            team: Team slug.
            env_id: Environment ID.
            environment: Updated environment configuration.

        Returns:
            Updated Environment object.
        """
        data = await self._patch_async(
            self._build_path(team, env_id),
            json=environment.to_jsonapi(env_id),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return Environment.from_jsonapi(data)

    async def delete_async(self, team: str, env_id: str) -> None:
        """Delete an environment (async).

        Args:
            team: Team slug.
            env_id: Environment ID.
        """
        await self._delete_async(self._build_path(team, env_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self, team: str) -> list[Environment]:
        """List all environments for a team.

        Args:
            team: Team slug.

        Returns:
            List of Environment objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")

        data = self._get_sync(self._build_path(team))

        # Parse JSON:API response
        if isinstance(data, dict) and "data" in data:
            items = data["data"]
            return [Environment.from_jsonapi({"data": item}) for item in items]
        return []

    def get(self, team: str, env_id: str) -> Environment:
        """Get a specific environment.

        Args:
            team: Team slug.
            env_id: Environment ID.

        Returns:
            Environment object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(team, env_id))
        return Environment.from_jsonapi(data)

    def create(self, team: str, environment: EnvironmentCreate) -> Environment:
        """Create a new environment.

        Args:
            team: Team slug.
            environment: Environment configuration.

        Returns:
            Created Environment object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(
            self._build_path(team),
            json=environment.to_jsonapi(),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return Environment.from_jsonapi(data)

    def update(self, team: str, env_id: str, environment: EnvironmentUpdate) -> Environment:
        """Update an existing environment.

        Args:
            team: Team slug.
            env_id: Environment ID.
            environment: Updated environment configuration.

        Returns:
            Updated Environment object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._patch_sync(
            self._build_path(team, env_id),
            json=environment.to_jsonapi(env_id),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        return Environment.from_jsonapi(data)

    def delete(self, team: str, env_id: str) -> None:
        """Delete an environment.

        Args:
            team: Team slug.
            env_id: Environment ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(team, env_id))
