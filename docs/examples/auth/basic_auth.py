"""Auth endpoint examples.

These examples demonstrate retrieving API key metadata
using both v1 and v2 auth endpoints.
"""

from __future__ import annotations

from honeycomb import HoneycombClient


# start_example:basic_usage
async def get_auth_info_basic(client: HoneycombClient):
    """Get auth info using an API key (v1).

    Args:
        client: Authenticated HoneycombClient with API key

    Returns:
        AuthInfo object with team and environment details
    """
    auth_info = await client.auth.get_async()

    print(f"Team: {auth_info.team_name}")
    print(f"Environment: {auth_info.environment_name}")
    print(f"Key Type: {auth_info.type}")
    return auth_info


# end_example:basic_usage


# start_example:management_key
async def get_auth_info_management(client: HoneycombClient):
    """Get auth info using management credentials (v2).

    Args:
        client: HoneycombClient with management_key and management_secret

    Returns:
        AuthInfoV2 object with scopes and team details
    """
    auth_info = await client.auth.get_async()  # Auto-detects v2
    print(f"Key Name: {auth_info.name}")
    print(f"Scopes: {auth_info.scopes}")
    print(f"Team: {auth_info.team_name}")
    return auth_info


# end_example:management_key


# start_example:explicit_v2
async def get_auth_explicit_v2(client: HoneycombClient):
    """Force v2 endpoint (errors if not using management key).

    Args:
        client: HoneycombClient with management credentials

    Returns:
        AuthInfoV2 object
    """
    auth_info = await client.auth.get_async(use_v2=True)
    return auth_info


# end_example:explicit_v2


# start_example:explicit_v1
async def get_auth_explicit_v1(client: HoneycombClient):
    """Force v1 endpoint (even with management key).

    Args:
        client: HoneycombClient

    Returns:
        AuthInfo object
    """
    auth_info = await client.auth.get_async(use_v2=False)
    return auth_info


# end_example:explicit_v1


# TEST_ASSERTIONS
async def test_basic_usage(auth_info) -> None:
    """Verify basic usage example worked correctly."""
    assert auth_info.team_name is not None
    assert auth_info.environment_name is not None
    assert auth_info.type in ("configuration", "ingest")


async def test_management_key(auth_info) -> None:
    """Verify management key example worked correctly."""
    assert auth_info.name is not None
    assert auth_info.key_type == "management"
    assert isinstance(auth_info.scopes, list)
    assert auth_info.team_name is not None
