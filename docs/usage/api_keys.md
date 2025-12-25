# Working with API Keys (v2)

API Keys are team-scoped resources that control access to your Honeycomb data. This v2 API requires Management Key authentication.

!!! note "Management Key Required"
    The API Keys API requires a Management Key (not a regular API key). See [Authentication](../getting-started/authentication.md#management-key-authentication) for setup.

!!! info "Automatic Pagination"
    The `list()` and `list_async()` methods automatically paginate through all results. For teams with many API keys, this may result in multiple API requests. The default rate limit is 100 requests per minute per operation. If you need higher limits, contact [Honeycomb support](https://www.honeycomb.io/support).

## Key Types

- **Ingest Keys**: For sending data to Honeycomb (used in instrumentation)
- **Configuration Keys**: For API access (querying, managing resources)

## Basic API Key Operations

### List API Keys

```python
from honeycomb import HoneycombClient

async with HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx"
) as client:
    keys = await client.api_keys.list_async(team="my-team")

    for key in keys:
        print(f"{key.name} ({key.key_type})")
        print(f"  ID: {key.id}")
        print(f"  Environment: {key.environment_id}")
        print(f"  Disabled: {key.disabled}")
```

### Filter by Key Type

```python
# List only ingest keys
ingest_keys = await client.api_keys.list_async(
    team="my-team",
    key_type="ingest"
)

# List only configuration keys
config_keys = await client.api_keys.list_async(
    team="my-team",
    key_type="configuration"
)
```

### Get a Specific API Key

```python
key = await client.api_keys.get_async("my-team", "hcxik_...")

print(f"Name: {key.name}")
print(f"Type: {key.key_type}")
print(f"Environment: {key.environment_id}")
```

### Delete an API Key

```python
await client.api_keys.delete_async("my-team", "hcxik_...")
```

## Creating API Keys

### Create an Ingest Key

```python
from honeycomb import ApiKeyCreate, ApiKeyType

key = await client.api_keys.create_async(
    "my-team",
    ApiKeyCreate(
        name="Production Ingest Key",
        key_type=ApiKeyType.INGEST,
        environment_id="env-123",
        disabled=False
    )
)

# IMPORTANT: Save the secret immediately - it's only shown once!
print(f"Key ID: {key.id}")
print(f"Secret: {key.secret}")  # Only available at creation time

# Combined key for use: {key.id}{key.secret}
full_key = f"{key.id}{key.secret}"
print(f"Use this in X-Honeycomb-Team header: {full_key}")
```

### Create a Configuration Key

```python
key = await client.api_keys.create_async(
    "my-team",
    ApiKeyCreate(
        name="CI/CD Configuration Key",
        key_type=ApiKeyType.CONFIGURATION,
        environment_id="env-123",
        disabled=False
    )
)

print(f"Config Key: {key.id}{key.secret}")
```

### Create a Disabled Key

Useful for pre-provisioning keys:

```python
key = await client.api_keys.create_async(
    "my-team",
    ApiKeyCreate(
        name="Future Production Key",
        key_type=ApiKeyType.INGEST,
        environment_id="env-123",
        disabled=True  # Enable later
    )
)
```

## Updating API Keys

You can update the name and disabled status:

```python
updated_key = await client.api_keys.update_async(
    "my-team",
    "hcxik_...",
    ApiKeyCreate(
        name="Updated Key Name",
        key_type=ApiKeyType.INGEST,  # Must match existing type
        environment_id="env-123",  # Must match existing environment
        disabled=True  # Disable the key
    )
)
```

## Sync Usage

```python
with HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx",
    sync=True
) as client:
    # List keys
    keys = client.api_keys.list("my-team")

    # Create key
    key = client.api_keys.create(
        "my-team",
        ApiKeyCreate(
            name="New Ingest Key",
            key_type=ApiKeyType.INGEST,
            environment_id="env-123"
        )
    )

    # Delete key
    client.api_keys.delete("my-team", "hcxik_...")
```

## Key Management Patterns

### Rotate Keys

```python
# 1. Create new key
new_key = await client.api_keys.create_async(
    "my-team",
    ApiKeyCreate(
        name="Production Ingest - 2024-Q1",
        key_type=ApiKeyType.INGEST,
        environment_id="prod-env-id"
    )
)
print(f"New key: {new_key.id}{new_key.secret}")

# 2. Update application configuration with new key
# (manual step or automation)

# 3. Disable old key
await client.api_keys.update_async(
    "my-team",
    "old-key-id",
    ApiKeyCreate(
        name="Production Ingest - OLD (disabled)",
        key_type=ApiKeyType.INGEST,
        environment_id="prod-env-id",
        disabled=True
    )
)

# 4. Monitor for 24-48 hours, then delete old key
await client.api_keys.delete_async("my-team", "old-key-id")
```

### Per-Service Keys

Create separate keys for different services:

```python
services = ["api", "worker", "cron"]
env_id = "prod-env-id"

for service in services:
    key = await client.api_keys.create_async(
        "my-team",
        ApiKeyCreate(
            name=f"Production - {service}",
            key_type=ApiKeyType.INGEST,
            environment_id=env_id
        )
    )
    print(f"{service}: {key.id}{key.secret}")
```

### Audit Keys

List and audit all keys across environments:

```python
keys = await client.api_keys.list_async("my-team")

by_env = {}
for key in keys:
    env = key.environment_id or "unknown"
    if env not in by_env:
        by_env[env] = []
    by_env[env].append(key)

for env, env_keys in by_env.items():
    print(f"\nEnvironment: {env}")
    for key in env_keys:
        status = "DISABLED" if key.disabled else "active"
        print(f"  {key.name} ({key.key_type}) - {status}")
```

## Key ID Prefixes

Key IDs have prefixes indicating their type:

- `hcxik_...` - Ingest Key
- `hcxlk_...` - Configuration Key (formerly "Legacy Key")

## Security Best Practices

1. **Rotate Regularly**: Rotate keys quarterly or after team changes
2. **Scope Keys**: Use per-service or per-environment keys
3. **Disable, Don't Delete**: Disable first to ensure no active usage
4. **Save Secrets**: Store secrets in secure credential management (Vault, etc.)
5. **Audit Usage**: Regular review what keys exist and their purpose
6. **Least Privilege**: Use ingest keys for data sending, config keys for API access
7. **Monitor Creation**: Alert on new key creation in production

## Example: Key Management Script

```python
from honeycomb import HoneycombClient, ApiKeyCreate, ApiKeyType
from datetime import datetime, timedelta

async def audit_and_rotate_keys(
    client: HoneycombClient,
    team: str,
    rotation_days: int = 90
):
    """Audit keys and flag those needing rotation."""
    keys = await client.api_keys.list_async(team)

    now = datetime.now()
    needs_rotation = []

    for key in keys:
        if key.created_at:
            age = now - key.created_at
            if age > timedelta(days=rotation_days):
                needs_rotation.append({
                    "key": key,
                    "age_days": age.days
                })

    if needs_rotation:
        print(f"⚠️  {len(needs_rotation)} keys need rotation:\n")
        for item in needs_rotation:
            key = item["key"]
            print(f"  {key.name} ({key.key_type})")
            print(f"    Age: {item['age_days']} days")
            print(f"    Environment: {key.environment_id}")
            print()

    return needs_rotation

# Usage
async with HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx"
) as client:
    old_keys = await audit_and_rotate_keys(client, "my-team", rotation_days=90)
```
