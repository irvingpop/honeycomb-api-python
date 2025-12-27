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


@pytest.fixture
async def ensure_columns(client: HoneycombClient, ensure_dataset: str) -> list[str]:
    """Ensure test columns exist by sending events with the required fields.

    Creates columns used in derived column expressions: status_code, trace.trace_id,
    trace.span_id, trace.parent_id, duration_ms, service, endpoint, error.

    Returns:
        List of column names created
    """
    import asyncio

    # Send events with the columns we need for derived column expressions
    test_events = [
        {
            "status_code": 200,
            "trace.trace_id": "abc123",
            "trace.span_id": "span456",
            "trace.parent_id": "parent789",
            "duration_ms": 45.0,
            "service": "api",
            "endpoint": "/users",
            "error": False,
        },
        {
            "status_code": 500,
            "trace.trace_id": "def456",
            "trace.span_id": "span789",
            "duration_ms": 1200.0,
            "service": "api",
            "endpoint": "/orders",
            "error": True,
        },
    ]

    for event in test_events:
        await client.events.send_async(ensure_dataset, data=event)

    # Wait for columns to be created
    await asyncio.sleep(2)

    return [
        "status_code",
        "trace.trace_id",
        "trace.span_id",
        "trace.parent_id",
        "duration_ms",
        "service",
        "endpoint",
        "error",
    ]


@pytest.fixture
async def ensure_sli(
    client: HoneycombClient,
    ensure_dataset: str,
    ensure_columns: list[str],  # noqa: ARG001
) -> str:
    """Create a derived column to use as an SLI for SLO testing.

    SLIs are derived columns that return boolean values. This creates one
    based on status_code < 500 (successful requests).

    Args:
        client: HoneycombClient for API calls
        ensure_dataset: Dataset slug (dependency)
        ensure_columns: List of columns (dependency, ensures columns exist)

    Returns:
        The SLI alias (derived column alias)
    """
    import asyncio

    from honeycomb import DerivedColumnCreate

    sli_alias = "test_sli_success_rate"

    # Check if SLI already exists
    try:
        existing = await client.derived_columns.list_async(ensure_dataset)
        for dc in existing:
            if dc.alias == sli_alias:
                return sli_alias
    except Exception:
        pass

    # Create the SLI derived column
    # Expression returns true if request was successful (status_code < 500)
    try:
        dc = DerivedColumnCreate(
            alias=sli_alias,
            expression="LT($status_code, 500)",
            description="SLI: True if request succeeded (status < 500)",
        )
        await client.derived_columns.create_async(ensure_dataset, dc)
    except Exception:
        # May already exist from a previous run
        pass

    # Wait for derived column to be available
    await asyncio.sleep(2)

    return sli_alias


@pytest.fixture
async def ensure_slo(
    client: HoneycombClient, ensure_dataset: str, ensure_sli: str
) -> tuple[str, str]:
    """Create an SLO for burn alert testing.

    Returns:
        Tuple of (slo_id, sli_alias)
    """
    import asyncio

    from honeycomb import SLI, SLOCreate

    slo_name = "Test SLO for Integration Tests"

    # Check if SLO already exists
    try:
        existing = await client.slos.list_async(ensure_dataset)
        for slo in existing:
            if slo.name == slo_name:
                return slo.id, ensure_sli
    except Exception:
        pass

    # Create the SLO
    slo = await client.slos.create_async(
        ensure_dataset,
        SLOCreate(
            name=slo_name,
            description="Test SLO for integration testing",
            sli=SLI(alias=ensure_sli),
            time_period_days=7,
            target_per_million=990000,  # 99%
        ),
    )

    # Wait for SLO to be available
    await asyncio.sleep(2)

    return slo.id, ensure_sli


@pytest.fixture
async def create_unique_sli(
    client: HoneycombClient,
    ensure_dataset: str,
    ensure_columns: list[str],  # noqa: ARG001
) -> str:
    """Create a unique derived column to use as an SLI for SLO CRUD testing.

    This creates a unique SLI that is not used by any existing SLO,
    allowing tests to create new SLOs without conflicts.

    Returns:
        The unique SLI alias
    """
    import asyncio
    import time

    from honeycomb import DerivedColumnCreate

    # Create a unique alias using timestamp
    sli_alias = f"test_sli_crud_{int(time.time())}"

    # Create the SLI derived column
    try:
        dc = DerivedColumnCreate(
            alias=sli_alias,
            expression="LT($status_code, 500)",
            description=f"Temp SLI for CRUD testing - {sli_alias}",
        )
        await client.derived_columns.create_async(ensure_dataset, dc)
    except Exception:
        # May fail if already exists, but with timestamp that's unlikely
        pass

    # Wait for derived column to be available
    await asyncio.sleep(2)

    return sli_alias


@pytest.fixture
async def ensure_recipient(client: HoneycombClient) -> str:
    """Create or retrieve a test recipient for burn alert testing.

    Returns:
        The recipient ID
    """
    from honeycomb import RecipientCreate, RecipientType

    # Check if recipient already exists
    try:
        existing = await client.recipients.list_async()
        for recipient in existing:
            if recipient.type == RecipientType.EMAIL:
                # Use any existing email recipient
                return recipient.id
    except Exception:
        pass

    # Create a new email recipient
    recipient = await client.recipients.create_async(
        RecipientCreate(
            type=RecipientType.EMAIL,
            details={"address": "test-integration@example.com"},
        )
    )

    return recipient.id


def load_management_credentials() -> tuple[str, str] | None:
    """Load management API credentials from environment.

    Returns:
        Tuple of (management_key, management_secret) or None if not available
    """
    mgmt_key = os.environ.get("HONEYCOMB_MANAGEMENT_KEY")
    mgmt_secret = os.environ.get("HONEYCOMB_MANAGEMENT_SECRET")

    if mgmt_key and mgmt_secret:
        return mgmt_key, mgmt_secret

    return None


@pytest.fixture(scope="session")
def management_credentials() -> tuple[str, str]:
    """Get management API credentials.

    Raises:
        pytest.skip: If management credentials are not available
    """
    creds = load_management_credentials()
    if not creds:
        pytest.skip(
            "Management credentials not available. Set HONEYCOMB_MANAGEMENT_KEY "
            "and HONEYCOMB_MANAGEMENT_SECRET in .envrc"
        )
    return creds


@pytest.fixture(scope="session")
def team_slug(management_credentials: tuple[str, str]) -> str:
    """Get team slug from management API.

    Raises:
        pytest.skip: If management credentials not available
    """
    import httpx

    mgmt_key, mgmt_secret = management_credentials

    # Get team slug from auth endpoint (sync call for session-scoped fixture)
    # Management API uses Authorization: Bearer {key_id}:{key_secret}
    with httpx.Client() as http:
        headers = {
            "Authorization": f"Bearer {mgmt_key}:{mgmt_secret}",
        }
        resp = http.get("https://api.honeycomb.io/2/auth", headers=headers)
        resp.raise_for_status()
        auth_data = resp.json()
        # Team info is in the "included" array, find the team type
        for included in auth_data.get("included", []):
            if included.get("type") == "teams":
                return included["attributes"]["slug"]
        raise ValueError("Team not found in auth response")


@pytest.fixture
async def management_client(
    management_credentials: tuple[str, str],
) -> AsyncGenerator[HoneycombClient, None]:
    """Create HoneycombClient with management key for testing.

    Yields:
        HoneycombClient with management authentication
    """
    from honeycomb import HoneycombClient

    mgmt_key, mgmt_secret = management_credentials

    async with HoneycombClient(management_key=mgmt_key, management_secret=mgmt_secret) as client:
        yield client
