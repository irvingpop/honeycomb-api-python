"""Pydantic models for Honeycomb API Keys (v2 team-scoped).

Re-exports generated models that match JSON:API structure exactly.
"""

from typing import Any

from honeycomb._generated_models import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListResponse,
    ApiKeyObjectType,
    ApiKeyResponse,
    ApiKeyUpdateRequest,
    ConfigurationKey,
    IngestKey,
)
from honeycomb._generated_models import (
    ApiKeyObject as _ApiKeyObjectGenerated,
)


class ApiKeyObject(_ApiKeyObjectGenerated):
    """API Key object with property accessors to hide JSON:API structure.

    Extends generated ApiKeyObject to provide convenient access to nested attributes
    and relationships without requiring .attributes.field or .relationships.field.
    """

    @property
    def name(self) -> str | None:
        """Get API key name from attributes."""
        return self.attributes.name if self.attributes else None

    @property
    def key_type(self) -> Any:
        """Get API key type from attributes."""
        return self.attributes.key_type if self.attributes else None

    @property
    def disabled(self) -> bool | None:
        """Get disabled status from attributes."""
        return self.attributes.disabled if self.attributes else None

    @property
    def permissions(self) -> Any:
        """Get permissions from attributes."""
        return self.attributes.permissions if self.attributes else None

    @property
    def timestamps(self) -> Any:
        """Get timestamps from attributes."""
        return self.attributes.timestamps if self.attributes else None

    @property
    def time_to_live(self) -> str | None:
        """Get time_to_live from attributes (ingest keys only)."""
        return getattr(self.attributes, "time_to_live", None) if self.attributes else None

    @property
    def secret(self) -> str | None:
        """Get secret from attributes (only available during creation)."""
        return getattr(self.attributes, "secret", None) if self.attributes else None

    @property
    def environment_id(self) -> str | None:
        """Get environment ID from relationships."""
        if self.relationships and self.relationships.environment:
            return self.relationships.environment.data.id
        return None

    @property
    def creator_id(self) -> str | None:
        """Get creator user ID from relationships."""
        if self.relationships and self.relationships.creator:
            return self.relationships.creator.data.id
        return None

    @property
    def editor_id(self) -> str | None:
        """Get editor user ID from relationships."""
        if self.relationships and self.relationships.editor:
            return self.relationships.editor.data.id
        return None


# Convenience type aliases
ApiKeyType = ApiKeyObjectType
ApiKey = ApiKeyObject  # Convenience alias for ApiKeyObject
ApiKeyCreate = ApiKeyCreateRequest
ApiKeyUpdate = ApiKeyUpdateRequest

__all__ = [
    "ApiKey",  # Convenience alias
    "ApiKeyCreate",  # Convenience alias
    "ApiKeyUpdate",  # Convenience alias
    "ApiKeyCreateRequest",
    "ApiKeyCreateResponse",
    "ApiKeyListResponse",
    "ApiKeyObject",
    "ApiKeyObjectType",
    "ApiKeyResponse",
    "ApiKeyUpdateRequest",
    "ApiKeyType",
    "ConfigurationKey",
    "IngestKey",
]
