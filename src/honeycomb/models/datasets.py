"""Pydantic models for Honeycomb Datasets."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DatasetCreate(BaseModel):
    """Model for creating a new dataset."""

    name: str = Field(description="Human-readable name for the dataset")
    description: str | None = Field(default=None, description="Longer description")
    expand_json_depth: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Depth to expand JSON fields (0-10)",
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {
            "name": self.name,
        }

        if self.description:
            data["description"] = self.description

        if self.expand_json_depth > 0:
            data["expand_json_depth"] = self.expand_json_depth

        return data


class DatasetUpdate(BaseModel):
    """Model for updating an existing dataset."""

    name: str | None = Field(default=None, description="Human-readable name for the dataset")
    description: str | None = Field(default=None, description="Longer description")
    expand_json_depth: int | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Depth to expand JSON fields (0-10)",
    )
    delete_protected: bool | None = Field(
        default=None, description="If true, the dataset cannot be deleted"
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {}

        if self.name is not None:
            data["name"] = self.name

        if self.description is not None:
            data["description"] = self.description

        if self.expand_json_depth is not None:
            data["expand_json_depth"] = self.expand_json_depth

        if self.delete_protected is not None:
            data["settings"] = {"delete_protected": self.delete_protected}

        return data


class Dataset(BaseModel):
    """A Honeycomb dataset (response model)."""

    name: str = Field(description="Dataset name")
    slug: str = Field(description="URL-safe identifier")
    description: str | None = Field(default=None, description="Longer description")
    expand_json_depth: int = Field(default=0, description="JSON expansion depth")
    delete_protected: bool = Field(default=False, description="If true, dataset cannot be deleted")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    last_written_at: datetime | None = Field(
        default=None, description="Last event written timestamp"
    )
    regular_columns_count: int | None = Field(default=None, description="Number of regular columns")

    model_config = {"extra": "allow"}

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> Dataset:
        """Parse from API response format, extracting settings."""
        settings = data.pop("settings", {}) if isinstance(data.get("settings"), dict) else {}
        delete_protected = settings.get("delete_protected", False)
        return cls(delete_protected=delete_protected, **data)
