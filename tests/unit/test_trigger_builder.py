"""Tests for TriggerBuilder."""

import pytest

from honeycomb import (
    CalcOp,
    TriggerAlertType,
    TriggerBuilder,
    TriggerCreate,
    TriggerThresholdOp,
)


class TestTriggerBuilderBasics:
    """Tests for basic TriggerBuilder functionality."""

    def test_minimal_trigger(self):
        """Test building minimal trigger with defaults."""
        trigger = TriggerBuilder("Test Trigger").last_30_minutes().count().threshold_gt(100).build()
        assert isinstance(trigger, TriggerCreate)
        assert trigger.name == "Test Trigger"
        assert trigger.threshold.op == TriggerThresholdOp.GREATER_THAN
        assert trigger.threshold.value == 100.0
        assert trigger.frequency == 900  # Default 15 minutes

    def test_trigger_with_description(self):
        """Test adding description."""
        trigger = (
            TriggerBuilder("Test Trigger")
            .description("Test description")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .build()
        )
        assert trigger.description == "Test description"

    def test_dataset_scoped_trigger(self):
        """Test dataset-scoped trigger."""
        builder = (
            TriggerBuilder("Test Trigger")
            .dataset("my-dataset")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
        )
        trigger = builder.build()
        assert builder.get_dataset() == "my-dataset"
        assert trigger.name == "Test Trigger"

    def test_environment_wide_trigger(self):
        """Test environment-wide trigger."""
        builder = (
            TriggerBuilder("Test Trigger")
            .environment_wide()
            .last_30_minutes()
            .count()
            .threshold_gt(100)
        )
        assert builder.get_dataset() == "__all__"


class TestTriggerBuilderThresholds:
    """Tests for threshold configuration."""

    def test_threshold_gt(self):
        """Test greater than threshold."""
        trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_gt(100.5).build()
        assert trigger.threshold.op == TriggerThresholdOp.GREATER_THAN
        assert trigger.threshold.value == 100.5

    def test_threshold_gte(self):
        """Test greater than or equal threshold."""
        trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_gte(50).build()
        assert trigger.threshold.op == TriggerThresholdOp.GREATER_THAN_OR_EQUAL
        assert trigger.threshold.value == 50.0

    def test_threshold_lt(self):
        """Test less than threshold."""
        trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_lt(10).build()
        assert trigger.threshold.op == TriggerThresholdOp.LESS_THAN
        assert trigger.threshold.value == 10.0

    def test_threshold_lte(self):
        """Test less than or equal threshold."""
        trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_lte(25).build()
        assert trigger.threshold.op == TriggerThresholdOp.LESS_THAN_OR_EQUAL
        assert trigger.threshold.value == 25.0

    def test_exceeded_limit(self):
        """Test exceeded limit configuration."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .exceeded_limit(3)
            .build()
        )
        assert trigger.threshold.exceeded_limit == 3

    def test_missing_threshold_raises_error(self):
        """Test that missing threshold raises error."""
        with pytest.raises(ValueError, match="Threshold is required"):
            TriggerBuilder("Test").last_30_minutes().count().build()


class TestTriggerBuilderFrequency:
    """Tests for frequency configuration."""

    def test_every_minute(self):
        """Test every minute frequency."""
        trigger = (
            TriggerBuilder("Test")
            .time_range(240)  # 4 minutes - max for every_minute (60*4=240)
            .count()
            .threshold_gt(100)
            .every_minute()
            .build()
        )
        assert trigger.frequency == 60

    def test_every_5_minutes(self):
        """Test every 5 minutes frequency."""
        trigger = (
            TriggerBuilder("Test")
            .time_range(1200)  # 20 minutes - within limit for every_5_minutes (300*4=1200)
            .count()
            .threshold_gt(100)
            .every_5_minutes()
            .build()
        )
        assert trigger.frequency == 300

    def test_every_15_minutes(self):
        """Test every 15 minutes frequency (default)."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .every_15_minutes()
            .build()
        )
        assert trigger.frequency == 900

    def test_every_30_minutes(self):
        """Test every 30 minutes frequency."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .every_30_minutes()
            .build()
        )
        assert trigger.frequency == 1800

    def test_every_hour(self):
        """Test every hour frequency."""
        trigger = (
            TriggerBuilder("Test").last_30_minutes().count().threshold_gt(100).every_hour().build()
        )
        assert trigger.frequency == 3600

    def test_custom_frequency(self):
        """Test custom frequency."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .frequency(600)
            .build()
        )
        assert trigger.frequency == 600

    def test_frequency_too_low_raises_error(self):
        """Test that frequency < 60 raises error."""
        with pytest.raises(ValueError, match="must be between 60 and 86400"):
            TriggerBuilder("Test").frequency(30)

    def test_frequency_too_high_raises_error(self):
        """Test that frequency > 86400 raises error."""
        with pytest.raises(ValueError, match="must be between 60 and 86400"):
            TriggerBuilder("Test").frequency(100000)


class TestTriggerBuilderAlertBehavior:
    """Tests for alert behavior configuration."""

    def test_alert_on_change_default(self):
        """Test alert on change (default)."""
        trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_gt(100).build()
        assert trigger.alert_type == TriggerAlertType.ON_CHANGE

    def test_alert_on_change_explicit(self):
        """Test explicit alert on change."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .alert_on_change()
            .build()
        )
        assert trigger.alert_type == TriggerAlertType.ON_CHANGE

    def test_alert_on_true(self):
        """Test alert on true."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .alert_on_true()
            .build()
        )
        assert trigger.alert_type == TriggerAlertType.ON_TRUE

    def test_disabled_default(self):
        """Test trigger enabled by default."""
        trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_gt(100).build()
        assert trigger.disabled is False

    def test_disabled_explicit(self):
        """Test disabled trigger."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .disabled(True)
            .build()
        )
        assert trigger.disabled is True

    def test_disabled_no_args(self):
        """Test disabled() with no args defaults to True."""
        trigger = (
            TriggerBuilder("Test").last_30_minutes().count().threshold_gt(100).disabled().build()
        )
        assert trigger.disabled is True


class TestTriggerBuilderQueryIntegration:
    """Tests for QueryBuilder integration."""

    def test_inherits_query_builder_methods(self):
        """Test that TriggerBuilder inherits QueryBuilder methods."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .gte("status", 500)
            .eq("service", "api")
            .group_by("endpoint")
            .threshold_gt(100)
            .build()
        )
        assert len(trigger.query.filters) == 2
        assert trigger.query.breakdowns == ["endpoint"]

    def test_single_calculation_allowed(self):
        """Test that single calculation is allowed."""
        trigger = (
            TriggerBuilder("Test").last_30_minutes().p99("duration_ms").threshold_gt(500).build()
        )
        assert len(trigger.query.calculations) == 1
        assert trigger.query.calculations[0].op == CalcOp.P99

    def test_multiple_calculations_raise_error(self):
        """Test that multiple calculations raise error."""
        with pytest.raises(ValueError, match="can only have one calculation"):
            (
                TriggerBuilder("Test")
                .last_30_minutes()
                .count()
                .p99("duration_ms")
                .threshold_gt(100)
                .build()
            )

    def test_time_range_within_limit(self):
        """Test that time range <= 3600 is allowed."""
        trigger = TriggerBuilder("Test").time_range(3600).count().threshold_gt(100).build()
        assert trigger.query.time_range == 3600

    def test_time_range_exceeds_limit_raises_error(self):
        """Test that time range > 3600 raises error."""
        with pytest.raises(ValueError, match="must be <= 3600 seconds"):
            (
                TriggerBuilder("Test")
                .last_2_hours()  # 7200 seconds
                .count()
                .threshold_gt(100)
                .build()
            )

    def test_absolute_time_not_allowed(self):
        """Test that absolute time ranges are not allowed."""
        with pytest.raises(ValueError, match="do not support absolute time"):
            (
                TriggerBuilder("Test")
                .absolute_time(1000000, 1003600)
                .count()
                .threshold_gt(100)
                .build()
            )

    def test_start_time_not_allowed(self):
        """Test that start_time is not allowed."""
        with pytest.raises(ValueError, match="do not support absolute time"):
            (
                TriggerBuilder("Test")
                .start_time(1000000)
                .end_time(1003600)
                .count()
                .threshold_gt(100)
                .build()
            )


class TestTriggerBuilderRecipients:
    """Tests for recipient integration via RecipientMixin."""

    def test_email_recipient(self):
        """Test adding email recipient."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .email("oncall@example.com")
            .build()
        )
        assert len(trigger.recipients) == 1
        assert trigger.recipients[0]["type"] == "email"
        assert trigger.recipients[0]["target"] == "oncall@example.com"

    def test_slack_recipient(self):
        """Test adding Slack recipient."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .slack("#alerts")
            .build()
        )
        assert trigger.recipients[0]["type"] == "slack"
        assert trigger.recipients[0]["target"] == "#alerts"

    def test_pagerduty_recipient(self):
        """Test adding PagerDuty recipient."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .pagerduty("routing-key-123", severity="critical")
            .build()
        )
        assert trigger.recipients[0]["type"] == "pagerduty"
        assert trigger.recipients[0]["target"] == "routing-key-123"
        assert trigger.recipients[0]["details"]["severity"] == "critical"

    def test_webhook_recipient(self):
        """Test adding webhook recipient."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .webhook("https://example.com/webhook")
            .build()
        )
        assert trigger.recipients[0]["type"] == "webhook"

    def test_msteams_recipient(self):
        """Test adding MS Teams recipient."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .msteams("https://outlook.office.com/webhook/...")
            .build()
        )
        assert trigger.recipients[0]["type"] == "msteams_workflow"

    def test_recipient_id(self):
        """Test adding recipient by ID."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .recipient_id("recipient-123")
            .build()
        )
        assert len(trigger.recipients) == 1
        assert trigger.recipients[0]["id"] == "recipient-123"

    def test_multiple_recipients(self):
        """Test adding multiple recipients."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .email("oncall@example.com")
            .slack("#alerts")
            .pagerduty("routing-key", severity="warning")
            .build()
        )
        assert len(trigger.recipients) == 3

    def test_no_recipients(self):
        """Test trigger without recipients."""
        trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_gt(100).build()
        assert trigger.recipients is None


class TestTriggerBuilderComplexScenarios:
    """Tests for complex trigger scenarios."""

    def test_complete_trigger(self):
        """Test building a complete trigger with all features."""
        trigger = (
            TriggerBuilder("High Error Rate")
            .description("Alert when error rate is high")
            .dataset("api-logs")
            .time_range(1200)  # 20 minutes - valid for 5 min frequency (300*4=1200)
            .count()
            .gte("status", 500)
            .group_by("service")
            .threshold_gt(100)
            .exceeded_limit(3)
            .every_5_minutes()
            .alert_on_true()
            .email("oncall@example.com")
            .slack("#alerts")
            .pagerduty("routing-key", severity="critical")
            .build()
        )
        assert trigger.name == "High Error Rate"
        assert trigger.description == "Alert when error rate is high"
        assert trigger.query.time_range == 1200
        assert trigger.threshold.value == 100.0
        assert trigger.threshold.exceeded_limit == 3
        assert trigger.frequency == 300
        assert trigger.alert_type == TriggerAlertType.ON_TRUE
        assert len(trigger.recipients) == 3

    def test_p99_latency_trigger(self):
        """Test P99 latency trigger pattern."""
        trigger = (
            TriggerBuilder("High Latency")
            .dataset("api-logs")
            .time_range(240)  # 4 minutes - max for every_minute (60*4=240)
            .p99("duration_ms")
            .eq("endpoint", "/api/users")
            .threshold_gt(1000)
            .every_minute()
            .email("oncall@example.com")
            .build()
        )
        assert trigger.query.calculations[0].op == CalcOp.P99
        assert trigger.query.calculations[0].column == "duration_ms"
        assert trigger.frequency == 60

    def test_error_rate_trigger(self):
        """Test error rate trigger pattern."""
        trigger = (
            TriggerBuilder("Error Spike")
            .environment_wide()
            .time_range(1200)  # 20 minutes - valid for every_5_minutes (300*4=1200)
            .count()
            .gte("status", 500)
            .threshold_gt(50)
            .every_5_minutes()
            .pagerduty("routing-key", severity="critical")
            .build()
        )
        assert trigger.query.filters[0].column == "status"
        assert trigger.threshold.op == TriggerThresholdOp.GREATER_THAN

    def test_method_chaining(self):
        """Test that all methods support chaining."""
        builder = TriggerBuilder("Test")
        result = (
            builder.description("desc")
            .dataset("ds")
            .last_30_minutes()
            .count()
            .eq("status", 200)
            .threshold_gt(100)
            .exceeded_limit(2)
            .every_5_minutes()
            .alert_on_change()
            .disabled(False)
            .email("test@example.com")
        )
        assert result is builder


class TestTriggerBuilderTags:
    """Tests for tag support via TagsMixin."""

    def test_single_tag(self):
        """Test adding a single tag."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .tag("team", "backend")
            .build()
        )
        assert trigger.tags == [{"key": "team", "value": "backend"}]

    def test_multiple_tags(self):
        """Test adding multiple tags."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .tag("team", "backend")
            .tag("env", "production")
            .tag("service", "api")
            .build()
        )
        assert len(trigger.tags) == 3

    def test_tags_via_dict(self):
        """Test adding tags via dictionary."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(100)
            .tags({"team": "backend", "env": "production"})
            .build()
        )
        assert len(trigger.tags) == 2

    def test_no_tags(self):
        """Test trigger without tags."""
        trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_gt(100).build()
        assert trigger.tags is None

    def test_tag_validation_enforced(self):
        """Test that tag validation is enforced."""
        with pytest.raises(ValueError, match="must contain only lowercase"):
            TriggerBuilder("Test").tag("Team", "backend")


class TestTriggerBuilderBaseline:
    """Tests for baseline threshold support."""

    def test_baseline_1_hour_ago_percentage(self):
        """Test baseline comparison to 1 hour ago (percentage)."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(10)
            .baseline_1_hour_ago("percentage")
            .build()
        )
        assert trigger.baseline_details == {"offset_minutes": 60, "type": "percentage"}

    def test_baseline_1_hour_ago_default(self):
        """Test baseline 1 hour ago with default percentage."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(10)
            .baseline_1_hour_ago()
            .build()
        )
        assert trigger.baseline_details["type"] == "percentage"

    def test_baseline_1_hour_ago_value(self):
        """Test baseline comparison to 1 hour ago (value)."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(10)
            .baseline_1_hour_ago("value")
            .build()
        )
        assert trigger.baseline_details == {"offset_minutes": 60, "type": "value"}

    def test_baseline_1_day_ago(self):
        """Test baseline comparison to 1 day ago."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(10)
            .baseline_1_day_ago()
            .build()
        )
        assert trigger.baseline_details == {"offset_minutes": 1440, "type": "percentage"}

    def test_baseline_1_week_ago(self):
        """Test baseline comparison to 1 week ago."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(10)
            .baseline_1_week_ago()
            .build()
        )
        assert trigger.baseline_details == {"offset_minutes": 10080, "type": "percentage"}

    def test_baseline_4_weeks_ago(self):
        """Test baseline comparison to 4 weeks ago."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(10)
            .baseline_4_weeks_ago()
            .build()
        )
        assert trigger.baseline_details == {"offset_minutes": 40320, "type": "percentage"}

    def test_baseline_custom_valid(self):
        """Test custom baseline with valid offset."""
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()
            .count()
            .threshold_gt(10)
            .baseline(10080, "value")
            .build()
        )
        assert trigger.baseline_details == {"offset_minutes": 10080, "type": "value"}

    def test_baseline_custom_invalid_offset(self):
        """Test that invalid baseline offset raises error."""
        with pytest.raises(ValueError, match="must be one of"):
            (
                TriggerBuilder("Test")
                .last_30_minutes()
                .count()
                .threshold_gt(10)
                .baseline(120, "percentage")  # Invalid: not 60, 1440, 10080, or 40320
            )

    def test_no_baseline(self):
        """Test trigger without baseline."""
        trigger = TriggerBuilder("Test").last_30_minutes().count().threshold_gt(100).build()
        assert trigger.baseline_details is None


class TestTriggerBuilderValidationConstraints:
    """Tests for additional validation constraints."""

    def test_exceeded_limit_range_min(self):
        """Test that exceeded_limit < 1 raises error."""
        with pytest.raises(ValueError, match="must be between 1 and 5"):
            TriggerBuilder("Test").exceeded_limit(0)

    def test_exceeded_limit_range_max(self):
        """Test that exceeded_limit > 5 raises error."""
        with pytest.raises(ValueError, match="must be between 1 and 5"):
            TriggerBuilder("Test").exceeded_limit(6)

    def test_exceeded_limit_valid_range(self):
        """Test all valid exceeded_limit values."""
        for limit in [1, 2, 3, 4, 5]:
            trigger = (
                TriggerBuilder("Test")
                .last_30_minutes()
                .count()
                .threshold_gt(100)
                .exceeded_limit(limit)
                .build()
            )
            assert trigger.threshold.exceeded_limit == limit

    def test_frequency_vs_duration_valid(self):
        """Test that duration <= frequency * 4 passes."""
        # 30 minutes (1800s) with every_minute (60s): 1800 <= 60 * 4 = 240 (FAILS)
        # So we need frequency of at least 450s for 30 min duration
        trigger = (
            TriggerBuilder("Test")
            .last_30_minutes()  # 1800s
            .count()
            .threshold_gt(100)
            .frequency(450)  # 1800 <= 450 * 4 = 1800 (OK)
            .build()
        )
        assert trigger.frequency == 450

    def test_frequency_vs_duration_invalid(self):
        """Test that duration > frequency * 4 raises error."""
        with pytest.raises(ValueError, match="cannot be more than 4x frequency"):
            (
                TriggerBuilder("Test")
                .last_30_minutes()  # 1800s
                .count()
                .threshold_gt(100)
                .every_minute()  # 60s: 1800 > 60 * 4 = 240 (FAIL)
                .build()
            )

    def test_frequency_vs_duration_edge_case(self):
        """Test frequency vs duration at exact boundary."""
        # 1 hour (3600s) with every 15 minutes (900s): 3600 <= 900 * 4 = 3600 (OK)
        trigger = (
            TriggerBuilder("Test")
            .last_1_hour()  # 3600s
            .count()
            .threshold_gt(100)
            .every_15_minutes()  # 900s: 3600 == 900 * 4 (OK)
            .build()
        )
        assert trigger.query.time_range == 3600
        assert trigger.frequency == 900

    def test_default_frequency_with_default_duration(self):
        """Test default frequency (900s) works with default duration (3600s)."""
        # Default: 1 hour (3600s) with 15 min frequency (900s): 3600 <= 900 * 4 = 3600 (OK)
        trigger = TriggerBuilder("Test").count().threshold_gt(100).build()
        assert trigger.query.time_range == 3600
        assert trigger.frequency == 900


class TestTriggerBuilderPhase25Integration:
    """Tests for Phase 2.5 features integrated together."""

    def test_trigger_with_tags_and_baseline(self):
        """Test trigger with both tags and baseline."""
        trigger = (
            TriggerBuilder("Test")
            .dataset("my-dataset")
            .last_30_minutes()
            .count()
            .gte("status", 500)
            .threshold_gt(100)
            .frequency(600)
            .tag("team", "backend")
            .tag("severity", "high")
            .baseline_1_hour_ago("percentage")
            .email("oncall@example.com")
            .build()
        )
        assert trigger.tags == [
            {"key": "team", "value": "backend"},
            {"key": "severity", "value": "high"},
        ]
        assert trigger.baseline_details == {"offset_minutes": 60, "type": "percentage"}
        assert trigger.frequency == 600

    def test_all_features_combined(self):
        """Test trigger using all Phase 2.5 features."""
        trigger = (
            TriggerBuilder("Complex Trigger")
            .description("Full feature test")
            .dataset("my-dataset")
            .last_1_hour()
            .p99("duration_ms")
            .eq("service", "api")
            .group_by("endpoint")
            .threshold_gt(500)
            .exceeded_limit(3)
            .frequency(1800)  # 30 min - allows 1 hour duration (3600 <= 1800*4)
            .alert_on_true()
            .email("oncall@example.com")
            .slack("#alerts")
            .tag("team", "platform")
            .tag("priority", "critical")
            .baseline_1_day_ago("percentage")
            .build()
        )
        assert trigger.threshold.exceeded_limit == 3
        assert len(trigger.tags) == 2
        assert trigger.baseline_details is not None
        assert trigger.frequency == 1800
