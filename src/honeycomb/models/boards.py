"""Pydantic models for Honeycomb Boards."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BoardCreate(BaseModel):
    """Model for creating a new board.

    The Honeycomb Board API only supports flexible boards.
    """

    name: str = Field(description="Human-readable name for the board")
    description: str | None = Field(default=None, description="Longer description")
    type: str = Field(
        default="flexible",
        description="Board type: only 'flexible' is supported",
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {
            "name": self.name,
            "type": self.type,
        }

        if self.description:
            data["description"] = self.description

        return data


class Board(BaseModel):
    """A Honeycomb board (response model)."""

    id: str = Field(description="Unique identifier")
    name: str = Field(description="Human-readable name")
    description: str | None = Field(default=None, description="Longer description")
    type: str = Field(default="flexible", description="Board type")
    panels: list[dict] | None = Field(default=None, description="Board panels")
    links: dict | None = Field(default=None, description="Board links")
    layout_generation: str | None = Field(
        default=None,
        description="Layout mode: 'auto' or 'manual'",
    )
    tags: list[dict] | None = Field(default=None, description="Board tags")

    model_config = {"extra": "allow"}
