"""Test CLI auto-detection of dataset for triggers and SLOs."""

from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from honeycomb.cli.slos import app as slos_app
from honeycomb.cli.triggers import app as triggers_app
from honeycomb.models.slos import SLO
from honeycomb.models.triggers import Trigger

runner = CliRunner()


@pytest.fixture
def mock_trigger():
    """Mock trigger object."""
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
def mock_slo():
    """Mock SLO object."""
    return SLO(
        id="slo123",
        name="Test SLO",
        dataset_slugs=["my-dataset"],
        sli={"alias": "test"},
        target_per_million=999000,
        time_period_days=30,
    )


def test_trigger_get_auto_detects_dataset(mock_trigger):
    """Test that trigger get auto-detects dataset from list when not provided."""
    with patch("honeycomb.cli.triggers.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.triggers.list.return_value = [mock_trigger]
        mock_get_client.return_value = mock_client

        result = runner.invoke(triggers_app, ["get", "trigger123"])

        # Should list all triggers to find the dataset
        mock_client.triggers.list.assert_called_once_with(dataset="__all__")
        # Should not call get since we have the trigger from list
        assert result.exit_code == 0
        assert "my-dataset" in result.stdout


def test_trigger_get_with_dataset_skips_list(mock_trigger):
    """Test that trigger get skips list when dataset is provided."""
    with patch("honeycomb.cli.triggers.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.triggers.get.return_value = mock_trigger
        mock_get_client.return_value = mock_client

        result = runner.invoke(triggers_app, ["get", "trigger123", "-d", "my-dataset"])

        # Should NOT list when dataset is provided
        mock_client.triggers.list.assert_not_called()
        # Should call get directly
        mock_client.triggers.get.assert_called_once_with(
            dataset="my-dataset", trigger_id="trigger123"
        )
        assert result.exit_code == 0


def test_trigger_get_not_found():
    """Test that trigger get returns error when trigger not found."""
    with patch("honeycomb.cli.triggers.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.triggers.list.return_value = []
        mock_get_client.return_value = mock_client

        result = runner.invoke(triggers_app, ["get", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.stdout


def test_slo_get_auto_detects_dataset(mock_slo):
    """Test that SLO get auto-detects dataset from list when not provided."""
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos.list.return_value = [mock_slo]
        mock_get_client.return_value = mock_client

        result = runner.invoke(slos_app, ["get", "slo123"])

        # Should list all SLOs to find the dataset
        mock_client.slos.list.assert_called_once_with(dataset="__all__")
        # Should not call get since we have the SLO from list
        assert result.exit_code == 0
        assert "my-dataset" in result.stdout


def test_slo_get_with_dataset_skips_list(mock_slo):
    """Test that SLO get skips list when dataset is provided."""
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos.get.return_value = mock_slo
        mock_get_client.return_value = mock_client

        result = runner.invoke(slos_app, ["get", "slo123", "-d", "my-dataset"])

        # Should NOT list when dataset is provided
        mock_client.slos.list.assert_not_called()
        # Should call get directly
        mock_client.slos.get.assert_called_once_with(dataset="my-dataset", slo_id="slo123")
        assert result.exit_code == 0


def test_trigger_delete_auto_detects_dataset(mock_trigger):
    """Test that trigger delete auto-detects dataset from list when not provided."""
    with patch("honeycomb.cli.triggers.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.triggers.list.return_value = [mock_trigger]
        mock_get_client.return_value = mock_client

        result = runner.invoke(triggers_app, ["delete", "trigger123", "-y"])

        # Should list all triggers to find the dataset
        mock_client.triggers.list.assert_called_once_with(dataset="__all__")
        # Should call delete with the found dataset
        mock_client.triggers.delete.assert_called_once_with(
            dataset="my-dataset", trigger_id="trigger123"
        )
        assert result.exit_code == 0


def test_trigger_list_includes_dataset_column(mock_trigger):
    """Test that trigger list includes dataset column in table output."""
    with patch("honeycomb.cli.triggers.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.triggers.list.return_value = [mock_trigger]
        mock_get_client.return_value = mock_client

        result = runner.invoke(triggers_app, ["list"])

        assert result.exit_code == 0
        assert "Dataset" in result.stdout  # Column header
        assert "my-dataset" in result.stdout  # Dataset value


def test_trigger_list_shows_environment_wide():
    """Test that trigger list shows 'environment-wide' for __all__ dataset."""
    env_trigger = Trigger(
        id="env-trigger",
        name="Env Trigger",
        dataset_slug="__all__",
        frequency=60,
        disabled=False,
        threshold={"op": ">=", "value": 1.0},
    )
    with patch("honeycomb.cli.triggers.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.triggers.list.return_value = [env_trigger]
        mock_get_client.return_value = mock_client

        result = runner.invoke(triggers_app, ["list"])

        assert result.exit_code == 0
        # Check for "environment" (may be truncated in table as "environment…")
        assert "environment" in result.stdout.lower()


def test_slo_list_includes_datasets_column(mock_slo):
    """Test that SLO list includes datasets column in table output."""
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos.list.return_value = [mock_slo]
        mock_get_client.return_value = mock_client

        result = runner.invoke(slos_app, ["list"])

        assert result.exit_code == 0
        assert "Datasets" in result.stdout  # Column header
        assert "my-dataset" in result.stdout  # Dataset value


def test_slo_list_shows_multiple_datasets():
    """Test that SLO list shows comma-separated datasets for multi-dataset SLOs."""
    multi_slo = SLO(
        id="multi-slo",
        name="Multi SLO",
        dataset_slugs=["dataset1", "dataset2", "dataset3"],
        sli={"alias": "test"},
        target_per_million=999000,
        time_period_days=30,
    )
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos.list.return_value = [multi_slo]
        mock_get_client.return_value = mock_client

        result = runner.invoke(slos_app, ["list"])

        assert result.exit_code == 0
        # Check for all datasets (may be wrapped across lines in table)
        assert "dataset1" in result.stdout
        assert "dataset2" in result.stdout
        assert "dataset3" in result.stdout


def test_slo_delete_multi_dataset_auto_uses_all():
    """Test that deleting multi-dataset SLO automatically uses __all__."""
    multi_slo = SLO(
        id="multi-slo",
        name="Multi SLO",
        dataset_slugs=["dataset1", "dataset2"],
        sli={"alias": "test"},
        target_per_million=999000,
        time_period_days=30,
    )
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos.list.return_value = [multi_slo]
        mock_get_client.return_value = mock_client

        # Should automatically use __all__ for multi-dataset SLOs
        result = runner.invoke(slos_app, ["delete", "multi-slo", "-y"])

        assert result.exit_code == 0
        assert "spans multiple datasets" in result.stdout
        assert "dataset1, dataset2" in result.stdout
        assert "dataset=__all__" in result.stdout
        mock_client.slos.delete.assert_called_once_with(dataset="__all__", slo_id="multi-slo")


def test_slo_delete_multi_dataset_errors_with_specific_dataset():
    """Test that deleting multi-dataset SLO with specific dataset (not __all__) errors."""
    multi_slo = SLO(
        id="multi-slo",
        name="Multi SLO",
        dataset_slugs=["dataset1", "dataset2"],
        sli={"alias": "test"},
        target_per_million=999000,
        time_period_days=30,
    )
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos.list.return_value = [multi_slo]
        mock_get_client.return_value = mock_client

        # Should error when trying to delete from specific dataset
        result = runner.invoke(slos_app, ["delete", "multi-slo", "-d", "dataset1", "-y"])

        assert result.exit_code == 1
        assert "spans multiple datasets" in result.stdout
        assert "can only be deleted with --dataset __all__" in result.stdout
        # Should not have attempted to delete
        mock_client.slos.delete.assert_not_called()


def test_slo_delete_multi_dataset_works_with_all():
    """Test that deleting multi-dataset SLO works with explicit --dataset __all__."""
    multi_slo = SLO(
        id="multi-slo",
        name="Multi SLO",
        dataset_slugs=["dataset1", "dataset2"],
        sli={"alias": "test"},
        target_per_million=999000,
        time_period_days=30,
    )
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos.list.return_value = [multi_slo]
        mock_get_client.return_value = mock_client

        # Should work with explicit --dataset __all__
        result = runner.invoke(slos_app, ["delete", "multi-slo", "-d", "__all__", "-y"])

        assert result.exit_code == 0
        mock_client.slos.delete.assert_called_once_with(dataset="__all__", slo_id="multi-slo")


def test_slo_get_multi_dataset_shows_warning():
    """Test that getting multi-dataset SLO shows a warning."""
    multi_slo = SLO(
        id="multi-slo",
        name="Multi SLO",
        dataset_slugs=["dataset1", "dataset2"],
        sli={"alias": "test"},
        target_per_million=999000,
        time_period_days=30,
    )
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos.list.return_value = [multi_slo]
        mock_get_client.return_value = mock_client

        result = runner.invoke(slos_app, ["get", "multi-slo"])

        assert result.exit_code == 0
        assert "spans multiple datasets" in result.stdout
        assert "dataset1, dataset2" in result.stdout


def test_slo_export_multi_dataset_shows_warning():
    """Test that exporting multi-dataset SLO shows a warning."""
    multi_slo = SLO(
        id="multi-slo",
        name="Multi SLO",
        dataset_slugs=["dataset1", "dataset2"],
        sli={"alias": "test"},
        target_per_million=999000,
        time_period_days=30,
    )
    with patch("honeycomb.cli.slos.get_client") as mock_get_client:
        mock_client = Mock()
        mock_client.slos.list.return_value = [multi_slo]
        mock_get_client.return_value = mock_client

        result = runner.invoke(slos_app, ["export", "multi-slo"])

        assert result.exit_code == 0
        assert "spans multiple datasets" in result.stdout
        assert "dataset1, dataset2" in result.stdout
