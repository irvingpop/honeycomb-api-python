# Working with Environments (v2)

Environments help organize your Honeycomb data and API keys by deployment stage (production, staging, etc.). This v2 API requires Management Key authentication.

!!! note "Management Key Required"
    The Environments API requires a Management Key (not a regular API key). See [Authentication](../getting-started/authentication.md#management-key-authentication) for setup.

!!! info "Automatic Pagination"
    The `list()` and `list_async()` methods automatically paginate through all results. For teams with many environments, this may result in multiple API requests. The default rate limit is 100 requests per minute per operation. If you need higher limits, contact [Honeycomb support](https://www.honeycomb.io/support).

## Basic Environment Operations

### List Environments

```python
from honeycomb import HoneycombClient

async with HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx"
) as client:
    environments = await client.environments.list_async(team="my-team")

    for env in environments:
        print(f"{env.name} ({env.slug})")
        print(f"  Color: {env.color}")
        print(f"  Protected: {env.delete_protected}")
```

### Get a Specific Environment

```python
env = await client.environments.get_async("my-team", "env-id")

print(f"Name: {env.name}")
print(f"Slug: {env.slug}")
print(f"Description: {env.description}")
print(f"Color: {env.color}")
```

### Delete an Environment

!!! warning
    Deleting an environment cannot be undone. Enable delete protection for critical environments.

```python
await client.environments.delete_async("my-team", "env-id")
```

## Creating Environments

### Basic Environment

```python
from honeycomb import EnvironmentCreate, EnvironmentColor

env = await client.environments.create_async(
    "my-team",
    EnvironmentCreate(
        name="Production",
        description="Production environment",
        color=EnvironmentColor.RED  # Visual indicator
    )
)

print(f"Created environment: {env.id}")
print(f"Slug: {env.slug}")
```

### Environment with Delete Protection

Protect critical environments from accidental deletion:

```python
env = await client.environments.create_async(
    "my-team",
    EnvironmentCreate(
        name="Production",
        description="Primary production environment - do not delete!",
        color=EnvironmentColor.RED
    )
)

# Enable delete protection after creation
await client.environments.update_async(
    "my-team",
    env.id,
    EnvironmentUpdate(delete_protected=True)
)
```

## Updating Environments

### Update Description and Color

```python
from honeycomb import EnvironmentUpdate, EnvironmentColor

updated_env = await client.environments.update_async(
    "my-team",
    "env-id",
    EnvironmentUpdate(
        description="Updated: Staging environment for QA",
        color=EnvironmentColor.LIGHT_BLUE
    )
)
```

### Enable/Disable Delete Protection

```python
# Enable protection
await client.environments.update_async(
    "my-team",
    "prod-env-id",
    EnvironmentUpdate(delete_protected=True)
)

# Disable protection (be careful!)
await client.environments.update_async(
    "my-team",
    "old-env-id",
    EnvironmentUpdate(delete_protected=False)
)
```

## Environment Colors

Visual indicators in the Honeycomb UI:

```python
from honeycomb import EnvironmentColor

colors = {
    "Production": EnvironmentColor.RED,
    "Staging": EnvironmentColor.GOLD,
    "Development": EnvironmentColor.BLUE,
    "Test": EnvironmentColor.LIGHT_BLUE,
    "Preview": EnvironmentColor.LIGHT_GREEN,
}

for name, color in colors.items():
    env = await client.environments.create_async(
        "my-team",
        EnvironmentCreate(name=name, color=color)
    )
    print(f"Created {name}: {env.slug}")
```

Available colors:

- Standard: `BLUE`, `GREEN`, `GOLD`, `RED`, `PURPLE`
- Light: `LIGHT_BLUE`, `LIGHT_GREEN`, `LIGHT_GOLD`, `LIGHT_RED`, `LIGHT_PURPLE`

## Sync Usage

```python
with HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx",
    sync=True
) as client:
    # List environments
    envs = client.environments.list("my-team")

    # Create environment
    env = client.environments.create(
        "my-team",
        EnvironmentCreate(
            name="Development",
            color=EnvironmentColor.BLUE
        )
    )

    # Update environment
    client.environments.update(
        "my-team",
        env.id,
        EnvironmentUpdate(delete_protected=True)
    )

    # Delete environment
    client.environments.delete("my-team", "env-id")
```

## Environment Management Patterns

### Standard Environment Setup

Create a standard set of environments:

```python
from honeycomb import EnvironmentCreate, EnvironmentColor, EnvironmentUpdate

standard_envs = [
    ("Production", EnvironmentColor.RED, True),    # protected
    ("Staging", EnvironmentColor.GOLD, False),
    ("Development", EnvironmentColor.BLUE, False),
    ("Test", EnvironmentColor.LIGHT_BLUE, False),
]

created_envs = []
for name, color, protected in standard_envs:
    # Create environment
    env = await client.environments.create_async(
        "my-team",
        EnvironmentCreate(
            name=name,
            description=f"{name} environment",
            color=color
        )
    )

    # Set protection if needed
    if protected:
        await client.environments.update_async(
            "my-team",
            env.id,
            EnvironmentUpdate(delete_protected=True)
        )

    created_envs.append(env)
    print(f"✓ Created {name} ({env.slug})")
```

### Environment Audit

Check environment configurations:

```python
envs = await client.environments.list_async("my-team")

print(f"Total environments: {len(envs)}\n")

protected = [e for e in envs if e.delete_protected]
unprotected = [e for e in envs if not e.delete_protected]

print(f"Protected ({len(protected)}):")
for env in protected:
    print(f"  🔒 {env.name}")

print(f"\nUnprotected ({len(unprotected)}):")
for env in unprotected:
    print(f"  🔓 {env.name}")
```

### Clone Environment Configuration

When creating a new environment similar to an existing one:

```python
# Get existing environment config
source_env = await client.environments.get_async("my-team", "staging-env-id")

# Create similar environment
new_env = await client.environments.create_async(
    "my-team",
    EnvironmentCreate(
        name=f"{source_env.name} - Clone",
        description=f"Cloned from {source_env.name}",
        color=source_env.color
    )
)

# Note: You'd also want to clone API keys, datasets, etc. separately
```

## Environments and API Keys

Environments are linked to API keys. When managing environments, also consider API keys:

```python
# List all API keys for an environment
all_keys = await client.api_keys.list_async("my-team")
env_keys = [k for k in all_keys if k.environment_id == "env-id"]

print(f"Keys in environment: {len(env_keys)}")
for key in env_keys:
    print(f"  {key.name} ({key.key_type})")
```

## Best Practices

1. **Use Delete Protection**: Always protect production environments
2. **Consistent Naming**: Use standard names (Production, Staging, Development)
3. **Color Coding**: Use consistent colors across teams
   - RED for production
   - GOLD/YELLOW for staging
   - BLUE for development
4. **Descriptions**: Document environment purpose and any special configuration
5. **Audit Regularly**: Review environment list and remove unused ones
6. **Coordinate Changes**: Notify team before deleting or significantly changing environments

## Example: Environment Lifecycle Management

```python
from honeycomb import (
    HoneycombClient,
    EnvironmentCreate,
    EnvironmentUpdate,
    EnvironmentColor
)

class EnvironmentManager:
    def __init__(self, client: HoneycombClient, team: str):
        self.client = client
        self.team = team

    async def create_feature_env(self, feature_name: str) -> str:
        """Create a temporary feature environment."""
        env = await self.client.environments.create_async(
            self.team,
            EnvironmentCreate(
                name=f"Feature: {feature_name}",
                description=f"Temporary environment for {feature_name} development",
                color=EnvironmentColor.LIGHT_GREEN
            )
        )
        return env.id

    async def promote_to_protected(self, env_id: str):
        """Promote environment to protected status."""
        await self.client.environments.update_async(
            self.team,
            env_id,
            EnvironmentUpdate(
                description="PROMOTED TO PROTECTED - DO NOT DELETE",
                delete_protected=True
            )
        )

    async def cleanup_feature_envs(self):
        """Remove unprotected feature environments."""
        envs = await self.client.environments.list_async(self.team)

        feature_envs = [
            e for e in envs
            if e.name.startswith("Feature:")
            and not e.delete_protected
        ]

        print(f"Found {len(feature_envs)} feature environments to clean up:")
        for env in feature_envs:
            print(f"  Deleting: {env.name}")
            await self.client.environments.delete_async(self.team, env.id)

# Usage
async with HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx"
) as client:
    manager = EnvironmentManager(client, "my-team")

    # Create feature environment
    feature_env_id = await manager.create_feature_env("oauth-integration")

    # Later: promote if it becomes permanent
    # await manager.promote_to_protected(feature_env_id)

    # Periodic cleanup
    await manager.cleanup_feature_envs()
```

## Troubleshooting

### Cannot Delete Environment

If you get an error when trying to delete:

1. Check if delete protection is enabled:
   ```python
   env = await client.environments.get_async("my-team", "env-id")
   if env.delete_protected:
       print("Environment is delete-protected")
   ```

2. Disable protection first:
   ```python
   await client.environments.update_async(
       "my-team",
       "env-id",
       EnvironmentUpdate(delete_protected=False)
   )
   # Now you can delete
   await client.environments.delete_async("my-team", "env-id")
   ```

### Environment Name vs. Slug

- **Name**: Display name (can have spaces, can be changed)
- **Slug**: URL-safe identifier (auto-generated, lowercase, cannot be changed)

```python
env = EnvironmentCreate(name="My Production Environment")
# Creates slug: "my-production-environment"
```
