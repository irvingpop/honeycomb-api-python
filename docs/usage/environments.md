# Working with Environments (v2)

Environments help organize your Honeycomb data and API keys by deployment stage (production, staging, etc.). This v2 API requires Management Key authentication.

!!! note "Management Key Required"
    The Environments API requires a Management Key (not a regular API key). See [Authentication](../getting-started/authentication.md#management-key-authentication) for setup.

!!! info "Automatic Pagination"
    The `list()` and `list_async()` methods automatically paginate through all results. For teams with many environments, this may result in multiple API requests. The default rate limit is 100 requests per minute per operation. If you need higher limits, contact [Honeycomb support](https://www.honeycomb.io/support).

## Basic Environment Operations

### List Environments

```python
{%
   include "../examples/environments/basic_environment.py"
   start="# start_example:list"
   end="# end_example:list"
%}
```

### Get a Specific Environment

```python
{%
   include "../examples/environments/basic_environment.py"
   start="# start_example:get"
   end="# end_example:get"
%}
```

### Create an Environment

```python
{%
   include "../examples/environments/basic_environment.py"
   start="# start_example:create"
   end="# end_example:create"
%}
```

### Update an Environment

```python
{%
   include "../examples/environments/basic_environment.py"
   start="# start_example:update"
   end="# end_example:update"
%}
```

### Delete an Environment

!!! warning
    Deleting an environment cannot be undone. Enable delete protection for critical environments.

```python
{%
   include "../examples/environments/basic_environment.py"
   start="# start_example:delete"
   end="# end_example:delete"
%}
```

## Environment Colors

Available colors: `BLUE`, `GREEN`, `GOLD`, `RED`, `PURPLE`, `LIGHT_BLUE`, `LIGHT_GREEN`, `LIGHT_GOLD`, `LIGHT_RED`, `LIGHT_PURPLE`

**Note**: `CLASSIC` is a special read-only color for auto-created Classic environments.

## Sync Usage

All environment operations have sync equivalents:

```python
with HoneycombClient(
    management_key="hcamk_xxx",
    management_secret="xxx",
    sync=True
) as client:
    envs = client.environments.list("my-team")
    env = client.environments.get("my-team", env_id)
    env = client.environments.create("my-team", EnvironmentCreate(...))
    updated = client.environments.update("my-team", env_id, EnvironmentUpdate(...))
    client.environments.delete("my-team", env_id)
```

## Delete Protection

Use `delete_protected=True` in `EnvironmentUpdate` to prevent accidental deletion of critical environments. To delete a protected environment, first disable protection via update.
