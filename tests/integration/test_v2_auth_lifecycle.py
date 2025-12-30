"""Live integration tests for v2 auth and management API lifecycle."""

import os
import uuid

import pytest

from honeycomb import HoneycombClient
from honeycomb.models.api_keys import ApiKeyCreate, ApiKeyType
from honeycomb.models.environments import EnvironmentColor, EnvironmentCreate, EnvironmentUpdate


@pytest.fixture
def management_client():
    """Get a management client from environment variables."""
    mgmt_key = os.environ.get("HONEYCOMB_MANAGEMENT_KEY")
    mgmt_secret = os.environ.get("HONEYCOMB_MANAGEMENT_SECRET")

    if not mgmt_key or not mgmt_secret:
        pytest.skip("Management credentials not configured")

    return HoneycombClient(
        management_key=mgmt_key,
        management_secret=mgmt_secret,
    )


@pytest.mark.live
@pytest.mark.asyncio
class TestV2AuthLifecycle:
    """Live API test for v2 auth and management operations.

    This test verifies the complete v2 management API lifecycle:
    1. Get auth info (verify management key works)
    2. Create a test environment
    3. Create an API key in that environment
    4. Delete the API key
    5. Delete the environment
    """

    async def test_full_v2_lifecycle(self, management_client):
        """Complete v2 lifecycle test."""
        unique_id = uuid.uuid4().hex[:8]

        # 1. Verify auth
        auth_info = await management_client.auth.get_async()
        assert auth_info.key_type == "management"
        assert auth_info.team_slug is not None
        team_slug = auth_info.team_slug

        print(f"Authenticated as: {auth_info.name}")
        print(f"Team: {team_slug}")
        print(f"Scopes: {auth_info.scopes}")

        # 2. Create environment
        env_name = f"test-auth-{unique_id}"
        env = await management_client.environments.create_async(
            environment=EnvironmentCreate(
                name=env_name,
                color=EnvironmentColor.BLUE,
            ),
        )
        print(f"Created environment: {env.id} ({env.name})")

        api_key = None
        try:
            # 3. Create API key in environment
            key_name = f"test-key-{unique_id}"
            api_key = await management_client.api_keys.create_async(
                api_key=ApiKeyCreate(
                    name=key_name,
                    key_type=ApiKeyType.INGEST,
                    environment_id=env.id,
                ),
            )
            print(f"Created API key: {api_key.id} ({api_key.name})")

            # Verify key attributes
            assert api_key.id is not None
            assert api_key.secret is not None  # Only returned on creation
            assert api_key.name == key_name
            assert api_key.key_type == ApiKeyType.INGEST

            # 4. Delete API key
            await management_client.api_keys.delete_async(key_id=api_key.id)
            print(f"Deleted API key: {api_key.id}")

        finally:
            # 5. Cleanup: Disable delete protection then delete environment
            await management_client.environments.update_async(
                env_id=env.id,
                environment=EnvironmentUpdate(delete_protected=False),
            )
            await management_client.environments.delete_async(
                env_id=env.id,
            )
            print(f"Deleted environment: {env.id}")

        print("V2 lifecycle test completed successfully!")
