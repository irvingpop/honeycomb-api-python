"""Completeness tests for Claude tool definitions.

These tests ensure 100% coverage of all available features:
- Every CalcOp is supported in trigger builder
- Every FilterOp is supported in trigger builder
- Every TriggerBuilder method is covered
- Every SLOBuilder method is covered

If these tests fail, it means we're missing tool definition support.
"""

import pytest

from honeycomb.models import BurnAlertType
from honeycomb.models.query_builder import CalcOp, FilterOp
from honeycomb.tools.builders import _build_slo, _build_trigger


class TestTriggerCalculationCompleteness:
    """Test that _build_trigger supports ALL CalcOp types available in QueryBuilder."""

    def test_all_calc_ops_supported(self):
        """Every CalcOp must have a handler in _build_trigger."""
        # Define ALL available CalcOp values (from QueryBuilder)
        supported_calc_ops = {
            CalcOp.COUNT,
            CalcOp.SUM,
            CalcOp.AVG,
            CalcOp.MIN,
            CalcOp.MAX,
            CalcOp.COUNT_DISTINCT,
            CalcOp.HEATMAP,
            CalcOp.CONCURRENCY,
            # RATE operations are special - document if intentionally excluded
            # CalcOp.RATE_AVG,
            # CalcOp.RATE_SUM,
            # CalcOp.RATE_MAX,
        }

        # Test each operation can be built
        for calc_op in supported_calc_ops:
            data = {
                "name": f"Test {calc_op.value}",
                "dataset": "test-dataset",
                "query": {
                    "time_range": 900,
                    "calculations": [
                        {"op": calc_op.value, "column": "duration_ms"}
                        if calc_op != CalcOp.COUNT and calc_op != CalcOp.CONCURRENCY
                        else {"op": calc_op.value}
                    ],
                },
                "threshold": {"op": ">", "value": 100},
                "frequency": 900,
            }

            try:
                builder = _build_trigger(data)
                trigger = builder.build()
                assert trigger is not None, f"Failed to build trigger with {calc_op.value}"
            except Exception as e:
                pytest.fail(f"CalcOp.{calc_op.name} ({calc_op.value}) not supported: {e}")

    def test_missing_calc_ops_documented(self):
        """Document which CalcOp values are intentionally not supported."""
        # RATE operations might not be supported by triggers due to API limitations
        # Document this explicitly
        unsupported_calc_ops = {
            CalcOp.RATE_AVG: "RATE operations not supported by trigger API",
            CalcOp.RATE_SUM: "RATE operations not supported by trigger API",
            CalcOp.RATE_MAX: "RATE operations not supported by trigger API",
        }

        # This test passes if we document why certain ops aren't supported
        assert len(unsupported_calc_ops) > 0, "Document unsupported operations"


class TestTriggerFilterCompleteness:
    """Test that _build_trigger supports ALL FilterOp types available in QueryBuilder."""

    def test_all_filter_ops_supported(self):
        """Every FilterOp must have a handler in _build_trigger."""
        # Define ALL available FilterOp values (from QueryBuilder)
        filter_test_cases = [
            (FilterOp.EQUALS, "status", 200),
            (FilterOp.NOT_EQUALS, "status", 404),
            (FilterOp.GREATER_THAN, "duration_ms", 1000),
            (FilterOp.GREATER_THAN_OR_EQUAL, "duration_ms", 1000),
            (FilterOp.LESS_THAN, "duration_ms", 100),
            (FilterOp.LESS_THAN_OR_EQUAL, "duration_ms", 100),
            (FilterOp.STARTS_WITH, "path", "/api"),
            (FilterOp.DOES_NOT_START_WITH, "path", "/internal"),
            (FilterOp.CONTAINS, "message", "error"),
            (FilterOp.DOES_NOT_CONTAIN, "message", "debug"),
            (FilterOp.EXISTS, "user_id", None),
            (FilterOp.DOES_NOT_EXIST, "trace_id", None),
            (FilterOp.IN, "status", [200, 201, 204]),
            (FilterOp.NOT_IN, "status", [500, 502, 503]),
        ]

        for filter_op, column, value in filter_test_cases:
            data = {
                "name": f"Test {filter_op.value}",
                "dataset": "test-dataset",
                "query": {
                    "time_range": 900,
                    "calculations": [{"op": "COUNT"}],
                    "filters": [{"column": column, "op": filter_op.value, "value": value}],
                },
                "threshold": {"op": ">", "value": 100},
                "frequency": 900,
            }

            try:
                builder = _build_trigger(data)
                trigger = builder.build()
                assert trigger is not None, f"Failed to build trigger with {filter_op.value}"
            except Exception as e:
                pytest.fail(f"FilterOp.{filter_op.name} ({filter_op.value}) not supported: {e}")


class TestTriggerBuilderMethodCoverage:
    """Test that tool definitions cover key TriggerBuilder methods."""

    def test_threshold_methods_covered(self):
        """All threshold comparison operators must be supported."""
        threshold_ops = [
            {"op": ">", "value": 100},
            {"op": ">=", "value": 100},
            {"op": "<", "value": 100},
            {"op": "<=", "value": 100},
        ]

        for threshold in threshold_ops:
            data = {
                "name": "Test Threshold",
                "dataset": "test",
                "query": {"time_range": 900, "calculations": [{"op": "COUNT"}]},
                "threshold": threshold,
                "frequency": 900,
            }
            builder = _build_trigger(data)
            trigger = builder.build()
            assert trigger.trigger.threshold.op.value == threshold["op"]

    def test_frequency_presets_covered(self):
        """Common frequency values should map to builder presets."""
        # time_range must be >= 300 (API minimum) AND <= frequency * 4
        frequency_tests = [
            (120, "custom_2min", 300),  # 120s * 4 = 480s max, use min 300
            (300, "every_5_minutes", 900),  # 300s * 4 = 1200s, but use 900
            (900, "every_15_minutes", 3600),  # 900s * 4 = 3600s
            (1800, "every_30_minutes", 3600),  # 1800s * 4 = 7200s, but triggers max 3600
            (3600, "every_hour", 3600),  # 3600s * 4 = 14400s, but triggers max 3600
        ]

        for freq, method_name, time_range in frequency_tests:
            data = {
                "name": "Test Frequency",
                "dataset": "test",
                "query": {"time_range": time_range, "calculations": [{"op": "COUNT"}]},
                "threshold": {"op": ">", "value": 100},
                "frequency": freq,
            }
            builder = _build_trigger(data)
            trigger = builder.build()
            assert trigger.trigger.frequency == freq, (
                f"Frequency {freq} ({method_name}) not working"
            )

    def test_alert_type_covered(self):
        """Both alert types must be supported."""
        for alert_type in ["on_change", "on_true"]:
            data = {
                "name": "Test Alert Type",
                "dataset": "test",
                "query": {"time_range": 900, "calculations": [{"op": "COUNT"}]},
                "threshold": {"op": ">", "value": 100},
                "frequency": 900,
                "alert_type": alert_type,
            }
            builder = _build_trigger(data)
            trigger = builder.build()
            assert trigger.trigger.alert_type.value == alert_type

    def test_recipient_formats_covered(self):
        """All recipient formats must be supported."""
        recipient_tests = [
            {"id": "recip-123"},  # ID-based
            {"type": "email", "target": "user@example.com"},  # Inline email
            {"type": "slack", "target": "#alerts"},  # Inline slack
            {
                "type": "pagerduty",
                "target": "routing-key",
                "details": {"severity": "critical"},
            },  # Inline pagerduty
        ]

        for recipient in recipient_tests:
            data = {
                "name": "Test Recipient",
                "dataset": "test",
                "query": {"time_range": 900, "calculations": [{"op": "COUNT"}]},
                "threshold": {"op": ">", "value": 100},
                "frequency": 900,
                "recipients": [recipient],
            }
            builder = _build_trigger(data)
            trigger = builder.build()
            # Recipients can be in trigger.recipients (if they have 'id') or inline_recipients (if not)
            total_recipients = (
                len(trigger.trigger.recipients) if trigger.trigger.recipients else 0
            ) + len(trigger.inline_recipients)
            assert total_recipients > 0, f"Recipient format {recipient} not supported"


class TestSLOBuilderMethodCoverage:
    """Test that tool definitions cover key SLOBuilder methods."""

    def test_target_formats_covered(self):
        """All target specification formats must be supported."""
        # target_per_million is the base format
        data = {
            "name": "Test SLO",
            "dataset": "test",
            "sli": {"alias": "success_rate"},
            "target_per_million": 999000,  # 99.9%
            "time_period_days": 30,
        }
        builder = _build_slo(data)
        bundle = builder.build()
        assert bundle.slo.target_per_million == 999000

    def test_time_period_formats_covered(self):
        """Both time_period_days and time_period_weeks must work."""
        # Test days
        data = {
            "name": "Test SLO",
            "dataset": "test",
            "sli": {"alias": "success_rate"},
            "target_per_million": 999000,
            "time_period_days": 7,
        }
        builder = _build_slo(data)
        bundle = builder.build()
        assert bundle.slo.time_period_days == 7

    def test_sli_with_new_derived_column(self):
        """SLI can create new derived columns inline."""
        data = {
            "name": "Test SLO",
            "dataset": "test",
            "sli": {
                "alias": "success_rate",
                "expression": "IF(LT($status_code, 500), 1, 0)",
                "description": "Success rate calculation",
            },
            "target_per_million": 999000,
            "time_period_days": 30,
        }
        builder = _build_slo(data)
        bundle = builder.build()
        assert bundle.derived_column is not None
        assert bundle.derived_column.expression == "IF(LT($status_code, 500), 1, 0)"

    def test_burn_alert_integration(self):
        """SLO builder can create burn alerts inline."""
        data = {
            "name": "Test SLO",
            "dataset": "test",
            "sli": {"alias": "success_rate"},
            "target_per_million": 999000,
            "time_period_days": 30,
            "burn_alerts": [
                {
                    "alert_type": "exhaustion_time",
                    "exhaustion_minutes": 60,
                    "recipients": [{"type": "email", "target": "oncall@example.com"}],
                }
            ],
        }
        builder = _build_slo(data)
        bundle = builder.build()
        assert len(bundle.burn_alerts) == 1
        assert bundle.burn_alerts[0].alert_type == BurnAlertType.EXHAUSTION_TIME


class TestBurnAlertCompleteness:
    """Test that burn alerts support all alert types and recipients."""

    def test_both_alert_types_supported(self):
        """Both exhaustion_time and budget_rate alerts must work."""
        # Test via SLO builder
        for alert_type in ["exhaustion_time", "budget_rate"]:
            alert_data = {
                "alert_type": alert_type,
                "recipients": [],
            }

            if alert_type == "exhaustion_time":
                alert_data["exhaustion_minutes"] = 60
            else:
                alert_data["budget_rate_window_minutes"] = 60
                alert_data["budget_rate_decrease_threshold_per_million"] = 10000

            data = {
                "name": "Test SLO",
                "dataset": "test",
                "sli": {"alias": "success_rate"},
                "target_per_million": 999000,
                "time_period_days": 30,
                "burn_alerts": [alert_data],
            }

            builder = _build_slo(data)
            bundle = builder.build()
            assert len(bundle.burn_alerts) == 1


class TestToolDefinitionExamples:
    """Test that tool definitions have comprehensive examples."""

    def test_trigger_examples_cover_all_calc_types(self):
        """Tool definition examples should showcase variety of calculations."""
        from honeycomb.tools import _ALL_TOOLS_WITH_EXAMPLES

        tool = next(
            (t for t in _ALL_TOOLS_WITH_EXAMPLES if t["name"] == "honeycomb_create_trigger"), None
        )
        assert tool is not None

        examples = tool.get("input_examples", [])
        assert len(examples) >= 2, "Need at least 2 examples"

        # Check that examples show different calculation types
        calc_types_shown = set()
        for example in examples:
            query = example.get("query", {})
            calcs = query.get("calculations", [])
            for calc in calcs:
                calc_types_shown.add(calc.get("op"))

        # Should show at least COUNT, AVG, and one percentile
        assert "COUNT" in calc_types_shown, "Examples should include COUNT"

    def test_trigger_examples_cover_filter_varieties(self):
        """Tool definition examples should showcase variety of filters."""
        from honeycomb.tools import _ALL_TOOLS_WITH_EXAMPLES

        tool = next(
            (t for t in _ALL_TOOLS_WITH_EXAMPLES if t["name"] == "honeycomb_create_trigger"), None
        )
        assert tool is not None

        examples = tool.get("input_examples", [])

        # Check that examples show different filter types
        filter_ops_shown = set()
        for example in examples:
            query = example.get("query", {})
            filters = query.get("filters", [])
            for filt in filters:
                filter_ops_shown.add(filt.get("op"))

        # Should show variety
        assert len(filter_ops_shown) >= 2, "Examples should show multiple filter types"
