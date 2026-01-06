"""Tests for BoardBuilder."""

import pytest

from honeycomb import BoardBuilder, BoardBundle
from honeycomb.models.boards import BoardViewFilter
from honeycomb.models.query_builder import FilterOp


class TestBoardBuilderBasics:
    """Tests for basic BoardBuilder functionality."""

    def test_minimal_board(self):
        """Test building minimal board."""
        bundle = BoardBuilder("Test Board").build()

        assert isinstance(bundle, BoardBundle)
        assert bundle.board_name == "Test Board"
        assert bundle.layout_generation == "manual"  # Default
        assert bundle.board_description is None
        assert len(bundle.query_builder_panels) == 0
        assert len(bundle.existing_query_panels) == 0
        assert bundle.tags is None

    def test_board_with_description(self):
        """Test adding description."""
        bundle = BoardBuilder("Test Board").description("Test description").build()

        assert bundle.board_description == "Test description"

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
        bundle = BoardBuilder("Test").auto_layout().build()

        assert bundle.layout_generation == "auto"

    def test_manual_layout(self):
        """Test manual layout mode (default)."""
        bundle = BoardBuilder("Test").manual_layout().build()

        assert bundle.layout_generation == "manual"

    def test_default_layout_is_manual(self):
        """Test that default layout is manual."""
        bundle = BoardBuilder("Test").build()

        assert bundle.layout_generation == "manual"


class TestBoardBuilderQueryPanels:
    """Tests for query panel configuration."""

    def test_query_panel_minimal(self):
        """Test adding minimal query panel."""
        bundle = BoardBuilder("Test").auto_layout().query("query-id-1", "annotation-id-1").build()

        assert len(bundle.existing_query_panels) == 1
        panel = bundle.existing_query_panels[0]
        assert panel.query_id == "query-id-1"
        assert panel.annotation_id == "annotation-id-1"
        assert panel.style == "graph"  # Default
        assert panel.position is None

    def test_query_panel_with_position(self):
        """Test adding query panel with position."""
        position = (0, 0, 8, 6)
        bundle = (
            BoardBuilder("Test")
            .manual_layout()
            .query("query-id-1", "annotation-id-1", position=position)
            .build()
        )

        panel = bundle.existing_query_panels[0]
        assert panel.position == position
        assert panel.position[0] == 0  # x
        assert panel.position[2] == 8  # width

    def test_query_panel_with_style(self):
        """Test query panel with different styles."""
        for style in ["graph", "table", "combo"]:
            bundle = (
                BoardBuilder("Test")
                .auto_layout()
                .query("query-id-1", "annotation-id-1", style=style)
                .build()
            )

            assert bundle.existing_query_panels[0].style == style

    def test_query_panel_with_dataset(self):
        """Test query panel with dataset."""
        bundle = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-id-1", "annotation-id-1", dataset="my-dataset")
            .build()
        )

        assert bundle.existing_query_panels[0].dataset == "my-dataset"

    def test_query_panel_with_visualization_settings(self):
        """Test query panel with visualization settings."""
        vis_settings = {"hide_markers": True, "utc_xaxis": True}
        bundle = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-id-1", "annotation-id-1", visualization=vis_settings)
            .build()
        )

        assert bundle.existing_query_panels[0].visualization == vis_settings


class TestBoardBuilderSLOPanels:
    """Tests for SLO panel configuration."""

    def test_slo_panel_minimal(self):
        """Test adding minimal SLO panel (existing SLO ID)."""
        bundle = BoardBuilder("Test").auto_layout().slo("slo-id-1").build()

        assert len(bundle.existing_slo_panels) == 1
        panel = bundle.existing_slo_panels[0]
        assert panel.slo_id == "slo-id-1"
        assert panel.position is None

    def test_slo_panel_with_position(self):
        """Test adding SLO panel with position."""
        position = (8, 0, 4, 6)
        bundle = BoardBuilder("Test").manual_layout().slo("slo-id-1", position=position).build()

        assert bundle.existing_slo_panels[0].position == position


class TestBoardBuilderTextPanels:
    """Tests for text panel configuration."""

    def test_text_panel_minimal(self):
        """Test adding minimal text panel."""
        bundle = BoardBuilder("Test").auto_layout().text("## Notes\n\nSome notes here").build()

        assert len(bundle.text_panels) == 1
        panel = bundle.text_panels[0]
        assert panel.content == "## Notes\n\nSome notes here"
        assert panel.position is None

    def test_text_panel_with_position(self):
        """Test adding text panel with position."""
        position = (0, 6, 12, 2)
        bundle = (
            BoardBuilder("Test").manual_layout().text("## Alert Info", position=position).build()
        )

        assert bundle.text_panels[0].position == position

    def test_text_panel_max_length_validation(self):
        """Test that text panel validates max length."""
        long_text = "x" * 10001  # Over 10000 char limit

        with pytest.raises(ValueError, match="Text content must be <= 10000 characters"):
            BoardBuilder("Test").auto_layout().text(long_text).build()


class TestBoardBuilderMixedPanels:
    """Tests for boards with multiple panel types."""

    def test_board_with_multiple_panel_types(self):
        """Test board with query, SLO, and text panels."""
        bundle = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-1", "annot-1")
            .slo("slo-1")
            .text("## Notes")
            .build()
        )

        assert len(bundle.existing_query_panels) == 1
        assert len(bundle.existing_slo_panels) == 1
        assert len(bundle.text_panels) == 1

    def test_board_with_multiple_queries(self):
        """Test board with multiple query panels."""
        bundle = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-1", "annot-1", style="graph")
            .query("query-2", "annot-2", style="table")
            .query("query-3", "annot-3", style="combo")
            .build()
        )

        assert len(bundle.existing_query_panels) == 3
        assert bundle.existing_query_panels[0].style == "graph"
        assert bundle.existing_query_panels[1].style == "table"
        assert bundle.existing_query_panels[2].style == "combo"


class TestBoardBuilderTags:
    """Tests for tag support via TagsMixin."""

    def test_single_tag(self):
        """Test adding single tag."""
        bundle = BoardBuilder("Test").tag("team", "platform").build()

        assert bundle.tags is not None
        assert len(bundle.tags) == 1
        assert bundle.tags[0] == {"key": "team", "value": "platform"}

    def test_multiple_tags(self):
        """Test adding multiple tags."""
        bundle = (
            BoardBuilder("Test").tag("team", "platform").tag("environment", "production").build()
        )

        assert bundle.tags is not None
        assert len(bundle.tags) == 2

    def test_tags_dict(self):
        """Test adding tags via dictionary."""
        bundle = (
            BoardBuilder("Test").tags({"team": "platform", "environment": "production"}).build()
        )

        assert bundle.tags is not None
        assert len(bundle.tags) == 2


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
        pos = (0, 0, 8, 6)

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
        bundle = (
            BoardBuilder("Test")
            .auto_layout()
            .query("query-1", "annot-1")  # No position
            .slo("slo-1")  # No position
            .build()
        )

        assert bundle.layout_generation == "auto"
        assert len(bundle.existing_query_panels) == 1
        assert len(bundle.existing_slo_panels) == 1


class TestBoardBuilderComplexScenarios:
    """Tests for complex board scenarios."""

    def test_complete_auto_layout_board(self):
        """Test complete board with auto layout."""
        bundle = (
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

        assert bundle.board_name == "Service Dashboard"
        assert bundle.board_description == "Comprehensive service monitoring"
        assert bundle.layout_generation == "auto"
        assert len(bundle.existing_query_panels) == 2
        assert len(bundle.existing_slo_panels) == 1
        assert len(bundle.text_panels) == 1
        assert bundle.tags is not None
        assert len(bundle.tags) == 2

    def test_complete_manual_layout_board(self):
        """Test complete board with manual layout."""
        bundle = (
            BoardBuilder("Custom Layout")
            .description("Precisely positioned dashboard")
            .manual_layout()
            .query("query-1", "annot-1", position=(0, 0, 8, 6))
            .slo("slo-1", position=(8, 0, 4, 6))
            .text("## Notes", position=(0, 6, 12, 2))
            .build()
        )

        assert bundle.board_name == "Custom Layout"
        assert bundle.layout_generation == "manual"
        assert len(bundle.existing_query_panels) == 1
        assert len(bundle.existing_slo_panels) == 1
        assert len(bundle.text_panels) == 1

        # Verify all panels have positions
        assert bundle.existing_query_panels[0].position == (0, 0, 8, 6)
        assert bundle.existing_slo_panels[0].position == (8, 0, 4, 6)
        assert bundle.text_panels[0].position == (0, 6, 12, 2)


class TestBoardBuilderViews:
    """Tests for board view support in BoardBuilder."""

    def test_add_view_with_dict_filters(self):
        """Test adding view with dict filters."""
        bundle = (
            BoardBuilder("Test")
            .auto_layout()
            .add_view("Active", [{"column": "status", "operation": "=", "value": "active"}])
            .build()
        )

        assert len(bundle.views) == 1
        assert bundle.views[0].name == "Active"
        assert len(bundle.views[0].filters) == 1
        assert bundle.views[0].filters[0].column == "status"
        assert bundle.views[0].filters[0].value == "active"

    def test_add_view_with_filter_objects(self):
        """Test adding view with BoardViewFilter objects."""
        bundle = (
            BoardBuilder("Test")
            .auto_layout()
            .add_view(
                "Errors",
                [
                    BoardViewFilter(
                        column="status_code",
                        operation=FilterOp.GREATER_THAN_OR_EQUAL,
                        value=400,
                    )
                ],
            )
            .build()
        )

        assert len(bundle.views) == 1
        assert bundle.views[0].name == "Errors"
        assert len(bundle.views[0].filters) == 1
        assert bundle.views[0].filters[0].column == "status_code"
        assert bundle.views[0].filters[0].value == 400

    def test_add_view_with_no_filters(self):
        """Test adding view with no filters."""
        bundle = BoardBuilder("Test").auto_layout().add_view("All Data").build()

        assert len(bundle.views) == 1
        assert bundle.views[0].name == "All Data"
        assert len(bundle.views[0].filters) == 0

    def test_add_multiple_views(self):
        """Test adding multiple views."""
        bundle = (
            BoardBuilder("Test")
            .auto_layout()
            .add_view("View 1", [])
            .add_view("View 2", [])
            .add_view("View 3", [])
            .build()
        )

        assert len(bundle.views) == 3
        assert bundle.views[0].name == "View 1"
        assert bundle.views[1].name == "View 2"
        assert bundle.views[2].name == "View 3"

    def test_add_view_with_multiple_filters(self):
        """Test adding view with multiple filters."""
        bundle = (
            BoardBuilder("Test")
            .auto_layout()
            .add_view(
                "Production Errors",
                [
                    {"column": "environment", "operation": "=", "value": "production"},
                    {"column": "status_code", "operation": ">=", "value": 500},
                ],
            )
            .build()
        )

        assert len(bundle.views) == 1
        assert len(bundle.views[0].filters) == 2

    def test_method_chaining_with_views(self):
        """Test that add_view returns self for chaining."""
        builder = BoardBuilder("Test")
        assert builder.add_view("Test View") is builder

    def test_complete_board_with_views(self):
        """Test complete board with panels and views."""
        bundle = (
            BoardBuilder("Service Dashboard")
            .description("Dashboard with views")
            .auto_layout()
            .query("query-1", "annot-1")
            .add_view("Active Only", [{"column": "status", "operation": "=", "value": "active"}])
            .add_view("Errors Only", [{"column": "status_code", "operation": ">=", "value": 400}])
            .build()
        )

        assert bundle.board_name == "Service Dashboard"
        assert len(bundle.existing_query_panels) == 1
        assert len(bundle.views) == 2
