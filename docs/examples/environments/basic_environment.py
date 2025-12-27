"""Basic environment CRUD examples.

These examples demonstrate managing environments using the Management API.
Requires management key authentication.
"""

from __future__ import annotations

from honeycomb import Environment, EnvironmentColor, EnvironmentCreate, EnvironmentUpdate, HoneycombClient


# start_example:list
async def list_environments(client: HoneycombClient, team: str) -> list[Environment]:
    """List all environments in a team.

    Args:
        client: HoneycombClient with management key
        team: Team slug

    Returns:
        List of environments
    """
    environments = await client.environments.list_async(team)
    for env in environments:
        color = f" ({env.color.value})" if env.color else ""
        print(f"{env.name}{color}: {env.slug}")
    return environments


# end_example:list


# start_example:get
async def get_environment(client: HoneycombClient, team: str, env_id: str) -> Environment:
    """Get a specific environment by ID.

    Args:
        client: HoneycombClient with management key
        team: Team slug
        env_id: Environment ID

    Returns:
        The environment object
    """
    env = await client.environments.get_async(team, env_id)
    print(f"Name: {env.name}")
    print(f"Slug: {env.slug}")
    print(f"Description: {env.description}")
    print(f"Delete Protected: {env.delete_protected}")
    return env


# end_example:get


# start_example:create
async def create_environment(client: HoneycombClient, team: str) -> str:
    """Create a new environment.

    Args:
        client: HoneycombClient with management key
        team: Team slug

    Returns:
        The created environment ID
    """
    env = await client.environments.create_async(
        team,
        EnvironmentCreate(
            name="Staging",
            description="Staging environment for testing",
            color=EnvironmentColor.BLUE,
        ),
    )
    return env.id


# end_example:create


# start_example:update
async def update_environment(client: HoneycombClient, team: str, env_id: str) -> Environment:
    """Update an environment's properties.

    Args:
        client: HoneycombClient with management key
        team: Team slug
        env_id: Environment ID to update

    Returns:
        The updated environment
    """
    updated = await client.environments.update_async(
        team,
        env_id,
        EnvironmentUpdate(
            description="Updated: Staging environment for pre-production testing",
            color=EnvironmentColor.GREEN,
            delete_protected=True,  # Prevent accidental deletion
        ),
    )
    return updated


# end_example:update


# start_example:delete
async def delete_environment(client: HoneycombClient, team: str, env_id: str) -> None:
    """Delete an environment.

    Args:
        client: HoneycombClient with management key
        team: Team slug
        env_id: Environment ID to delete

    Note: If the environment is delete_protected, this will fail with a 409 error.
    """
    await client.environments.delete_async(team, env_id)


# end_example:delete


# TEST_ASSERTIONS
async def test_list_environments(environments: list[Environment]) -> None:
    """Verify list example worked."""
    assert isinstance(environments, list)


async def test_get_environment(env: Environment, expected_env_id: str) -> None:
    """Verify get example worked."""
    assert env.id == expected_env_id
    assert env.name is not None


async def test_create_environment(env_id: str) -> None:
    """Verify create example worked."""
    assert env_id is not None
    assert isinstance(env_id, str)


async def test_update_environment(updated: Environment, original_env_id: str) -> None:
    """Verify update example worked."""
    assert updated.id == original_env_id
    assert "Updated:" in updated.description
    assert updated.color == EnvironmentColor.GREEN
    assert updated.delete_protected is True


# CLEANUP
async def cleanup(client: HoneycombClient, team: str, env_id: str) -> None:
    """Clean up resources created by example."""
    # Need to disable delete protection first if it was set
    try:
        await client.environments.update_async(
            team,
            env_id,
            EnvironmentUpdate(delete_protected=False),
        )
    except Exception:
        pass  # May already be unprotected

    await delete_environment(client, team, env_id)
