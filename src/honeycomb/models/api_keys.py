"""Pydantic models for Honeycomb API Keys (v2 team-scoped).

Re-exports generated models that match JSON:API structure exactly.
"""

from honeycomb._generated_models import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListResponse,
    ApiKeyObject,
    ApiKeyObjectType,
    ApiKeyResponse,
    ApiKeyUpdateRequest,
    ConfigurationKey,
    IngestKey,
)

# Re-export for convenience
ApiKeyType = ApiKeyObjectType

__all__ = [
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
