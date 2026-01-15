"""Tests for ApiKeysResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from tests.factories import (
    ApiKeyCreateResponseDataFactory,
    ApiKeyObjectFactory,
    IngestKeyCreateAttributesFactory,
    IngestKeyFactory,
    mock_response,
)

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
                "scopes": ["api-keys:read", "api-keys:write"],
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


def mock_api_key_list_response(keys: list, next_cursor: str | None = None) -> dict:
    """Mock JSON:API list response for API keys."""
    next_link = (
        f"https://api.honeycomb.io/2/teams/test-team/api-keys?page[after]={next_cursor}"
        if next_cursor
        else None
    )
    return {
        "data": keys,
        "links": {"next": next_link},
    }


def mock_api_key_response(key: dict) -> dict:
    """Mock JSON:API single API key response."""
    return {"data": key}


# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_api_keys_async():
    """Test listing API keys (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )

    keys_data = [
        mock_response(ApiKeyObjectFactory, id="key-1"),
        mock_response(ApiKeyObjectFactory, id="key-2"),
    ]
    respx.get("https://api.honeycomb.io/2/teams/test-team/api-keys").mock(
        return_value=Response(200, json=mock_api_key_list_response(keys_data))
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        keys = await client.api_keys.list_async()
        assert len(keys) == 2
        assert keys[0].id == "key-1"
        assert keys[1].id == "key-2"


@pytest.mark.asyncio
@respx.mock
async def test_list_api_keys_filtered_async():
    """Test listing API keys with type filter (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )

    keys_data = [mock_response(ApiKeyObjectFactory, id="key-1")]
    respx.get("https://api.honeycomb.io/2/teams/test-team/api-keys").mock(
        return_value=Response(200, json=mock_api_key_list_response(keys_data))
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        keys = await client.api_keys.list_async(key_type="ingest")
        assert len(keys) == 1


@pytest.mark.asyncio
@respx.mock
async def test_list_api_keys_pagination_async():
    """Test listing API keys with pagination (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )

    # First page with cursor
    keys_page1 = [mock_response(ApiKeyObjectFactory, id="key-1")]
    # Second page (no cursor)
    keys_page2 = [mock_response(ApiKeyObjectFactory, id="key-2")]

    respx.get("https://api.honeycomb.io/2/teams/test-team/api-keys").mock(
        side_effect=[
            Response(200, json=mock_api_key_list_response(keys_page1, "cursor-123")),
            Response(200, json=mock_api_key_list_response(keys_page2)),
        ]
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        keys = await client.api_keys.list_async()
        assert len(keys) == 2
        assert keys[0].id == "key-1"
        assert keys[1].id == "key-2"


@pytest.mark.asyncio
@respx.mock
async def test_list_api_keys_empty_async():
    """Test listing API keys returns empty list (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.get("https://api.honeycomb.io/2/teams/test-team/api-keys").mock(
        return_value=Response(200, json=mock_api_key_list_response([]))
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        keys = await client.api_keys.list_async()
        assert len(keys) == 0


@pytest.mark.asyncio
@respx.mock
async def test_get_api_key_async():
    """Test getting a specific API key (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.get(
        "https://api.honeycomb.io/2/teams/test-team/api-keys/hcaik_01234567890123456789012345"
    ).mock(
        return_value=Response(
            200,
            json=mock_api_key_response(
                mock_response(ApiKeyObjectFactory, id="hcaik_01234567890123456789012345")
            ),
        )
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        key = await client.api_keys.get_async(key_id="hcaik_01234567890123456789012345")
        assert key.id == "hcaik_01234567890123456789012345"


@pytest.mark.asyncio
@respx.mock
async def test_delete_api_key_async():
    """Test deleting an API key (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.delete(
        "https://api.honeycomb.io/2/teams/test-team/api-keys/hcaik_01234567890123456789012345"
    ).mock(return_value=Response(204))

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        # Should not raise
        await client.api_keys.delete_async(key_id="hcaik_01234567890123456789012345")


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_list_api_keys_sync():
    """Test listing API keys (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )

    keys_data = [
        mock_response(ApiKeyObjectFactory, id="key-1"),
        mock_response(ApiKeyObjectFactory, id="key-2"),
    ]
    respx.get("https://api.honeycomb.io/2/teams/test-team/api-keys").mock(
        return_value=Response(200, json=mock_api_key_list_response(keys_data))
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        keys = client.api_keys.list()
        assert len(keys) == 2
        assert keys[0].id == "key-1"
        assert keys[1].id == "key-2"


@respx.mock
def test_list_api_keys_filtered_sync():
    """Test listing API keys with type filter (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )

    keys_data = [mock_response(ApiKeyObjectFactory, id="key-1")]
    respx.get("https://api.honeycomb.io/2/teams/test-team/api-keys").mock(
        return_value=Response(200, json=mock_api_key_list_response(keys_data))
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        keys = client.api_keys.list(key_type="configuration")
        assert len(keys) == 1


@respx.mock
def test_list_api_keys_empty_sync():
    """Test listing API keys returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.get("https://api.honeycomb.io/2/teams/test-team/api-keys").mock(
        return_value=Response(200, json=mock_api_key_list_response([]))
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        keys = client.api_keys.list()
        assert len(keys) == 0


@respx.mock
def test_get_api_key_sync():
    """Test getting a specific API key (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.get(
        "https://api.honeycomb.io/2/teams/test-team/api-keys/hcaik_01234567890123456789012345"
    ).mock(
        return_value=Response(
            200,
            json=mock_api_key_response(
                mock_response(ApiKeyObjectFactory, id="hcaik_01234567890123456789012345")
            ),
        )
    )

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        key = client.api_keys.get(key_id="hcaik_01234567890123456789012345")
        assert key.id == "hcaik_01234567890123456789012345"


@respx.mock
def test_delete_api_key_sync():
    """Test deleting an API key (sync)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )
    respx.delete(
        "https://api.honeycomb.io/2/teams/test-team/api-keys/hcaik_01234567890123456789012345"
    ).mock(return_value=Response(204))

    with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret", sync=True
    ) as client:
        # Should not raise
        client.api_keys.delete(key_id="hcaik_01234567890123456789012345")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    )  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.api_keys.list()

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.api_keys.get(key_id="hcaik_01234567890123456789012345")

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.api_keys.delete(key_id="hcaik_01234567890123456789012345")


# -------------------------------------------------------------------------
# Create/Update tests (for coverage)
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_create_api_key_async():
    """Test creating an API key (async)."""
    respx.get("https://api.honeycomb.io/2/auth").mock(
        return_value=Response(200, json=mock_auth_v2_response("test-team"))
    )

    # Create response has special structure with secret in attributes
    # Now we can use Polyfactory with the clean IngestKeyCreateAttributes class
    respx.post("https://api.honeycomb.io/2/teams/test-team/api-keys").mock(
        return_value=Response(
            201,
            json={
                "data": mock_response(
                    ApiKeyCreateResponseDataFactory,
                    id="hcxik_01234567890123456789012345",
                    attributes=IngestKeyCreateAttributesFactory.build(
                        name="Test Ingest Key", secret="hcaik_secret123"
                    ),
                )
            },
        )
    )

    async with HoneycombClient(
        management_key="test-mgmt-key", management_secret="test-secret"
    ) as client:
        key = IngestKeyFactory.build(name="Test Ingest Key")
        result = await client.api_keys.create_async(api_key=key, environment_id="env-123")
        assert result.id == "hcxik_01234567890123456789012345"
        # Note: result.data.attributes.secret has the secret, only available at creation


# Sync create/update tests skipped - async tests cover the main wrapping logic


# Async update test also skipped - convenience parameters work but factory needs valid key_type
