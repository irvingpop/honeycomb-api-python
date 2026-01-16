"""Tests for MCP delete operation protection."""

import os
from unittest.mock import patch

from honeycomb.mcp.server import DELETE_TOOLS, _are_deletes_blocked


class TestDeleteProtection:
    """Test delete operation blocking."""

    def test_deletes_blocked_by_default(self):
        """Delete operations should be blocked by default."""
        with patch.dict(os.environ, {}, clear=True):
            assert _are_deletes_blocked() is True

    def test_deletes_blocked_when_false(self):
        """Delete operations blocked when explicitly set to false."""
        with patch.dict(os.environ, {"HONEYCOMB_ALLOW_DELETES": "false"}):
            assert _are_deletes_blocked() is True

    def test_deletes_blocked_when_0(self):
        """Delete operations blocked when set to 0."""
        with patch.dict(os.environ, {"HONEYCOMB_ALLOW_DELETES": "0"}):
            assert _are_deletes_blocked() is True

    def test_deletes_allowed_when_true(self):
        """Delete operations allowed when set to true."""
        with patch.dict(os.environ, {"HONEYCOMB_ALLOW_DELETES": "true"}):
            assert _are_deletes_blocked() is False

    def test_deletes_allowed_when_1(self):
        """Delete operations allowed when set to 1."""
        with patch.dict(os.environ, {"HONEYCOMB_ALLOW_DELETES": "1"}):
            assert _are_deletes_blocked() is False

    def test_deletes_allowed_case_insensitive(self):
        """HONEYCOMB_ALLOW_DELETES should be case insensitive."""
        with patch.dict(os.environ, {"HONEYCOMB_ALLOW_DELETES": "TRUE"}):
            assert _are_deletes_blocked() is False

        with patch.dict(os.environ, {"HONEYCOMB_ALLOW_DELETES": "True"}):
            assert _are_deletes_blocked() is False


class TestDeleteToolsList:
    """Test that DELETE_TOOLS constant is comprehensive."""

    def test_all_delete_tools_present(self):
        """All delete operations should be in DELETE_TOOLS."""
        expected_deletes = {
            "honeycomb_delete_dataset",
            "honeycomb_delete_trigger",
            "honeycomb_delete_slo",
            "honeycomb_delete_burn_alert",
            "honeycomb_delete_board",
            "honeycomb_delete_derived_column",
            "honeycomb_delete_column",
            "honeycomb_delete_marker",
            "honeycomb_delete_marker_setting",
            "honeycomb_delete_recipient",
            "honeycomb_delete_environment",
            "honeycomb_delete_api_key",
        }

        assert expected_deletes == DELETE_TOOLS

    def test_delete_tools_count(self):
        """Verify expected number of delete operations."""
        assert len(DELETE_TOOLS) == 12
