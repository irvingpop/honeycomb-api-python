"""Tests for MarkerBuilder."""

import time

import pytest

from honeycomb import MarkerBuilder, MarkerCreate, MarkerSettingCreate


class TestMarkerBuilderBasics:
    """Tests for basic MarkerBuilder functionality."""

    def test_minimal_point_marker(self):
        """Test building minimal point marker."""
        marker = MarkerBuilder("Deploy v1.0").type("deploy").build()

        assert isinstance(marker, MarkerCreate)
        assert marker.message == "Deploy v1.0"
        assert marker.type == "deploy"
        assert marker.start_time is None
        assert marker.end_time is None
        assert marker.url is None

    def test_marker_with_url(self):
        """Test adding URL to marker."""
        marker = (
            MarkerBuilder("Hotfix deployed")
            .type("deploy")
            .url("https://github.com/org/repo/pull/123")
            .build()
        )

        assert marker.url == "https://github.com/org/repo/pull/123"

    def test_method_chaining(self):
        """Test that methods return self for chaining."""
        builder = MarkerBuilder("Test")
        assert builder.type("deploy") is builder
        assert builder.url("https://example.com") is builder
        assert builder.start_time(123) is builder
        assert builder.end_time(456) is builder


class TestMarkerBuilderTime:
    """Tests for time configuration."""

    def test_start_time(self):
        """Test setting start time."""
        marker = MarkerBuilder("Test").type("deploy").start_time(1703980800).build()

        assert marker.start_time == 1703980800
        assert marker.end_time is None

    def test_end_time(self):
        """Test setting end time."""
        marker = (
            MarkerBuilder("Test")
            .type("maintenance")
            .start_time(1703980800)
            .end_time(1703984400)
            .build()
        )

        assert marker.start_time == 1703980800
        assert marker.end_time == 1703984400

    def test_duration_minutes(self):
        """Test setting duration from now in minutes."""
        before = int(time.time())
        marker = MarkerBuilder("Test").type("maintenance").duration_minutes(30).build()
        after = int(time.time())

        # Start time should be around current time
        assert before <= marker.start_time <= after + 1

        # End time should be 30 minutes (1800 seconds) after start
        assert marker.end_time == marker.start_time + (30 * 60)

    def test_duration_hours(self):
        """Test setting duration from now in hours."""
        before = int(time.time())
        marker = MarkerBuilder("Test").type("maintenance").duration_hours(2).build()
        after = int(time.time())

        # Start time should be around current time
        assert before <= marker.start_time <= after + 1

        # End time should be 2 hours (7200 seconds) after start
        assert marker.end_time == marker.start_time + (2 * 60 * 60)


class TestMarkerBuilderValidation:
    """Tests for MarkerBuilder validation."""

    def test_build_without_type_raises_error(self):
        """Test that building without type raises error."""
        with pytest.raises(ValueError, match="Marker type is required. Use type\\(\\)."):
            MarkerBuilder("Test marker").build()


class TestMarkerBuilderStaticMethods:
    """Tests for static helper methods."""

    def test_setting_creation(self):
        """Test creating marker setting."""
        setting = MarkerBuilder.setting("deploy", "#00FF00")

        assert isinstance(setting, MarkerSettingCreate)
        assert setting.type == "deploy"
        assert setting.color == "#00FF00"


class TestMarkerBuilderScenarios:
    """Tests for real-world marker scenarios."""

    def test_deployment_marker(self):
        """Test creating a deployment marker."""
        marker = (
            MarkerBuilder("Deployed v1.2.3")
            .type("deploy")
            .url("https://github.com/org/repo/releases/v1.2.3")
            .build()
        )

        assert marker.message == "Deployed v1.2.3"
        assert marker.type == "deploy"
        assert marker.url == "https://github.com/org/repo/releases/v1.2.3"
        assert marker.start_time is None  # Point marker
        assert marker.end_time is None

    def test_maintenance_window_marker(self):
        """Test creating a maintenance window marker."""
        marker = (
            MarkerBuilder("Database migration")
            .type("maintenance")
            .start_time(1703980800)
            .end_time(1703984400)
            .url("https://runbooks.example.com/db-migration")
            .build()
        )

        assert marker.message == "Database migration"
        assert marker.type == "maintenance"
        assert marker.start_time == 1703980800
        assert marker.end_time == 1703984400
        assert marker.url == "https://runbooks.example.com/db-migration"

    def test_incident_marker(self):
        """Test creating an incident marker."""
        before = int(time.time())
        marker = (
            MarkerBuilder("Production outage - API timeout")
            .type("incident")
            .duration_hours(2)
            .url("https://status.example.com/incidents/2024-001")
            .build()
        )

        assert marker.message == "Production outage - API timeout"
        assert marker.type == "incident"
        assert marker.url == "https://status.example.com/incidents/2024-001"
        assert marker.start_time >= before
        assert marker.end_time == marker.start_time + (2 * 60 * 60)

    def test_config_change_marker(self):
        """Test creating a config change marker."""
        marker = (
            MarkerBuilder("Updated rate limit: 100 -> 200 req/s")
            .type("config-change")
            .url("https://github.com/org/repo/pull/456")
            .build()
        )

        assert marker.message == "Updated rate limit: 100 -> 200 req/s"
        assert marker.type == "config-change"
        assert marker.url == "https://github.com/org/repo/pull/456"

    def test_feature_flag_marker(self):
        """Test creating a feature flag toggle marker."""
        marker = MarkerBuilder("Enabled: new-checkout-flow").type("feature-flag").build()

        assert marker.message == "Enabled: new-checkout-flow"
        assert marker.type == "feature-flag"
