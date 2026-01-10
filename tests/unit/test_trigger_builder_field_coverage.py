"""Test that _build_trigger() correctly maps all tool input fields to TriggerBuilder.

This test prevents regressions where new fields are added but not properly
handled in the builder conversion logic.
"""

from honeycomb.tools.builders import _build_trigger


def test_all_trigger_fields_are_mapped():
    """Test that all trigger tool input fields are correctly mapped to TriggerBuilder."""
    # Tool input with ALL possible fields
    tool_input = {
        "name": "Complete Trigger Test",
        "description": "Tests all trigger fields",
        "dataset": "test-dataset",
        "query": {
            "time_range": 900,
            "calculations": [{"op": "COUNT"}],
            "filters": [{"column": "status_code", "op": ">=", "value": 500}],
            "filter_combination": "AND",
            "breakdowns": ["service"],
            "granularity": 60,
        },
        "threshold": {
            "op": ">",
            "value": 100,
            "exceeded_limit": 3,
        },
        "frequency": 900,
        "alert_type": "on_true",
        "disabled": True,
        "recipients": [{"type": "email", "target": "test@example.com"}],
        "tags": [{"key": "team", "value": "platform"}],
    }

    # Build and verify
    builder = _build_trigger(tool_input)
    bundle = builder.build()
    trigger = bundle.trigger

    # Verify all fields are set
    assert trigger.name == "Complete Trigger Test"
    assert trigger.description == "Tests all trigger fields"
    assert trigger.query.time_range == 900
    assert trigger.query.granularity == 60, "granularity not set!"
    assert trigger.query.filters is not None and len(trigger.query.filters) == 1
    assert trigger.query.filter_combination == "AND", "filter_combination not set!"
    assert trigger.query.breakdowns == ["service"]
    assert trigger.threshold.op.value == ">"
    assert trigger.threshold.value == 100
    assert trigger.threshold.exceeded_limit == 3
    assert trigger.frequency == 900
    assert trigger.alert_type.value == "on_true"
    assert trigger.disabled is True
    assert len(bundle.trigger.tags) == 1
    assert bundle.trigger.tags[0].key == "team"


def test_trigger_granularity_is_preserved():
    """Regression test for granularity field in triggers."""
    tool_input = {
        "name": "Granularity Test",
        "dataset": "test",
        "query": {
            "time_range": 900,
            "calculations": [{"op": "COUNT"}],
            "granularity": 120,  # Must be preserved
        },
        "threshold": {"op": ">", "value": 100},
        "frequency": 900,
    }

    builder = _build_trigger(tool_input)
    bundle = builder.build()

    assert bundle.trigger.query.granularity == 120, "granularity was lost"
