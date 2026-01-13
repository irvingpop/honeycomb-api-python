"""Environments resource for Honeycomb API (v2 team-scoped)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

from ..models.environments import (
    CreateEnvironmentRequest,
    Environment,
    EnvironmentListResponse,
    EnvironmentResponse,
    UpdateEnvironmentRequest,
)
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
        ...     # See models.environments for CreateEnvironmentRequest structure
        ...     env = await client.environments.create_async(request)

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
        from honeycomb.models.auth import Auth, AuthV2Response

        auth_info = await self._client.auth.get_async()

        # Extract team slug based on auth response type
        if isinstance(auth_info, AuthV2Response):
            # v2 management key - extract team slug from included resources
            if not auth_info.included:
                raise ValueError("Cannot auto-detect team slug from management key credentials.")
            team_slug = None
            for resource in auth_info.included:
                if resource.type == "teams":
                    attrs = resource.attributes
                    if hasattr(attrs, "slug") and attrs is not None:
                        team_slug = attrs.slug
                    elif isinstance(attrs, dict):
                        team_slug = attrs.get("slug")
                    break
            if not team_slug:
                raise ValueError("Cannot auto-detect team slug from management key credentials.")
        elif isinstance(auth_info, Auth):
            # v1 API key - team slug is in nested team object
            team_slug = auth_info.team.slug
            if not team_slug:
                raise ValueError("Cannot auto-detect team slug from management key credentials.")
        else:
            raise ValueError("Unexpected auth response type")

        self._cached_team_slug = team_slug
        return team_slug

    def _get_team_slug(self) -> str:
        """Get team slug (sync), auto-detecting from auth."""
        # Use cached value if available
        if self._cached_team_slug:
            return self._cached_team_slug

        # Auto-detect from auth endpoint
        from honeycomb.models.auth import Auth, AuthV2Response

        auth_info = self._client.auth.get()

        # Extract team slug based on auth response type
        if isinstance(auth_info, AuthV2Response):
            # v2 management key - extract team slug from included resources
            if not auth_info.included:
                raise ValueError("Cannot auto-detect team slug from management key credentials.")
            team_slug = None
            for resource in auth_info.included:
                if resource.type == "teams":
                    attrs = resource.attributes
                    if hasattr(attrs, "slug") and attrs is not None:
                        team_slug = attrs.slug
                    elif isinstance(attrs, dict):
                        team_slug = attrs.get("slug")
                    break
            if not team_slug:
                raise ValueError("Cannot auto-detect team slug from management key credentials.")
        elif isinstance(auth_info, Auth):
            # v1 API key - team slug is in nested team object
            team_slug = auth_info.team.slug
            if not team_slug:
                raise ValueError("Cannot auto-detect team slug from management key credentials.")
        else:
            raise ValueError("Unexpected auth response type")

        self._cached_team_slug = team_slug
        return team_slug

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
            response = self._parse_model(EnvironmentListResponse, data)
            results.extend(response.data)

            # Check for next page
            cursor = self._extract_cursor(response.links.next if response.links else None)
            if not cursor:
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
        response = self._parse_model(EnvironmentResponse, data)
        return response.data

    async def create_async(
        self,
        environment: CreateEnvironmentRequest | None = None,
        *,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
    ) -> Environment:
        """Create a new environment (async).

        Args:
            environment: Full JSON:API environment creation request (advanced usage).
            name: Environment name (convenience parameter).
            description: Environment description (convenience parameter).
            color: Environment color (convenience parameter).

        Returns:
            Created Environment object.

        Examples:
            >>> # Simple convenience syntax
            >>> env = await client.environments.create_async(
            ...     name="Staging",
            ...     description="Staging environment",
            ...     color="blue"
            ... )
            >>>
            >>> # Advanced JSON:API syntax
            >>> env = await client.environments.create_async(
            ...     environment=CreateEnvironmentRequest(...)
            ... )
        """
        from honeycomb._generated_models import (
            CreateEnvironmentRequestData,
            CreateEnvironmentRequestDataAttributes,
            EnvironmentRelationshipDataType,
        )

        # Build request from convenience parameters if not provided
        if environment is None:
            if name is None:
                raise ValueError("Either 'environment' or 'name' must be provided")

            environment = CreateEnvironmentRequest(
                data=CreateEnvironmentRequestData(
                    type=EnvironmentRelationshipDataType.environments,
                    attributes=CreateEnvironmentRequestDataAttributes(
                        name=name,
                        description=description,
                        color=color,
                    ),
                )
            )

        team = await self._get_team_slug_async()
        data = await self._post_async(
            self._build_path(team),
            json=environment.model_dump(mode="json", exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        response = self._parse_model(EnvironmentResponse, data)
        return response.data

    async def update_async(
        self,
        env_id: str,
        environment: UpdateEnvironmentRequest | None = None,
        *,
        description: str | None = None,
        color: str | None = None,
        delete_protected: bool | None = None,
    ) -> Environment:
        """Update an existing environment (async).

        Args:
            env_id: Environment ID to update.
            environment: Full JSON:API update request (advanced usage).
            description: New description (convenience parameter).
            color: New color (convenience parameter).
            delete_protected: Enable/disable delete protection (convenience parameter).

        Returns:
            Updated Environment object.

        Examples:
            >>> # Simple convenience syntax
            >>> env = await client.environments.update_async(
            ...     env_id="hcaen_123",
            ...     description="Updated description",
            ...     delete_protected=False
            ... )
            >>>
            >>> # Advanced JSON:API syntax
            >>> env = await client.environments.update_async(
            ...     env_id="hcaen_123",
            ...     environment=UpdateEnvironmentRequest(...)
            ... )
        """
        from honeycomb._generated_models import (
            EnvironmentRelationshipDataType,
            UpdateEnvironmentRequestData,
            UpdateEnvironmentRequestDataAttributes,
            UpdateEnvironmentRequestDataAttributesSettings,
        )

        # Build request from convenience parameters if not provided
        if environment is None:
            settings = None
            if delete_protected is not None:
                settings = UpdateEnvironmentRequestDataAttributesSettings(
                    delete_protected=delete_protected
                )

            environment = UpdateEnvironmentRequest(
                data=UpdateEnvironmentRequestData(
                    id=env_id,
                    type=EnvironmentRelationshipDataType.environments,
                    attributes=UpdateEnvironmentRequestDataAttributes(
                        description=description,
                        color=color,
                        settings=settings,
                    ),
                )
            )
        else:
            # env_id comes from environment.data.id if using advanced syntax
            env_id = environment.data.id

        team = await self._get_team_slug_async()
        data = await self._patch_async(
            self._build_path(team, env_id),
            json=environment.model_dump(mode="json", exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        response = self._parse_model(EnvironmentResponse, data)
        return response.data

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
            response = self._parse_model(EnvironmentListResponse, data)
            results.extend(response.data)

            # Check for next page
            cursor = self._extract_cursor(response.links.next if response.links else None)
            if not cursor:
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
        response = self._parse_model(EnvironmentResponse, data)
        return response.data

    def create(
        self,
        environment: CreateEnvironmentRequest | None = None,
        *,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
    ) -> Environment:
        """Create a new environment.

        Args:
            environment: Full JSON:API environment creation request (advanced usage).
            name: Environment name (convenience parameter).
            description: Environment description (convenience parameter).
            color: Environment color (convenience parameter).

        Returns:
            Created Environment object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")

        from honeycomb._generated_models import (
            CreateEnvironmentRequestData,
            CreateEnvironmentRequestDataAttributes,
            EnvironmentRelationshipDataType,
        )

        # Build request from convenience parameters if not provided
        if environment is None:
            if name is None:
                raise ValueError("Either 'environment' or 'name' must be provided")

            environment = CreateEnvironmentRequest(
                data=CreateEnvironmentRequestData(
                    type=EnvironmentRelationshipDataType.environments,
                    attributes=CreateEnvironmentRequestDataAttributes(
                        name=name,
                        description=description,
                        color=color,
                    ),
                )
            )

        team = self._get_team_slug()
        data = self._post_sync(
            self._build_path(team),
            json=environment.model_dump(mode="json", exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        response = self._parse_model(EnvironmentResponse, data)
        return response.data

    def update(
        self,
        env_id: str,
        environment: UpdateEnvironmentRequest | None = None,
        *,
        description: str | None = None,
        color: str | None = None,
        delete_protected: bool | None = None,
    ) -> Environment:
        """Update an existing environment.

        Args:
            env_id: Environment ID to update.
            environment: Full JSON:API update request (advanced usage).
            description: New description (convenience parameter).
            color: New color (convenience parameter).
            delete_protected: Enable/disable delete protection (convenience parameter).

        Returns:
            Updated Environment object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")

        from honeycomb._generated_models import (
            EnvironmentRelationshipDataType,
            UpdateEnvironmentRequestData,
            UpdateEnvironmentRequestDataAttributes,
            UpdateEnvironmentRequestDataAttributesSettings,
        )

        # Build request from convenience parameters if not provided
        if environment is None:
            settings = None
            if delete_protected is not None:
                settings = UpdateEnvironmentRequestDataAttributesSettings(
                    delete_protected=delete_protected
                )

            environment = UpdateEnvironmentRequest(
                data=UpdateEnvironmentRequestData(
                    id=env_id,
                    type=EnvironmentRelationshipDataType.environments,
                    attributes=UpdateEnvironmentRequestDataAttributes(
                        description=description,
                        color=color,
                        settings=settings,
                    ),
                )
            )
        else:
            # env_id comes from environment.data.id if using advanced syntax
            env_id = environment.data.id

        team = self._get_team_slug()
        data = self._patch_sync(
            self._build_path(team, env_id),
            json=environment.model_dump(mode="json", exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        response = self._parse_model(EnvironmentResponse, data)
        return response.data

    def delete(self, env_id: str) -> None:
        """Delete an environment.

        Args:
            env_id: Environment ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        self._delete_sync(self._build_path(team, env_id))
