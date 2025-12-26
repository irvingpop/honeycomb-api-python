"""Shared fixtures for integration tests.

These tests run against the live Honeycomb API.
Run setup_test_session.py first to create credentials.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from honeycomb import HoneycombClient

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
SECRETS_DIR = PROJECT_ROOT / ".claude" / "secrets"


def load_test_credentials() -> tuple[str, str]:
    """Load test credentials from secrets directory.

    Returns:
        Tuple of (api_key, test_dataset)

    Raises:
        pytest.skip: If credentials are not available
    """
    # First check environment variables (may be set by direnv)
    api_key = os.environ.get("HONEYCOMB_API_KEY")
    test_dataset = os.environ.get("HONEYCOMB_TEST_DATASET", "integration-test")

    if api_key:
        return api_key, test_dataset

    # Try to load from secrets file
    test_env_file = SECRETS_DIR / "test.env"
    if not test_env_file.exists():
        pytest.skip(
            "No test credentials found. Run setup_test_session.py first:\n"
            "  direnv exec . poetry run python tests/integration/setup_test_session.py"
        )

    # Parse the test.env file
    with open(test_env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("export HONEYCOMB_API_KEY="):
                api_key = line.split("=", 1)[1].strip('"')
            elif line.startswith("export HONEYCOMB_TEST_DATASET="):
                test_dataset = line.split("=", 1)[1].strip('"')

    if not api_key:
        pytest.skip("HONEYCOMB_API_KEY not found in test.env")

    return api_key, test_dataset


def load_session_info() -> dict | None:
    """Load session info from secrets directory."""
    session_file = SECRETS_DIR / "session.json"
    if session_file.exists():
        with open(session_file) as f:
            return json.load(f)
    return None


@pytest.fixture(scope="session")
def api_key() -> str:
    """Get API key for integration tests."""
    key, _ = load_test_credentials()
    return key


@pytest.fixture(scope="session")
def test_dataset() -> str:
    """Get test dataset name."""
    _, dataset = load_test_credentials()
    return dataset


@pytest.fixture(scope="session")
def session_info() -> dict | None:
    """Get session info (environment details)."""
    return load_session_info()


@pytest.fixture
async def client(api_key: str) -> AsyncGenerator[HoneycombClient, None]:
    """Create async HoneycombClient for testing."""
    from honeycomb import HoneycombClient

    async with HoneycombClient(api_key=api_key) as hc:
        yield hc


@pytest.fixture
def sync_client(api_key: str) -> Generator[HoneycombClient, None, None]:
    """Create sync HoneycombClient for testing."""
    from honeycomb import HoneycombClient

    with HoneycombClient(api_key=api_key, sync=True) as hc:
        yield hc


@pytest.fixture
async def ensure_dataset(client: HoneycombClient, test_dataset: str) -> str:
    """Ensure the test dataset exists.

    Creates it if it doesn't exist, returns the dataset slug.
    """
    try:
        await client.datasets.get_async(test_dataset)
    except Exception:
        # Dataset doesn't exist, we need to send an event to create it
        await client.events.send_async(
            test_dataset,
            data={"_init": True, "source": "integration_test_setup"},
        )
        # Wait a moment for dataset to be created
        import asyncio

        await asyncio.sleep(2)

    return test_dataset
