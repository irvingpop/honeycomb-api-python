"""Unit tests for board duplicate query validation."""

import pytest
from pydantic import ValidationError

from honeycomb.models.tool_inputs import BoardToolInput


def test_duplicate_queries_rejected():
    """Test that duplicate query specifications are rejected."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [
            {
                "type": "query",
                "name": "Application Errors",
                "dataset": "java-honeycomb",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": "=", "value": 2}],
                "breakdowns": ["service.name"],
                "orders": [{"op": "COUNT", "order": "descending"}],
                "limit": 50,
                "time_range": 3600,
                "chart_type": "cbar",
            },
            {
                "type": "query",
                "name": "Bytes Received/s - Errors by Service",
                "dataset": "java-honeycomb",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": "=", "value": 2}],
                "breakdowns": ["service.name"],
                "time_range": 3600,
                "chart_type": "stacked",  # Different visualization
            },
        ],
    }

    with pytest.raises(ValidationError) as exc_info:
        BoardToolInput.model_validate(test_data)

    error_str = str(exc_info.value)
    assert "Duplicate query specifications detected" in error_str
    assert "Application Errors" in error_str
    assert "Bytes Received/s" in error_str


def test_multiple_duplicate_sets():
    """Test that multiple sets of duplicates are all reported."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [
            {
                "type": "query",
                "name": "Panel 1",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": "=", "value": 2}],
                "time_range": 3600,
            },
            {
                "type": "query",
                "name": "Panel 2",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": "=", "value": 2}],
                "time_range": 3600,
            },
            {
                "type": "query",
                "name": "Panel 3",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": "=", "value": 1}],
                "time_range": 3600,
            },
            {
                "type": "query",
                "name": "Panel 4",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": "=", "value": 1}],
                "time_range": 3600,
            },
        ],
    }

    with pytest.raises(ValidationError) as exc_info:
        BoardToolInput.model_validate(test_data)

    error_str = str(exc_info.value)
    # Should mention both duplicate pairs
    assert "Panel 1" in error_str and "Panel 2" in error_str
    assert "Panel 3" in error_str and "Panel 4" in error_str


def test_different_orders_still_duplicate():
    """Test that different orders don't prevent duplicate detection."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [
            {
                "type": "query",
                "name": "Panel 1",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "breakdowns": ["service"],
                "orders": [{"op": "COUNT", "order": "descending"}],
                "time_range": 3600,
            },
            {
                "type": "query",
                "name": "Panel 2",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "breakdowns": ["service"],
                "orders": [{"op": "COUNT", "order": "ascending"}],  # Different order
                "time_range": 3600,
            },
        ],
    }

    with pytest.raises(ValidationError) as exc_info:
        BoardToolInput.model_validate(test_data)

    error_str = str(exc_info.value)
    assert "orders, limits, or chart_types do NOT make queries unique" in error_str


def test_different_limits_still_duplicate():
    """Test that different limits don't prevent duplicate detection."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [
            {
                "type": "query",
                "name": "Panel 1",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": ">=", "value": 500}],
                "limit": 10,
                "time_range": 3600,
            },
            {
                "type": "query",
                "name": "Panel 2",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": ">=", "value": 500}],
                "limit": 50,  # Different limit
                "time_range": 3600,
            },
        ],
    }

    with pytest.raises(ValidationError):
        BoardToolInput.model_validate(test_data)


def test_non_duplicate_queries_accepted():
    """Test that non-duplicate queries are accepted."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [
            {
                "type": "query",
                "name": "Error Count",
                "dataset": "java-honeycomb",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": ">=", "value": 500}],
                "time_range": 3600,
            },
            {
                "type": "query",
                "name": "P99 Latency",
                "dataset": "java-honeycomb",
                "calculations": [{"op": "P99", "column": "duration_ms"}],
                "time_range": 3600,
            },
        ],
    }

    # Should not raise
    board = BoardToolInput.model_validate(test_data)
    assert board.name == "Test Dashboard"
    assert len(board.panels) == 2


def test_different_filters_not_duplicate():
    """Test that different filters make queries unique."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [
            {
                "type": "query",
                "name": "Errors",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": "=", "value": 500}],
                "time_range": 3600,
            },
            {
                "type": "query",
                "name": "Warnings",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": "=", "value": 400}],
                "time_range": 3600,
            },
        ],
    }

    # Should not raise
    board = BoardToolInput.model_validate(test_data)
    assert len(board.panels) == 2


def test_different_breakdowns_not_duplicate():
    """Test that different breakdowns make queries unique."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [
            {
                "type": "query",
                "name": "By Service",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "breakdowns": ["service"],
                "time_range": 3600,
            },
            {
                "type": "query",
                "name": "By Endpoint",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "breakdowns": ["endpoint"],
                "time_range": 3600,
            },
        ],
    }

    # Should not raise
    board = BoardToolInput.model_validate(test_data)
    assert len(board.panels) == 2


def test_different_calculations_not_duplicate():
    """Test that different calculations make queries unique."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [
            {
                "type": "query",
                "name": "Count",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "time_range": 3600,
            },
            {
                "type": "query",
                "name": "Average",
                "dataset": "test-dataset",
                "calculations": [{"op": "AVG", "column": "duration_ms"}],
                "time_range": 3600,
            },
        ],
    }

    # Should not raise
    board = BoardToolInput.model_validate(test_data)
    assert len(board.panels) == 2


def test_no_query_panels():
    """Test that boards with no query panels don't error."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [{"type": "text", "content": "## Test"}],
    }

    # Should not raise
    board = BoardToolInput.model_validate(test_data)
    assert board.name == "Test Dashboard"
    assert len(board.panels) == 1


def test_mixed_panel_types_no_duplicate_error():
    """Test that boards with mixed panel types validate correctly."""
    test_data = {
        "name": "Test Dashboard",
        "panels": [
            {
                "type": "query",
                "name": "Error Count",
                "dataset": "test-dataset",
                "calculations": [{"op": "COUNT"}],
                "time_range": 3600,
            },
            {"type": "text", "content": "## Section Header"},
            {"type": "existing_slo", "slo_id": "slo-123"},
        ],
    }

    # Should not raise
    board = BoardToolInput.model_validate(test_data)
    assert board.name == "Test Dashboard"
    assert len(board.panels) == 3
