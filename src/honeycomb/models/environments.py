"""Pydantic models for Honeycomb Environments (v2 team-scoped)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EnvironmentColor(str, Enum):
    """Environment display colors."""

    BLUE = "blue"
    GREEN = "green"
    GOLD = "gold"
    RED = "red"
    PURPLE = "purple"
    LIGHT_BLUE = "lightBlue"
    LIGHT_GREEN = "lightGreen"
    LIGHT_GOLD = "lightGold"
    LIGHT_RED = "lightRed"
    LIGHT_PURPLE = "lightPurple"


class EnvironmentCreate(BaseModel):
    """Model for creating a new environment."""

    name: str = Field(description="Name for the environment", max_length=255)
    description: str | None = Field(
        default=None, description="Description of the environment", max_length=255
    )
    color: EnvironmentColor | None = Field(default=None, description="Display color")

    def to_jsonapi(self) -> dict[str, Any]:
        """Convert to JSON:API format for API request."""
        attributes: dict[str, Any] = {"name": self.name}
        if self.description:
            attributes["description"] = self.description
        if self.color:
            attributes["color"] = self.color.value

        return {"data": {"type": "environments", "attributes": attributes}}


class EnvironmentUpdate(BaseModel):
    """Model for updating an environment."""

    description: str | None = Field(default=None, description="Description", max_length=255)
    color: EnvironmentColor | None = Field(default=None, description="Display color")
    delete_protected: bool | None = Field(
        default=None, description="If true, environment cannot be deleted"
    )

    def to_jsonapi(self, env_id: str) -> dict[str, Any]:
        """Convert to JSON:API format for API request."""
        attributes: dict[str, Any] = {}
        if self.description is not None:
            attributes["description"] = self.description
        if self.color:
            attributes["color"] = self.color.value
        if self.delete_protected is not None:
            attributes["settings"] = {"delete_protected": self.delete_protected}

        return {"data": {"id": env_id, "type": "environments", "attributes": attributes}}


class Environment(BaseModel):
    """A Honeycomb environment (response model)."""

    id: str = Field(description="Unique identifier")
    name: str = Field(description="Name of the environment")
    slug: str = Field(description="URL-friendly slug")
    description: str | None = Field(default=None, description="Description")
    color: EnvironmentColor | None = Field(default=None, description="Display color")
    delete_protected: bool = Field(default=False, description="Whether delete-protected")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}

    @classmethod
    def from_jsonapi(cls, data: dict[str, Any]) -> Environment:
        """Parse from JSON:API format."""
        obj = data.get("data", data)  # Handle both wrapped and unwrapped
        attributes = obj.get("attributes", {})
        settings = attributes.get("settings", {})

        return cls(
            id=obj.get("id", ""),
            name=attributes.get("name", ""),
            slug=attributes.get("slug", ""),
            description=attributes.get("description"),
            color=attributes.get("color"),
            delete_protected=settings.get("delete_protected", False),
            created_at=attributes.get("created_at"),
            updated_at=attributes.get("updated_at"),
        )
