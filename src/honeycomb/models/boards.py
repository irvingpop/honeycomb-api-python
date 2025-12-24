"""Pydantic models for Honeycomb Boards."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BoardCreate(BaseModel):
    """Model for creating a new board."""

    name: str = Field(description="Human-readable name for the board")
    description: str | None = Field(default=None, description="Longer description")
    column_layout: str = Field(default="multi", description="Layout style: 'multi' or 'single'")
    style: str = Field(default="visual", description="Display style: 'visual' or 'list'")

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {
            "name": self.name,
            "column_layout": self.column_layout,
            "style": self.style,
        }

        if self.description:
            data["description"] = self.description

        return data


class Board(BaseModel):
    """A Honeycomb board (response model)."""

    id: str = Field(description="Unique identifier")
    name: str = Field(description="Human-readable name")
    description: str | None = Field(default=None, description="Longer description")
    column_layout: str = Field(default="multi", description="Layout style")
    style: str = Field(default="visual", description="Display style")
    queries: list[dict] | None = Field(default=None, description="Board queries")
    links: dict | None = Field(default=None, description="Board links")

    model_config = {"extra": "allow"}
