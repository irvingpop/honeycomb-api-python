"""Tests for SLOBuilder, BurnAlertBuilder, and SLO model."""

import pytest

from honeycomb import (
    SLI,
    BurnAlertBuilder,
    BurnAlertDefinition,
    BurnAlertType,
    SLIDefinition,
    SLOBuilder,
    SLOBundle,
    SLOCreate,
)
from honeycomb.models.slos import SLO


class TestBurnAlertBuilderBasics:
    """Tests for basic BurnAlertBuilder functionality."""

    def test_exhaustion_time_alert(self):
        """Test building exhaustion time alert."""
        alert_def = BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME).exhaustion_minutes(60).build()

        assert isinstance(alert_def, BurnAlertDefinition)
        assert alert_def.alert_type == BurnAlertType.EXHAUSTION_TIME
        assert alert_def.exhaustion_minutes == 60
        assert alert_def.description is None
        assert alert_def.budget_rate_window_minutes is None
        assert alert_def.budget_rate_decrease_percent is None
        assert alert_def.recipients == []

    def test_budget_rate_alert(self):
        """Test building budget rate alert."""
        alert_def = (
            BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
            .window_minutes(60)
            .threshold_percent(2.0)
            .build()
        )

        assert isinstance(alert_def, BurnAlertDefinition)
        assert alert_def.alert_type == BurnAlertType.BUDGET_RATE
        assert alert_def.budget_rate_window_minutes == 60
        assert alert_def.budget_rate_decrease_percent == 2.0
        assert alert_def.exhaustion_minutes is None
        assert alert_def.recipients == []

    def test_alert_with_description(self):
        """Test adding description to alert."""
        alert_def = (
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            .exhaustion_minutes(120)
            .description("Alert when budget exhausts in 2 hours")
            .build()
        )

        assert alert_def.description == "Alert when budget exhausts in 2 hours"

    def test_method_chaining(self):
        """Test that methods return self for chaining."""
        builder = BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
        assert builder.exhaustion_minutes(60) is builder
        assert builder.description("test") is builder


class TestBurnAlertBuilderWithRecipients:
    """Tests for BurnAlertBuilder with recipients (RecipientMixin)."""

    def test_alert_with_email_recipient(self):
        """Test adding email recipient to burn alert."""
        alert_def = (
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            .exhaustion_minutes(60)
            .email("oncall@example.com")
            .build()
        )

        assert len(alert_def.recipients) == 1
        assert alert_def.recipients[0]["type"] == "email"
        assert alert_def.recipients[0]["target"] == "oncall@example.com"

    def test_alert_with_slack_recipient(self):
        """Test adding Slack recipient to burn alert."""
        alert_def = (
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            .exhaustion_minutes(60)
            .slack("#alerts")
            .build()
        )

        assert len(alert_def.recipients) == 1
        assert alert_def.recipients[0]["type"] == "slack"
        assert alert_def.recipients[0]["target"] == "#alerts"

    def test_alert_with_pagerduty_recipient(self):
        """Test adding PagerDuty recipient to burn alert."""
        alert_def = (
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            .exhaustion_minutes(60)
            .pagerduty("routing-key-123", severity="critical")
            .build()
        )

        assert len(alert_def.recipients) == 1
        assert alert_def.recipients[0]["type"] == "pagerduty"
        assert alert_def.recipients[0]["target"] == "routing-key-123"
        assert alert_def.recipients[0]["details"]["severity"] == "critical"

    def test_alert_with_multiple_recipients(self):
        """Test adding multiple recipients to burn alert."""
        alert_def = (
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            .exhaustion_minutes(60)
            .email("oncall@example.com")
            .slack("#alerts")
            .pagerduty("routing-key")
            .build()
        )

        assert len(alert_def.recipients) == 3
        assert alert_def.recipients[0]["type"] == "email"
        assert alert_def.recipients[1]["type"] == "slack"
        assert alert_def.recipients[2]["type"] == "pagerduty"

    def test_alert_with_recipient_id(self):
        """Test referencing existing recipient by ID."""
        alert_def = (
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            .exhaustion_minutes(60)
            .recipient_id("existing-recipient-id")
            .build()
        )

        assert len(alert_def.recipients) == 1
        assert alert_def.recipients[0]["id"] == "existing-recipient-id"


class TestBurnAlertBuilderValidation:
    """Tests for BurnAlertBuilder validation."""

    def test_exhaustion_time_without_minutes_raises_error(self):
        """Test that exhaustion time alert without minutes raises error."""
        with pytest.raises(
            ValueError,
            match="exhaustion_minutes is required for EXHAUSTION_TIME alerts",
        ):
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME).build()

    def test_budget_rate_without_window_raises_error(self):
        """Test that budget rate alert without window raises error."""
        with pytest.raises(ValueError, match="window_minutes is required for BUDGET_RATE alerts"):
            BurnAlertBuilder(BurnAlertType.BUDGET_RATE).threshold_percent(2.0).build()

    def test_budget_rate_without_threshold_raises_error(self):
        """Test that budget rate alert without threshold raises error."""
        with pytest.raises(
            ValueError, match="threshold_percent is required for BUDGET_RATE alerts"
        ):
            BurnAlertBuilder(BurnAlertType.BUDGET_RATE).window_minutes(60).build()


class TestSLOBuilderBasics:
    """Tests for basic SLOBuilder functionality."""

    def test_minimal_slo_single_dataset(self):
        """Test building minimal SLO with single dataset."""
        bundle = (
            SLOBuilder("API Availability")
            .dataset("api-logs")
            .target_percentage(99.9)
            .sli(alias="success_rate")
            .build()
        )

        assert isinstance(bundle, SLOBundle)
        assert isinstance(bundle.slo, SLOCreate)
        assert bundle.slo.name == "API Availability"
        assert bundle.slo.sli.alias == "success_rate"
        assert bundle.slo.target_per_million == 999000  # 99.9%
        assert bundle.slo.time_period_days == 30  # Default
        assert bundle.datasets == ["api-logs"]
        assert bundle.derived_column is None
        assert bundle.derived_column_environment_wide is False
        assert bundle.burn_alerts == []

    def test_slo_with_description(self):
        """Test adding description to SLO."""
        bundle = (
            SLOBuilder("API Availability")
            .description("Track API success rate")
            .dataset("api-logs")
            .target_percentage(99.9)
            .sli(alias="success_rate")
            .build()
        )

        assert bundle.slo.description == "Track API success rate"

    def test_method_chaining(self):
        """Test that methods return self for chaining."""
        builder = SLOBuilder("Test SLO")
        assert builder.dataset("test-dataset") is builder
        assert builder.target_percentage(99.9) is builder
        assert builder.target_per_million(999000) is builder
        assert builder.sli(alias="test") is builder
        assert builder.description("test") is builder


class TestSLOBuilderTargets:
    """Tests for target configuration methods."""

    def test_target_percentage(self):
        """Test setting target as percentage."""
        bundle = (
            SLOBuilder("Test SLO").dataset("test").target_percentage(99.9).sli(alias="test").build()
        )

        assert bundle.slo.target_per_million == 999000

    def test_target_percentage_decimal(self):
        """Test setting target with decimal precision."""
        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.95)
            .sli(alias="test")
            .build()
        )

        assert bundle.slo.target_per_million == 999500

    def test_target_per_million(self):
        """Test setting target directly as per-million value."""
        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_per_million(995000)
            .sli(alias="test")
            .build()
        )

        assert bundle.slo.target_per_million == 995000


class TestSLOBuilderTimePeriod:
    """Tests for time period configuration."""

    def test_time_period_days(self):
        """Test setting time period in days."""
        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.9)
            .time_period_days(7)
            .sli(alias="test")
            .build()
        )

        assert bundle.slo.time_period_days == 7

    def test_time_period_weeks(self):
        """Test setting time period in weeks."""
        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.9)
            .time_period_weeks(4)
            .sli(alias="test")
            .build()
        )

        assert bundle.slo.time_period_days == 28

    def test_time_period_days_validation_too_low(self):
        """Test that time period < 1 day raises error."""
        with pytest.raises(ValueError, match="Time period must be between 1 and 90 days"):
            (
                SLOBuilder("Test SLO")
                .dataset("test")
                .target_percentage(99.9)
                .time_period_days(0)
                .sli(alias="test")
                .build()
            )

    def test_time_period_days_validation_too_high(self):
        """Test that time period > 90 days raises error."""
        with pytest.raises(ValueError, match="Time period must be between 1 and 90 days"):
            (
                SLOBuilder("Test SLO")
                .dataset("test")
                .target_percentage(99.9)
                .time_period_days(91)
                .sli(alias="test")
                .build()
            )

    def test_default_time_period(self):
        """Test that default time period is 30 days."""
        bundle = (
            SLOBuilder("Test SLO").dataset("test").target_percentage(99.9).sli(alias="test").build()
        )

        assert bundle.slo.time_period_days == 30


class TestSLOBuilderDatasets:
    """Tests for dataset scoping."""

    def test_single_dataset(self):
        """Test single dataset scope."""
        bundle = (
            SLOBuilder("Test SLO")
            .dataset("api-logs")
            .target_percentage(99.9)
            .sli(alias="test")
            .build()
        )

        assert bundle.datasets == ["api-logs"]
        assert bundle.derived_column_environment_wide is False

    def test_multiple_datasets(self):
        """Test multiple dataset scope."""
        bundle = (
            SLOBuilder("Test SLO")
            .datasets(["api-logs", "web-logs", "worker-logs"])
            .target_percentage(99.9)
            .sli(alias="test")
            .build()
        )

        assert bundle.datasets == ["api-logs", "web-logs", "worker-logs"]
        assert bundle.derived_column_environment_wide is True

    def test_dataset_overwrite(self):
        """Test that calling dataset() after datasets() overwrites."""
        bundle = (
            SLOBuilder("Test SLO")
            .datasets(["api-logs", "web-logs"])
            .dataset("single-dataset")
            .target_percentage(99.9)
            .sli(alias="test")
            .build()
        )

        assert bundle.datasets == ["single-dataset"]


class TestSLOBuilderSLI:
    """Tests for SLI definition."""

    def test_sli_existing_derived_column(self):
        """Test using existing derived column."""
        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.9)
            .sli(alias="existing_column")
            .build()
        )

        assert bundle.slo.sli == SLI(alias="existing_column")
        assert bundle.derived_column is None

    def test_sli_new_derived_column(self):
        """Test creating new derived column."""
        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.9)
            .sli(
                alias="new_column",
                expression="IF(LT($status, 400), 1, 0)",
                description="Success indicator",
            )
            .build()
        )

        assert bundle.slo.sli == SLI(alias="new_column")
        assert bundle.derived_column is not None
        assert bundle.derived_column.alias == "new_column"
        assert bundle.derived_column.expression == "IF(LT($status, 400), 1, 0)"
        assert bundle.derived_column.description == "Success indicator"

    def test_sli_new_derived_column_without_description(self):
        """Test creating new derived column without description."""
        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.9)
            .sli(alias="new_column", expression="IF(LT($status, 400), 1, 0)")
            .build()
        )

        assert bundle.derived_column is not None
        assert bundle.derived_column.description is None

    def test_sli_definition_is_new_derived_column(self):
        """Test SLIDefinition.is_new_derived_column() method."""
        # Existing column
        sli_existing = SLIDefinition(alias="existing")
        assert not sli_existing.is_new_derived_column()

        # New column
        sli_new = SLIDefinition(alias="new", expression="IF(LT($status, 400), 1, 0)")
        assert sli_new.is_new_derived_column()


class TestSLOBuilderBurnAlerts:
    """Tests for burn alert integration."""

    def test_slo_with_exhaustion_alert(self):
        """Test adding exhaustion time burn alert."""
        alert = BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME).exhaustion_minutes(60)

        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.9)
            .sli(alias="test")
            .exhaustion_alert(alert)
            .build()
        )

        assert len(bundle.burn_alerts) == 1
        assert bundle.burn_alerts[0].alert_type == BurnAlertType.EXHAUSTION_TIME
        assert bundle.burn_alerts[0].exhaustion_minutes == 60

    def test_slo_with_budget_rate_alert(self):
        """Test adding budget rate burn alert."""
        alert = (
            BurnAlertBuilder(BurnAlertType.BUDGET_RATE).window_minutes(60).threshold_percent(2.0)
        )

        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.9)
            .sli(alias="test")
            .budget_rate_alert(alert)
            .build()
        )

        assert len(bundle.burn_alerts) == 1
        assert bundle.burn_alerts[0].alert_type == BurnAlertType.BUDGET_RATE
        assert bundle.burn_alerts[0].budget_rate_window_minutes == 60
        assert bundle.burn_alerts[0].budget_rate_decrease_percent == 2.0

    def test_slo_with_multiple_burn_alerts(self):
        """Test adding multiple burn alerts."""
        exhaustion = BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME).exhaustion_minutes(60)
        budget_rate = (
            BurnAlertBuilder(BurnAlertType.BUDGET_RATE).window_minutes(60).threshold_percent(2.0)
        )

        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.9)
            .sli(alias="test")
            .exhaustion_alert(exhaustion)
            .budget_rate_alert(budget_rate)
            .build()
        )

        assert len(bundle.burn_alerts) == 2
        assert bundle.burn_alerts[0].alert_type == BurnAlertType.EXHAUSTION_TIME
        assert bundle.burn_alerts[1].alert_type == BurnAlertType.BUDGET_RATE

    def test_slo_with_burn_alert_with_recipients(self):
        """Test burn alert with recipients."""
        alert = (
            BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
            .exhaustion_minutes(60)
            .email("oncall@example.com")
            .slack("#alerts")
        )

        bundle = (
            SLOBuilder("Test SLO")
            .dataset("test")
            .target_percentage(99.9)
            .sli(alias="test")
            .exhaustion_alert(alert)
            .build()
        )

        assert len(bundle.burn_alerts[0].recipients) == 2

    def test_exhaustion_alert_with_wrong_type_raises_error(self):
        """Test that using wrong alert type for exhaustion_alert raises error."""
        alert = (
            BurnAlertBuilder(BurnAlertType.BUDGET_RATE).window_minutes(60).threshold_percent(2.0)
        )

        with pytest.raises(
            ValueError, match="exhaustion_alert\\(\\) requires EXHAUSTION_TIME alert type"
        ):
            (
                SLOBuilder("Test SLO")
                .dataset("test")
                .target_percentage(99.9)
                .sli(alias="test")
                .exhaustion_alert(alert)
                .build()
            )

    def test_budget_rate_alert_with_wrong_type_raises_error(self):
        """Test that using wrong alert type for budget_rate_alert raises error."""
        alert = BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME).exhaustion_minutes(60)

        with pytest.raises(
            ValueError, match="budget_rate_alert\\(\\) requires BUDGET_RATE alert type"
        ):
            (
                SLOBuilder("Test SLO")
                .dataset("test")
                .target_percentage(99.9)
                .sli(alias="test")
                .budget_rate_alert(alert)
                .build()
            )


class TestSLOBuilderValidation:
    """Tests for SLOBuilder validation."""

    def test_build_without_dataset_raises_error(self):
        """Test that building without dataset raises error."""
        with pytest.raises(
            ValueError,
            match="At least one dataset is required. Use dataset\\(\\) or datasets\\(\\).",
        ):
            SLOBuilder("Test SLO").target_percentage(99.9).sli(alias="test").build()

    def test_build_without_target_raises_error(self):
        """Test that building without target raises error."""
        with pytest.raises(
            ValueError,
            match="Target is required. Use target_percentage\\(\\) or target_per_million\\(\\).",
        ):
            SLOBuilder("Test SLO").dataset("test").sli(alias="test").build()

    def test_build_without_sli_raises_error(self):
        """Test that building without SLI raises error."""
        with pytest.raises(
            ValueError, match="SLI is required. Use sli\\(alias=...\\) to define it."
        ):
            SLOBuilder("Test SLO").dataset("test").target_percentage(99.9).build()


class TestSLOBuilderComplexScenarios:
    """Tests for complex SLO builder scenarios."""

    def test_complete_slo_single_dataset_new_column(self):
        """Test complete SLO with new derived column and burn alerts."""
        bundle = (
            SLOBuilder("API Availability")
            .description("Track API request success rate")
            .dataset("api-logs")
            .target_percentage(99.9)
            .time_period_days(30)
            .sli(
                alias="api_success",
                expression="IF(LT($status_code, 400), 1, 0)",
                description="1 for success, 0 for failure",
            )
            .exhaustion_alert(
                BurnAlertBuilder(BurnAlertType.EXHAUSTION_TIME)
                .exhaustion_minutes(60)
                .description("Budget exhausts in 1 hour")
                .email("oncall@example.com")
                .slack("#alerts")
            )
            .budget_rate_alert(
                BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
                .window_minutes(60)
                .threshold_percent(2.0)
                .pagerduty("routing-key", severity="critical")
            )
            .build()
        )

        # Verify SLO
        assert bundle.slo.name == "API Availability"
        assert bundle.slo.description == "Track API request success rate"
        assert bundle.slo.target_per_million == 999000
        assert bundle.slo.time_period_days == 30
        assert bundle.slo.sli.alias == "api_success"

        # Verify datasets
        assert bundle.datasets == ["api-logs"]
        assert bundle.derived_column_environment_wide is False

        # Verify derived column
        assert bundle.derived_column is not None
        assert bundle.derived_column.alias == "api_success"
        assert bundle.derived_column.expression == "IF(LT($status_code, 400), 1, 0)"
        assert bundle.derived_column.description == "1 for success, 0 for failure"

        # Verify burn alerts
        assert len(bundle.burn_alerts) == 2

        # Exhaustion alert
        assert bundle.burn_alerts[0].alert_type == BurnAlertType.EXHAUSTION_TIME
        assert bundle.burn_alerts[0].exhaustion_minutes == 60
        assert bundle.burn_alerts[0].description == "Budget exhausts in 1 hour"
        assert len(bundle.burn_alerts[0].recipients) == 2

        # Budget rate alert
        assert bundle.burn_alerts[1].alert_type == BurnAlertType.BUDGET_RATE
        assert bundle.burn_alerts[1].budget_rate_window_minutes == 60
        assert bundle.burn_alerts[1].budget_rate_decrease_percent == 2.0
        assert len(bundle.burn_alerts[1].recipients) == 1

    def test_complete_slo_multi_dataset_new_column(self):
        """Test complete SLO with multiple datasets and environment-wide derived column."""
        bundle = (
            SLOBuilder("Cross-Service Availability")
            .description("Overall service availability")
            .datasets(["api-logs", "web-logs", "worker-logs"])
            .target_percentage(99.9)
            .time_period_weeks(4)
            .sli(
                alias="service_success",
                expression="IF(EQUALS($status, 200), 1, 0)",
                description="Success indicator",
            )
            .budget_rate_alert(
                BurnAlertBuilder(BurnAlertType.BUDGET_RATE)
                .window_minutes(60)
                .threshold_percent(1.0)
                .email("platform@example.com")
            )
            .build()
        )

        # Verify SLO
        assert bundle.slo.name == "Cross-Service Availability"
        assert bundle.slo.time_period_days == 28

        # Verify datasets (multi-dataset)
        assert bundle.datasets == ["api-logs", "web-logs", "worker-logs"]
        assert bundle.derived_column_environment_wide is True

        # Verify derived column will be environment-wide
        assert bundle.derived_column is not None
        assert bundle.derived_column.alias == "service_success"

        # Verify burn alerts
        assert len(bundle.burn_alerts) == 1


class TestSLOModel:
    """Tests for SLO model properties and methods."""

    def test_target_percentage_converts_from_per_million(self) -> None:
        """SLO.target_percentage correctly converts from target_per_million."""
        slo = SLO(
            id="slo123",
            name="Test SLO",
            dataset_slugs=["my-dataset"],
            sli={"alias": "test"},
            target_per_million=999000,
            time_period_days=30,
        )
        assert slo.target_percentage == 99.9

    def test_target_percentage_various_values(self) -> None:
        """SLO.target_percentage handles various target values correctly."""
        test_cases = [
            (995000, 99.5),
            (990000, 99.0),
            (999900, 99.99),
            (1000000, 100.0),
            (0, 0.0),
        ]
        for target_per_million, expected_percentage in test_cases:
            slo = SLO(
                id="test",
                name="Test",
                dataset_slugs=["test"],
                sli={"alias": "test"},
                target_per_million=target_per_million,
                time_period_days=30,
            )
            assert slo.target_percentage == expected_percentage, (
                f"Expected {expected_percentage} for {target_per_million}, got {slo.target_percentage}"
            )

    def test_dataset_property_returns_first_dataset(self) -> None:
        """SLO.dataset property returns the first dataset slug."""
        slo = SLO(
            id="test",
            name="Test",
            dataset_slugs=["first-dataset", "second-dataset"],
            sli={"alias": "test"},
            target_per_million=999000,
            time_period_days=30,
        )
        assert slo.dataset == "first-dataset"

    def test_dataset_property_returns_none_for_empty_list(self) -> None:
        """SLO.dataset property returns None when dataset_slugs is empty."""
        slo = SLO(
            id="test",
            name="Test",
            dataset_slugs=[],
            sli={"alias": "test"},
            target_per_million=999000,
            time_period_days=30,
        )
        assert slo.dataset is None

    def test_dataset_property_returns_none_when_not_set(self) -> None:
        """SLO.dataset property returns None when dataset_slugs is None."""
        slo = SLO(
            id="test",
            name="Test",
            dataset_slugs=None,
            sli={"alias": "test"},
            target_per_million=999000,
            time_period_days=30,
        )
        assert slo.dataset is None
