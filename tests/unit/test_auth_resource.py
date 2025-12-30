"""Tests for AuthResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from honeycomb.models.auth import AuthInfo, AuthInfoV2


@pytest.fixture
def api_key_client():
    """Client with API key auth."""
    return HoneycombClient(api_key="test-api-key", sync=True)


@pytest.fixture
def management_client():
    """Client with management key auth."""
    return HoneycombClient(
        management_key="test-mgmt-key",
        management_secret="test-secret",
        sync=True,
    )


class TestAuthResource:
    """Tests for auth resource."""

    @respx.mock
    def test_get_v1_auto_detect(self, api_key_client):
        """Auto-detects v1 endpoint with API key credentials."""
        respx.get("https://api.honeycomb.io/1/auth").mock(
            return_value=Response(
                200,
                json={
                    "id": "key123",
                    "type": "configuration",
                    "team": {"name": "Test Team", "slug": "test-team"},
                    "environment": {"name": "Test Env", "slug": "test-env"},
                    "api_key_access": {"events": True, "markers": True},
                },
            )
        )

        result = api_key_client.auth.get()

        assert isinstance(result, AuthInfo)
        assert result.id == "key123"
        assert result.type == "configuration"
        assert result.team_name == "Test Team"
        assert result.environment_slug == "test-env"

    @respx.mock
    def test_get_v2_auto_detect(self, management_client):
        """Auto-detects v2 endpoint with management credentials."""
        respx.get("https://api.honeycomb.io/2/auth").mock(
            return_value=Response(
                200,
                json={
                    "data": {
                        "id": "mgmt123",
                        "type": "api-keys",
                        "attributes": {
                            "name": "My Mgmt Key",
                            "key_type": "management",
                            "disabled": False,
                            "scopes": ["environments:read", "api-keys:write"],
                            "timestamps": {},
                        },
                        "relationships": {"team": {"data": {"type": "teams", "id": "team123"}}},
                    },
                    "included": [
                        {
                            "id": "team123",
                            "type": "teams",
                            "attributes": {"name": "My Team", "slug": "my-team"},
                        }
                    ],
                },
            )
        )

        result = management_client.auth.get()

        assert isinstance(result, AuthInfoV2)
        assert result.id == "mgmt123"
        assert result.name == "My Mgmt Key"
        assert result.team_name == "My Team"
        assert "api-keys:write" in result.scopes

    def test_explicit_v2_with_api_key_raises(self, api_key_client):
        """Raises ValueError when forcing v2 with API key credentials."""
        with pytest.raises(ValueError, match="requires management key"):
            api_key_client.auth.get(use_v2=True)

    @respx.mock
    def test_explicit_v1_with_management_key(self, management_client):
        """Can force v1 endpoint even with management credentials."""
        respx.get("https://api.honeycomb.io/1/auth").mock(
            return_value=Response(
                200,
                json={
                    "id": "key123",
                    "type": "ingest",
                    "team": {"name": "Team", "slug": "team"},
                    "environment": {"name": "Env", "slug": "env"},
                    "api_key_access": {},
                },
            )
        )

        result = management_client.auth.get(use_v2=False)

        assert isinstance(result, AuthInfo)
