"""Tests for auth CLI commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from honeycomb.cli import app
from honeycomb.models.auth import AuthInfo

runner = CliRunner()


class TestAuthCLI:
    """Tests for auth CLI."""

    @patch("honeycomb.cli.auth.get_client")
    def test_get_auth_default(self, mock_get_client):
        """hny auth get works with default settings (v1)."""
        mock_client = MagicMock()
        mock_client.auth.get.return_value = AuthInfo(
            id="key123",
            type="configuration",
            team_name="Test Team",
            team_slug="test-team",
            environment_name="Production",
            environment_slug="production",
            api_key_access={"events": True},
        )
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["auth", "get"])

        assert result.exit_code == 0
        assert "Test Team" in result.stdout or "key123" in result.stdout
        # Should use v1 by default
        mock_client.auth.get.assert_called_once_with(use_v2=False)

    @patch("honeycomb.cli.auth.get_client")
    def test_get_auth_v2_flag(self, mock_get_client):
        """hny auth get --v2 uses v2 endpoint."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["auth", "get", "--v2"])

        assert result.exit_code == 0
        mock_client.auth.get.assert_called_once_with(use_v2=True)

    @patch("honeycomb.cli.auth.get_client")
    def test_get_auth_json_output(self, mock_get_client):
        """hny auth get --output json outputs JSON."""
        mock_client = MagicMock()
        mock_client.auth.get.return_value = AuthInfo(
            id="key123",
            type="configuration",
            team_name="Team",
            team_slug="team",
            environment_name="Env",
            environment_slug="env",
            api_key_access={},
        )
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["auth", "get", "--output", "json"])

        assert result.exit_code == 0
        assert '"id"' in result.stdout or '"team_name"' in result.stdout
