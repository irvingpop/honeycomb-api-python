"""Pydantic models for Honeycomb Boards."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated

from pydantic import Field, model_validator

from honeycomb._generated_models import Board as _BoardGenerated
from honeycomb._generated_models import (
    BoardLayoutGeneration,
    BoardPanelPosition,
    BoardQueryVisualizationSettings,
    BoardQueryVisualizationSettingsChart,
    BoardType,
    BoardViewFilterBoardViewFilterOperation,
)
from honeycomb._generated_models import BoardViewResponse as _BoardViewResponseGenerated
from honeycomb._generated_models import CreateBoardViewRequest as _CreateBoardViewRequestGenerated
from honeycomb._generated_models import QueryPanel as _QueryPanelGenerated
from honeycomb._generated_models import QueryPanelQueryPanel as _QueryPanelQueryPanelGenerated
from honeycomb._generated_models import SLOPanel as _SLOPanelGenerated
from honeycomb._generated_models import SLOPanelSloPanel as _SLOPanelSloPanelGenerated
from honeycomb._generated_models import TextPanel as _TextPanelGenerated
from honeycomb._generated_models import TextPanelTextPanel as _TextPanelTextPanelGenerated

# Alias the long generated enum name to something shorter
BoardViewFilterOperation = BoardViewFilterBoardViewFilterOperation


# Wrapper models to handle API inconsistencies (some boards return panels without data)
class QueryPanelQueryPanel(_QueryPanelQueryPanelGenerated):
    """Query panel query panel wrapper with validation.

    Validates that query_annotation_id is not mistakenly set to the query_id.
    """

    @model_validator(mode="after")
    def validate_annotation_id(self) -> QueryPanelQueryPanel:
        """Validate that annotation_id is not the same as query_id.

        This catches a common mistake where users pass the query ID as the annotation ID.
        Query annotations are separate objects that provide metadata for queries.
        """
        if self.query_id and self.query_annotation_id == self.query_id:
            raise ValueError(
                f"query_annotation_id cannot be the same as query_id ('{self.query_id}'). "
                "Query annotations are separate metadata objects. "
                "Create a query annotation first using client.query_annotations.create_async() "
                "or use BoardBuilder with QueryBuilder to create them automatically."
            )
        return self


class QueryPanel(_QueryPanelGenerated):
    """Query panel wrapper that makes query_panel optional for broken API responses."""

    query_panel: QueryPanelQueryPanel | None = None  # type: ignore[assignment]


class SLOPanel(_SLOPanelGenerated):
    """SLO panel wrapper that makes slo_panel optional for broken API responses."""

    slo_panel: _SLOPanelSloPanelGenerated | None = None  # type: ignore[assignment]


class TextPanel(_TextPanelGenerated):
    """Text panel wrapper that makes text_panel optional for broken API responses."""

    text_panel: _TextPanelTextPanelGenerated | None = None  # type: ignore[assignment]


# Re-export generated types for public API
__all__ = [
    "Board",
    "BoardCreate",
    "BoardType",
    "BoardLayoutGeneration",
    "BoardPanelPosition",
    "BoardQueryVisualizationSettings",
    "BoardQueryVisualizationSettingsChart",
    "QueryPanel",
    "QueryPanelQueryPanel",
    "SLOPanel",
    "TextPanel",
    "BoardView",
    "BoardViewCreate",
    "BoardViewFilter",
    "BoardViewFilterOperation",
]


class BoardCreate(_BoardGenerated):
    """Board creation model.

    Uses the generated Board model which has optional id/links.
    Pydantic will exclude unset fields during serialization.

    The Honeycomb Board API only supports flexible boards.

    Example:
        >>> from honeycomb.models.boards import BoardCreate
        >>> board = BoardCreate(
        ...     name="My Board",
        ...     description="A test board",
        ...     panels=[...],  # QueryPanel, SLOPanel, or TextPanel objects
        ... )
    """

    # Override to add defaults and descriptions for Claude tool schema
    type: BoardType = Field(
        default=BoardType.flexible,
        description="Board type (only 'flexible' is currently supported)",
    )
    panels: (
        list[Annotated[QueryPanel | SLOPanel | TextPanel, Field(discriminator="type")]] | None
    ) = Field(  # type: ignore[assignment]
        default=None,
        description="Array of board panels (query panels, SLO panels, or text panels)",
    )


class Board(_BoardGenerated):
    """Honeycomb board (response model).

    Extends generated Board with convenience methods.
    Overrides panels field to use wrapper types that handle incomplete API responses.
    """

    model_config = {"extra": "allow"}

    # Override panels to use wrapper types with optional nested data
    panels: (
        list[Annotated[QueryPanel | SLOPanel | TextPanel, Field(discriminator="type")]] | None
    ) = None  # type: ignore[assignment]


# =============================================================================
# Board Views
# =============================================================================


# Import generated BoardViewFilter to wrap it
from honeycomb._generated_models import BoardViewFilter as _BoardViewFilterGenerated  # noqa: E402


class BoardViewFilter(_BoardViewFilterGenerated):
    """Board view filter.

    Extends generated filter with strict validation (extra="forbid").
    """

    model_config = {"extra": "forbid"}


class BoardViewCreate(_CreateBoardViewRequestGenerated):
    """Board view creation/update model.

    Board views are filtered perspectives on a board, with each board
    supporting up to 50 views maximum.

    Example:
        >>> from honeycomb.models.boards import BoardViewCreate, BoardViewFilter, BoardViewFilterOperation
        >>> view = BoardViewCreate(
        ...     name="Active Services",
        ...     filters=[
        ...         BoardViewFilter(
        ...             column="status",
        ...             operation=BoardViewFilterOperation.EQUALS,
        ...             value="active"
        ...         )
        ...     ]
        ... )
    """

    # Override to allow empty filters (no min_length constraint) and use our wrapped type
    filters: Sequence[BoardViewFilter] = Field(  # type: ignore[assignment]
        default_factory=list,
        description="The filters to apply to this view",
    )


class BoardView(_BoardViewResponseGenerated):
    """A board view (response model).

    Board views are filtered perspectives on a board, with each board
    supporting up to 50 views maximum.
    """

    model_config = {"extra": "allow"}

    # Override filters to use our wrapped BoardViewFilter type
    filters: list[BoardViewFilter] = []  # type: ignore[assignment]
