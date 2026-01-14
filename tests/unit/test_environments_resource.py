"""Tests for EnvironmentsResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from tests.factories import EnvironmentCreateFactory, EnvironmentFactory, mock_response

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------


def mock_auth_v2_response(team_slug: str = "test-team") -> dict:
    """Mock v2 auth response with team slug for management keys."""
    return {
        "data": {
            "id": "mgmt123",
            "type": "api-keys",
            "attributes": {
                "name": "Test Mgmt Key",
                "key_type": "management",
                "disabled": False,
                "scopes": ["environments:read", "environments:write"],
                "timestamps": {},
            },
            "relationships": {"team": {"data": {"type": "teams", "id": "team123"}}},
        },
        "included": [
            {
                "id": "team123",
                "type": "teams",
                "attributes": {"name": "Test Team", "slug": team_slug},
            }
        ],
    }


def mock_environment_list_response(environments: list, next_cursor: str | None = None) -> dict:
    """Mock JSON:API list response."""
    next_link = (
        f"https://api.honeycomb.io/2/teams/test-team/environments?page[after]={next_cursor}"
        if next_cursor
        else None
    )
    return {
        "data": environments,
        "links": {"next": next_link},
    }


def mock_environment_response(environment: dict) -> dict:
    """Mock JSON:API single environment response."""
    return {"data": environment}


# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_environments_async():
    """Test listing environments (async)."""
    # Mock v2 auth endpoint for team slug detection
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )

    # Mock list endpoint
    env_data = [
        mock_response(EnvironmentFactory, id="env-1"),
        mock_response(EnvironmentFactory, id="env-2"),
    ]
    respx.get("https://api.honeycomb.io/2/teams/test-team/environments").mock(
        return_value=Response(200, json=mock_environment_list_response(env_data))
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        envs = await client.environments.list_async()
        assert len(envs) == 2
        assert envs[0].id == "env-1"
        assert envs[1].id == "env-2"


@pytest.mark.asyncio
@respx.mock
async def test_list_environments_empty_async():
    """Test listing environments returns empty list (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.get("https://api.honeycomb.io/2/teams/test-team/environments").mock(
        return_value=Response(200, json=mock_environment_list_response([]))
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        envs = await client.environments.list_async()
        assert len(envs) == 0


@pytest.mark.asyncio
@respx.mock
async def test_list_environments_pagination_async():
    """Test listing environments with pagination (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )

    # First page with cursor (no query params)
    env_data_page1 = [mock_response(EnvironmentFactory, id="env-1")]
    respx.get("https://api.honeycomb.io/2/teams/test-team/environments").mock(
        side_effect=[
            Response(200, json=mock_environment_list_response(env_data_page1, "cursor-123")),
            Response(
                200,
                json=mock_environment_list_response(
                    [mock_response(EnvironmentFactory, id="env-2")]
                ),
            ),
        ]
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        envs = await client.environments.list_async()
        assert len(envs) == 2
        assert envs[0].id == "env-1"
        assert envs[1].id == "env-2"


@pytest.mark.asyncio
@respx.mock
async def test_get_environment_async():
    """Test getting a specific environment (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.get("https://api.honeycomb.io/2/teams/test-team/environments/env-123").mock(
        return_value=Response(
            200, json=mock_environment_response(mock_response(EnvironmentFactory, id="env-123"))
        )
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        env = await client.environments.get_async(env_id="env-123")
        assert env.id == "env-123"


@pytest.mark.asyncio
@respx.mock
async def test_create_environment_with_convenience_params_async():
    """Test creating environment with convenience parameters (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.post("https://api.honeycomb.io/2/teams/test-team/environments").mock(
        return_value=Response(
            201,
            json=mock_environment_response(mock_response(EnvironmentFactory, id="new-env")),
        )
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        env = await client.environments.create_async(
            name="New Environment", description="Test env", color="blue"
        )
        assert env.id == "new-env"


@pytest.mark.asyncio
@respx.mock
async def test_create_environment_with_request_object_async():
    """Test creating environment with request object (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.post("https://api.honeycomb.io/2/teams/test-team/environments").mock(
        return_value=Response(
            201,
            json=mock_environment_response(mock_response(EnvironmentFactory, id="new-env")),
        )
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        request = EnvironmentCreateFactory.build()
        env = await client.environments.create_async(environment=request)
        assert env.id == "new-env"


@pytest.mark.asyncio
@respx.mock
async def test_update_environment_async():
    """Test updating an environment (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.patch("https://api.honeycomb.io/2/teams/test-team/environments/env-123").mock(
        return_value=Response(
            200,
            json=mock_environment_response(mock_response(EnvironmentFactory, id="env-123")),
        )
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        env = await client.environments.update_async(
            env_id="env-123", description="Updated", delete_protected=True
        )
        assert env.id == "env-123"


@pytest.mark.asyncio
@respx.mock
async def test_delete_environment_async():
    """Test deleting an environment (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.delete("https://api.honeycomb.io/2/teams/test-team/environments/env-123").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        # Should not raise
        await client.environments.delete_async(env_id="env-123")


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_list_environments_sync():
    """Test listing environments (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    env_data = [
        mock_response(EnvironmentFactory, id="env-1"),
        mock_response(EnvironmentFactory, id="env-2"),
    ]
    respx.get("https://api.honeycomb.io/2/teams/test-team/environments").mock(
        return_value=Response(200, json=mock_environment_list_response(env_data))
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        envs = client.environments.list()
        assert len(envs) == 2
        assert envs[0].id == "env-1"
        assert envs[1].id == "env-2"


@respx.mock
def test_list_environments_empty_sync():
    """Test listing environments returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.get("https://api.honeycomb.io/2/teams/test-team/environments").mock(
        return_value=Response(200, json=mock_environment_list_response([]))
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        envs = client.environments.list()
        assert len(envs) == 0


@respx.mock
def test_get_environment_sync():
    """Test getting a specific environment (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.get("https://api.honeycomb.io/2/teams/test-team/environments/env-123").mock(
        return_value=Response(
            200, json=mock_environment_response(mock_response(EnvironmentFactory, id="env-123"))
        )
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        env = client.environments.get(env_id="env-123")
        assert env.id == "env-123"


@respx.mock
def test_create_environment_sync():
    """Test creating environment (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.post("https://api.honeycomb.io/2/teams/test-team/environments").mock(
        return_value=Response(
            201,
            json=mock_environment_response(mock_response(EnvironmentFactory, id="new-env")),
        )
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        env = client.environments.create(name="New Environment")
        assert env.id == "new-env"


@respx.mock
def test_update_environment_sync():
    """Test updating an environment (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.patch("https://api.honeycomb.io/2/teams/test-team/environments/env-123").mock(
        return_value=Response(
            200,
            json=mock_environment_response(mock_response(EnvironmentFactory, id="env-123")),
        )
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        env = client.environments.update(env_id="env-123", description="Updated")
        assert env.id == "env-123"


@respx.mock
def test_delete_environment_sync():
    """Test deleting an environment (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.delete("https://api.honeycomb.io/2/teams/test-team/environments/env-123").mock(
        return_value=Response(204)
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        # Should not raise
        client.environments.delete(env_id="env-123")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    )  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.environments.list()

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.environments.get(env_id="env-123")

    with pytest.raises(RuntimeError, match="Use create_async"):
        client.environments.create(name="Test")

    with pytest.raises(RuntimeError, match="Use update_async"):
        client.environments.update(env_id="env-123", description="Test")

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.environments.delete(env_id="env-123")
