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

All API key operations have sync equivalents:

```python
with HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx",
    sync=True
) as client:
    keys = client.api_keys.list("my-team")
    key = client.api_keys.get("my-team", key_id)
    key = client.api_keys.create("my-team", ApiKeyCreate(...))
    updated = client.api_keys.update("my-team", key_id, ApiKeyCreate(...))
    client.api_keys.delete("my-team", key_id)
```

**Important**: The `secret` field is only returned when creating a key. Save it immediately - it cannot be retrieved later!
