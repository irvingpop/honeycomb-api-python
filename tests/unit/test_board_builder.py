"""Tests for BoardBuilder."""

import pytest

from honeycomb import (
    BoardBuilder,
    BoardCreate,
    BoardPanelPosition,
    BoardPanelType,
)


class TestBoardBuilderBasics:
    """Tests for basic BoardBuilder functionality."""

    def test_minimal_board(self):
        """Test building minimal board."""
        board = BoardBuilder("Test Board").build()

        assert isinstance(board, BoardCreate)
        assert board.name == "Test Board"
        assert board.type == "flexible"
        assert board.layout_generation == "manual"  # Default
        assert board.description is None
        assert board.panels is None
        assert board.tags is None

    def test_board_with_description(self):
        """Test adding description."""
        board = BoardBuilder("Test Board").description("Test description").build()

        assert board.description == "Test description"

    def test_method_chaining(self):
        """Test that methods return self for chaining."""
        builder = BoardBuilder("Test")
        assert builder.description("test") is builder
        assert builder.auto_layout() is builder
        assert builder.manual_layout() is builder


class TestBoardBuilderLayout:
    """Tests for layout configuration."""

    def test_auto_layout(self):
        """Test auto layout mode."""
        board = BoardBuilder("Test").auto_layout().build()

        assert board.layout_generation == "auto"

    def test_manual_layout(self):
        """Test manual layout mode (default)."""
        board = BoardBuilder("Test").manual_layout().build()

        assert board.layout_generation == "manual"

    def test_default_layout_is_manual(self):
        """Test that default layout is manual."""
        board = BoardBuilder("Test").build()

        assert board.layout_generation == "manual"


class TestBoardBuilderQueryPanels:
    """Tests for query panel configuration."""

    def test_query_panel_minimal(self):
        """Test adding minimal query panel."""
        builder = BoardBuilder("Test").auto_layout().query("query-id-1", "annotation-id-1")

        panels = builder.get_panels()
        assert len(panels) == 1
        assert panels[0].panel_type == BoardPanelType.QUERY
        assert panels[0].query_panel.query_id == "query-id-1"
        assert panels[0].query_panel.query_annotation_id == "annotation-id-1"
        assert panels[0].query_panel.query_style == "graph"  # Default
        assert panels[0].position is None

    def test_query_panel_with_position(self):
        """Test adding query panel with position."""
        position = BoardPanelPosition(x_coordinate=0, y_coordinate=0, width=8, height=6)
        builder = (
            BoardBuilder("Test")
            .manual_layout()
            .query("query-id-1", "annotation-id-1", position=position)
        )

        panels = builder.get_panels()
        assert panels[0].position == position
        assert panels[0].position.x_coordinate == 0
        assert panels[0].position.width == 8

    def test_query_panel_with_style(self):
        """Test query panel with different styles."""
        for style in ["graph", "table", "combo"]:
            builder = (
                BoardBuilder("Test")
                .auto_layout()
                .query("query-id-1", "annotation-id-1", style=style)
            )

            panels = builder.get_panels()
            assert panels[0].query_panel.query_style == style

    def test_query_panel_with_dataset(self):
        """Test query panel with dataset."""
        builder = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-id-1", "annotation-id-1", dataset="my-dataset")
        )

        panels = builder.get_panels()
        assert panels[0].query_panel.dataset == "my-dataset"

    def test_query_panel_with_visualization_settings(self):
        """Test query panel with visualization settings."""
        vis_settings = {"hide_markers": True, "utc_xaxis": True}
        builder = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-id-1", "annotation-id-1", visualization_settings=vis_settings)
        )

        panels = builder.get_panels()
        assert panels[0].query_panel.visualization_settings == vis_settings


class TestBoardBuilderSLOPanels:
    """Tests for SLO panel configuration."""

    def test_slo_panel_minimal(self):
        """Test adding minimal SLO panel."""
        builder = BoardBuilder("Test").auto_layout().slo("slo-id-1")

        panels = builder.get_panels()
        assert len(panels) == 1
        assert panels[0].panel_type == BoardPanelType.SLO
        assert panels[0].slo_panel.slo_id == "slo-id-1"
        assert panels[0].position is None

    def test_slo_panel_with_position(self):
        """Test adding SLO panel with position."""
        position = BoardPanelPosition(x_coordinate=8, y_coordinate=0, width=4, height=6)
        builder = BoardBuilder("Test").manual_layout().slo("slo-id-1", position=position)

        panels = builder.get_panels()
        assert panels[0].position == position


class TestBoardBuilderTextPanels:
    """Tests for text panel configuration."""

    def test_text_panel_minimal(self):
        """Test adding minimal text panel."""
        builder = BoardBuilder("Test").auto_layout().text("## Notes\n\nSome notes here")

        panels = builder.get_panels()
        assert len(panels) == 1
        assert panels[0].panel_type == BoardPanelType.TEXT
        assert panels[0].text_panel.content == "## Notes\n\nSome notes here"
        assert panels[0].position is None

    def test_text_panel_with_position(self):
        """Test adding text panel with position."""
        position = BoardPanelPosition(x_coordinate=0, y_coordinate=6, width=12, height=2)
        builder = BoardBuilder("Test").manual_layout().text("## Alert Info", position=position)

        panels = builder.get_panels()
        assert panels[0].position == position

    def test_text_panel_max_length_validation(self):
        """Test that text panel validates max length."""
        long_text = "x" * 10001  # Over 10000 char limit

        with pytest.raises(ValueError, match="Text panel content must be <= 10000 characters"):
            BoardBuilder("Test").auto_layout().text(long_text).build()


class TestBoardBuilderMixedPanels:
    """Tests for boards with multiple panel types."""

    def test_board_with_multiple_panel_types(self):
        """Test board with query, SLO, and text panels."""
        builder = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-1", "annot-1")
            .slo("slo-1")
            .text("## Notes")
        )

        panels = builder.get_panels()
        assert len(panels) == 3
        assert panels[0].panel_type == BoardPanelType.QUERY
        assert panels[1].panel_type == BoardPanelType.SLO
        assert panels[2].panel_type == BoardPanelType.TEXT

    def test_board_with_multiple_queries(self):
        """Test board with multiple query panels."""
        builder = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-1", "annot-1", style="graph")
            .query("query-2", "annot-2", style="table")
            .query("query-3", "annot-3", style="combo")
        )

        panels = builder.get_panels()
        assert len(panels) == 3
        assert all(p.panel_type == BoardPanelType.QUERY for p in panels)
        assert panels[0].query_panel.query_style == "graph"
        assert panels[1].query_panel.query_style == "table"
        assert panels[2].query_panel.query_style == "combo"


class TestBoardBuilderTags:
    """Tests for tag support via TagsMixin."""

    def test_single_tag(self):
        """Test adding single tag."""
        board = BoardBuilder("Test").tag("team", "platform").build()

        assert board.tags is not None
        assert len(board.tags) == 1
        assert board.tags[0] == {"key": "team", "value": "platform"}

    def test_multiple_tags(self):
        """Test adding multiple tags."""
        board = (
            BoardBuilder("Test").tag("team", "platform").tag("environment", "production").build()
        )

        assert board.tags is not None
        assert len(board.tags) == 2

    def test_tags_dict(self):
        """Test adding tags via dictionary."""
        board = BoardBuilder("Test").tags({"team": "platform", "environment": "production"}).build()

        assert board.tags is not None
        assert len(board.tags) == 2


class TestBoardBuilderValidation:
    """Tests for BoardBuilder validation."""

    def test_manual_layout_without_positions_raises_error(self):
        """Test that manual layout without positions raises error."""
        with pytest.raises(
            ValueError,
            match="Manual layout requires position for all panels",
        ):
            (
                BoardBuilder("Test")
                .manual_layout()
                .query("query-1", "annot-1")  # No position specified
                .build()
            )

    def test_manual_layout_with_partial_positions_raises_error(self):
        """Test that manual layout with partial positions raises error."""
        pos = BoardPanelPosition(x_coordinate=0, y_coordinate=0, width=8, height=6)

        with pytest.raises(
            ValueError,
            match="Manual layout requires position for all panels",
        ):
            (
                BoardBuilder("Test")
                .manual_layout()
                .query("query-1", "annot-1", position=pos)  # Has position
                .slo("slo-1")  # Missing position
                .build()
            )

    def test_auto_layout_allows_missing_positions(self):
        """Test that auto layout allows missing positions."""
        board = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-1", "annot-1")  # No position
            .slo("slo-1")  # No position
            .build()
        )

        assert board.layout_generation == "auto"
        assert board.panels is not None


class TestBoardBuilderComplexScenarios:
    """Tests for complex board scenarios."""

    def test_complete_auto_layout_board(self):
        """Test complete board with auto layout."""
        board = (
            BoardBuilder("Service Dashboard")
            .description("Comprehensive service monitoring")
            .auto_layout()
            .tag("team", "backend")
            .tag("service", "api")
            .query("query-1", "annot-1", style="graph")
            .query("query-2", "annot-2", style="table", dataset="api-logs")
            .slo("slo-1")
            .text("## Dashboard Notes\n\nMonitor during deployments")
            .build()
        )

        assert board.name == "Service Dashboard"
        assert board.description == "Comprehensive service monitoring"
        assert board.layout_generation == "auto"
        assert board.panels is not None
        assert len(board.panels) == 4
        assert board.tags is not None
        assert len(board.tags) == 2

    def test_complete_manual_layout_board(self):
        """Test complete board with manual layout."""
        board = (
            BoardBuilder("Custom Layout")
            .description("Precisely positioned dashboard")
            .manual_layout()
            .query(
                "query-1",
                "annot-1",
                position=BoardPanelPosition(x_coordinate=0, y_coordinate=0, width=8, height=6),
            )
            .slo(
                "slo-1",
                position=BoardPanelPosition(x_coordinate=8, y_coordinate=0, width=4, height=6),
            )
            .text(
                "## Notes",
                position=BoardPanelPosition(x_coordinate=0, y_coordinate=6, width=12, height=2),
            )
            .build()
        )

        assert board.name == "Custom Layout"
        assert board.layout_generation == "manual"
        assert board.panels is not None
        assert len(board.panels) == 3

        # Verify all panels have positions
        for panel_data in board.panels:
            assert "position" in panel_data
