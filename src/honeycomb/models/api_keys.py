"""Pydantic models for Honeycomb API Keys (v2 team-scoped)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ApiKeyType(str, Enum):
    """API key types."""

    INGEST = "ingest"
    CONFIGURATION = "configuration"


class ApiKeyCreate(BaseModel):
    """Model for creating a new API key."""

    name: str = Field(description="Name for the API key")
    key_type: ApiKeyType = Field(description="Type of API key")
    environment_id: str = Field(description="Environment ID this key belongs to")
    disabled: bool = Field(default=False, description="Whether key is disabled")

    def to_jsonapi(self) -> dict[str, Any]:
        """Convert to JSON:API format for API request."""
        return {
            "data": {
                "type": "api-keys",
                "attributes": {
                    "name": self.name,
                    "key_type": self.key_type.value,
                    "disabled": self.disabled,
                },
                "relationships": {
                    "environment": {"data": {"type": "environments", "id": self.environment_id}}
                },
            }
        }


class ApiKey(BaseModel):
    """A Honeycomb API key (response model)."""

    id: str = Field(description="Unique identifier (includes key prefix)")
    name: str = Field(description="Name of the API key")
    key_type: ApiKeyType = Field(description="Type of API key")
    environment_id: str | None = Field(default=None, description="Environment ID")
    disabled: bool = Field(default=False, description="Whether key is disabled")
    secret: str | None = Field(
        default=None, description="Key secret (only available during creation)"
    )
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}

    @classmethod
    def from_jsonapi(cls, data: dict[str, Any]) -> ApiKey:
        """Parse from JSON:API format."""
        obj = data.get("data", data)  # Handle both wrapped and unwrapped
        attributes = obj.get("attributes", {})
        relationships = obj.get("relationships", {})

        env_id = None
        if "environment" in relationships:
            env_data = relationships["environment"].get("data", {})
            env_id = env_data.get("id")

        return cls(
            id=obj.get("id", ""),
            name=attributes.get("name", ""),
            key_type=attributes.get("key_type", "ingest"),
            environment_id=env_id,
            disabled=attributes.get("disabled", False),
            secret=attributes.get("secret"),
            created_at=attributes.get("created_at"),
            updated_at=attributes.get("updated_at"),
        )
