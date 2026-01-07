"""Tests for board view models."""

from honeycomb.models.boards import (
    BoardView,
    BoardViewCreate,
    BoardViewFilter,
)
from honeycomb.models.query_builder import FilterOp


class TestFilterOp:
    """Tests for FilterOp enum (board view operations)."""

    def test_comparison_operators(self):
        """Test comparison operator values."""
        assert FilterOp.EQUALS.value == "="
        assert FilterOp.NOT_EQUALS.value == "!="
        assert FilterOp.GREATER_THAN.value == ">"
        assert FilterOp.GREATER_THAN_OR_EQUAL.value == ">="
        assert FilterOp.LESS_THAN.value == "<"
        assert FilterOp.LESS_THAN_OR_EQUAL.value == "<="

    def test_string_operators(self):
        """Test string operator values."""
        assert FilterOp.CONTAINS.value == "contains"
        assert FilterOp.DOES_NOT_CONTAIN.value == "does-not-contain"
        assert FilterOp.STARTS_WITH.value == "starts-with"
        assert FilterOp.DOES_NOT_START_WITH.value == "does-not-start-with"
        assert FilterOp.ENDS_WITH.value == "ends-with"
        assert FilterOp.DOES_NOT_END_WITH.value == "does-not-end-with"

    def test_existence_operators(self):
        """Test existence check operator values."""
        assert FilterOp.EXISTS.value == "exists"
        assert FilterOp.DOES_NOT_EXIST.value == "does-not-exist"

    def test_set_operators(self):
        """Test set operation values."""
        assert FilterOp.IN.value == "in"
        assert FilterOp.NOT_IN.value == "not-in"


class TestBoardViewFilter:
    """Tests for BoardViewFilter."""

    def test_filter_with_value(self):
        """Test filter with value."""
        f = BoardViewFilter(column="status", operation=FilterOp.EQUALS, value="active")
        assert f.column == "status"
        assert f.operation == FilterOp.EQUALS
        assert f.value == "active"

    def test_filter_without_value(self):
        """Test filter without value (exists/does-not-exist)."""
        f = BoardViewFilter(column="error", operation=FilterOp.EXISTS)
        assert f.column == "error"
        assert f.operation == FilterOp.EXISTS
        assert f.value is None

    def test_filter_with_numeric_value(self):
        """Test filter with numeric value."""
        f = BoardViewFilter(
            column="status_code", operation=FilterOp.GREATER_THAN_OR_EQUAL, value=400
        )
        assert f.column == "status_code"
        assert f.value == 400

    def test_filter_with_list_value(self):
        """Test filter with list value for IN operation."""
        f = BoardViewFilter(
            column="environment",
            operation=FilterOp.IN,
            value=["prod", "staging"],
        )
        assert f.column == "environment"
        assert f.value == ["prod", "staging"]

    def test_filter_serialization_with_value(self):
        """Test serialization with value."""
        f = BoardViewFilter(
            column="status_code", operation=FilterOp.GREATER_THAN_OR_EQUAL, value=400
        )
        data = f.model_dump_for_api()
        assert data == {"column": "status_code", "operation": ">=", "value": 400}

    def test_filter_serialization_without_value(self):
        """Test serialization without value."""
        f = BoardViewFilter(column="trace_id", operation=FilterOp.EXISTS)
        data = f.model_dump_for_api()
        assert data == {"column": "trace_id", "operation": "exists"}
        assert "value" not in data

    def test_filter_from_dict(self):
        """Test creating filter from dict."""
        f = BoardViewFilter.model_validate(
            {"column": "status", "operation": FilterOp.EQUALS, "value": "active"}
        )
        assert f.column == "status"
        assert f.operation == FilterOp.EQUALS
        assert f.value == "active"


class TestBoardViewCreate:
    """Tests for BoardViewCreate."""

    def test_create_with_filters(self):
        """Test creating view with filters."""
        view = BoardViewCreate(
            name="Active Services",
            filters=[BoardViewFilter(column="status", operation=FilterOp.EQUALS, value="active")],
        )
        assert view.name == "Active Services"
        assert len(view.filters) == 1
        assert view.filters[0].column == "status"

    def test_create_with_empty_filters(self):
        """Test creating view with empty filters."""
        view = BoardViewCreate(name="All Data", filters=[])
        assert view.name == "All Data"
        assert len(view.filters) == 0

    def test_create_with_multiple_filters(self):
        """Test creating view with multiple filters."""
        view = BoardViewCreate(
            name="Production Errors",
            filters=[
                BoardViewFilter(
                    column="environment",
                    operation=FilterOp.EQUALS,
                    value="production",
                ),
                BoardViewFilter(
                    column="status_code",
                    operation=FilterOp.GREATER_THAN_OR_EQUAL,
                    value=400,
                ),
            ],
        )
        assert view.name == "Production Errors"
        assert len(view.filters) == 2

    def test_serialization(self):
        """Test serialization to API format."""
        view = BoardViewCreate(
            name="Error View",
            filters=[
                BoardViewFilter(
                    column="status_code",
                    operation=FilterOp.GREATER_THAN_OR_EQUAL,
                    value=400,
                )
            ],
        )
        data = view.model_dump_for_api()
        assert data["name"] == "Error View"
        assert len(data["filters"]) == 1
        assert data["filters"][0]["column"] == "status_code"
        assert data["filters"][0]["operation"] == ">="
        assert data["filters"][0]["value"] == 400

    def test_serialization_empty_filters(self):
        """Test serialization with empty filters."""
        view = BoardViewCreate(name="All Data", filters=[])
        data = view.model_dump_for_api()
        assert data["name"] == "All Data"
        assert data["filters"] == []


class TestBoardView:
    """Tests for BoardView (response model)."""

    def test_create_from_dict(self):
        """Test creating BoardView from API response dict."""
        data = {
            "id": "view-123",
            "name": "My View",
            "filters": [{"column": "status", "operation": "=", "value": "active"}],
        }
        view = BoardView.model_validate(data)
        assert view.id == "view-123"
        assert view.name == "My View"
        assert len(view.filters) == 1
        assert view.filters[0].column == "status"

    def test_create_with_no_filters(self):
        """Test creating BoardView with no filters."""
        data = {"id": "view-456", "name": "All Data", "filters": []}
        view = BoardView.model_validate(data)
        assert view.id == "view-456"
        assert view.name == "All Data"
        assert len(view.filters) == 0

    def test_serialization_excludes_id(self):
        """Test serialization can exclude ID for export."""
        view = BoardView(
            id="view-789",
            name="Test View",
            filters=[BoardViewFilter(column="status", operation=FilterOp.EQUALS, value="active")],
        )
        data = view.model_dump(exclude={"id"}, mode="json")
        assert "id" not in data
        assert data["name"] == "Test View"
        assert len(data["filters"]) == 1
