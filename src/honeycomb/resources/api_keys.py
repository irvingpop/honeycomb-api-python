"""API Keys resource for Honeycomb API (v2 team-scoped)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

from honeycomb._generated_models import ApiKeyCreateResponseData

from ..models.api_keys import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListResponse,
    ApiKeyObject,
    ApiKeyResponse,
    ApiKeyUpdateRequest,
    ConfigurationKey,
    IngestKey,
)
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
        ...     # Create uses JSON:API format - see models.api_keys for structure
        ...     key = await client.api_keys.create_async(create_request)

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
        from honeycomb.models.auth import Auth, AuthV2Response

        auth_info = await self._client.auth.get_async()

        # Extract team slug based on auth response type
        if isinstance(auth_info, AuthV2Response):
            # v2 management key - extract team slug from included resources
            if not auth_info.included:
                raise ValueError(
                    "Cannot auto-detect team slug. Please provide team parameter explicitly."
                )
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
                raise ValueError(
                    "Cannot auto-detect team slug. Please provide team parameter explicitly."
                )
        elif isinstance(auth_info, Auth):
            # v1 API key - team slug is in nested team object
            team_slug = auth_info.team.slug
            if not team_slug:
                raise ValueError(
                    "Cannot auto-detect team slug. Please provide team parameter explicitly."
                )
        else:
            raise ValueError("Unexpected auth response type")

        self._cached_team_slug = team_slug
        return team_slug

    def _get_team_slug(self, team: str | None = None) -> str:
        """Get team slug (sync), auto-detecting from auth if not provided."""
        if team:
            return team

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
                raise ValueError(
                    "Cannot auto-detect team slug. Please provide team parameter explicitly."
                )
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
                raise ValueError(
                    "Cannot auto-detect team slug. Please provide team parameter explicitly."
                )
        elif isinstance(auth_info, Auth):
            # v1 API key - team slug is in nested team object
            team_slug = auth_info.team.slug
            if not team_slug:
                raise ValueError(
                    "Cannot auto-detect team slug. Please provide team parameter explicitly."
                )
        else:
            raise ValueError("Unexpected auth response type")

        self._cached_team_slug = team_slug
        return team_slug

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

    async def list_async(self, key_type: str | None = None) -> list[ApiKeyObject]:
        """List all API keys for the authenticated team (async).

        Automatically paginates through all results. For teams with many API keys,
        this may result in multiple API requests.

        Args:
            key_type: Optional filter by key type ('ingest' or 'configuration').

        Returns:
            List of ApiKeyObject objects.

        Note:
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        team = await self._get_team_slug_async()
        results: list[ApiKeyObject] = []
        cursor: str | None = None
        path = self._build_path(team)

        while True:
            params = self._build_params(key_type=key_type, cursor=cursor)
            data = await self._get_async(path, params=params)

            # Parse JSON:API response
            if isinstance(data, dict) and "data" in data:
                response = self._parse_model(ApiKeyListResponse, data)
                # Convert generated ApiKeyObject instances to our extended version
                for item in response.data:
                    results.append(ApiKeyObject.model_validate(item.model_dump()))

                # Check for next page
                next_link = response.links.next if response.links else None
                cursor = self._extract_cursor(next_link)
                if not cursor:
                    break
            else:
                break

        return results

    async def get_async(self, key_id: str) -> ApiKeyObject:
        """Get a specific API key (async).

        Args:
            key_id: API Key ID.

        Returns:
            ApiKeyObject.
        """
        team = await self._get_team_slug_async()
        data = await self._get_async(self._build_path(team, key_id))
        response = self._parse_model(ApiKeyResponse, data)
        # Convert generated ApiKeyObject to our extended version
        return ApiKeyObject.model_validate(response.data.model_dump())

    async def create_async(
        self,
        api_key: ApiKeyCreateRequest | ConfigurationKey | IngestKey,
        environment_id: str | None = None,
    ) -> ApiKeyCreateResponseData:
        """Create a new API key (async).

        Args:
            api_key: Either a full ApiKeyCreateRequest (JSON:API format) or
                    ConfigurationKey/IngestKey (convenience - auto-wrapped).
            environment_id: Environment ID (required when using ConfigurationKey/IngestKey).

        Returns:
            Created API key with secret in attributes (save it immediately!).

        Examples:
            >>> # Simple syntax with ConfigurationKey
            >>> from honeycomb import ConfigurationKey
            >>> key = await client.api_keys.create_async(
            ...     api_key=ConfigurationKey(
            ...         key_type="configuration",
            ...         name="My Key",
            ...         permissions={"send_events": True}
            ...     ),
            ...     environment_id="hcaen_123"
            ... )
        """
        from honeycomb._generated_models import (
            ApiKeyCreateRequestData,
            ApiKeyCreateRequestDataRelationships,
            ApiKeyObjectType,
            EnvironmentRelationship,
            EnvironmentRelationshipData,
            EnvironmentRelationshipDataType,
        )

        # Auto-wrap ConfigurationKey or IngestKey in JSON:API structure
        if isinstance(api_key, (ConfigurationKey, IngestKey)):
            if not environment_id:
                raise ValueError("environment_id is required when using ConfigurationKey/IngestKey")

            # Build JSON:API request
            api_key_request = ApiKeyCreateRequest(
                data=ApiKeyCreateRequestData(
                    type=ApiKeyObjectType.api_keys,
                    attributes=api_key,
                    relationships=ApiKeyCreateRequestDataRelationships(
                        environment=EnvironmentRelationship(
                            data=EnvironmentRelationshipData(
                                id=environment_id,
                                type=EnvironmentRelationshipDataType.environments,
                            )
                        )
                    ),
                )
            )
            api_key = api_key_request

        team = await self._get_team_slug_async()
        data = await self._post_async(
            self._build_path(team),
            json=api_key.model_dump(mode="json", exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        response = self._parse_model(ApiKeyCreateResponse, data)
        # Return create response data directly - attributes includes secret (only available at creation)
        return response.data

    async def update_async(
        self,
        key_id: str,
        api_key: ApiKeyUpdateRequest | None = None,
        *,
        name: str | None = None,
        disabled: bool | None = None,
        permissions: dict[str, bool] | None = None,
    ) -> ApiKeyObject:
        """Update an existing API key (async).

        Args:
            key_id: API key ID to update.
            api_key: Full JSON:API update request (advanced usage) or update attributes.
            name: New name (convenience parameter).
            disabled: Enable/disable the key (convenience parameter).
            permissions: Updated permissions dict (convenience parameter).

        Returns:
            Updated ApiKeyObject.

        Examples:
            >>> # Simple syntax
            >>> key = await client.api_keys.update_async(
            ...     key_id="hcalk_123",
            ...     name="Updated Key Name",
            ...     disabled=True
            ... )
        """
        from honeycomb._generated_models import (
            ApiKeyObjectType,
            ConfigurationKeyUpdate,
            ConfigurationKeyUpdateAttributes,
            ConfigurationKeyUpdateAttributesPermissions,
            IngestKeyUpdate,
            IngestKeyUpdateAttributes,
        )

        team = await self._get_team_slug_async()

        # Build request from convenience parameters if not provided
        if api_key is None:
            # Get existing key to determine type
            existing = await self.get_async(key_id)

            update_data: ConfigurationKeyUpdate | IngestKeyUpdate
            if existing.key_type == "configuration":
                perms = None
                if permissions is not None:
                    perms = ConfigurationKeyUpdateAttributesPermissions(**permissions)

                update_data = ConfigurationKeyUpdate(
                    id=key_id,
                    type=ApiKeyObjectType.api_keys,
                    attributes=ConfigurationKeyUpdateAttributes(
                        name=name,
                        disabled=disabled,
                        permissions=perms,
                    ),
                )
            else:  # ingest key
                update_data = IngestKeyUpdate(
                    id=key_id,
                    type=ApiKeyObjectType.api_keys,
                    attributes=IngestKeyUpdateAttributes(
                        name=name,
                        disabled=disabled,
                    ),
                )

            api_key = ApiKeyUpdateRequest(data=update_data)
        else:
            # Extract key_id from the request data if using full JSON:API request
            key_id = api_key.data.id

        data = await self._patch_async(
            self._build_path(team, key_id),
            json=api_key.model_dump(mode="json", exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        response = self._parse_model(ApiKeyResponse, data)
        # Convert generated ApiKeyObject to our extended version
        return ApiKeyObject.model_validate(response.data.model_dump())

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

    def list(self, key_type: str | None = None) -> list[ApiKeyObject]:
        """List all API keys for the authenticated team.

        Automatically paginates through all results. For teams with many API keys,
        this may result in multiple API requests.

        Args:
            key_type: Optional filter by key type ('ingest' or 'configuration').

        Returns:
            List of ApiKeyObject objects.

        Note:
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")

        team = self._get_team_slug()
        results: list[ApiKeyObject] = []
        cursor: str | None = None
        path = self._build_path(team)

        while True:
            params = self._build_params(key_type=key_type, cursor=cursor)
            data = self._get_sync(path, params=params)

            # Parse JSON:API response
            if isinstance(data, dict) and "data" in data:
                response = self._parse_model(ApiKeyListResponse, data)
                # Convert generated ApiKeyObject instances to our extended version
                for item in response.data:
                    results.append(ApiKeyObject.model_validate(item.model_dump()))

                # Check for next page
                next_link = response.links.next if response.links else None
                cursor = self._extract_cursor(next_link)
                if not cursor:
                    break
            else:
                break

        return results

    def get(self, key_id: str) -> ApiKeyObject:
        """Get a specific API key.

        Args:
            key_id: API Key ID.

        Returns:
            ApiKeyObject.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        data = self._get_sync(self._build_path(team, key_id))
        response = self._parse_model(ApiKeyResponse, data)
        # Convert generated ApiKeyObject to our extended version
        return ApiKeyObject.model_validate(response.data.model_dump())

    def create(
        self,
        api_key: ApiKeyCreateRequest | ConfigurationKey | IngestKey,
        environment_id: str | None = None,
    ) -> ApiKeyCreateResponseData:
        """Create a new API key.

        Args:
            api_key: Either a full ApiKeyCreateRequest (JSON:API format) or
                    ConfigurationKey/IngestKey (convenience - auto-wrapped).
            environment_id: Environment ID (required when using ConfigurationKey/IngestKey).

        Returns:
            Created API key with secret in attributes (save it immediately!).
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")

        from honeycomb._generated_models import (
            ApiKeyCreateRequestData,
            ApiKeyCreateRequestDataRelationships,
            ApiKeyObjectType,
            EnvironmentRelationship,
            EnvironmentRelationshipData,
            EnvironmentRelationshipDataType,
        )

        # Auto-wrap ConfigurationKey or IngestKey in JSON:API structure
        if isinstance(api_key, (ConfigurationKey, IngestKey)):
            if not environment_id:
                raise ValueError("environment_id is required when using ConfigurationKey/IngestKey")

            # Build JSON:API request
            api_key_request = ApiKeyCreateRequest(
                data=ApiKeyCreateRequestData(
                    type=ApiKeyObjectType.api_keys,
                    attributes=api_key,
                    relationships=ApiKeyCreateRequestDataRelationships(
                        environment=EnvironmentRelationship(
                            data=EnvironmentRelationshipData(
                                id=environment_id,
                                type=EnvironmentRelationshipDataType.environments,
                            )
                        )
                    ),
                )
            )
            api_key = api_key_request

        team = self._get_team_slug()
        data = self._post_sync(
            self._build_path(team),
            json=api_key.model_dump(mode="json", exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        response = self._parse_model(ApiKeyCreateResponse, data)
        # Return create response data directly - attributes includes secret (only available at creation)
        return response.data

    def update(self, api_key: ApiKeyUpdateRequest) -> ApiKeyObject:
        """Update an existing API key.

        Args:
            api_key: API key update request (JSON:API format, includes key_id in data.id).

        Returns:
            Updated ApiKeyObject.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        # Extract key_id from the request data
        key_id = api_key.data.id if hasattr(api_key.data, "id") else None
        if not key_id:
            raise ValueError("ApiKeyUpdateRequest must include data.id")

        data = self._patch_sync(
            self._build_path(team, key_id),
            json=api_key.model_dump(mode="json", exclude_none=True, by_alias=True),
            headers={"Content-Type": "application/vnd.api+json"},
        )
        response = self._parse_model(ApiKeyResponse, data)
        # Convert generated ApiKeyObject to our extended version
        return ApiKeyObject.model_validate(response.data.model_dump())

    def delete(self, key_id: str) -> None:
        """Delete an API key.

        Args:
            key_id: API Key ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        team = self._get_team_slug()
        self._delete_sync(self._build_path(team, key_id))
