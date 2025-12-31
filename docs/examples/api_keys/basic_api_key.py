"""Basic API key CRUD examples.

These examples demonstrate managing API keys using the Management API.
Requires management key authentication.
"""

from __future__ import annotations

from honeycomb import ApiKey, ApiKeyCreate, ApiKeyType, HoneycombClient


# start_example:list
async def list_api_keys(client: HoneycombClient) -> list[ApiKey]:
    """List all API keys in the authenticated team.

    Args:
        client: HoneycombClient with management key

    Returns:
        List of API keys
    """
    keys = await client.api_keys.list_async()
    for key in keys:
        disabled = " (disabled)" if key.disabled else ""
        print(f"{key.name} ({key.key_type.value}){disabled}: {key.id}")
    return keys


# end_example:list


# start_example:list_by_type
async def list_ingest_keys(client: HoneycombClient) -> list[ApiKey]:
    """List only ingest keys.

    Args:
        client: HoneycombClient with management key

    Returns:
        List of ingest API keys
    """
    keys = await client.api_keys.list_async(key_type="ingest")
    print(f"Found {len(keys)} ingest keys")
    return keys


# end_example:list_by_type


# start_example:get
async def get_api_key(client: HoneycombClient, key_id: str) -> ApiKey:
    """Get a specific API key by ID.

    Args:
        client: HoneycombClient with management key
        key_id: API key ID

    Returns:
        The API key object
    """
    key = await client.api_keys.get_async(key_id)
    print(f"Name: {key.name}")
    print(f"Type: {key.key_type.value}")
    print(f"Environment: {key.environment_id}")
    print(f"Disabled: {key.disabled}")
    if key.permissions:
        print(f"Permissions: {list(k for k, v in key.permissions.items() if v)}")
    return key


# end_example:get


# start_example:create
async def create_api_key(client: HoneycombClient, environment_id: str) -> tuple[str, str]:
    """Create a new configuration API key with full permissions.

    Args:
        client: HoneycombClient with management key
        environment_id: Environment ID for the key

    Returns:
        Tuple of (key_id, secret)

    Note: The secret is only returned during creation. Save it securely!
    """
    key = await client.api_keys.create_async(
        api_key=ApiKeyCreate(
            name="Integration Test Key",
            key_type=ApiKeyType.CONFIGURATION,
            environment_id=environment_id,
            permissions={
                "create_datasets": True,
                "send_events": True,
                "manage_markers": True,
                "manage_triggers": True,
                "manage_boards": True,
                "run_queries": True,
                "manage_columns": True,
                "manage_slos": True,
                "manage_recipients": True,
                "manage_privateBoards": True,
            },
        ),
    )

    # Secret is only available during creation!
    print(f"Created key: {key.id}")
    print(f"Secret: {key.secret}")
    print("⚠️  Save the secret - it won't be shown again!")

    return key.id, key.secret or ""


# end_example:create


# start_example:update
async def update_api_key(client: HoneycombClient, key_id: str) -> ApiKey:
    """Update an API key's name and status.

    Args:
        client: HoneycombClient with management key
        key_id: API key ID to update

    Returns:
        The updated API key
    """
    from honeycomb.models.api_keys import ApiKeyUpdate

    # Update with new values
    updated = await client.api_keys.update_async(
        key_id=key_id,
        api_key=ApiKeyUpdate(
            name="Updated Integration Test Key",
            disabled=True,  # Disable the key
        ),
    )
    return updated


# end_example:update


# start_example:delete
async def delete_api_key(client: HoneycombClient, key_id: str) -> None:
    """Delete an API key.

    Args:
        client: HoneycombClient with management key
        key_id: API key ID to delete

    Warning: Deleting a key immediately revokes access. Applications using
    this key will fail to authenticate.
    """
    await client.api_keys.delete_async(key_id=key_id)


# end_example:delete


# TEST_ASSERTIONS
async def test_list_api_keys(keys: list[ApiKey]) -> None:
    """Verify list example worked."""
    assert isinstance(keys, list)


async def test_get_api_key(key: ApiKey, expected_key_id: str) -> None:
    """Verify get example worked."""
    assert key.id == expected_key_id
    assert key.name is not None


async def test_create_api_key(key_id: str, secret: str) -> None:
    """Verify create example worked."""
    assert key_id is not None
    assert secret is not None
    assert isinstance(key_id, str)
    assert isinstance(secret, str)


async def test_update_api_key(updated: ApiKey, original_key_id: str) -> None:
    """Verify update example worked."""
    assert updated.id == original_key_id
    assert "Updated" in updated.name
    assert updated.disabled is True


# CLEANUP
async def cleanup(client: HoneycombClient, key_id: str) -> None:
    """Clean up resources created by example."""
    await delete_api_key(client, key_id)
