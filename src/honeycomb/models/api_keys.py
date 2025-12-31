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
    permissions: dict[str, bool] | None = Field(
        default=None,
        description=(
            "Permissions for configuration keys (REQUIRED for configuration type). "
            "Available permissions: 'create_datasets', 'send_events', 'manage_markers', "
            "'manage_triggers', 'manage_boards', 'run_queries', 'manage_columns', "
            "'manage_slos', 'manage_recipients', 'manage_privateBoards', "
            "'read_service_maps', 'visible_team_members'. "
            "Ignored for ingest keys."
        ),
    )

    def to_jsonapi(self) -> dict[str, Any]:
        """Convert to JSON:API format for API request."""
        attributes: dict[str, Any] = {
            "name": self.name,
            "key_type": self.key_type.value,
            "disabled": self.disabled,
        }

        # Add permissions for configuration keys
        if self.permissions is not None:
            attributes["permissions"] = self.permissions

        return {
            "data": {
                "type": "api-keys",
                "attributes": attributes,
                "relationships": {
                    "environment": {"data": {"type": "environments", "id": self.environment_id}}
                },
            }
        }


class ApiKeyUpdate(BaseModel):
    """Model for updating an API key."""

    name: str | None = Field(default=None, description="New name for the API key")
    disabled: bool | None = Field(default=None, description="Enable/disable the key")

    def to_jsonapi(self, key_id: str) -> dict[str, Any]:
        """Convert to JSON:API format for API request."""
        attributes: dict[str, Any] = {}
        if self.name is not None:
            attributes["name"] = self.name
        if self.disabled is not None:
            attributes["disabled"] = self.disabled

        return {
            "data": {
                "id": key_id,
                "type": "api-keys",
                "attributes": attributes,
            }
        }


class ApiKey(BaseModel):
    """A Honeycomb API key (response model)."""

    id: str = Field(description="Unique identifier (includes key prefix)")
    name: str = Field(description="Name of the API key")
    key_type: ApiKeyType = Field(description="Type of API key")
    environment_id: str | None = Field(default=None, description="Environment ID")
    disabled: bool = Field(default=False, description="Whether key is disabled")
    permissions: dict[str, bool] | None = Field(
        default=None, description="Permissions for configuration keys"
    )
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
            permissions=attributes.get("permissions"),
            secret=attributes.get("secret"),
            created_at=attributes.get("created_at"),
            updated_at=attributes.get("updated_at"),
        )
