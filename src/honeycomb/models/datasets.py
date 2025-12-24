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


class Dataset(BaseModel):
    """A Honeycomb dataset (response model)."""

    name: str = Field(description="Dataset name")
    slug: str = Field(description="URL-safe identifier")
    description: str | None = Field(default=None, description="Longer description")
    expand_json_depth: int = Field(default=0, description="JSON expansion depth")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    last_written_at: datetime | None = Field(
        default=None, description="Last event written timestamp"
    )
    regular_columns_count: int | None = Field(default=None, description="Number of regular columns")

    model_config = {"extra": "allow"}
