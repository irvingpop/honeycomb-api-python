"""Tests for tool input models."""

import pytest
from pydantic import ValidationError

from honeycomb.models.query_builder import CalcOp, Calculation, Filter, FilterCombination, FilterOp
from honeycomb.models.tool_inputs import (
    BoardToolInput,
    BoardViewFilter,
    BoardViewInput,
    BurnAlertInput,
    CalculatedFieldInput,
    ChartSettingsInput,
    PositionInput,
    PresetFilterInput,
    QueryPanelInput,
    RecipientInput,
    SLIInput,
    SLOPanelInput,
    SLOToolInput,
    TagInput,
    TextPanelInput,
    VisualizationSettingsInput,
)


class TestPositionInput:
    """Test PositionInput model."""

    def test_valid_position(self):
        """Test that valid position is accepted."""
        pos = PositionInput(x_coordinate=0, y_coordinate=0, width=8, height=6)
        assert pos.x_coordinate == 0
        assert pos.y_coordinate == 0
        assert pos.width == 8
        assert pos.height == 6

    def test_validates_width_range(self):
        """Test that width must be 1-24."""
        with pytest.raises(ValidationError):
            PositionInput(x_coordinate=0, y_coordinate=0, width=0, height=6)
        with pytest.raises(ValidationError):
            PositionInput(x_coordinate=0, y_coordinate=0, width=25, height=6)

    def test_validates_height_range(self):
        """Test that height must be 1-24."""
        with pytest.raises(ValidationError):
            PositionInput(x_coordinate=0, y_coordinate=0, width=8, height=0)
        with pytest.raises(ValidationError):
            PositionInput(x_coordinate=0, y_coordinate=0, width=8, height=25)

    def test_validates_coordinates_non_negative(self):
        """Test that coordinates must be non-negative."""
        with pytest.raises(ValidationError):
            PositionInput(x_coordinate=-1, y_coordinate=0, width=8, height=6)
        with pytest.raises(ValidationError):
            PositionInput(x_coordinate=0, y_coordinate=-1, width=8, height=6)

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PositionInput(x_coordinate=0, y_coordinate=0, width=8, height=6, extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestQueryPanelInput:
    """Test QueryPanelInput model."""

    def test_minimal_panel(self):
        """Test minimal valid panel."""
        panel = QueryPanelInput(name="Test Panel")
        assert panel.name == "Test Panel"
        assert panel.style == "graph"  # default

    def test_panel_with_query_fields(self):
        """Test panel with query specification."""
        panel = QueryPanelInput(
            name="CPU Panel",
            dataset="metrics",
            time_range=3600,
            calculations=[Calculation(op=CalcOp.AVG, column="cpu_percent")],
        )
        assert panel.dataset == "metrics"
        assert panel.time_range == 3600
        assert len(panel.calculations) == 1

    def test_accepts_typed_models(self):
        """Test that typed models are accepted."""
        panel = QueryPanelInput(
            name="Test",
            calculations=[Calculation(op=CalcOp.COUNT)],
            filters=[Filter(column="status", op=FilterOp.EQUALS, value=200)],
            filter_combination=FilterCombination.AND,
        )
        assert isinstance(panel.calculations[0], Calculation)
        assert isinstance(panel.filters[0], Filter)
        assert panel.filter_combination == FilterCombination.AND

    def test_accepts_string_enum_coercion(self):
        """Test that string enums are coerced."""
        panel = QueryPanelInput(
            name="Test",
            style="table",  # Should work
            filter_combination="OR",  # Should coerce to FilterCombination.OR
        )
        assert panel.style == "table"
        assert panel.filter_combination == FilterCombination.OR

    def test_rejects_invalid_style(self):
        """Test that invalid style is rejected."""
        with pytest.raises(ValidationError):
            QueryPanelInput(name="Test", style="invalid")

    def test_rejects_nested_query_object(self):
        """Test that nested query object is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            QueryPanelInput(
                name="Test",
                query={"dataset": "metrics", "time_range": 3600},  # Invalid nesting
            )

        error = exc_info.value
        assert "extra_forbidden" in str(error)

    def test_accepts_chart_type(self):
        """Test that chart_type shorthand is accepted."""
        panel = QueryPanelInput(name="Test", chart_type="line")
        assert panel.chart_type == "line"

    def test_accepts_visualization_settings(self):
        """Test that visualization settings are accepted."""
        panel = QueryPanelInput(
            name="Test",
            visualization=VisualizationSettingsInput(
                utc_xaxis=True,
                charts=[ChartSettingsInput(chart_type="stacked", log_scale=True)],
            ),
        )
        assert panel.visualization.utc_xaxis is True
        assert panel.visualization.charts[0].chart_type == "stacked"

    def test_accepts_calculated_fields(self):
        """Test that calculated_fields are accepted."""
        panel = QueryPanelInput(
            name="Test",
            calculated_fields=[
                CalculatedFieldInput(
                    name="latency_bucket", expression="IF(LTE($duration_ms, 100), 'fast', 'slow')"
                )
            ],
        )
        assert len(panel.calculated_fields) == 1
        assert panel.calculated_fields[0].name == "latency_bucket"

    def test_accepts_compare_time_offset(self):
        """Test that compare_time_offset_seconds is accepted."""
        panel = QueryPanelInput(name="Test", compare_time_offset_seconds=86400)
        assert panel.compare_time_offset_seconds == 86400

    def test_rejects_invalid_compare_time_offset(self):
        """Test that invalid compare_time_offset values are rejected."""
        with pytest.raises(ValidationError):
            QueryPanelInput(name="Test", compare_time_offset_seconds=1234)  # Not a valid offset

    def test_rejects_extra_fields(self):
        """Test that unknown extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            QueryPanelInput(name="Test", unknown_field="value")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestChartSettingsInput:
    """Test ChartSettingsInput model."""

    def test_default_values(self):
        """Test default values."""
        chart = ChartSettingsInput()
        assert chart.chart_index == 0
        assert chart.chart_type == "default"
        assert chart.log_scale is False
        assert chart.omit_missing_values is False

    def test_valid_chart_types(self):
        """Test all valid chart types."""
        for chart_type in ["default", "line", "stacked", "stat", "tsbar", "cbar", "cpie"]:
            chart = ChartSettingsInput(chart_type=chart_type)
            assert chart.chart_type == chart_type

    def test_rejects_invalid_chart_type(self):
        """Test that invalid chart type is rejected."""
        with pytest.raises(ValidationError):
            ChartSettingsInput(chart_type="invalid")

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChartSettingsInput(extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestVisualizationSettingsInput:
    """Test VisualizationSettingsInput model."""

    def test_default_values(self):
        """Test default values."""
        viz = VisualizationSettingsInput()
        assert viz.hide_compare is False
        assert viz.hide_hovers is False
        assert viz.hide_markers is False
        assert viz.utc_xaxis is False
        assert viz.overlaid_charts is False
        assert viz.charts is None

    def test_with_charts(self):
        """Test with chart settings."""
        viz = VisualizationSettingsInput(
            utc_xaxis=True,
            charts=[
                ChartSettingsInput(chart_type="line"),
                ChartSettingsInput(chart_index=1, chart_type="stacked"),
            ],
        )
        assert viz.utc_xaxis is True
        assert len(viz.charts) == 2
        assert viz.charts[0].chart_type == "line"
        assert viz.charts[1].chart_index == 1

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            VisualizationSettingsInput(extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestCalculatedFieldInput:
    """Test CalculatedFieldInput model."""

    def test_valid_calculated_field(self):
        """Test valid calculated field."""
        field = CalculatedFieldInput(
            name="latency_bucket",
            expression="IF(LTE($duration_ms, 100), 'fast', 'slow')",
        )
        assert field.name == "latency_bucket"
        assert "IF(" in field.expression

    def test_requires_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            CalculatedFieldInput(expression="1+1")

    def test_requires_expression(self):
        """Test that expression is required."""
        with pytest.raises(ValidationError):
            CalculatedFieldInput(name="test")

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CalculatedFieldInput(name="test", expression="1", extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestSLIInput:
    """Test SLIInput model."""

    def test_sli_with_alias_only(self):
        """Test SLI referencing existing column."""
        sli = SLIInput(alias="success_rate")
        assert sli.alias == "success_rate"
        assert sli.expression is None

    def test_sli_with_expression(self):
        """Test SLI with inline column creation."""
        sli = SLIInput(alias="success_rate", expression="LTE($duration_ms, 500)")
        assert sli.alias == "success_rate"
        assert sli.expression == "LTE($duration_ms, 500)"

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SLIInput(alias="test", unknown="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestRecipientInput:
    """Test RecipientInput model."""

    def test_recipient_by_id(self):
        """Test referencing existing recipient."""
        recipient = RecipientInput(id="recip_123")
        assert recipient.id == "recip_123"

    def test_recipient_inline_email(self):
        """Test inline email recipient creation."""
        recipient = RecipientInput(type="email", target="test@example.com")
        assert recipient.type == "email"
        assert recipient.target == "test@example.com"

    def test_recipient_inline_webhook(self):
        """Test inline webhook recipient creation."""
        recipient = RecipientInput(type="webhook", target="https://example.com/hook")
        assert recipient.type == "webhook"
        assert recipient.target == "https://example.com/hook"

    def test_rejects_invalid_type(self):
        """Test that invalid type is rejected."""
        with pytest.raises(ValidationError):
            RecipientInput(type="invalid", target="test")

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RecipientInput(id="test", extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestBurnAlertInput:
    """Test BurnAlertInput model."""

    def test_exhaustion_time_alert(self):
        """Test exhaustion time alert."""
        alert = BurnAlertInput(alert_type="exhaustion_time", exhaustion_minutes=60)
        assert alert.alert_type == "exhaustion_time"
        assert alert.exhaustion_minutes == 60

    def test_budget_rate_alert(self):
        """Test budget rate alert."""
        alert = BurnAlertInput(
            alert_type="budget_rate",
            budget_rate_window_minutes=60,
            budget_rate_decrease_threshold_per_million=50000,
        )
        assert alert.alert_type == "budget_rate"
        assert alert.budget_rate_window_minutes == 60
        assert alert.budget_rate_decrease_threshold_per_million == 50000

    def test_alert_with_recipients(self):
        """Test alert with recipients."""
        alert = BurnAlertInput(
            alert_type="exhaustion_time",
            exhaustion_minutes=60,
            recipients=[RecipientInput(type="email", target="test@example.com")],
        )
        assert len(alert.recipients) == 1

    def test_rejects_invalid_alert_type(self):
        """Test that invalid alert type is rejected."""
        with pytest.raises(ValidationError):
            BurnAlertInput(alert_type="invalid")

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BurnAlertInput(alert_type="exhaustion_time", exhaustion_minutes=60, extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestSLOToolInput:
    """Test SLOToolInput model."""

    def test_minimal_slo(self):
        """Test minimal valid SLO with single dataset."""
        slo = SLOToolInput(
            name="API Success Rate",
            sli=SLIInput(alias="success_rate"),
            datasets=["api-logs"],
            target_percentage=99.9,
        )
        assert slo.name == "API Success Rate"
        assert slo.target_percentage == 99.9
        assert slo.time_period_days == 30  # default
        assert slo.datasets == ["api-logs"]

    def test_slo_with_single_dataset(self):
        """Test SLO with single dataset as single-element list."""
        slo = SLOToolInput(
            name="Test",
            sli=SLIInput(alias="test"),
            datasets=["api-logs"],
            target_percentage=99.9,
        )
        assert slo.datasets == ["api-logs"]
        assert len(slo.datasets) == 1

    def test_slo_with_multiple_datasets(self):
        """Test SLO with multiple datasets."""
        slo = SLOToolInput(
            name="Test",
            sli=SLIInput(alias="test"),
            datasets=["api-logs", "web-logs"],
            target_percentage=99.9,
        )
        assert slo.datasets == ["api-logs", "web-logs"]

    def test_slo_with_burn_alerts(self):
        """Test SLO with inline burn alerts."""
        slo = SLOToolInput(
            name="Test",
            sli=SLIInput(alias="test"),
            datasets=["api-logs"],
            target_percentage=99.9,
            burn_alerts=[BurnAlertInput(alert_type="exhaustion_time", exhaustion_minutes=60)],
        )
        assert len(slo.burn_alerts) == 1

    def test_rejects_empty_datasets(self):
        """Test that empty datasets list is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SLOToolInput(
                name="Test",
                sli=SLIInput(alias="test"),
                datasets=[],  # Empty list not allowed
                target_percentage=99.9,
            )

        error = exc_info.value
        assert "at least 1 item" in str(error).lower() or "min_length" in str(error).lower()

    def test_rejects_target_nines(self):
        """Test that target_nines is not accepted (removed)."""
        with pytest.raises(ValidationError) as exc_info:
            SLOToolInput(
                name="Test",
                sli=SLIInput(alias="test"),
                datasets=["api-logs"],
                target_nines=3,  # Should be rejected
            )

        error = exc_info.value
        assert "extra_forbidden" in str(error)

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SLOToolInput(
                name="Test",
                sli=SLIInput(alias="test"),
                datasets=["api-logs"],
                target_percentage=99.9,
                extra="field",
            )

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestTextPanelInput:
    """Test TextPanelInput model."""

    def test_text_panel(self):
        """Test text panel creation."""
        panel = TextPanelInput(content="# Welcome")
        assert panel.content == "# Welcome"

    def test_text_panel_with_position(self):
        """Test text panel with position."""
        panel = TextPanelInput(
            content="Test",
            position=PositionInput(x_coordinate=0, y_coordinate=0, width=8, height=4),
        )
        assert panel.position is not None

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TextPanelInput(content="Test", extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestSLOPanelInput:
    """Test SLOPanelInput model."""

    def test_slo_panel(self):
        """Test SLO panel creation."""
        panel = SLOPanelInput(
            name="API SLO",
            dataset="api-logs",
            sli=SLIInput(alias="success_rate"),
            target_percentage=99.9,
        )
        assert panel.name == "API SLO"
        assert panel.target_percentage == 99.9
        assert panel.time_period_days == 30  # default

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SLOPanelInput(
                name="Test",
                dataset="test",
                sli=SLIInput(alias="test"),
                target_percentage=99.9,
                extra="field",
            )

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestTagInput:
    """Test TagInput model."""

    def test_tag(self):
        """Test tag creation."""
        tag = TagInput(key="team", value="platform")
        assert tag.key == "team"
        assert tag.value == "platform"

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="test", value="test", extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestPresetFilterInput:
    """Test PresetFilterInput model."""

    def test_preset_filter(self):
        """Test preset filter creation."""
        filt = PresetFilterInput(column="service", alias="Service Name")
        assert filt.column == "service"
        assert filt.alias == "Service Name"

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PresetFilterInput(column="test", alias="test", extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestBoardViewFilter:
    """Test BoardViewFilter model from tool_inputs."""

    def test_view_filter(self):
        """Test view filter creation."""
        filt = BoardViewFilter(column="status", operation=FilterOp.EQUALS, value="active")
        assert filt.column == "status"
        assert filt.operation == FilterOp.EQUALS

    def test_accepts_string_enum_coercion(self):
        """Test that string values are coerced to enum."""
        filt = BoardViewFilter(column="status", operation="=", value="active")
        assert filt.operation == FilterOp.EQUALS
        assert isinstance(filt.operation, FilterOp)

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BoardViewFilter(
                column="status", operation=FilterOp.EQUALS, value="active", extra="field"
            )

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestBoardViewInput:
    """Test BoardViewInput model."""

    def test_view(self):
        """Test view creation."""
        view = BoardViewInput(
            name="Production",
            filters=[BoardViewFilter(column="env", operation=FilterOp.EQUALS, value="prod")],
        )
        assert view.name == "Production"
        assert len(view.filters) == 1

    def test_view_without_filters(self):
        """Test view without filters."""
        view = BoardViewInput(name="All")
        assert view.name == "All"
        assert view.filters is None

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BoardViewInput(name="Test", extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestBoardToolInput:
    """Test BoardToolInput model."""

    def test_minimal_board(self):
        """Test minimal valid board."""
        board = BoardToolInput(name="My Board")
        assert board.name == "My Board"
        assert board.layout_generation == "auto"  # default

    def test_board_with_query_panels(self):
        """Test board with query panels."""
        board = BoardToolInput(
            name="Dashboard",
            inline_query_panels=[QueryPanelInput(name="Panel 1")],
        )
        assert len(board.inline_query_panels) == 1

    def test_board_with_all_panel_types(self):
        """Test board with all panel types."""
        board = BoardToolInput(
            name="Complete Board",
            inline_query_panels=[QueryPanelInput(name="Query")],
            inline_slo_panels=[
                SLOPanelInput(
                    name="SLO",
                    dataset="test",
                    sli=SLIInput(alias="test"),
                    target_percentage=99.9,
                )
            ],
            text_panels=[TextPanelInput(content="# Header")],
            slo_panels=["slo_123"],
        )
        assert len(board.inline_query_panels) == 1
        assert len(board.inline_slo_panels) == 1
        assert len(board.text_panels) == 1
        assert len(board.slo_panels) == 1

    def test_board_with_features(self):
        """Test board with tags, filters, and views."""
        board = BoardToolInput(
            name="Board",
            tags=[TagInput(key="team", value="platform")],
            preset_filters=[PresetFilterInput(column="service", alias="Service")],
            views=[BoardViewInput(name="Production")],
        )
        assert len(board.tags) == 1
        assert len(board.preset_filters) == 1
        assert len(board.views) == 1

    def test_manual_layout_mode(self):
        """Test manual layout mode."""
        board = BoardToolInput(name="Board", layout_generation="manual")
        assert board.layout_generation == "manual"

    def test_rejects_invalid_layout_generation(self):
        """Test that invalid layout mode is rejected."""
        with pytest.raises(ValidationError):
            BoardToolInput(name="Board", layout_generation="invalid")

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BoardToolInput(name="Board", extra="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestModelJsonSchema:
    """Test that models generate valid JSON schemas."""

    def test_position_schema(self):
        """Test PositionInput generates schema."""
        schema = PositionInput.model_json_schema()
        assert schema["type"] == "object"
        assert "additionalProperties" in schema
        assert schema["additionalProperties"] is False
        assert "x_coordinate" in schema["properties"]

    def test_query_panel_schema(self):
        """Test QueryPanelInput generates schema."""
        schema = QueryPanelInput.model_json_schema()
        assert schema["type"] == "object"
        assert "additionalProperties" in schema
        assert schema["additionalProperties"] is False
        assert "name" in schema["properties"]
        assert "calculations" in schema["properties"]

    def test_slo_tool_schema(self):
        """Test SLOToolInput generates schema."""
        schema = SLOToolInput.model_json_schema()
        assert schema["type"] == "object"
        assert "additionalProperties" in schema
        assert schema["additionalProperties"] is False
        assert "target_percentage" in schema["properties"]
        assert "target_nines" not in schema["properties"]  # Removed

    def test_board_tool_schema(self):
        """Test BoardToolInput generates schema."""
        schema = BoardToolInput.model_json_schema()
        assert schema["type"] == "object"
        assert "additionalProperties" in schema
        assert schema["additionalProperties"] is False
        assert "inline_query_panels" in schema["properties"]
