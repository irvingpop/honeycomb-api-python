"""Pydantic models for Honeycomb Boards."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from .query_builder import FilterOp


class BoardCreate(BaseModel):
    """Model for creating a new board.

    The Honeycomb Board API only supports flexible boards.

    Attributes:
        name: Human-readable name (1-255 chars)
        description: Longer description (0-1024 chars)
        type: Board type (only "flexible" is supported)
        panels: Array of board panels (queries, SLOs, text)
        layout_generation: Layout mode - "auto" or "manual" (default: "manual")
        tags: Array of tag objects (max 10 items)
        preset_filters: Array of preset filter objects
    """

    name: str = Field(description="Human-readable name for the board (1-255 chars)")
    description: str | None = Field(default=None, description="Longer description (0-1024 chars)")
    type: str = Field(
        default="flexible",
        description="Board type: only 'flexible' is supported",
    )
    panels: list[dict[str, Any]] | None = Field(
        default=None,
        description="Array of board panels (queries, SLOs, text)",
    )
    layout_generation: Literal["auto", "manual"] = Field(
        default="manual",
        description="Layout mode: 'auto' or 'manual'",
    )
    tags: list[dict[str, str]] | None = Field(
        default=None,
        description="Array of tag objects (max 10)",
    )
    preset_filters: list[dict[str, str]] | None = Field(
        default=None,
        description="Array of preset filter objects",
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {
            "name": self.name,
            "type": self.type,
            "layout_generation": self.layout_generation,
        }

        if self.description:
            data["description"] = self.description

        if self.panels:
            data["panels"] = self.panels

        if self.tags:
            data["tags"] = self.tags

        if self.preset_filters:
            data["preset_filters"] = self.preset_filters

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


# =============================================================================
# Board Views
# =============================================================================


class BoardViewFilter(BaseModel):
    """Filter for board views.

    Uses the same FilterOp enum as QueryBuilder for consistency.

    Attributes:
        column: Column name to filter on
        operation: Filter operation to apply
        value: Filter value (optional for exists/does-not-exist operations)

    Example:
        >>> BoardViewFilter(column="status", operation=FilterOp.EQUALS, value="active")
        >>> BoardViewFilter(column="error", operation=FilterOp.EXISTS)
    """

    column: str = Field(description="Column name to filter on")
    operation: FilterOp = Field(description="Filter operation")
    value: Any | None = Field(
        default=None,
        description="Filter value (optional for exists/does-not-exist)",
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {
            "column": self.column,
            "operation": self.operation.value,
        }
        if self.value is not None:
            data["value"] = self.value
        return data


class BoardViewCreate(BaseModel):
    """Model for creating or updating a board view.

    Attributes:
        name: View name
        filters: List of filters to apply to this view

    Example:
        >>> BoardViewCreate(
        ...     name="Active Services",
        ...     filters=[
        ...         BoardViewFilter(column="status", operation=FilterOp.EQUALS, value="active")
        ...     ]
        ... )
    """

    name: str = Field(description="View name")
    filters: list[BoardViewFilter] = Field(
        default_factory=list,
        description="List of filters",
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        return {
            "name": self.name,
            "filters": [f.model_dump_for_api() for f in self.filters],
        }


class BoardView(BaseModel):
    """A board view (response model).

    Board views are filtered perspectives on a board, with each board
    supporting up to 50 views maximum.

    Attributes:
        id: Unique identifier
        name: View name
        filters: List of filters applied to this view
    """

    id: str = Field(description="Unique identifier")
    name: str = Field(description="View name")
    filters: list[BoardViewFilter] = Field(
        default_factory=list,
        description="Filters",
    )

    model_config = {"extra": "allow"}
