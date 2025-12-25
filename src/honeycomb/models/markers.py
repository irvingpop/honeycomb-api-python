"""Pydantic models for Honeycomb Markers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MarkerCreate(BaseModel):
    """Model for creating a new marker."""

    message: str = Field(description="Message to describe this marker")
    type: str = Field(description="Groups similar markers (e.g., 'deploy')")
    start_time: int | None = Field(
        default=None,
        description="Unix timestamp when marker should be placed (defaults to now)",
    )
    end_time: int | None = Field(
        default=None, description="Unix timestamp for end of marker (for time ranges)"
    )
    url: str | None = Field(default=None, description="Target URL for the marker")

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {"message": self.message, "type": self.type}
        if self.start_time is not None:
            data["start_time"] = self.start_time
        if self.end_time is not None:
            data["end_time"] = self.end_time
        if self.url:
            data["url"] = self.url
        return data


class Marker(BaseModel):
    """A Honeycomb marker (response model)."""

    id: str = Field(description="Unique identifier (6 character hex)")
    message: str = Field(description="Message describing this marker")
    type: str = Field(description="Groups similar markers")
    start_time: int = Field(description="Unix timestamp when marker is placed")
    end_time: int | None = Field(default=None, description="Unix timestamp for end of marker")
    url: str | None = Field(default=None, description="Target URL for the marker")
    color: str | None = Field(default=None, description="Hex color code (from marker settings)")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}


class MarkerSettingCreate(BaseModel):
    """Model for creating a new marker setting."""

    type: str = Field(description="Marker type to configure")
    color: str = Field(description="Hex color code (e.g., '#F96E11')")

    def model_dump_for_api(self) -> dict[str, str]:
        """Serialize for API request."""
        return {"type": self.type, "color": self.color}


class MarkerSetting(BaseModel):
    """A Honeycomb marker setting (response model)."""

    id: str = Field(description="Unique identifier")
    type: str = Field(description="Marker type")
    color: str = Field(description="Hex color code")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}
