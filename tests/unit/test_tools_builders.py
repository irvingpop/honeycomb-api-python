"""Unit tests for tool input to Builder conversion."""

from honeycomb.models import BurnAlertType
from honeycomb.tools.builders import _build_slo, _build_trigger


class TestBuildTrigger:
    """Test _build_trigger converter."""

    def test_minimal_trigger(self):
        """Can build trigger with minimal fields."""
        data = {
            "name": "Test Trigger",
            "dataset": "test-dataset",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        }

        builder = _build_trigger(data)
        trigger = builder.build()

        assert trigger.name == "Test Trigger"
        assert trigger.threshold.op.value == ">"
        assert trigger.threshold.value == 100
        assert trigger.frequency == 900

    def test_trigger_with_all_calculation_types(self):
        """All calculation types should work."""
        calc_types = [
            ("COUNT", None),
            ("AVG", "duration_ms"),
            ("SUM", "bytes_sent"),
            ("MIN", "response_time"),
            ("MAX", "response_time"),
            ("COUNT_DISTINCT", "user_id"),
            ("HEATMAP", "duration_ms"),
            ("CONCURRENCY", None),
            ("P50", "duration_ms"),
            ("P90", "duration_ms"),
            ("P95", "duration_ms"),
            ("P99", "duration_ms"),
        ]

        for op, column in calc_types:
            calc_dict = {"op": op}
            if column:
                calc_dict["column"] = column

            data = {
                "name": f"Test {op}",
                "dataset": "test",
                "query": {
                    "time_range": 900,
                    "calculations": [calc_dict],
                },
                "threshold": {"op": ">", "value": 100},
                "frequency": 900,
            }

            builder = _build_trigger(data)
            trigger = builder.build()
            assert trigger is not None, f"Failed to build trigger with {op}"

    def test_trigger_with_all_filter_operators(self):
        """All filter operators should work."""
        filter_tests = [
            ("=", "status", 200),
            ("!=", "status", 404),
            (">", "duration_ms", 1000),
            (">=", "duration_ms", 1000),
            ("<", "duration_ms", 100),
            ("<=", "duration_ms", 100),
            ("starts-with", "path", "/api"),
            ("does-not-start-with", "path", "/internal"),
            ("contains", "message", "error"),
            ("does-not-contain", "message", "debug"),
            ("exists", "user_id", None),
            ("does-not-exist", "trace_id", None),
            ("in", "status", [200, 201, 204]),
            ("not-in", "status", [500, 502, 503]),
        ]

        for op, column, value in filter_tests:
            data = {
                "name": f"Test {op}",
                "dataset": "test",
                "query": {
                    "time_range": 900,
                    "calculations": [{"op": "COUNT"}],
                    "filters": [{"column": column, "op": op, "value": value}],
                },
                "threshold": {"op": ">", "value": 100},
                "frequency": 900,
            }

            builder = _build_trigger(data)
            trigger = builder.build()
            assert trigger is not None, f"Failed to build trigger with filter op {op}"

    def test_trigger_with_recipients(self):
        """Can build trigger with various recipient formats."""
        data = {
            "name": "Test Recipients",
            "dataset": "test",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
            "recipients": [
                {"id": "recip-123"},
                {"type": "email", "target": "oncall@example.com"},
                {"type": "slack", "target": "#alerts"},
                {"type": "pagerduty", "target": "routing-key", "details": {"severity": "critical"}},
            ],
        }

        builder = _build_trigger(data)
        trigger = builder.build()
        assert len(trigger.recipients) == 4

    def test_trigger_with_tags(self):
        """Can build trigger with tags."""
        data = {
            "name": "Test Tags",
            "dataset": "test",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
            "tags": [
                {"key": "team", "value": "platform"},
                {"key": "severity", "value": "high"},
            ],
        }

        builder = _build_trigger(data)
        trigger = builder.build()
        assert trigger.tags is not None
        assert len(trigger.tags) == 2

    def test_trigger_frequency_presets(self):
        """Common frequencies should work."""
        frequencies = [60, 300, 900, 1800, 3600]

        for freq in frequencies:
            data = {
                "name": "Test Frequency",
                "dataset": "test",
                "query": {
                    "time_range": min(freq, 3600),  # Ensure time_range <= freq * 4
                    "calculations": [{"op": "COUNT"}],
                },
                "threshold": {"op": ">", "value": 100},
                "frequency": freq,
            }

            builder = _build_trigger(data)
            trigger = builder.build()
            assert trigger.frequency == freq

    def test_trigger_alert_types(self):
        """Both alert types should work."""
        for alert_type in ["on_change", "on_true"]:
            data = {
                "name": "Test Alert Type",
                "dataset": "test",
                "query": {
                    "time_range": 900,
                    "calculations": [{"op": "COUNT"}],
                },
                "threshold": {"op": ">", "value": 100},
                "frequency": 900,
                "alert_type": alert_type,
            }

            builder = _build_trigger(data)
            trigger = builder.build()
            assert trigger.alert_type.value == alert_type


class TestBuildSLO:
    """Test _build_slo converter."""

    def test_minimal_slo(self):
        """Can build SLO with minimal fields."""
        data = {
            "name": "Test SLO",
            "dataset": "test-dataset",
            "sli": {"alias": "success_rate"},
            "target_per_million": 999000,
            "time_period_days": 30,
        }

        builder = _build_slo(data)
        bundle = builder.build()

        assert bundle.slo.name == "Test SLO"
        assert bundle.slo.target_per_million == 999000
        assert bundle.slo.time_period_days == 30
        assert "test-dataset" in bundle.datasets

    def test_slo_with_new_derived_column(self):
        """Can build SLO that creates new derived column."""
        data = {
            "name": "Test SLO",
            "dataset": "test",
            "sli": {
                "alias": "success_rate",
                "expression": "IF(LT($status_code, 500), 1, 0)",
                "description": "Success rate",
            },
            "target_per_million": 999000,
            "time_period_days": 30,
        }

        builder = _build_slo(data)
        bundle = builder.build()

        assert bundle.derived_column is not None
        assert bundle.derived_column.alias == "success_rate"
        assert bundle.derived_column.expression == "IF(LT($status_code, 500), 1, 0)"

    def test_slo_with_burn_alerts(self):
        """Can build SLO with burn alerts."""
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
                },
                {
                    "alert_type": "budget_rate",
                    "budget_rate_window_minutes": 60,
                    "budget_rate_decrease_threshold_per_million": 10000,
                    "recipients": [{"type": "slack", "target": "#alerts"}],
                },
            ],
        }

        builder = _build_slo(data)
        bundle = builder.build()

        assert len(bundle.burn_alerts) == 2
        assert bundle.burn_alerts[0].alert_type == BurnAlertType.EXHAUSTION_TIME
        assert bundle.burn_alerts[0].exhaustion_minutes == 60
        assert bundle.burn_alerts[1].alert_type == BurnAlertType.BUDGET_RATE

    def test_slo_with_description(self):
        """Can build SLO with description."""
        data = {
            "name": "Test SLO",
            "description": "Testing SLO builder",
            "dataset": "test",
            "sli": {"alias": "success_rate"},
            "target_per_million": 999000,
            "time_period_days": 30,
        }

        builder = _build_slo(data)
        bundle = builder.build()

        assert bundle.slo.description == "Testing SLO builder"


class TestBuilderEdgeCases:
    """Test edge cases and error handling."""

    def test_trigger_with_exceeded_limit(self):
        """Can build trigger with exceeded_limit threshold."""
        data = {
            "name": "Test Exceeded Limit",
            "dataset": "test",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
            },
            "threshold": {"op": ">", "value": 100, "exceeded_limit": 3},
            "frequency": 900,
        }

        builder = _build_trigger(data)
        trigger = builder.build()

        assert trigger.threshold.exceeded_limit == 3

    def test_trigger_with_multiple_filters_and_combination(self):
        """Can build trigger with multiple filters and combination."""
        data = {
            "name": "Complex Filters",
            "dataset": "test",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
                "filters": [
                    {"column": "status", "op": ">=", "value": 500},
                    {"column": "service", "op": "=", "value": "api"},
                ],
                "filter_combination": "AND",
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        }

        builder = _build_trigger(data)
        trigger = builder.build()

        assert len(trigger.query.filters) == 2

    def test_trigger_with_breakdowns(self):
        """Can build trigger with breakdowns (group by)."""
        data = {
            "name": "Test Breakdowns",
            "dataset": "test",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
                "breakdowns": ["endpoint", "status_code"],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        }

        builder = _build_trigger(data)
        trigger = builder.build()

        assert trigger.query.breakdowns == ["endpoint", "status_code"]
