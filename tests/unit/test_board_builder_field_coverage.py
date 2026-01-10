"""Test that _build_board() correctly maps all QueryPanelInput fields to QueryBuilder.

This test prevents regressions where new fields added to QueryPanelInput are
not properly handled in the board builder conversion logic.
"""

from honeycomb.tools.builders import _build_board


def test_all_query_panel_fields_are_mapped():
    """Test that all QueryPanelInput query fields are correctly mapped to QueryBuilder.

    This is a regression test for bugs like missing granularity, filter_combination,
    or havings fields that caused duplicate QueryID errors.
    """
    # Create tool input with EVERY possible query field populated
    tool_input = {
        "name": "Complete Field Test",
        "layout_generation": "auto",
        "inline_query_panels": [
            {
                # Panel metadata
                "name": "Complete Query Panel",
                "description": "Tests all query fields",
                "style": "graph",
                # Query specification - ALL fields
                "dataset": "test-dataset",
                "time_range": 3600,
                "granularity": 60,  # CRITICAL: Must be set
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status", "op": "=", "value": 1}],
                "filter_combination": "AND",  # CRITICAL: Must be set
                "breakdowns": ["service"],
                "orders": [{"op": "COUNT", "order": "descending"}],
                "limit": 100,
                "havings": [
                    {"calculate_op": "COUNT", "op": ">", "value": 10}
                ],  # CRITICAL: Must be set
                "calculated_fields": [
                    {"name": "test_field", "expression": "MULTIPLY($duration_ms, 1000)"}
                ],
                "compare_time_offset_seconds": 86400,
                "chart_type": "line",
            }
        ],
    }

    # Build via _build_board()
    builder = _build_board(tool_input)
    bundle = builder.build()

    # Get the QueryBuilder that was created
    assert len(bundle.query_builder_panels) == 1
    qb_panel = bundle.query_builder_panels[0]
    qb = qb_panel.builder

    # Build the QuerySpec to inspect what was actually set
    spec = qb.build()

    # Verify ALL QuerySpec fields are correctly set (dataset is on builder, not spec)
    assert qb.get_dataset() == "test-dataset", "dataset not set"
    assert spec.time_range == 3600, "time_range not set"
    assert spec.granularity == 60, "granularity not set (BUG!)"
    assert spec.calculations is not None and len(spec.calculations) == 1, "calculations not set"
    assert spec.filters is not None and len(spec.filters) == 1, "filters not set"
    assert spec.filter_combination == "AND", "filter_combination not set (BUG!)"
    assert spec.breakdowns is not None and "service" in spec.breakdowns, "breakdowns not set"
    assert spec.orders is not None and len(spec.orders) == 1, "orders not set"
    assert spec.limit == 100, "limit not set"
    assert spec.havings is not None and len(spec.havings) == 1, "havings not set (BUG!)"
    assert spec.calculated_fields is not None and len(spec.calculated_fields) == 1, (
        "calculated_fields not set"
    )
    assert spec.compare_time_offset_seconds == 86400, "compare_time_offset_seconds not set"


def test_granularity_is_preserved():
    """Specific regression test for granularity field (caused duplicate QueryID bug)."""
    tool_input = {
        "name": "Granularity Test",
        "inline_query_panels": [
            {
                "name": "With Granularity",
                "dataset": "test",
                "time_range": 3600,
                "granularity": 120,  # Must be preserved
                "calculations": [{"op": "COUNT"}],
                "breakdowns": ["service"],
            }
        ],
    }

    builder = _build_board(tool_input)
    bundle = builder.build()
    spec = bundle.query_builder_panels[0].builder.build()

    assert spec.granularity == 120, "granularity was lost during conversion"


def test_filter_combination_is_preserved():
    """Specific regression test for filter_combination field."""
    tool_input = {
        "name": "Filter Combination Test",
        "inline_query_panels": [
            {
                "name": "OR Filters",
                "dataset": "test",
                "time_range": 3600,
                "calculations": [{"op": "COUNT"}],
                "filters": [
                    {"column": "status", "op": "=", "value": 500},
                    {"column": "status", "op": "=", "value": 404},
                ],
                "filter_combination": "OR",  # Must be preserved
            }
        ],
    }

    builder = _build_board(tool_input)
    bundle = builder.build()
    spec = bundle.query_builder_panels[0].builder.build()

    assert spec.filter_combination == "OR", "filter_combination was lost"


def test_havings_is_preserved():
    """Specific regression test for havings field."""
    tool_input = {
        "name": "Havings Test",
        "inline_query_panels": [
            {
                "name": "With Having Clause",
                "dataset": "test",
                "time_range": 3600,
                "calculations": [{"op": "COUNT"}],
                "breakdowns": ["service"],
                "havings": [
                    {"calculate_op": "COUNT", "op": ">", "value": 100}
                ],  # Must be preserved
            }
        ],
    }

    builder = _build_board(tool_input)
    bundle = builder.build()
    spec = bundle.query_builder_panels[0].builder.build()

    assert spec.havings is not None and len(spec.havings) == 1, "havings was lost"
    assert spec.havings[0].calculate_op.value == "COUNT"


def test_no_granularity_remains_none():
    """Test that missing granularity stays None (not replaced with default)."""
    tool_input = {
        "name": "No Granularity Test",
        "inline_query_panels": [
            {
                "name": "Without Granularity",
                "dataset": "test",
                "time_range": 3600,
                "calculations": [{"op": "COUNT"}],
                # No granularity field
            }
        ],
    }

    builder = _build_board(tool_input)
    bundle = builder.build()
    spec = bundle.query_builder_panels[0].builder.build()

    assert spec.granularity is None, "granularity should remain None when not specified"
