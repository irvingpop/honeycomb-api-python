"""Test CLI auto-detection of dataset for triggers and SLOs.

This module tests the CLI's ability to automatically detect which dataset a trigger
or SLO belongs to when the user doesn't explicitly provide the --dataset flag.

Testing Approach:
-----------------
We use unittest.mock.patch rather than respx (used elsewhere in this codebase) because:
1. CLI tests need to mock at the client level, not HTTP level
2. The CLI code calls sync methods on the HoneycombClient, which internally manage
   their own HTTP clients
3. Mocking get_client() is simpler and more maintainable than setting up HTTP mocks
   for each CLI command path

All tests use JSON output format (--output json) to avoid fragile table output that
varies with terminal width and other environment factors.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, create_autospec, patch

import pytest
from typer.testing import CliRunner

from honeycomb.cli.slos import app as slos_app
from honeycomb.cli.triggers import app as triggers_app
from honeycomb.models.slos import SLO
from honeycomb.models.triggers import Trigger
from honeycomb.resources.slos import SLOsResource
from honeycomb.resources.triggers import TriggersResource

if TYPE_CHECKING:
    from collections.abc import Generator

runner = CliRunner()


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def mock_triggers_resource() -> Mock:
    """Create a mock TriggersResource with autospec for type safety."""
    return create_autospec(TriggersResource, instance=True)


@pytest.fixture
def mock_slos_resource() -> Mock:
    """Create a mock SLOsResource with autospec for type safety."""
    return create_autospec(SLOsResource, instance=True)


@pytest.fixture
def mock_trigger() -> Trigger:
    """Create a sample trigger for testing."""
    return Trigger(
        id="trigger123",
        name="Test Trigger",
        dataset_slug="my-dataset",
        query_id="query123",
        frequency=60,
        disabled=False,
        threshold={"op": ">=", "value": 1.0},
    )


@pytest.fixture
def mock_env_trigger() -> Trigger:
    """Create an environment-wide trigger for testing."""
    return Trigger(
        id="env-trigger",
        name="Environment Trigger",
        dataset_slug="__all__",
        frequency=60,
        disabled=False,
        threshold={"op": ">=", "value": 1.0},
    )


@pytest.fixture
def mock_slo() -> SLO:
    """Create a sample SLO for testing."""
    return SLO(
        id="slo123",
        name="Test SLO",
        dataset_slugs=["my-dataset"],
        sli={"alias": "test"},
        target_per_million=999000,
        time_period_days=30,
    )


@pytest.fixture
def mock_multi_dataset_slo() -> SLO:
    """Create a multi-dataset SLO for testing."""
    return SLO(
        id="multi-slo",
        name="Multi Dataset SLO",
        dataset_slugs=["dataset1", "dataset2"],
        sli={"alias": "test"},
        target_per_million=999000,
        time_period_days=30,
    )


@pytest.fixture
def trigger_client(mock_triggers_resource: Mock) -> Generator[Mock, None, None]:
    """Fixture providing a mocked client for trigger CLI tests."""
    with patch("honeycomb.cli.triggers.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.triggers = mock_triggers_resource
        mock_get_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def slo_client(mock_slos_resource: Mock) -> Generator[Mock, None, None]:
    """Fixture providing a mocked client for SLO CLI tests."""
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos = mock_slos_resource
        mock_get_client.return_value = mock_client
        yield mock_client


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_pattern.sub("", text)


def parse_json_output(result: Any) -> dict | list:
    """Parse JSON from CLI output, handling Rich console formatting artifacts."""
    # Strip ANSI escape codes that Rich may add
    stdout = strip_ansi_codes(result.stdout)

    # The output may contain status messages before the JSON
    # Find the JSON portion (starts with { or [)
    for i, char in enumerate(stdout):
        if char in "{[":
            try:
                return json.loads(stdout[i:])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"No valid JSON found in output: {stdout}")


def assert_json_contains(result: Any, expected_key: str, expected_value: Any) -> None:
    """Assert that the JSON output contains a specific key-value pair."""
    data = parse_json_output(result)
    if isinstance(data, list):
        # For list output, check first item
        assert len(data) > 0, "Expected non-empty list"
        data = data[0]
    assert expected_key in data, f"Key '{expected_key}' not found in {data.keys()}"
    assert data[expected_key] == expected_value, (
        f"Expected {expected_key}={expected_value}, got {data[expected_key]}"
    )


# -----------------------------------------------------------------------------
# Trigger Tests - Auto-detection
# -----------------------------------------------------------------------------


class TestTriggerGetAutoDetection:
    """Tests for trigger get command with dataset auto-detection."""

    def test_auto_detects_dataset_from_list(
        self, trigger_client: Mock, mock_trigger: Trigger
    ) -> None:
        """When dataset not provided, trigger get lists all and finds the matching trigger."""
        trigger_client.triggers.list.return_value = [mock_trigger]

        result = runner.invoke(triggers_app, ["get", "trigger123", "-o", "json"])

        assert result.exit_code == 0
        trigger_client.triggers.list.assert_called_once_with(dataset="__all__")
        # Should NOT call get since we found it in list
        trigger_client.triggers.get.assert_not_called()
        assert_json_contains(result, "id", "trigger123")
        assert_json_contains(result, "dataset_slug", "my-dataset")

    def test_skips_list_when_dataset_provided(
        self, trigger_client: Mock, mock_trigger: Trigger
    ) -> None:
        """When dataset is explicitly provided, trigger get fetches directly."""
        trigger_client.triggers.get.return_value = mock_trigger

        result = runner.invoke(
            triggers_app, ["get", "trigger123", "-d", "my-dataset", "-o", "json"]
        )

        assert result.exit_code == 0
        trigger_client.triggers.list.assert_not_called()
        trigger_client.triggers.get.assert_called_once_with(
            dataset="my-dataset", trigger_id="trigger123"
        )
        assert_json_contains(result, "id", "trigger123")

    def test_returns_error_when_not_found(self, trigger_client: Mock) -> None:
        """When trigger not found in any dataset, returns appropriate error."""
        trigger_client.triggers.list.return_value = []

        result = runner.invoke(triggers_app, ["get", "nonexistent", "-o", "json"])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()


class TestTriggerDeleteAutoDetection:
    """Tests for trigger delete command with dataset auto-detection."""

    def test_auto_detects_dataset_for_delete(
        self, trigger_client: Mock, mock_trigger: Trigger
    ) -> None:
        """When dataset not provided, trigger delete lists all to find the dataset."""
        trigger_client.triggers.list.return_value = [mock_trigger]

        result = runner.invoke(triggers_app, ["delete", "trigger123", "-y"])

        assert result.exit_code == 0
        trigger_client.triggers.list.assert_called_once_with(dataset="__all__")
        trigger_client.triggers.delete.assert_called_once_with(
            dataset="my-dataset", trigger_id="trigger123"
        )


class TestTriggerList:
    """Tests for trigger list command."""

    def test_list_all_triggers(self, trigger_client: Mock, mock_trigger: Trigger) -> None:
        """Trigger list returns all triggers in JSON format."""
        trigger_client.triggers.list.return_value = [mock_trigger]

        result = runner.invoke(triggers_app, ["list", "-o", "json"])

        assert result.exit_code == 0
        trigger_client.triggers.list.assert_called_once_with(dataset="__all__")
        data = parse_json_output(result)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "trigger123"

    def test_list_environment_wide_trigger(
        self, trigger_client: Mock, mock_env_trigger: Trigger
    ) -> None:
        """Trigger list correctly handles environment-wide triggers."""
        trigger_client.triggers.list.return_value = [mock_env_trigger]

        result = runner.invoke(triggers_app, ["list", "-o", "json"])

        assert result.exit_code == 0
        data = parse_json_output(result)
        assert data[0]["dataset_slug"] == "__all__"


# -----------------------------------------------------------------------------
# SLO Tests - Auto-detection
# -----------------------------------------------------------------------------


class TestSLOGetAutoDetection:
    """Tests for SLO get command with dataset auto-detection."""

    def test_auto_detects_dataset_from_list(self, slo_client: Mock, mock_slo: SLO) -> None:
        """When dataset not provided, SLO get lists all and finds the matching SLO."""
        slo_client.slos.list.return_value = [mock_slo]

        result = runner.invoke(slos_app, ["get", "slo123", "-o", "json"])

        assert result.exit_code == 0
        slo_client.slos.list.assert_called_once_with(dataset="__all__")
        # Should NOT call get since we found it in list
        slo_client.slos.get.assert_not_called()
        assert_json_contains(result, "id", "slo123")

    def test_skips_list_when_dataset_provided(self, slo_client: Mock, mock_slo: SLO) -> None:
        """When dataset is explicitly provided, SLO get fetches directly."""
        slo_client.slos.get.return_value = mock_slo

        result = runner.invoke(slos_app, ["get", "slo123", "-d", "my-dataset", "-o", "json"])

        assert result.exit_code == 0
        slo_client.slos.list.assert_not_called()
        slo_client.slos.get.assert_called_once_with(dataset="my-dataset", slo_id="slo123")

    def test_multi_dataset_slo_get_succeeds(
        self, slo_client: Mock, mock_multi_dataset_slo: SLO
    ) -> None:
        """Getting a multi-dataset SLO succeeds and shows warning."""
        slo_client.slos.list.return_value = [mock_multi_dataset_slo]

        result = runner.invoke(slos_app, ["get", "multi-slo", "-o", "json"])

        assert result.exit_code == 0
        assert_json_contains(result, "id", "multi-slo")


class TestSLODeleteAutoDetection:
    """Tests for SLO delete command with dataset auto-detection."""

    def test_multi_dataset_auto_uses_all(
        self, slo_client: Mock, mock_multi_dataset_slo: SLO
    ) -> None:
        """Deleting multi-dataset SLO without --dataset automatically uses __all__."""
        slo_client.slos.list.return_value = [mock_multi_dataset_slo]

        result = runner.invoke(slos_app, ["delete", "multi-slo", "-y"])

        assert result.exit_code == 0
        slo_client.slos.delete.assert_called_once_with(dataset="__all__", slo_id="multi-slo")

    def test_multi_dataset_with_specific_dataset_errors(
        self, slo_client: Mock, mock_multi_dataset_slo: SLO
    ) -> None:
        """Deleting multi-dataset SLO with a specific dataset (not __all__) errors."""
        slo_client.slos.list.return_value = [mock_multi_dataset_slo]

        result = runner.invoke(slos_app, ["delete", "multi-slo", "-d", "dataset1", "-y"])

        assert result.exit_code == 1
        slo_client.slos.delete.assert_not_called()
        assert "multiple datasets" in result.stdout.lower()

    def test_multi_dataset_with_explicit_all_succeeds(
        self, slo_client: Mock, mock_multi_dataset_slo: SLO
    ) -> None:
        """Deleting multi-dataset SLO with explicit --dataset __all__ succeeds."""
        slo_client.slos.list.return_value = [mock_multi_dataset_slo]

        result = runner.invoke(slos_app, ["delete", "multi-slo", "-d", "__all__", "-y"])

        assert result.exit_code == 0
        slo_client.slos.delete.assert_called_once_with(dataset="__all__", slo_id="multi-slo")


class TestSLOList:
    """Tests for SLO list command."""

    def test_list_all_slos(self, slo_client: Mock, mock_slo: SLO) -> None:
        """SLO list returns all SLOs in JSON format."""
        slo_client.slos.list.return_value = [mock_slo]

        result = runner.invoke(slos_app, ["list", "-o", "json"])

        assert result.exit_code == 0
        slo_client.slos.list.assert_called_once_with(dataset="__all__")
        data = parse_json_output(result)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "slo123"

    def test_list_multi_dataset_slo(self, slo_client: Mock, mock_multi_dataset_slo: SLO) -> None:
        """SLO list correctly handles multi-dataset SLOs."""
        slo_client.slos.list.return_value = [mock_multi_dataset_slo]

        result = runner.invoke(slos_app, ["list", "-o", "json"])

        assert result.exit_code == 0
        data = parse_json_output(result)
        assert data[0]["dataset_slugs"] == ["dataset1", "dataset2"]


class TestSLOExport:
    """Tests for SLO export command."""

    def test_export_multi_dataset_slo(self, slo_client: Mock, mock_multi_dataset_slo: SLO) -> None:
        """Exporting multi-dataset SLO succeeds with warning."""
        slo_client.slos.list.return_value = [mock_multi_dataset_slo]

        result = runner.invoke(slos_app, ["export", "multi-slo"])

        assert result.exit_code == 0
        slo_client.slos.list.assert_called_once_with(dataset="__all__")


# -----------------------------------------------------------------------------
# Error Handling Tests
# -----------------------------------------------------------------------------


class TestErrorHandling:
    """Tests for error handling in CLI commands."""

    def test_trigger_list_api_error(self, trigger_client: Mock) -> None:
        """Trigger list gracefully handles API errors."""
        trigger_client.triggers.list.side_effect = Exception("API connection failed")

        result = runner.invoke(triggers_app, ["list", "-o", "json"])

        assert result.exit_code == 1
        assert "error" in result.stdout.lower()
        assert "api connection failed" in result.stdout.lower()

    def test_trigger_get_api_error(self, trigger_client: Mock) -> None:
        """Trigger get gracefully handles API errors during list."""
        trigger_client.triggers.list.side_effect = Exception("Unauthorized")

        result = runner.invoke(triggers_app, ["get", "trigger123", "-o", "json"])

        assert result.exit_code == 1
        assert "error" in result.stdout.lower()

    def test_slo_list_api_error(self, slo_client: Mock) -> None:
        """SLO list gracefully handles API errors."""
        slo_client.slos.list.side_effect = Exception("Rate limited")

        result = runner.invoke(slos_app, ["list", "-o", "json"])

        assert result.exit_code == 1
        assert "error" in result.stdout.lower()
        assert "rate limited" in result.stdout.lower()

    def test_slo_get_not_found(self, slo_client: Mock) -> None:
        """SLO get returns appropriate error when SLO not found."""
        slo_client.slos.list.return_value = []

        result = runner.invoke(slos_app, ["get", "nonexistent", "-o", "json"])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_trigger_delete_not_found(self, trigger_client: Mock) -> None:
        """Trigger delete returns appropriate error when trigger not found."""
        trigger_client.triggers.list.return_value = []

        result = runner.invoke(triggers_app, ["delete", "nonexistent", "-y"])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()


# -----------------------------------------------------------------------------
# Parameterized Tests for Common Patterns
# -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "app,list_fixture,item_id",
    [
        ("triggers", "mock_trigger", "trigger123"),
        ("slos", "mock_slo", "slo123"),
    ],
)
def test_get_auto_detection_pattern(
    app: str,
    list_fixture: str,
    item_id: str,
    request: pytest.FixtureRequest,
) -> None:
    """Parameterized test verifying auto-detection pattern for both triggers and SLOs."""
    mock_item = request.getfixturevalue(list_fixture)
    app_module = triggers_app if app == "triggers" else slos_app
    patch_path = f"honeycomb.cli.{app}.get_client"

    with patch(patch_path) as mock_get_client:
        mock_client = Mock()
        mock_resource = Mock()
        mock_resource.list.return_value = [mock_item]
        setattr(mock_client, app, mock_resource)
        mock_get_client.return_value = mock_client

        result = runner.invoke(app_module, ["get", item_id, "-o", "json"])

        assert result.exit_code == 0
        mock_resource.list.assert_called_once_with(dataset="__all__")
        assert_json_contains(result, "id", item_id)
