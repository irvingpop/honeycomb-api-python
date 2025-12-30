"""Auth endpoint models for API key metadata."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuthInfo(BaseModel):
    """v1 auth endpoint response - API key metadata."""

    id: str = Field(description="Unique identifier of the API key")
    type: str = Field(description="Key type: 'configuration' or 'ingest'")
    team_name: str = Field(description="Name of the team")
    team_slug: str = Field(description="URL-safe team identifier")
    environment_name: str = Field(description="Name of the environment")
    environment_slug: str = Field(description="URL-safe environment identifier")
    api_key_access: dict[str, Any] = Field(description="Key capabilities/permissions")
    time_to_live: str | None = Field(default=None, description="Expiration time (RFC3339)")

    model_config = {"extra": "allow"}


class AuthInfoV2(BaseModel):
    """v2 auth endpoint response - Management key metadata."""

    id: str = Field(description="Unique identifier of the management key")
    name: str = Field(description="Human-readable name")
    key_type: str = Field(description="Key type: 'management'")
    disabled: bool = Field(default=False, description="Whether the key is disabled")
    scopes: list[str] = Field(default_factory=list, description="Authorized scopes")
    team_id: str = Field(description="Team ID this key belongs to")
    team_name: str | None = Field(default=None, description="Team name")
    team_slug: str | None = Field(default=None, description="Team slug")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}

    @classmethod
    def from_jsonapi(cls, data: dict[str, Any]) -> "AuthInfoV2":
        """Parse from JSON:API format."""
        obj = data.get("data", data)
        attrs = obj.get("attributes", {})
        rels = obj.get("relationships", {})
        included = data.get("included", [])

        # Extract team info from relationships and included
        team_id = rels.get("team", {}).get("data", {}).get("id", "")
        team_name = None
        team_slug = None
        for inc in included:
            if inc.get("type") == "teams" and inc.get("id") == team_id:
                team_attrs = inc.get("attributes", {})
                team_name = team_attrs.get("name")
                team_slug = team_attrs.get("slug")
                break

        timestamps = attrs.get("timestamps", {})
        return cls(
            id=obj.get("id", ""),
            name=attrs.get("name", ""),
            key_type=attrs.get("key_type", "management"),
            disabled=attrs.get("disabled", False),
            scopes=attrs.get("scopes", []),
            team_id=team_id,
            team_name=team_name,
            team_slug=team_slug,
            created_at=timestamps.get("created_at"),
            updated_at=timestamps.get("updated_at"),
        )
