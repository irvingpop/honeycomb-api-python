"""Test that _build_trigger() correctly maps all tool input fields to TriggerBuilder.

This test prevents regressions where new fields are added but not properly
handled in the builder conversion logic.
"""

from honeycomb.tools.builders import _build_trigger


def test_all_trigger_fields_are_mapped():
    """Test that all trigger tool input fields are correctly mapped to TriggerBuilder."""
    # Tool input with ALL possible fields (except granularity - not supported by API)
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
    assert trigger.query["time_range"] == 900
    # Note: granularity removed - API doesn't support it for triggers
    assert "granularity" not in trigger.query
    assert trigger.query["filters"] is not None and len(trigger.query["filters"]) == 1
    assert trigger.query["filter_combination"] == "AND", "filter_combination not set!"
    assert trigger.query["breakdowns"] == ["service"]
    assert trigger.threshold.op.value == ">"
    assert trigger.threshold.value == 100
    assert trigger.threshold.exceeded_limit == 3
    assert trigger.frequency == 900
    assert trigger.alert_type.value == "on_true"
    assert trigger.disabled is True
    assert len(bundle.trigger.tags) == 1
    assert bundle.trigger.tags[0].key == "team"


def test_trigger_granularity_is_rejected():
    """Test that granularity field is properly rejected by TriggerBuilder.

    Honeycomb API does not support granularity in trigger queries.
    """
    from pydantic import ValidationError

    tool_input = {
        "name": "Granularity Test",
        "dataset": "test",
        "query": {
            "time_range": 900,
            "calculations": [{"op": "COUNT"}],
            "granularity": 120,  # Should be rejected
        },
        "threshold": {"op": ">", "value": 100},
        "frequency": 900,
    }

    # Should fail validation (granularity not allowed in TriggerQueryInput)
    try:
        _build_trigger(tool_input)
        assert False, "Expected ValidationError for granularity field"
    except ValidationError as e:
        assert "granularity" in str(e).lower() or "extra" in str(e).lower()
