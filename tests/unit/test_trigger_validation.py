"""Unit tests for trigger validation (shared validators and TriggerToolInput)."""

import pytest
from pydantic import ValidationError

from honeycomb.models.tool_inputs import TriggerToolInput
from honeycomb.validation.triggers import (
    validate_exceeded_limit,
    validate_time_range_frequency_ratio,
    validate_trigger_frequency,
    validate_trigger_time_range,
)


class TestSharedValidationFunctions:
    """Test shared validation functions directly."""

    def test_validate_trigger_time_range_valid(self):
        """Test valid time ranges pass."""
        validate_trigger_time_range(300)  # 5 min
        validate_trigger_time_range(1800)  # 30 min
        validate_trigger_time_range(3600)  # 1 hour (max)

    def test_validate_trigger_time_range_too_large(self):
        """Test time range > 3600s is rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_trigger_time_range(7200)

        error_str = str(exc_info.value)
        assert "3600" in error_str
        assert "7200" in error_str

    def test_validate_trigger_frequency_valid(self):
        """Test valid frequencies pass."""
        validate_trigger_frequency(60)  # 1 min (min)
        validate_trigger_frequency(300)  # 5 min
        validate_trigger_frequency(86400)  # 1 day (max)

    def test_validate_trigger_frequency_too_low(self):
        """Test frequency < 60s is rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_trigger_frequency(30)

        error_str = str(exc_info.value)
        assert "60" in error_str
        assert "30" in error_str

    def test_validate_trigger_frequency_too_high(self):
        """Test frequency > 86400s is rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_trigger_frequency(100000)

        error_str = str(exc_info.value)
        assert "86400" in error_str

    def test_validate_time_range_frequency_ratio_valid(self):
        """Test valid time_range/frequency ratios."""
        validate_time_range_frequency_ratio(240, 60)  # 240 = 60 * 4
        validate_time_range_frequency_ratio(1200, 300)  # 1200 = 300 * 4
        validate_time_range_frequency_ratio(3600, 900)  # 3600 = 900 * 4

    def test_validate_time_range_frequency_ratio_invalid(self):
        """Test time_range > frequency * 4 is rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_time_range_frequency_ratio(300, 60)  # 300 > 60*4=240

        error_str = str(exc_info.value)
        assert "300" in error_str
        assert "60" in error_str
        assert "240" in error_str
        assert "4x" in error_str.lower()

    def test_validate_exceeded_limit_valid(self):
        """Test valid exceeded_limit values."""
        validate_exceeded_limit(1)
        validate_exceeded_limit(3)
        validate_exceeded_limit(5)

    def test_validate_exceeded_limit_too_low(self):
        """Test exceeded_limit < 1 is rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_exceeded_limit(0)

        error_str = str(exc_info.value)
        assert "1-5" in error_str or "1" in error_str

    def test_validate_exceeded_limit_too_high(self):
        """Test exceeded_limit > 5 is rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_exceeded_limit(10)

        error_str = str(exc_info.value)
        assert "1-5" in error_str or "5" in error_str


class TestTriggerToolInputValidation:
    """Test TriggerToolInput model validation."""

    def test_valid_trigger_simple(self):
        """Test valid simple trigger."""
        data = {
            "name": "High Error Rate",
            "dataset": "api-logs",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        }

        trigger = TriggerToolInput.model_validate(data)
        assert trigger.name == "High Error Rate"
        assert trigger.query.time_range == 900
        assert trigger.frequency == 900

    def test_time_range_exceeds_max_rejected(self):
        """Test that time_range > 3600s is rejected."""
        data = {
            "name": "Test",
            "dataset": "test",
            "query": {"time_range": 7200, "calculations": [{"op": "COUNT"}]},
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        }

        with pytest.raises(ValidationError) as exc_info:
            TriggerToolInput.model_validate(data)

        error_str = str(exc_info.value)
        assert "3600" in error_str
        assert "7200" in error_str

    def test_time_range_frequency_ratio_violated(self):
        """Test that time_range > frequency * 4 is rejected."""
        data = {
            "name": "Test",
            "dataset": "test",
            "query": {"time_range": 300, "calculations": [{"op": "COUNT"}]},
            "threshold": {"op": ">", "value": 100},
            "frequency": 60,  # 60 * 4 = 240, but time_range=300
        }

        with pytest.raises(ValidationError) as exc_info:
            TriggerToolInput.model_validate(data)

        error_str = str(exc_info.value)
        assert "300" in error_str
        assert "60" in error_str
        assert "240" in error_str
        assert "4x" in error_str.lower()

    def test_frequency_too_low_rejected(self):
        """Test that frequency < 60s is rejected at field level."""
        data = {
            "name": "Test",
            "dataset": "test",
            "query": {"time_range": 300, "calculations": [{"op": "COUNT"}]},
            "threshold": {"op": ">", "value": 100},
            "frequency": 30,  # Too low
        }

        with pytest.raises(ValidationError) as exc_info:
            TriggerToolInput.model_validate(data)

        error_str = str(exc_info.value)
        assert "frequency" in error_str.lower()

    def test_exceeded_limit_too_high_rejected(self):
        """Test that exceeded_limit > 5 is rejected at field level."""
        data = {
            "name": "Test",
            "dataset": "test",
            "query": {"time_range": 900, "calculations": [{"op": "COUNT"}]},
            "threshold": {"op": ">", "value": 100, "exceeded_limit": 10},
            "frequency": 900,
        }

        with pytest.raises(ValidationError) as exc_info:
            TriggerToolInput.model_validate(data)

        error_str = str(exc_info.value)
        assert "exceeded_limit" in error_str.lower()

    def test_multiple_calculations_rejected(self):
        """Test that triggers with >1 calculation are rejected."""
        data = {
            "name": "Test",
            "dataset": "test",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}, {"op": "AVG", "column": "duration_ms"}],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        }

        with pytest.raises(ValidationError) as exc_info:
            TriggerToolInput.model_validate(data)

        error_str = str(exc_info.value)
        assert "calculation" in error_str.lower()

    def test_valid_trigger_with_filters(self):
        """Test valid trigger with filters."""
        data = {
            "name": "High Error Rate",
            "dataset": "api-logs",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": ">=", "value": 500}],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        }

        trigger = TriggerToolInput.model_validate(data)
        assert len(trigger.query.filters) == 1
        assert trigger.query.filters[0].column == "status_code"

    def test_valid_trigger_with_all_fields(self):
        """Test valid trigger with all optional fields."""
        data = {
            "name": "Production Errors",
            "description": "Alert on production errors",
            "dataset": "api-logs",
            "query": {
                "time_range": 1200,
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "env", "op": "=", "value": "production"}],
                "breakdowns": ["service"],
            },
            "threshold": {"op": ">=", "value": 50, "exceeded_limit": 2},
            "frequency": 300,
            "alert_type": "on_true",
            "disabled": False,
            "recipients": [{"type": "email", "target": "oncall@example.com"}],
            "tags": [{"key": "team", "value": "platform"}],
        }

        trigger = TriggerToolInput.model_validate(data)
        assert trigger.name == "Production Errors"
        assert trigger.description == "Alert on production errors"
        assert trigger.threshold.exceeded_limit == 2
        assert trigger.alert_type == "on_true"
        assert len(trigger.recipients) == 1
        assert len(trigger.tags) == 1

    def test_tags_limit_enforced(self):
        """Test that >10 tags are rejected."""
        key_names = [
            "team",
            "environment",
            "region",
            "owner",
            "service_type",
            "cost_center",
            "application",
            "tier",
            "criticality",
            "version",
            "extra",
        ]
        tags = [{"key": key_names[i], "value": f"value{i}"} for i in range(11)]

        data = {
            "name": "Test",
            "dataset": "test",
            "query": {"time_range": 900, "calculations": [{"op": "COUNT"}]},
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
            "tags": tags,
        }

        with pytest.raises(ValidationError) as exc_info:
            TriggerToolInput.model_validate(data)

        error_str = str(exc_info.value)
        assert "11" in error_str
        assert "10" in error_str


class TestTriggerValidationErrorMessages:
    """Test that validation error messages are clear and actionable."""

    def test_time_range_frequency_error_message(self):
        """Test that time_range/frequency violation has clear message."""
        data = {
            "name": "Test",
            "dataset": "test",
            "query": {"time_range": 500, "calculations": [{"op": "COUNT"}]},
            "threshold": {"op": ">", "value": 100},
            "frequency": 60,  # Max time_range = 60*4 = 240
        }

        with pytest.raises(ValidationError) as exc_info:
            TriggerToolInput.model_validate(data)

        error_str = str(exc_info.value)
        assert "500" in error_str  # Current time_range
        assert "60" in error_str  # Frequency
        assert "240" in error_str  # Max allowed (60*4)
        assert "increase frequency" in error_str.lower()
        assert "decrease time range" in error_str.lower()

    def test_time_range_max_error_message(self):
        """Test that time_range > 3600 has clear message."""
        data = {
            "name": "Test",
            "dataset": "test",
            "query": {"time_range": 10000, "calculations": [{"op": "COUNT"}]},
            "threshold": {"op": ">", "value": 100},
            "frequency": 3600,
        }

        with pytest.raises(ValidationError) as exc_info:
            TriggerToolInput.model_validate(data)

        error_str = str(exc_info.value)
        assert "3600" in error_str
        assert "10000" in error_str


class TestTriggerValidationRealWorldScenarios:
    """Test validation with real-world trigger scenarios."""

    def test_common_valid_triggers(self):
        """Test common valid trigger patterns."""
        valid_triggers = [
            # Every minute, 10 min lookback
            {
                "name": "High Error Rate",
                "dataset": "api-logs",
                "query": {"time_range": 240, "calculations": [{"op": "COUNT"}]},
                "threshold": {"op": ">", "value": 100},
                "frequency": 60,
            },
            # Every 5 min, 20 min lookback
            {
                "name": "P99 Latency",
                "dataset": "api-logs",
                "query": {
                    "time_range": 1200,
                    "calculations": [{"op": "P99", "column": "duration_ms"}],
                },
                "threshold": {"op": ">=", "value": 2000},
                "frequency": 300,
            },
            # Every 15 min, 1 hour lookback
            {
                "name": "Error Count",
                "dataset": "api-logs",
                "query": {"time_range": 3600, "calculations": [{"op": "COUNT"}]},
                "threshold": {"op": ">", "value": 50},
                "frequency": 900,
            },
        ]

        for trigger_data in valid_triggers:
            trigger = TriggerToolInput.model_validate(trigger_data)
            assert trigger.name == trigger_data["name"]

    def test_common_invalid_triggers(self):
        """Test common invalid trigger patterns."""
        invalid_triggers = [
            # time_range too long for frequency
            {
                "name": "Bad Ratio",
                "dataset": "test",
                "query": {"time_range": 300, "calculations": [{"op": "COUNT"}]},
                "threshold": {"op": ">", "value": 100},
                "frequency": 60,  # 60*4=240 < 300
            },
            # time_range > 3600
            {
                "name": "Too Long",
                "dataset": "test",
                "query": {"time_range": 7200, "calculations": [{"op": "COUNT"}]},
                "threshold": {"op": ">", "value": 100},
                "frequency": 3600,
            },
            # frequency too low
            {
                "name": "Too Frequent",
                "dataset": "test",
                "query": {"time_range": 60, "calculations": [{"op": "COUNT"}]},
                "threshold": {"op": ">", "value": 100},
                "frequency": 30,
            },
        ]

        for trigger_data in invalid_triggers:
            with pytest.raises(ValidationError):
                TriggerToolInput.model_validate(trigger_data)


class TestTriggerQueryConstraints:
    """Test trigger-specific query field constraints per Honeycomb API rules."""

    def test_heatmap_calculation_rejected(self):
        """Test that HEATMAP calculations are rejected for triggers."""
        data = {
            "name": "Invalid HEATMAP Trigger",
            "dataset": "test",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "HEATMAP", "column": "duration_ms"}],
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900,
        }

        with pytest.raises(ValidationError) as exc_info:
            TriggerToolInput.model_validate(data)

        error_str = str(exc_info.value)
        assert "heatmap" in error_str.lower()
        assert "may not use" in error_str.lower()

    def test_trigger_query_input_rejects_orders_field(self):
        """Test that TriggerQueryInput model doesn't accept orders field.

        This enforces the Honeycomb API constraint: triggers don't support orders.
        The field is excluded from the model (extra="forbid").
        """
        from honeycomb.models.tool_inputs import TriggerQueryInput

        # This should fail because TriggerQueryInput doesn't have orders field
        with pytest.raises(ValidationError) as exc_info:
            TriggerQueryInput(
                time_range=900,
                calculations=[{"op": "COUNT"}],
                orders=[{"op": "COUNT", "order": "descending"}],  # Not allowed!
            )

        error_str = str(exc_info.value)
        assert "extra" in error_str.lower() or "not permitted" in error_str.lower()
        assert "orders" in error_str.lower()

    def test_trigger_query_input_rejects_limit_field(self):
        """Test that TriggerQueryInput model doesn't accept limit field.

        This enforces the Honeycomb API constraint: triggers don't support limit.
        The field is excluded from the model (extra="forbid").
        """
        from honeycomb.models.tool_inputs import TriggerQueryInput

        # This should fail because TriggerQueryInput doesn't have limit field
        with pytest.raises(ValidationError) as exc_info:
            TriggerQueryInput(
                time_range=900,
                calculations=[{"op": "COUNT"}],
                limit=100,  # Not allowed!
            )

        error_str = str(exc_info.value)
        assert "extra" in error_str.lower() or "not permitted" in error_str.lower()
        assert "limit" in error_str.lower()
