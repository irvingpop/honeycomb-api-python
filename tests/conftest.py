"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def api_key() -> str:
    """Test API key."""
    return "test-api-key"
