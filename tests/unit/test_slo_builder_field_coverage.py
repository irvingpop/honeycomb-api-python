"""Test that _build_slo() correctly maps all SLOToolInput fields to SLOBuilder.

This test prevents regressions where new fields are added but not properly
handled in the builder conversion logic.
"""

from honeycomb.tools.builders import _build_slo


def test_all_slo_fields_are_mapped():
    """Test that all SLOToolInput fields are correctly mapped to SLOBuilder."""
    # Tool input with ALL possible fields
    tool_input = {
        "name": "Complete SLO Test",
        "description": "Tests all SLO fields",
        "datasets": ["test-dataset"],
        "sli": {
            "alias": "success_rate",
            "expression": "IF(LT($status_code, 400), 1, 0)",
            "description": "Success indicator",
        },
        "target_percentage": 99.9,
        "time_period_days": 30,
        "tags": [{"key": "team", "value": "platform"}],
        "burn_alerts": [
            {
                "alert_type": "exhaustion_time",
                "description": "Budget exhausting",
                "exhaustion_minutes": 60,
                "recipients": [{"type": "email", "target": "oncall@example.com"}],
            }
        ],
    }

    # Build and verify
    builder = _build_slo(tool_input)
    bundle = builder.build()

    # Get the SLO
    slo = bundle.slo

    # Verify all fields are set
    assert slo.name == "Complete SLO Test"
    assert slo.description == "Tests all SLO fields"
    assert slo.sli.alias == "success_rate"
    assert slo.target_per_million == 999000  # 99.9% as per-million
    assert slo.time_period_days == 30
    assert len(slo.tags) == 1
    assert slo.tags[0].key == "team"

    # Verify burn alert was created
    assert len(bundle.burn_alerts) == 1
    assert bundle.burn_alerts[0].alert_type.value == "exhaustion_time"


def test_slo_tags_are_preserved():
    """Regression test for tags field in SLOs."""
    tool_input = {
        "name": "Tags Test",
        "datasets": ["test"],
        "sli": {"alias": "success"},
        "target_percentage": 99.9,
        "tags": [
            {"key": "team", "value": "platform"},
            {"key": "environment", "value": "production"},
        ],
    }

    builder = _build_slo(tool_input)
    bundle = builder.build()
    slo = bundle.slo

    assert len(slo.tags) == 2, "tags were lost"
    assert slo.tags[0].key == "team"
    assert slo.tags[1].key == "environment"
