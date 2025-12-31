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
{%
   include "../examples/api_keys/basic_api_key.py"
   start="# start_example:list"
   end="# end_example:list"
%}
```

### Filter by Key Type

```python
{%
   include "../examples/api_keys/basic_api_key.py"
   start="# start_example:list_by_type"
   end="# end_example:list_by_type"
%}
```

### Get a Specific API Key

```python
{%
   include "../examples/api_keys/basic_api_key.py"
   start="# start_example:get"
   end="# end_example:get"
%}
```

### Create an API Key

```python
{%
   include "../examples/api_keys/basic_api_key.py"
   start="# start_example:create"
   end="# end_example:create"
%}
```

### Update an API Key

```python
{%
   include "../examples/api_keys/basic_api_key.py"
   start="# start_example:update"
   end="# end_example:update"
%}
```

### Delete an API Key

```python
{%
   include "../examples/api_keys/basic_api_key.py"
   start="# start_example:delete"
   end="# end_example:delete"
%}
```

## Key ID Prefixes

Key IDs have prefixes indicating their type:
- `hcxik_...` - Ingest Key
- `hcxlk_...` - Configuration Key

## Sync Usage

All API key operations have sync equivalents (team is auto-detected):

```python
with HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx",
    sync=True
) as client:
    keys = client.api_keys.list()
    key = client.api_keys.get(key_id)
    key = client.api_keys.create(ApiKeyCreate(...))
    updated = client.api_keys.update(key_id, ApiKeyUpdate(...))
    client.api_keys.delete(key_id)
```

## Configuration Key Permissions

When creating configuration keys, you **MUST** specify permissions. Without them, the key will have NO permissions:

```python
from honeycomb.models.api_keys import ApiKeyCreate, ApiKeyType

# Full access configuration key
key = await client.api_keys.create_async(
    api_key=ApiKeyCreate(
        name="Full Access Key",
        key_type=ApiKeyType.CONFIGURATION,
        environment_id="hcaen_xxx",
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
        }
    )
)
```

Available permissions:
- `create_datasets` - Create and manage datasets
- `send_events` - Send events to datasets
- `manage_markers` - Create and manage markers
- `manage_triggers` - Create and manage triggers
- `manage_boards` - Create and manage boards
- `run_queries` - Execute queries
- `manage_columns` - Manage columns
- `manage_slos` - Create and manage SLOs
- `manage_recipients` - Manage recipients
- `manage_privateBoards` - Manage private boards

**Important**: The `secret` field is only returned when creating a key. Save it immediately - it cannot be retrieved later!
