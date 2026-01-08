"""Board Builder - Fluent interface for creating boards with panels."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from honeycomb.models.boards import BoardViewCreate, BoardViewFilter
from honeycomb.models.tags_mixin import TagsMixin
from honeycomb.models.tool_inputs import PositionInput

if TYPE_CHECKING:
    from honeycomb.models.query_builder import QueryBuilder
    from honeycomb.models.slo_builder import SLOBuilder


# =============================================================================
# BoardBundle Data Structures
# =============================================================================


@dataclass
class QueryBuilderPanel:
    """Query panel from inline QueryBuilder (needs creation).

    Attributes:
        builder: QueryBuilder instance with .name() set
        position: Optional PositionInput for manual layout
        style: Display style (graph, table, combo)
        visualization: Optional visualization settings dict
        dataset_override: Optional dataset override
    """

    builder: QueryBuilder
    position: PositionInput | None
    style: Literal["graph", "table", "combo"]
    visualization: dict[str, Any] | None
    dataset_override: str | None


@dataclass
class ExistingQueryPanel:
    """Query panel from existing query ID.

    Attributes:
        query_id: ID of saved query
        annotation_id: Annotation ID of query
        position: Optional PositionInput for manual layout
        style: Display style (graph, table, combo)
        visualization: Optional visualization settings dict
        dataset: Optional dataset name
    """

    query_id: str
    annotation_id: str
    position: PositionInput | None
    style: Literal["graph", "table", "combo"]
    visualization: dict[str, Any] | None
    dataset: str | None


@dataclass
class SLOBuilderPanel:
    """SLO panel from inline SLOBuilder (needs creation).

    Attributes:
        builder: SLOBuilder instance
        position: Optional PositionInput for manual layout
    """

    builder: SLOBuilder
    position: PositionInput | None


@dataclass
class ExistingSLOPanel:
    """SLO panel from existing SLO ID.

    Attributes:
        slo_id: ID of the SLO
        position: Optional PositionInput for manual layout
    """

    slo_id: str
    position: PositionInput | None


@dataclass
class TextPanel:
    """Text panel.

    Attributes:
        content: Markdown text content
        position: Optional PositionInput for manual layout
    """

    content: str
    position: PositionInput | None


@dataclass
class BoardBundle:
    """Board creation bundle for orchestration.

    Returned by BoardBuilder.build(), consumed by boards.create_from_bundle_async().

    Attributes:
        board_name: Board name
        board_description: Optional board description
        layout_generation: Layout mode (auto or manual)
        tags: Optional tags list
        preset_filters: Optional preset filters list
        query_builder_panels: Panels from QueryBuilder instances
        existing_query_panels: Panels from existing query IDs
        slo_panels: SLO panels
        text_panels: Text panels
        views: Board views to create
    """

    board_name: str
    board_description: str | None
    layout_generation: Literal["auto", "manual"]
    tags: list[dict[str, str]] | None
    preset_filters: list[dict[str, str]] | None
    # Panels (in order added)
    query_builder_panels: list[QueryBuilderPanel]
    existing_query_panels: list[ExistingQueryPanel]
    slo_builder_panels: list[SLOBuilderPanel]
    existing_slo_panels: list[ExistingSLOPanel]
    text_panels: list[TextPanel]
    # Views
    views: list[BoardViewCreate]


class BoardBuilder(TagsMixin):
    """Fluent builder for boards with inline QueryBuilder or existing query IDs.

    Example - Inline QueryBuilder with auto-layout:
        board = await client.boards.create_from_bundle_async(
            BoardBuilder("Service Dashboard")
            .description("Overview of API health")
            .auto_layout()
            .query(
                QueryBuilder("Request Count")
                .dataset("api-logs")
                .last_1_hour()
                .count()
            )
            .slo("slo-id-1")
            .text("## Notes\\nMonitor during peak hours")
            .build()
        )

    Example - Manual layout with PositionInput:
        from honeycomb.models.tool_inputs import PositionInput

        board = await client.boards.create_from_bundle_async(
            BoardBuilder("Custom Layout")
            .manual_layout()
            .query(
                QueryBuilder("Requests").dataset("api-logs").last_1_hour().count(),
                position=PositionInput(x_coordinate=0, y_coordinate=0, width=8, height=6)
            )
            .slo("slo-id-1", position=PositionInput(x_coordinate=8, y_coordinate=0, width=4, height=6))
            .build()
        )
    """

    def __init__(self, name: str):
        TagsMixin.__init__(self)
        self._name = name
        self._description: str | None = None
        self._layout_generation: Literal["auto", "manual"] = "manual"
        self._preset_filters: list[dict[str, str]] = []
        # Panel storage (in order added)
        self._query_builder_panels: list[QueryBuilderPanel] = []
        self._existing_query_panels: list[ExistingQueryPanel] = []
        self._slo_builder_panels: list[SLOBuilderPanel] = []
        self._existing_slo_panels: list[ExistingSLOPanel] = []
        self._text_panels: list[TextPanel] = []
        # Views
        self._views: list[BoardViewCreate] = []

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
        query: QueryBuilder | str,
        annotation_id: str | None = None,
        *,
        position: PositionInput | None = None,
        style: Literal["graph", "table", "combo"] = "graph",
        visualization: dict[str, Any] | None = None,
        dataset: str | None = None,
    ) -> BoardBuilder:
        """Add a query panel.

        Args:
            query: QueryBuilder with .name() OR existing query_id string
            annotation_id: Required only if query is string
            position: PositionInput for manual layout
            style: graph | table | combo
            visualization: {"hide_markers": True, "utc_xaxis": True, ...}
            dataset: Override QueryBuilder's dataset

        Example - Inline QueryBuilder:
            from honeycomb.models.tool_inputs import PositionInput

            .query(
                QueryBuilder("Request Count")
                    .dataset("api-logs")
                    .last_24_hours()
                    .count()
                    .group_by("service")
                    .description("Requests by service over 24h"),
                position=PositionInput(x_coordinate=0, y_coordinate=0, width=9, height=6),
                style="graph",
                visualization={"hide_markers": True, "utc_xaxis": True}
            )

        Example - Existing query:
            .query("query-id-123", "annotation-id-456", style="table")
        """
        from honeycomb.models.query_builder import QueryBuilder

        if isinstance(query, QueryBuilder):
            if not query.has_name():
                raise ValueError("QueryBuilder must have name in constructor for board panels")

            self._query_builder_panels.append(
                QueryBuilderPanel(
                    builder=query,
                    position=position,
                    style=style,
                    visualization=visualization,
                    dataset_override=dataset,
                )
            )
        else:
            if not annotation_id:
                raise ValueError("annotation_id required when using existing query ID")

            self._existing_query_panels.append(
                ExistingQueryPanel(
                    query_id=query,
                    annotation_id=annotation_id,
                    position=position,
                    style=style,
                    visualization=visualization,
                    dataset=dataset,
                )
            )
        return self

    def slo(
        self,
        slo: SLOBuilder | str,
        *,
        position: PositionInput | None = None,
    ) -> BoardBuilder:
        """Add an SLO panel.

        Args:
            slo: SLOBuilder instance OR existing SLO ID string
            position: PositionInput for manual layout

        Example - Inline SLOBuilder:
            from honeycomb.models.tool_inputs import PositionInput

            .slo(
                SLOBuilder("API Availability")
                    .dataset("api-logs")
                    .target_percentage(99.9)
                    .sli(alias="success_rate"),
                position=PositionInput(x_coordinate=9, y_coordinate=0, width=3, height=6)
            )

        Example - Existing SLO:
            .slo("slo-id-123", position=PositionInput(x_coordinate=8, y_coordinate=0, width=4, height=6))
        """
        from honeycomb.models.slo_builder import SLOBuilder

        if isinstance(slo, SLOBuilder):
            self._slo_builder_panels.append(SLOBuilderPanel(builder=slo, position=position))
        else:
            self._existing_slo_panels.append(ExistingSLOPanel(slo_id=slo, position=position))
        return self

    def text(
        self,
        content: str,
        *,
        position: PositionInput | None = None,
    ) -> BoardBuilder:
        """Add a text panel (supports markdown, max 10000 chars).

        Args:
            content: Markdown text content
            position: PositionInput for manual layout

        Example:
            from honeycomb.models.tool_inputs import PositionInput

            .text(
                "## Service Status\\n\\nAll systems operational",
                position=PositionInput(x_coordinate=0, y_coordinate=6, width=12, height=2)
            )
        """
        if len(content) > 10000:
            raise ValueError(f"Text content must be <= 10000 characters, got {len(content)}")
        self._text_panels.append(TextPanel(content=content, position=position))
        return self

    # -------------------------------------------------------------------------
    # Board Views
    # -------------------------------------------------------------------------

    def add_view(
        self,
        name: str,
        filters: list[BoardViewFilter] | list[dict[str, Any]] | None = None,
    ) -> BoardBuilder:
        """Add a view to the board.

        Views are filtered perspectives on board data. Each board can have up to 50 views.

        Args:
            name: View name
            filters: List of BoardViewFilter objects or dicts with column/operation/value

        Example with dict filters:
            .add_view("Active Services", [
                {"column": "status", "operation": "=", "value": "active"},
                {"column": "environment", "operation": "in", "value": ["prod", "staging"]}
            ])

        Example with BoardViewFilter objects:
            from honeycomb.models.boards import BoardViewFilter
            from honeycomb.models.query_builder import FilterOp

            .add_view("Error View", [
                BoardViewFilter(
                    column="status_code",
                    operation=FilterOp.GREATER_THAN_OR_EQUAL,
                    value=400
                )
            ])

        Example with no filters (all data):
            .add_view("All Data")
        """
        if filters is None:
            filters = []

        # Convert dict filters to BoardViewFilter objects
        filter_objs: list[BoardViewFilter] = []
        for f in filters:
            if isinstance(f, BoardViewFilter):
                filter_objs.append(f)
            else:
                # Convert dict to BoardViewFilter
                filter_objs.append(BoardViewFilter.model_validate(f))

        self._views.append(BoardViewCreate(name=name, filters=filter_objs))
        return self

    # -------------------------------------------------------------------------
    # Build
    # -------------------------------------------------------------------------

    def build(self) -> BoardBundle:
        """Build BoardBundle for orchestration.

        Returns:
            BoardBundle (not BoardCreate) for client orchestration

        Raises:
            ValueError: If manual layout requires positions but some are missing
        """
        # Validate manual layout requires all positions
        if self._layout_generation == "manual":
            all_panels = (
                self._query_builder_panels
                + self._existing_query_panels
                + self._slo_builder_panels
                + self._existing_slo_panels
                + self._text_panels
            )
            for i, panel in enumerate(all_panels):
                if panel.position is None:
                    raise ValueError(
                        f"Manual layout requires position for all panels. "
                        f"Panel {i} missing position. Use position=PositionInput(x_coordinate=..., y_coordinate=..., width=..., height=...)"
                    )

        return BoardBundle(
            board_name=self._name,
            board_description=self._description,
            layout_generation=self._layout_generation,
            tags=self._get_all_tags(),
            preset_filters=self._preset_filters if self._preset_filters else None,
            query_builder_panels=self._query_builder_panels,
            existing_query_panels=self._existing_query_panels,
            slo_builder_panels=self._slo_builder_panels,
            existing_slo_panels=self._existing_slo_panels,
            text_panels=self._text_panels,
            views=self._views,
        )
