# Authentication Info

The `auth` resource lets you retrieve metadata about the API key currently being used to authenticate with Honeycomb.

## Use Cases

- Verify your API key is working correctly
- Discover which team/environment a key belongs to
- Check key permissions and scopes
- Audit key expiration dates

## Basic Usage

Get auth info using a configuration key (v1) `$HONEYCOMB_API_KEY`:

```python
{%
   include "../examples/auth/basic_auth.py"
   start="# start_example:basic_usage"
   end="# end_example:basic_usage"
%}
```

## Management Key

Get auth info using a management key (v2) `$HONEYCOMB_MANAGEMENT_KEY` and `$HONEYCOMB_MANAGEMENT_SECRET`:

```python
{%
   include "../examples/auth/basic_auth.py"
   start="# start_example:management_key"
   end="# end_example:management_key"
%}
```

## Explicit Version Selection

Force v2 endpoint (errors if not using management key):

```python
{%
   include "../examples/auth/basic_auth.py"
   start="# start_example:explicit_v2"
   end="# end_example:explicit_v2"
%}
```

Force v1 endpoint (even with management key):

```python
{%
   include "../examples/auth/basic_auth.py"
   start="# start_example:explicit_v1"
   end="# end_example:explicit_v1"
%}
```

## Response Models

### AuthInfo (v1)

| Field | Type | Description |
|-------|------|-------------|
| id | str | API key identifier |
| type | str | `configuration` or `ingest` |
| team_name | str | Team name |
| team_slug | str | Team URL slug |
| environment_name | str | Environment name |
| environment_slug | str | Environment URL slug |
| api_key_access | dict | Key capabilities |
| time_to_live | str? | Expiration time (RFC3339) |

### AuthInfoV2 (v2 - Management Key)

| Field | Type | Description |
|-------|------|-------------|
| id | str | Management key identifier |
| name | str | Human-readable name |
| key_type | str | Always `management` |
| disabled | bool | Whether key is disabled |
| scopes | list[str] | Authorized scopes |
| team_id | str | Team identifier |
| team_name | str? | Team name |
| team_slug | str? | Team URL slug |
| created_at | datetime? | Creation timestamp |
| updated_at | datetime? | Last update timestamp |
