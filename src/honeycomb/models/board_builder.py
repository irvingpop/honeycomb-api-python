"""Board Builder - Fluent interface for creating boards with panels."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

from honeycomb.models.boards import BoardCreate
from honeycomb.models.tags_mixin import TagsMixin


@dataclass
class BoardPanelPosition:
    """Position and size of a board panel.

    Attributes:
        x_coordinate: X-axis origin point (0+)
        y_coordinate: Y-axis origin point (0+)
        width: Panel width (0 = auto-calculated)
        height: Panel height (0 = auto-calculated)
    """

    x_coordinate: int = 0
    y_coordinate: int = 0
    width: int = 0  # 0 = auto-calculated
    height: int = 0  # 0 = auto-calculated


class BoardPanelType(str, Enum):
    """Types of panels that can be added to a board."""

    QUERY = "query"
    SLO = "slo"
    TEXT = "text"


@dataclass
class BoardQueryPanel:
    """Query panel configuration.

    Attributes:
        query_id: ID of the saved query
        query_annotation_id: Annotation ID of the query
        query_style: Display style (graph, table, combo)
        dataset: Dataset name (optional, read-only from query)
        visualization_settings: Advanced visualization configuration
    """

    query_id: str
    query_annotation_id: str
    query_style: Literal["graph", "table", "combo"] = "graph"
    dataset: str | None = None
    visualization_settings: dict[str, Any] | None = None


@dataclass
class BoardSLOPanel:
    """SLO panel configuration.

    Attributes:
        slo_id: ID of the saved SLO
    """

    slo_id: str


@dataclass
class BoardTextPanel:
    """Text panel configuration.

    Attributes:
        content: Markdown-formatted text content (max 10000 chars)
    """

    content: str


@dataclass
class BoardPanel:
    """A panel on a board (query, SLO, or text).

    Attributes:
        panel_type: Type of panel (query, slo, text)
        position: Optional position and size
        query_panel: Query panel configuration (if panel_type=query)
        slo_panel: SLO panel configuration (if panel_type=slo)
        text_panel: Text panel configuration (if panel_type=text)
    """

    panel_type: BoardPanelType
    position: BoardPanelPosition | None = None
    # Type-specific configurations
    query_panel: BoardQueryPanel | None = None
    slo_panel: BoardSLOPanel | None = None
    text_panel: BoardTextPanel | None = None


class BoardBuilder(TagsMixin):
    """Fluent builder for boards with queries, SLOs, and text panels.

    Example - Basic board with auto-layout:
        board = (
            BoardBuilder("Service Dashboard")
            .description("Overview of API health")
            .auto_layout()
            .query("query-id-1", "annotation-id-1")
            .slo("slo-id-1")
            .text("## Notes\\nMonitor during peak hours")
            .build()
        )

    Example - Manual layout with positioning:
        board = (
            BoardBuilder("Custom Layout")
            .manual_layout()
            .query(
                "query-id-1",
                "annotation-id-1",
                position=BoardPanelPosition(x_coordinate=0, y_coordinate=0, width=8, height=6)
            )
            .slo(
                "slo-id-1",
                position=BoardPanelPosition(x_coordinate=8, y_coordinate=0, width=4, height=6)
            )
            .build()
        )
    """

    def __init__(self, name: str):
        TagsMixin.__init__(self)
        self._name = name
        self._description: str | None = None
        self._layout_generation: Literal["auto", "manual"] = "manual"
        self._panels: list[BoardPanel] = []
        self._preset_filters: list[dict[str, str]] = []

    def description(self, desc: str) -> BoardBuilder:
        """Set board description (max 1024 chars).

        Args:
            desc: Description text
        """
        self._description = desc
        return self

    # -------------------------------------------------------------------------
    # Layout configuration
    # -------------------------------------------------------------------------

    def auto_layout(self) -> BoardBuilder:
        """Use automatic layout positioning.

        Panels will be arranged automatically. Position can be omitted.
        """
        self._layout_generation = "auto"
        return self

    def manual_layout(self) -> BoardBuilder:
        """Use manual layout positioning (default).

        When using manual layout, you must specify position for all panels.
        """
        self._layout_generation = "manual"
        return self

    # -------------------------------------------------------------------------
    # Preset filters
    # -------------------------------------------------------------------------

    def preset_filter(self, column: str, alias: str) -> BoardBuilder:
        """Add a preset filter to the board.

        Preset filters allow dynamic filtering of board data by specific columns.

        Args:
            column: Original column name to filter on
            alias: Display name for the filter in the UI

        Example:
            .preset_filter("service_name", "Service")
            .preset_filter("environment", "Environment")
        """
        self._preset_filters.append({"column": column, "alias": alias})
        return self

    # -------------------------------------------------------------------------
    # Add panels
    # -------------------------------------------------------------------------

    def query(
        self,
        query_id: str,
        query_annotation_id: str,
        *,
        position: BoardPanelPosition | None = None,
        style: Literal["graph", "table", "combo"] = "graph",
        dataset: str | None = None,
        visualization_settings: dict[str, Any] | None = None,
    ) -> BoardBuilder:
        """Add a saved query panel to the board.

        Args:
            query_id: ID of the saved query
            query_annotation_id: Annotation ID of the query
            position: Optional position and size (None for auto-layout)
            style: Display style - graph, table, or combo (default: graph)
            dataset: Optional dataset name
            visualization_settings: Optional advanced visualization configuration

        Example:
            .query(
                "query-id-123",
                "annotation-456",
                position=BoardPanelPosition(x_coordinate=0, y_coordinate=0, width=8, height=6),
                style="graph"
            )
        """
        self._panels.append(
            BoardPanel(
                panel_type=BoardPanelType.QUERY,
                position=position,
                query_panel=BoardQueryPanel(
                    query_id=query_id,
                    query_annotation_id=query_annotation_id,
                    query_style=style,
                    dataset=dataset,
                    visualization_settings=visualization_settings,
                ),
            )
        )
        return self

    def slo(
        self,
        slo_id: str,
        *,
        position: BoardPanelPosition | None = None,
    ) -> BoardBuilder:
        """Add an SLO panel to the board.

        Args:
            slo_id: ID of the SLO
            position: Optional position and size (None for auto-layout)

        Example:
            .slo(
                "slo-id-123",
                position=BoardPanelPosition(x_coordinate=8, y_coordinate=0, width=4, height=6)
            )
        """
        self._panels.append(
            BoardPanel(
                panel_type=BoardPanelType.SLO,
                position=position,
                slo_panel=BoardSLOPanel(slo_id=slo_id),
            )
        )
        return self

    def text(
        self,
        content: str,
        *,
        position: BoardPanelPosition | None = None,
    ) -> BoardBuilder:
        """Add a text panel to the board (supports markdown).

        Args:
            content: Markdown-formatted text (max 10000 chars)
            position: Optional position and size (None for auto-layout)

        Example:
            .text(
                "## Service Status\\n\\nAll systems operational",
                position=BoardPanelPosition(x_coordinate=0, y_coordinate=6, width=12, height=2)
            )
        """
        if len(content) > 10000:
            raise ValueError(f"Text panel content must be <= 10000 characters, got {len(content)}")

        self._panels.append(
            BoardPanel(
                panel_type=BoardPanelType.TEXT,
                position=position,
                text_panel=BoardTextPanel(content=content),
            )
        )
        return self

    # -------------------------------------------------------------------------
    # Build
    # -------------------------------------------------------------------------

    def build(self) -> BoardCreate:
        """Build BoardCreate with validation.

        Returns:
            BoardCreate object ready for API submission

        Raises:
            ValueError: If manual layout is used without positions
        """
        # Validate manual layout requires positions
        if self._layout_generation == "manual":
            for i, panel in enumerate(self._panels):
                if panel.position is None:
                    raise ValueError(
                        f"Manual layout requires position for all panels. "
                        f"Panel {i} ({panel.panel_type.value}) has no position. "
                        "Use auto_layout() or specify positions for all panels."
                    )

        # Build panels array
        panels_data = []
        for panel in self._panels:
            panel_dict: dict[str, Any] = {"type": panel.panel_type.value}

            # Add type-specific configuration
            if panel.query_panel:
                query_panel_dict: dict[str, Any] = {
                    "query_id": panel.query_panel.query_id,
                    "query_annotation_id": panel.query_panel.query_annotation_id,
                    "query_style": panel.query_panel.query_style,
                }
                if panel.query_panel.dataset:
                    query_panel_dict["dataset"] = panel.query_panel.dataset
                if panel.query_panel.visualization_settings:
                    query_panel_dict["visualization_settings"] = (
                        panel.query_panel.visualization_settings
                    )
                panel_dict["query_panel"] = query_panel_dict

            elif panel.slo_panel:
                panel_dict["slo_panel"] = {"slo_id": panel.slo_panel.slo_id}

            elif panel.text_panel:
                panel_dict["text_panel"] = {"content": panel.text_panel.content}

            # Add position if specified
            if panel.position:
                panel_dict["position"] = {
                    "x_coordinate": panel.position.x_coordinate,
                    "y_coordinate": panel.position.y_coordinate,
                    "width": panel.position.width,
                    "height": panel.position.height,
                }

            panels_data.append(panel_dict)

        # Build tags
        tags_data = self._get_all_tags()

        return BoardCreate(
            name=self._name,
            description=self._description,
            type="flexible",
            panels=panels_data if panels_data else None,
            layout_generation=self._layout_generation,
            tags=tags_data,
            preset_filters=self._preset_filters if self._preset_filters else None,
        )

    def get_panels(self) -> list[BoardPanel]:
        """Get board panels for inspection.

        Returns:
            List of BoardPanel objects
        """
        return self._panels
