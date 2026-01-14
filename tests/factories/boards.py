"""Factories for Board and BoardView models."""

from honeycomb._generated_models import (
    BoardLayoutGeneration,
    BoardLinks,
    BoardPanelPosition,
    BoardQueryVisualizationSettings,
    BoardType,
    BoardViewFilter,
    QueryPanelQueryPanel,
)
from honeycomb.models import Board, BoardCreate, BoardView, BoardViewCreate
from honeycomb.models.boards import BoardViewFilterOperation

from .base import HoneycombFactory


class BoardLinksFactory(HoneycombFactory):
    """Factory for BoardLinks."""

    __model__ = BoardLinks

    @classmethod
    def build(cls, **kwargs):
        board_id = kwargs.get("board_id", HoneycombFactory._honeycomb_id())
        return super().build(
            board_url=f"https://ui.honeycomb.io/team/board/{board_id}",
            **{k: v for k, v in kwargs.items() if k != "board_id"},
        )


class BoardPanelPositionFactory(HoneycombFactory):
    """Factory for BoardPanelPosition."""

    __model__ = BoardPanelPosition

    x = lambda: HoneycombFactory.__random__.randint(0, 3)
    y = lambda: HoneycombFactory.__random__.randint(0, 10)
    width = lambda: HoneycombFactory.__random__.randint(1, 4)
    height = lambda: HoneycombFactory.__random__.randint(1, 4)


class QueryPanelQueryPanelFactory(HoneycombFactory):
    """Factory for QueryPanelQueryPanel (inner query panel structure)."""

    __model__ = QueryPanelQueryPanel

    query_id = lambda: HoneycombFactory._honeycomb_id()
    query_style = "graph"


class BoardQueryVisualizationSettingsFactory(HoneycombFactory):
    """Factory for BoardQueryVisualizationSettings."""

    __model__ = BoardQueryVisualizationSettings


class BoardFactory(HoneycombFactory):
    """Factory for Board response model.

    Example:
        board = BoardFactory.build(id="board-123")
        board_list = BoardFactory.batch(5)
    """

    __model__ = Board

    id = lambda: HoneycombFactory._honeycomb_id()
    name = lambda: f"Test Board {HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test board"
    type = BoardType.flexible
    layout_generation = BoardLayoutGeneration.manual
    panels = None  # Empty panels by default


class BoardCreateFactory(HoneycombFactory):
    """Factory for BoardCreate request model.

    Example:
        payload = BoardCreateFactory.build(name="New Board")
    """

    __model__ = BoardCreate

    name = lambda: f"Test Board {HoneycombFactory._honeycomb_id()}"
    description = lambda: "A test board"
    type = BoardType.flexible


# =============================================================================
# Board View Factories
# =============================================================================


class BoardViewFilterFactory(HoneycombFactory):
    """Factory for BoardViewFilter."""

    __model__ = BoardViewFilter

    column = lambda: f"column_{HoneycombFactory._honeycomb_id()}"
    op = BoardViewFilterOperation.EQUALS


class BoardViewFactory(HoneycombFactory):
    """Factory for BoardView response model.

    Example:
        view = BoardViewFactory.build(id="view-123")
        views = BoardViewFactory.batch(3)
    """

    __model__ = BoardView

    id = lambda: f"eC_{HoneycombFactory._honeycomb_id()}"
    name = lambda: f"Test View {HoneycombFactory._honeycomb_id()}"
    filters = lambda: []  # Empty filters by default


class BoardViewCreateFactory(HoneycombFactory):
    """Factory for BoardViewCreate request model.

    Example:
        payload = BoardViewCreateFactory.build(name="Active Services")
    """

    __model__ = BoardViewCreate

    name = lambda: f"Test View {HoneycombFactory._honeycomb_id()}"
    filters = lambda: []  # Empty filters by default
