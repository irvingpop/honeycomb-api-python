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
from honeycomb.models.recipients import EmailRecipientDetails
from honeycomb.models.triggers import (
    TriggerAlertType,
    TriggerThreshold,
    TriggerThresholdOp,
    TriggerWithInlineQuery,
    TriggerWithQueryReference,
)


class TestTriggerSerialization:
    """Trigger serialization must not change after migration."""

    def test_basic_trigger_manual_construction(self):
        """Test basic trigger with manual construction."""
        trigger = TriggerWithInlineQuery(
            name="Test Trigger",
            description="Test description",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query={
                "time_range": 900,
                "calculations": [Calculation(op=CalcOp.COUNT)],
            },
        )

        payload = trigger.model_dump(
            mode="json", exclude_none=True, exclude_defaults=True, by_alias=True
        )

        # Snapshot the exact structure
        # Note: disabled and alert_type excluded as they're default values (cleaner API payloads)
        assert payload == {
            "name": "Test Trigger",
            "description": "Test description",
            "threshold": {"op": ">", "value": 100.0},
            "frequency": 900,
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
            },
        }

    def test_trigger_with_threshold_exceeded_limit(self):
        """Test trigger with exceeded_limit in threshold."""
        trigger = TriggerWithInlineQuery(
            name="Test",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN_OR_EQUAL, value=150.0, exceeded_limit=3
            ),
            frequency=900,
            query={"time_range": 900},
        )

        payload = trigger.model_dump(
            mode="json", exclude_none=True, exclude_defaults=True, by_alias=True
        )

        assert payload["threshold"] == {"op": ">=", "value": 150.0, "exceeded_limit": 3}

    def test_trigger_with_complex_query(self):
        """Test trigger with filters and breakdowns."""
        trigger = TriggerWithInlineQuery(
            name="Complex Query Trigger",
            threshold=TriggerThreshold(op=TriggerThresholdOp.LESS_THAN, value=50.0),
            frequency=900,
            query={
                "time_range": 1800,
                "granularity": 60,
                "calculations": [Calculation(op=CalcOp.P99, column="duration_ms")],
                "filters": [
                    Filter(column="status_code", op=FilterOp.EQUALS, value=500),
                ],
                "breakdowns": ["endpoint"],
            },
        )

        payload = trigger.model_dump(
            mode="json", exclude_none=True, exclude_defaults=True, by_alias=True
        )

        assert payload["query"] == {
            "time_range": 1800,
            "granularity": 60,
            "calculations": [{"op": "P99", "column": "duration_ms"}],
            "filters": [{"column": "status_code", "op": "=", "value": 500}],
            "breakdowns": ["endpoint"],
        }

    def test_trigger_with_query_id(self):
        """Test trigger referencing a saved query."""
        trigger = TriggerWithQueryReference(
            name="Saved Query Trigger",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query_id="abc123",
        )

        payload = trigger.model_dump(
            mode="json", exclude_none=True, exclude_defaults=True, by_alias=True
        )

        assert "query" not in payload
        assert payload["query_id"] == "abc123"

    def test_trigger_with_alert_type_on_true(self):
        """Test trigger with on_true alert type."""
        trigger = TriggerWithInlineQuery(
            name="On True Trigger",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query={"time_range": 900},
            alert_type=TriggerAlertType.on_true,
        )

        payload = trigger.model_dump(
            mode="json", exclude_none=True, exclude_defaults=True, by_alias=True
        )

        assert payload["alert_type"] == "on_true"

    def test_trigger_disabled(self):
        """Test disabled trigger."""
        trigger = TriggerWithInlineQuery(
            name="Disabled Trigger",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query={"time_range": 900},
            disabled=True,
        )

        payload = trigger.model_dump(
            mode="json", exclude_none=True, exclude_defaults=True, by_alias=True
        )

        assert payload["disabled"] is True

    def test_trigger_with_recipients(self):
        """Test trigger with recipient list."""
        trigger = TriggerWithInlineQuery(
            name="Trigger with Recipients",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            frequency=900,
            query={"time_range": 900},
            recipients=[{"id": "recip1"}, {"id": "recip2"}],
        )

        payload = trigger.model_dump(
            mode="json", exclude_none=True, exclude_defaults=True, by_alias=True
        )

        assert payload["recipients"] == [{"id": "recip1"}, {"id": "recip2"}]

    def test_trigger_minimal(self):
        """Test trigger with minimal required fields."""
        trigger = TriggerWithInlineQuery(
            name="Minimal",
            threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100.0),
            query={"time_range": 900},
        )

        payload = trigger.model_dump(
            mode="json", exclude_none=True, exclude_defaults=True, by_alias=True
        )

        # Defaults are excluded for cleaner API payloads (API assumes defaults)
        assert "description" not in payload
        assert "query_id" not in payload
        assert "recipients" not in payload
        assert "tags" not in payload
        assert "baseline_details" not in payload
        assert "frequency" not in payload  # default 900 - excluded
        assert "disabled" not in payload  # default False - excluded
        assert "alert_type" not in payload  # default on_change - excluded


class TestColumnSerialization:
    """Column serialization must not change after migration."""

    def test_basic_column(self):
        """Test basic column with required fields."""
        column = ColumnCreate(key_name="test_column", type=ColumnType.string)

        payload = column.model_dump(mode="json", exclude_none=True)

        assert payload == {
            "key_name": "test_column",
            "type": "string",
            "hidden": False,
        }

    def test_column_with_description(self):
        """Test column with description."""
        column = ColumnCreate(
            key_name="duration_ms",
            type=ColumnType.float,
            description="Request duration in milliseconds",
        )

        payload = column.model_dump(mode="json", exclude_none=True)

        assert payload == {
            "key_name": "duration_ms",
            "type": "float",
            "hidden": False,
            "description": "Request duration in milliseconds",
        }

    def test_column_hidden(self):
        """Test hidden column."""
        column = ColumnCreate(key_name="internal_id", type=ColumnType.integer, hidden=True)

        payload = column.model_dump(mode="json", exclude_none=True)

        assert payload["hidden"] is True

    def test_column_all_types(self):
        """Test all column types serialize correctly."""
        types_map = {
            ColumnType.string: "string",
            ColumnType.integer: "integer",
            ColumnType.float: "float",
            ColumnType.boolean: "boolean",
        }

        for col_type, expected_str in types_map.items():
            column = ColumnCreate(key_name="test", type=col_type)
            payload = column.model_dump(mode="json", exclude_none=True)
            assert payload["type"] == expected_str


class TestMarkerSerialization:
    """Marker serialization must not change after migration."""

    def test_basic_marker(self):
        """Test basic marker with required fields."""
        marker = MarkerCreate(message="Test deploy", type="deploy")

        payload = marker.model_dump(mode="json", exclude_none=True)

        assert payload == {
            "message": "Test deploy",
            "type": "deploy",
        }

    def test_marker_with_start_time(self):
        """Test marker with explicit start time."""
        marker = MarkerCreate(message="Test deploy", type="deploy", start_time=1234567890)

        payload = marker.model_dump(mode="json", exclude_none=True)

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

        payload = marker.model_dump(mode="json", exclude_none=True)

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

        payload = marker.model_dump(mode="json", exclude_none=True)

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

        payload = marker.model_dump(mode="json", exclude_none=True)

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
        from honeycomb.models.recipients import EmailRecipient

        recipient = EmailRecipient(
            type="email",
            details=EmailRecipientDetails(email_address="alerts@example.com"),
        )

        payload = recipient.model_dump(mode="json", exclude_none=True)

        assert payload == {
            "type": "email",
            "details": {"email_address": "alerts@example.com"},
        }

    def test_email_recipient_dict_details(self):
        """Test email recipient with dict details (Pydantic converts)."""
        from honeycomb.models.recipients import EmailRecipient

        recipient = EmailRecipient(
            type="email",
            details={"email_address": "test@example.com"},  # type: ignore
        )

        payload = recipient.model_dump(mode="json", exclude_none=True)

        assert payload == {
            "type": "email",
            "details": {"email_address": "test@example.com"},
        }


class TestSLOSerialization:
    """SLO serialization must not change after migration."""

    def test_basic_slo(self):
        """Test basic SLO with required fields."""
        from honeycomb.models.slos import SLOCreate, SLOCreateSli

        slo = SLOCreate(
            name="API Availability",
            sli=SLOCreateSli(alias="success_rate"),
            time_period_days=30,
            target_per_million=999000,
        )

        payload = slo.model_dump(mode="json", exclude_none=True)

        assert payload == {
            "name": "API Availability",
            "sli": {"alias": "success_rate"},
            "time_period_days": 30,
            "target_per_million": 999000,
        }

    def test_slo_with_string_alias(self):
        """Test SLO with string alias (validator convenience)."""
        from honeycomb.models.slos import SLOCreate

        slo = SLOCreate(
            name="API Availability",
            sli="success_rate",  # String alias
            time_period_days=30,
            target_per_million=999000,
        )

        payload = slo.model_dump(mode="json", exclude_none=True)

        # Should serialize the same way as SLOCreateSli
        assert payload == {
            "name": "API Availability",
            "sli": {"alias": "success_rate"},
            "time_period_days": 30,
            "target_per_million": 999000,
        }

    def test_slo_with_description(self):
        """Test SLO with description."""
        from honeycomb.models.slos import SLOCreate, SLOCreateSli

        slo = SLOCreate(
            name="API Availability",
            description="Ensure API requests succeed",
            sli=SLOCreateSli(alias="success_rate"),
            time_period_days=30,
            target_per_million=999000,
        )

        payload = slo.model_dump(mode="json", exclude_none=True)

        assert payload["description"] == "Ensure API requests succeed"

    def test_slo_with_tags(self):
        """Test SLO with tags."""
        from honeycomb.models.slos import SLOCreate, SLOCreateSli, Tag

        slo = SLOCreate(
            name="API Availability",
            sli=SLOCreateSli(alias="success_rate"),
            time_period_days=30,
            target_per_million=999000,
            tags=[Tag(key="team", value="platform")],
        )

        payload = slo.model_dump(mode="json", exclude_none=True)

        assert payload["tags"] == [{"key": "team", "value": "platform"}]

    def test_slo_with_multiple_tags(self):
        """Test SLO with multiple tags."""
        from honeycomb.models.slos import SLOCreate, SLOCreateSli, Tag

        slo = SLOCreate(
            name="API Availability",
            sli=SLOCreateSli(alias="success_rate"),
            time_period_days=30,
            target_per_million=999000,
            tags=[
                Tag(key="team", value="platform"),
                Tag(key="service", value="api"),
            ],
        )

        payload = slo.model_dump(mode="json", exclude_none=True)

        assert payload["tags"] == [
            {"key": "team", "value": "platform"},
            {"key": "service", "value": "api"},
        ]

    def test_slo_with_dataset_slugs(self):
        """Test multi-dataset SLO."""
        from honeycomb.models.slos import SLOCreate, SLOCreateSli

        slo = SLOCreate(
            name="Multi-Dataset SLO",
            sli=SLOCreateSli(alias="success_rate"),
            time_period_days=30,
            target_per_million=999000,
            dataset_slugs=["api-logs", "web-logs"],
        )

        payload = slo.model_dump(mode="json", exclude_none=True)

        assert payload["dataset_slugs"] == ["api-logs", "web-logs"]

    def test_slo_excludes_none_values(self):
        """Test that SLO excludes None values from payload."""
        from honeycomb.models.slos import SLOCreate, SLOCreateSli

        slo = SLOCreate(
            name="Test SLO",
            sli=SLOCreateSli(alias="success_rate"),
            time_period_days=30,
            target_per_million=999000,
            description=None,
            tags=None,
            dataset_slugs=None,
        )

        payload = slo.model_dump(mode="json", exclude_none=True)

        assert "description" not in payload
        assert "tags" not in payload
        assert "dataset_slugs" not in payload


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
