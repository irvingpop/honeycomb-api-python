"""Serialization snapshot tests - capture CURRENT behavior before DMCG migration.

These tests ensure that after migrating to datamodel-code-generator models,
the API payloads remain IDENTICAL to prevent breaking changes.

IMPORTANT: These tests capture the pre-migration baseline. Do NOT modify these
tests until after the migration is complete and validated.
"""

import pytest

from honeycomb.models.columns import ColumnCreate, ColumnType
from honeycomb.models.markers import MarkerCreate
from honeycomb.models.query_builder import CalcOp, Calculation, Filter, FilterOp
from honeycomb.models.recipients import EmailRecipientDetails, RecipientCreate, RecipientType
from honeycomb.models.triggers import (
    TriggerAlertType,
    TriggerCreate,
    TriggerQuery,
    TriggerThreshold,
    TriggerThresholdOp,
)


class TestTriggerSerialization:
    """Trigger serialization must not change after migration."""

    def test_basic_trigger_manual_construction(self):
        """Test basic trigger with manual construction."""
        trigger = TriggerCreate(
            name="Test Trigger",
            description="Test description",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query=TriggerQuery(
                time_range=900,
                calculations=[Calculation(op=CalcOp.COUNT)],
            ),
        )

        payload = trigger.model_dump_for_api()

        # Snapshot the exact structure
        assert payload == {
            "name": "Test Trigger",
            "description": "Test description",
            "threshold": {"op": ">", "value": 100.0},
            "frequency": 900,
            "disabled": False,
            "alert_type": "on_change",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
            },
        }

    def test_trigger_with_threshold_exceeded_limit(self):
        """Test trigger with exceeded_limit in threshold."""
        trigger = TriggerCreate(
            name="Test",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN_OR_EQUAL, value=150.0, exceeded_limit=3
            ),
            frequency=900,
            query=TriggerQuery(time_range=900),
        )

        payload = trigger.model_dump_for_api()

        assert payload["threshold"] == {"op": ">=", "value": 150.0, "exceeded_limit": 3}

    def test_trigger_with_complex_query(self):
        """Test trigger with filters and breakdowns."""
        trigger = TriggerCreate(
            name="Complex Query Trigger",
            threshold=TriggerThreshold(op=TriggerThresholdOp.LESS_THAN, value=50.0),
            frequency=900,
            query=TriggerQuery(
                time_range=1800,
                granularity=60,
                calculations=[Calculation(op=CalcOp.P99, column="duration_ms")],
                filters=[
                    Filter(column="status_code", op=FilterOp.EQUALS, value=500),
                ],
                breakdowns=["endpoint"],
            ),
        )

        payload = trigger.model_dump_for_api()

        assert payload["query"] == {
            "time_range": 1800,
            "granularity": 60,
            "calculations": [{"op": "P99", "column": "duration_ms"}],
            "filters": [{"column": "status_code", "op": "=", "value": 500}],
            "breakdowns": ["endpoint"],
        }

    def test_trigger_with_query_id(self):
        """Test trigger referencing a saved query."""
        trigger = TriggerCreate(
            name="Saved Query Trigger",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query_id="abc123",
        )

        payload = trigger.model_dump_for_api()

        assert "query" not in payload
        assert payload["query_id"] == "abc123"

    def test_trigger_with_alert_type_on_true(self):
        """Test trigger with on_true alert type."""
        trigger = TriggerCreate(
            name="On True Trigger",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query=TriggerQuery(time_range=900),
            alert_type=TriggerAlertType.ON_TRUE,
        )

        payload = trigger.model_dump_for_api()

        assert payload["alert_type"] == "on_true"

    def test_trigger_disabled(self):
        """Test disabled trigger."""
        trigger = TriggerCreate(
            name="Disabled Trigger",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query=TriggerQuery(time_range=900),
            disabled=True,
        )

        payload = trigger.model_dump_for_api()

        assert payload["disabled"] is True

    def test_trigger_with_recipients(self):
        """Test trigger with recipient list."""
        trigger = TriggerCreate(
            name="Trigger with Recipients",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query=TriggerQuery(time_range=900),
            recipients=[{"id": "recip1"}, {"id": "recip2"}],
        )

        payload = trigger.model_dump_for_api()

        assert payload["recipients"] == [{"id": "recip1"}, {"id": "recip2"}]

    def test_trigger_minimal(self):
        """Test trigger with minimal required fields."""
        trigger = TriggerCreate(
            name="Minimal",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            query=TriggerQuery(time_range=900),
        )

        payload = trigger.model_dump_for_api()

        # Should have defaults but no optional fields
        assert "description" not in payload
        assert "query_id" not in payload
        assert "recipients" not in payload
        assert "tags" not in payload
        assert "baseline_details" not in payload
        assert payload["frequency"] == 900  # default
        assert payload["disabled"] is False  # default
        assert payload["alert_type"] == "on_change"  # default


class TestColumnSerialization:
    """Column serialization must not change after migration."""

    def test_basic_column(self):
        """Test basic column with required fields."""
        column = ColumnCreate(key_name="test_column", type=ColumnType.STRING)

        payload = column.model_dump_for_api()

        assert payload == {
            "key_name": "test_column",
            "type": "string",
            "hidden": False,
        }

    def test_column_with_description(self):
        """Test column with description."""
        column = ColumnCreate(
            key_name="duration_ms",
            type=ColumnType.FLOAT,
            description="Request duration in milliseconds",
        )

        payload = column.model_dump_for_api()

        assert payload == {
            "key_name": "duration_ms",
            "type": "float",
            "hidden": False,
            "description": "Request duration in milliseconds",
        }

    def test_column_hidden(self):
        """Test hidden column."""
        column = ColumnCreate(key_name="internal_id", type=ColumnType.INTEGER, hidden=True)

        payload = column.model_dump_for_api()

        assert payload["hidden"] is True

    def test_column_all_types(self):
        """Test all column types serialize correctly."""
        types_map = {
            ColumnType.STRING: "string",
            ColumnType.INTEGER: "integer",
            ColumnType.FLOAT: "float",
            ColumnType.BOOLEAN: "boolean",
        }

        for col_type, expected_str in types_map.items():
            column = ColumnCreate(key_name="test", type=col_type)
            payload = column.model_dump_for_api()
            assert payload["type"] == expected_str


class TestMarkerSerialization:
    """Marker serialization must not change after migration."""

    def test_basic_marker(self):
        """Test basic marker with required fields."""
        marker = MarkerCreate(message="Test deploy", type="deploy")

        payload = marker.model_dump_for_api()

        assert payload == {
            "message": "Test deploy",
            "type": "deploy",
        }

    def test_marker_with_start_time(self):
        """Test marker with explicit start time."""
        marker = MarkerCreate(message="Test deploy", type="deploy", start_time=1234567890)

        payload = marker.model_dump_for_api()

        assert payload == {
            "message": "Test deploy",
            "type": "deploy",
            "start_time": 1234567890,
        }

    def test_marker_with_time_range(self):
        """Test marker with start and end times."""
        marker = MarkerCreate(
            message="Maintenance window",
            type="maintenance",
            start_time=1234567890,
            end_time=1234571490,
        )

        payload = marker.model_dump_for_api()

        assert payload == {
            "message": "Maintenance window",
            "type": "maintenance",
            "start_time": 1234567890,
            "end_time": 1234571490,
        }

    def test_marker_with_url(self):
        """Test marker with URL."""
        marker = MarkerCreate(
            message="Release v1.2.3",
            type="deploy",
            url="https://github.com/org/repo/releases/v1.2.3",
        )

        payload = marker.model_dump_for_api()

        assert payload == {
            "message": "Release v1.2.3",
            "type": "deploy",
            "url": "https://github.com/org/repo/releases/v1.2.3",
        }

    def test_marker_all_fields(self):
        """Test marker with all optional fields."""
        marker = MarkerCreate(
            message="Deploy with all details",
            type="deploy",
            start_time=1234567890,
            end_time=1234571490,
            url="https://example.com/deploy/123",
        )

        payload = marker.model_dump_for_api()

        assert payload == {
            "message": "Deploy with all details",
            "type": "deploy",
            "start_time": 1234567890,
            "end_time": 1234571490,
            "url": "https://example.com/deploy/123",
        }


class TestRecipientSerialization:
    """Recipient serialization must not change after migration."""

    def test_email_recipient(self):
        """Test email recipient."""
        recipient = RecipientCreate(
            type=RecipientType.EMAIL,
            details=EmailRecipientDetails(email_address="alerts@example.com"),
        )

        payload = recipient.model_dump_for_api()

        assert payload == {
            "type": "email",
            "details": {"email_address": "alerts@example.com"},
        }

    def test_email_recipient_dict_details(self):
        """Test email recipient with dict details (validator converts)."""
        recipient = RecipientCreate(
            type=RecipientType.EMAIL,
            details={"email_address": "test@example.com"},  # type: ignore
        )

        payload = recipient.model_dump_for_api()

        assert payload == {
            "type": "email",
            "details": {"email_address": "test@example.com"},
        }


class TestQueryComponentSerialization:
    """Test serialization of query components (Calculation, Filter) used in triggers."""

    def test_calculation_count(self):
        """Test COUNT calculation."""
        calc = Calculation(op=CalcOp.COUNT)
        assert calc.to_dict() == {"op": "COUNT"}

    def test_calculation_with_column(self):
        """Test calculation with column."""
        calc = Calculation(op=CalcOp.P99, column="duration_ms")
        assert calc.to_dict() == {"op": "P99", "column": "duration_ms"}

    def test_filter_equals(self):
        """Test filter with equals operator."""
        filt = Filter(column="status_code", op=FilterOp.EQUALS, value=200)
        assert filt.to_dict() == {"column": "status_code", "op": "=", "value": 200}

    def test_filter_exists(self):
        """Test filter with exists operator (no value)."""
        filt = Filter(column="error", op=FilterOp.EXISTS)
        result = filt.to_dict()
        assert result["column"] == "error"
        assert result["op"] == "exists"
        assert "value" not in result

    def test_filter_in_list(self):
        """Test filter with in operator (list value)."""
        filt = Filter(column="endpoint", op=FilterOp.IN, value=["/api/users", "/api/posts"])
        assert filt.to_dict() == {
            "column": "endpoint",
            "op": "in",
            "value": ["/api/users", "/api/posts"],
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
