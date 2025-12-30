# Auth Endpoint Implementation Plan

## Overview

Add first-class support for the `/1/auth` (v1) and `/2/auth` (v2) endpoints to retrieve API key metadata. This includes a resource layer, CLI commands, Claude tools, unit tests, documentation, and a comprehensive live integration test.

## Requirements Checklist

- [ ] **AuthResource** - New resource with auto-detection of v1/v2 based on credentials
- [ ] **HONEYCOMB_TOOLS** - Add `honeycomb_get_auth` tool
- [ ] **CLI** - Add `hny auth get` command with `--v2` flag
- [ ] **Unit tests** - Full coverage of resource, CLI, and tools
- [ ] **Documentation** - Usage docs and docstrings
- [ ] **Live integration test** - Full v2 lifecycle: auth info -> create env -> create key -> delete key -> delete env

---

## Design Decisions

### Auto-Detection Strategy

The AuthResource will automatically choose the correct endpoint based on the client's auth strategy:
- `APIKeyAuth` (api_key provided) -> `/1/auth`
- `ManagementKeyAuth` (management_key provided) -> `/2/auth`

Users can explicitly override with `use_v2=True` parameter, which will error if management credentials aren't configured.

### Model Design

Create simplified Pydantic models that flatten the generated models for better usability:

```python
# v1 Auth response (flat structure)
class AuthInfo:
    id: str
    type: str  # "configuration" or "ingest"
    team_name: str
    team_slug: str
    environment_name: str
    environment_slug: str
    api_key_access: dict  # capabilities

# v2 Auth response (management key info)
class AuthInfoV2:
    id: str
    name: str
    key_type: str  # "management"
    disabled: bool
    scopes: list[str]
    team_id: str
    team_name: str | None
    team_slug: str | None
```

---

## Phase 1: Models

### Deliverables
- [ ] Create `src/honeycomb/models/auth.py` with AuthInfo and AuthInfoV2 models
- [ ] Edit `src/honeycomb/models/__init__.py` to export new models
- [ ] Edit `src/honeycomb/__init__.py` to add models to public API

### Implementation Details

**src/honeycomb/models/auth.py:**
```python
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class AuthInfo(BaseModel):
    """v1 auth endpoint response - API key metadata."""
    id: str = Field(description="Unique identifier of the API key")
    type: str = Field(description="Key type: 'configuration' or 'ingest'")
    team_name: str = Field(description="Name of the team")
    team_slug: str = Field(description="URL-safe team identifier")
    environment_name: str = Field(description="Name of the environment")
    environment_slug: str = Field(description="URL-safe environment identifier")
    api_key_access: dict[str, Any] = Field(description="Key capabilities/permissions")
    time_to_live: str | None = Field(default=None, description="Expiration time (RFC3339)")

    model_config = {"extra": "allow"}

class AuthInfoV2(BaseModel):
    """v2 auth endpoint response - Management key metadata."""
    id: str = Field(description="Unique identifier of the management key")
    name: str = Field(description="Human-readable name")
    key_type: str = Field(description="Key type: 'management'")
    disabled: bool = Field(default=False, description="Whether the key is disabled")
    scopes: list[str] = Field(default_factory=list, description="Authorized scopes")
    team_id: str = Field(description="Team ID this key belongs to")
    team_name: str | None = Field(default=None, description="Team name")
    team_slug: str | None = Field(default=None, description="Team slug")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}

    @classmethod
    def from_jsonapi(cls, data: dict[str, Any]) -> "AuthInfoV2":
        """Parse from JSON:API format."""
        obj = data.get("data", data)
        attrs = obj.get("attributes", {})
        rels = obj.get("relationships", {})
        included = data.get("included", [])

        # Extract team info from relationships and included
        team_id = rels.get("team", {}).get("data", {}).get("id", "")
        team_name = None
        team_slug = None
        for inc in included:
            if inc.get("type") == "teams" and inc.get("id") == team_id:
                team_attrs = inc.get("attributes", {})
                team_name = team_attrs.get("name")
                team_slug = team_attrs.get("slug")
                break

        timestamps = attrs.get("timestamps", {})
        return cls(
            id=obj.get("id", ""),
            name=attrs.get("name", ""),
            key_type=attrs.get("key_type", "management"),
            disabled=attrs.get("disabled", False),
            scopes=attrs.get("scopes", []),
            team_id=team_id,
            team_name=team_name,
            team_slug=team_slug,
            created_at=timestamps.get("created_at"),
            updated_at=timestamps.get("updated_at"),
        )
```

---

## Phase 2: Resource

### Deliverables
- [ ] Create `src/honeycomb/resources/auth.py` with AuthResource class
- [ ] Edit `src/honeycomb/resources/__init__.py` to export AuthResource
- [ ] Edit `src/honeycomb/client.py` to add `auth` property

### Implementation Details

**src/honeycomb/resources/auth.py:**
```python
from __future__ import annotations
from typing import TYPE_CHECKING, Union

from honeycomb.models.auth import AuthInfo, AuthInfoV2
from honeycomb.resources.base import BaseResource

if TYPE_CHECKING:
    from honeycomb.client import HoneycombClient

class AuthResource(BaseResource):
    """Access authentication metadata for the current API key.

    Example:
        >>> # Auto-detects endpoint based on credentials
        >>> auth_info = await client.auth.get_async()
        >>> print(f"Team: {auth_info.team_name}")

        >>> # Force v2 endpoint (requires management key)
        >>> auth_info = await client.auth.get_async(use_v2=True)
        >>> print(f"Scopes: {auth_info.scopes}")
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _is_management_auth(self) -> bool:
        """Check if client is using management key authentication."""
        from honeycomb.auth import ManagementKeyAuth
        return isinstance(self._client._auth, ManagementKeyAuth)

    def _require_management_auth(self) -> None:
        """Raise error if not using management key authentication."""
        if not self._is_management_auth():
            raise ValueError(
                "v2 auth endpoint requires management key authentication. "
                "Initialize client with management_key and management_secret."
            )

    async def get_async(self, *, use_v2: bool | None = None) -> Union[AuthInfo, AuthInfoV2]:
        """Get metadata about the current API key.

        Args:
            use_v2: Force v2 endpoint. If None, auto-detects based on credentials.
                   If True with API key credentials, raises ValueError.

        Returns:
            AuthInfo for v1 (API key) or AuthInfoV2 for v2 (management key).
        """
        if use_v2 is None:
            use_v2 = self._is_management_auth()

        if use_v2:
            self._require_management_auth()
            data = await self._get_async("/2/auth")
            return AuthInfoV2.from_jsonapi(data)

        data = await self._get_async("/1/auth")
        return AuthInfo(
            id=data.get("id", ""),
            type=data.get("type", ""),
            team_name=data.get("team", {}).get("name", ""),
            team_slug=data.get("team", {}).get("slug", ""),
            environment_name=data.get("environment", {}).get("name", ""),
            environment_slug=data.get("environment", {}).get("slug", ""),
            api_key_access=data.get("api_key_access", {}),
            time_to_live=data.get("time_to_live"),
        )

    def get(self, *, use_v2: bool | None = None) -> Union[AuthInfo, AuthInfoV2]:
        """Get metadata about the current API key (sync version)."""
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")

        if use_v2 is None:
            use_v2 = self._is_management_auth()

        if use_v2:
            self._require_management_auth()
            data = self._get_sync("/2/auth")
            return AuthInfoV2.from_jsonapi(data)

        data = self._get_sync("/1/auth")
        return AuthInfo(
            id=data.get("id", ""),
            type=data.get("type", ""),
            team_name=data.get("team", {}).get("name", ""),
            team_slug=data.get("team", {}).get("slug", ""),
            environment_name=data.get("environment", {}).get("name", ""),
            environment_slug=data.get("environment", {}).get("slug", ""),
            api_key_access=data.get("api_key_access", {}),
            time_to_live=data.get("time_to_live"),
        )
```

**client.py addition:**
```python
# In __init__, add:
self._auth_resource: AuthResource | None = None

# Add property:
@property
def auth(self) -> AuthResource:
    """Access the Auth API."""
    if self._auth_resource is None:
        from .resources.auth import AuthResource
        self._auth_resource = AuthResource(self)
    return self._auth_resource
```

---

## Phase 3: CLI

### Deliverables
- [ ] Create `src/honeycomb/cli/auth.py` with `get` command
- [ ] Edit `src/honeycomb/cli/__init__.py` to register auth commands

### Implementation Details

**src/honeycomb/cli/auth.py:**
```python
"""Authentication information commands."""

import typer
from rich.console import Console

from honeycomb.cli.config import get_client
from honeycomb.cli.formatters import DEFAULT_OUTPUT_FORMAT, OutputFormat, output_result

app = typer.Typer(help="Authentication and API key information")
console = Console()

@app.command("get")
def get_auth(
    v2: bool = typer.Option(False, "--v2", help="Use v2 endpoint (requires management key)"),
    profile: str | None = typer.Option(None, "--profile", "-p", help="Config profile to use"),
    api_key: str | None = typer.Option(None, "--api-key", envvar="HONEYCOMB_API_KEY"),
    management_key: str | None = typer.Option(
        None, "--management-key", envvar="HONEYCOMB_MANAGEMENT_KEY"
    ),
    management_secret: str | None = typer.Option(
        None, "--management-secret", envvar="HONEYCOMB_MANAGEMENT_SECRET"
    ),
    output: OutputFormat = typer.Option(DEFAULT_OUTPUT_FORMAT, "--output", "-o"),
) -> None:
    """Get metadata about the current API key.

    Shows information about the API key being used, including:
    - Team and environment details
    - Key type and permissions
    - Expiration (if applicable)

    Examples:
        # Auto-detect endpoint based on credentials
        hny auth get

        # Force v2 endpoint (management key)
        hny auth get --v2

        # Output as JSON
        hny auth get --output json
    """
    try:
        client = get_client(
            profile=profile,
            api_key=api_key,
            management_key=management_key,
            management_secret=management_secret,
        )

        use_v2 = v2 if v2 else None  # None means auto-detect
        auth_info = client.auth.get(use_v2=use_v2)
        output_result(auth_info, output)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
```

**cli/__init__.py addition:**
```python
from honeycomb.cli import auth
app.add_typer(auth.app, name="auth")
```

---

## Phase 4: Claude Tools

### Deliverables
- [ ] Edit `src/honeycomb/tools/descriptions.py` to add auth description
- [ ] Edit `src/honeycomb/tools/generator.py` to add generate_get_auth_tool
- [ ] Edit `src/honeycomb/tools/executor.py` to add _execute_get_auth

### Implementation Details

**descriptions.py addition:**
```python
AUTH_DESCRIPTIONS = {
    "honeycomb_get_auth": (
        "Returns metadata about the API key used to authenticate with Honeycomb. "
        "Use this to verify authentication is working correctly, check key permissions and scopes, "
        "or discover which team and environment the key belongs to. "
        "Automatically detects whether to use the v1 endpoint (for regular API keys) or "
        "v2 endpoint (for management keys) based on the configured credentials. "
        "Set use_v2=true to explicitly request management key information, which includes "
        "scopes and team details. Returns an error if use_v2=true but management credentials "
        "are not configured."
    ),
}
```

**generator.py additions:**
```python
def generate_get_auth_tool() -> dict[str, Any]:
    """Generate the honeycomb_get_auth tool definition."""
    schema = {
        "type": "object",
        "properties": {
            "use_v2": {
                "type": "boolean",
                "description": (
                    "Force use of v2 endpoint for management key info. "
                    "If not specified, auto-detects based on configured credentials."
                ),
            }
        },
        "required": [],
    }

    return create_tool_definition(
        name="honeycomb_get_auth",
        description=get_description("honeycomb_get_auth"),
        input_schema=schema,
        input_examples=[
            {},
            {"use_v2": True},
        ],
    )

# In generate_all_tools(), add near the top (auth is foundational):
def generate_all_tools() -> list[dict[str, Any]]:
    tools = [
        generate_get_auth_tool(),  # Add this
        # ... existing tools ...
    ]
```

**executor.py additions:**
```python
async def _execute_get_auth(
    client: HoneycombClient, tool_input: dict[str, Any]
) -> str:
    """Execute honeycomb_get_auth tool."""
    use_v2 = tool_input.get("use_v2")
    result = await client.auth.get_async(use_v2=use_v2)
    return json.dumps(result.model_dump(), default=str)

# In execute_tool(), add:
if tool_name == "honeycomb_get_auth":
    return await _execute_get_auth(client, tool_input)
```

---

## Phase 5: Unit Tests

### Deliverables
- [ ] Create `tests/unit/test_auth_resource.py`
- [ ] Create `tests/unit/test_cli_auth.py`
- [ ] Add auth tool tests to `tests/unit/test_tools_executor.py`
- [ ] Add `management_client` fixture to `tests/conftest.py` if needed

### Implementation Details

**tests/unit/test_auth_resource.py:**
```python
"""Tests for AuthResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from honeycomb.models.auth import AuthInfo, AuthInfoV2


@pytest.fixture
def api_key_client():
    """Client with API key auth."""
    return HoneycombClient(api_key="test-api-key", sync=True)


@pytest.fixture
def management_client():
    """Client with management key auth."""
    return HoneycombClient(
        management_key="test-mgmt-key",
        management_secret="test-secret",
        sync=True,
    )


class TestAuthResource:
    """Tests for auth resource."""

    @respx.mock
    def test_get_v1_auto_detect(self, api_key_client):
        """Auto-detects v1 endpoint with API key credentials."""
        respx.get("https://api.honeycomb.io/1/auth").mock(
            return_value=Response(200, json={
                "id": "key123",
                "type": "configuration",
                "team": {"name": "Test Team", "slug": "test-team"},
                "environment": {"name": "Test Env", "slug": "test-env"},
                "api_key_access": {"events": True, "markers": True},
            })
        )

        result = api_key_client.auth.get()

        assert isinstance(result, AuthInfo)
        assert result.id == "key123"
        assert result.type == "configuration"
        assert result.team_name == "Test Team"
        assert result.environment_slug == "test-env"

    @respx.mock
    def test_get_v2_auto_detect(self, management_client):
        """Auto-detects v2 endpoint with management credentials."""
        respx.get("https://api.honeycomb.io/2/auth").mock(
            return_value=Response(200, json={
                "data": {
                    "id": "mgmt123",
                    "type": "api-keys",
                    "attributes": {
                        "name": "My Mgmt Key",
                        "key_type": "management",
                        "disabled": False,
                        "scopes": ["environments:read", "api-keys:write"],
                        "timestamps": {},
                    },
                    "relationships": {
                        "team": {"data": {"type": "teams", "id": "team123"}}
                    },
                },
                "included": [
                    {"id": "team123", "type": "teams", "attributes": {"name": "My Team", "slug": "my-team"}}
                ],
            })
        )

        result = management_client.auth.get()

        assert isinstance(result, AuthInfoV2)
        assert result.id == "mgmt123"
        assert result.name == "My Mgmt Key"
        assert result.team_name == "My Team"
        assert "api-keys:write" in result.scopes

    def test_explicit_v2_with_api_key_raises(self, api_key_client):
        """Raises ValueError when forcing v2 with API key credentials."""
        with pytest.raises(ValueError, match="requires management key"):
            api_key_client.auth.get(use_v2=True)

    @respx.mock
    def test_explicit_v1_with_management_key(self, management_client):
        """Can force v1 endpoint even with management credentials."""
        respx.get("https://api.honeycomb.io/1/auth").mock(
            return_value=Response(200, json={
                "id": "key123",
                "type": "ingest",
                "team": {"name": "Team", "slug": "team"},
                "environment": {"name": "Env", "slug": "env"},
                "api_key_access": {},
            })
        )

        result = management_client.auth.get(use_v2=False)

        assert isinstance(result, AuthInfo)
```

**tests/unit/test_cli_auth.py:**
```python
"""Tests for auth CLI commands."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from honeycomb.cli import app
from honeycomb.models.auth import AuthInfo


runner = CliRunner()


class TestAuthCLI:
    """Tests for auth CLI."""

    @patch("honeycomb.cli.auth.get_client")
    def test_get_auth_default(self, mock_get_client):
        """hny auth get works with default settings."""
        mock_client = MagicMock()
        mock_client.auth.get.return_value = AuthInfo(
            id="key123",
            type="configuration",
            team_name="Test Team",
            team_slug="test-team",
            environment_name="Production",
            environment_slug="production",
            api_key_access={"events": True},
        )
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["auth", "get"])

        assert result.exit_code == 0
        assert "Test Team" in result.stdout or "key123" in result.stdout
        mock_client.auth.get.assert_called_once_with(use_v2=None)

    @patch("honeycomb.cli.auth.get_client")
    def test_get_auth_v2_flag(self, mock_get_client):
        """hny auth get --v2 uses v2 endpoint."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        runner.invoke(app, ["auth", "get", "--v2"])

        mock_client.auth.get.assert_called_once_with(use_v2=True)

    @patch("honeycomb.cli.auth.get_client")
    def test_get_auth_json_output(self, mock_get_client):
        """hny auth get --output json outputs JSON."""
        mock_client = MagicMock()
        mock_client.auth.get.return_value = AuthInfo(
            id="key123",
            type="configuration",
            team_name="Team",
            team_slug="team",
            environment_name="Env",
            environment_slug="env",
            api_key_access={},
        )
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["auth", "get", "--output", "json"])

        assert result.exit_code == 0
        assert '"id"' in result.stdout or '"team_name"' in result.stdout
```

---

## Phase 6: Documentation

### Deliverables
- [ ] Create `docs/usage/auth.md`
- [ ] Edit `docs/index.md` or `mkdocs.yml` to add auth to navigation

### Implementation Details

**docs/usage/auth.md:**
```markdown
# Authentication Info

The `auth` resource lets you retrieve metadata about the API key currently being used to authenticate with Honeycomb.

## Use Cases

- Verify your API key is working correctly
- Discover which team/environment a key belongs to
- Check key permissions and scopes
- Audit key expiration dates

## Python API

### Basic Usage

```python
from honeycomb import HoneycombClient

# Using an API key (v1)
client = HoneycombClient(api_key="your-api-key")
auth_info = client.auth.get()

print(f"Team: {auth_info.team_name}")
print(f"Environment: {auth_info.environment_name}")
print(f"Key Type: {auth_info.type}")
```

### Management Key (v2)

```python
# Using management credentials
client = HoneycombClient(
    management_key="your-management-key",
    management_secret="your-secret"
)

auth_info = client.auth.get()  # Auto-detects v2
print(f"Key Name: {auth_info.name}")
print(f"Scopes: {auth_info.scopes}")
print(f"Team: {auth_info.team_name}")
```

### Async Usage

```python
async with HoneycombClient(api_key="your-key") as client:
    auth_info = await client.auth.get_async()
    print(f"Team: {auth_info.team_name}")
```

### Explicit Version Selection

```python
# Force v2 (errors if not using management key)
auth_info = client.auth.get(use_v2=True)

# Force v1 (even with management key)
auth_info = client.auth.get(use_v2=False)
```

## CLI

### Get Auth Info

```bash
# Auto-detect endpoint based on credentials
hny auth get

# Force v2 endpoint (requires management key)
hny auth get --v2

# Output as JSON
hny auth get --output json

# Use specific profile
hny auth get --profile production
```

### Example Output

```
id: hcaik_01234567890123456789
type: configuration
team_name: My Team
team_slug: my-team
environment_name: Production
environment_slug: production
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
```

---

## Phase 7: Live Integration Test

### Deliverables
- [ ] Create `tests/integration/test_v2_auth_lifecycle.py`
- [ ] Update `tests/integration/conftest.py` with management_client fixture if needed

### Implementation Details

**tests/integration/test_v2_auth_lifecycle.py:**
```python
"""Live integration tests for v2 auth and management API lifecycle."""

import uuid
import pytest

from honeycomb import HoneycombClient
from honeycomb.models.api_keys import ApiKeyCreate, ApiKeyType
from honeycomb.models.environments import EnvironmentCreate, EnvironmentColor


@pytest.fixture
def management_client():
    """Get a management client from environment variables."""
    import os

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
            team=team_slug,
            environment=EnvironmentCreate(
                name=env_name,
                color=EnvironmentColor.BLUE,
            )
        )
        print(f"Created environment: {env.id} ({env.name})")

        api_key = None
        try:
            # 3. Create API key in environment
            key_name = f"test-key-{unique_id}"
            api_key = await management_client.api_keys.create_async(
                team=team_slug,
                api_key=ApiKeyCreate(
                    name=key_name,
                    key_type=ApiKeyType.INGEST,
                    environment_id=env.id,
                )
            )
            print(f"Created API key: {api_key.id} ({api_key.name})")

            # Verify key attributes
            assert api_key.id is not None
            assert api_key.secret is not None  # Only returned on creation
            assert api_key.name == key_name
            assert api_key.key_type == ApiKeyType.INGEST

            # 4. Delete API key
            await management_client.api_keys.delete_async(
                team=team_slug,
                key_id=api_key.id,
            )
            print(f"Deleted API key: {api_key.id}")

        finally:
            # 5. Cleanup: Delete environment
            await management_client.environments.delete_async(
                team=team_slug,
                environment_id=env.id,
            )
            print(f"Deleted environment: {env.id}")

        print("V2 lifecycle test completed successfully!")
```

---

## File Change Summary

### New Files (7)
| File | Phase |
|------|-------|
| `src/honeycomb/models/auth.py` | 1 |
| `src/honeycomb/resources/auth.py` | 2 |
| `src/honeycomb/cli/auth.py` | 3 |
| `tests/unit/test_auth_resource.py` | 5 |
| `tests/unit/test_cli_auth.py` | 5 |
| `tests/integration/test_v2_auth_lifecycle.py` | 7 |
| `docs/usage/auth.md` | 6 |

### Modified Files (9)
| File | Phase | Change |
|------|-------|--------|
| `src/honeycomb/models/__init__.py` | 1 | Export AuthInfo, AuthInfoV2 |
| `src/honeycomb/__init__.py` | 1 | Add to public API |
| `src/honeycomb/resources/__init__.py` | 2 | Export AuthResource |
| `src/honeycomb/client.py` | 2 | Add `auth` property |
| `src/honeycomb/cli/__init__.py` | 3 | Register auth commands |
| `src/honeycomb/tools/descriptions.py` | 4 | Add auth description |
| `src/honeycomb/tools/generator.py` | 4 | Add generate_get_auth_tool |
| `src/honeycomb/tools/executor.py` | 4 | Add _execute_get_auth |
| `docs/index.md` or `mkdocs.yml` | 6 | Add auth to nav |

---

## Implementation Order

- [ ] **Phase 1**: Models (foundation)
- [ ] **Phase 2**: Resource (core functionality)
- [ ] **Phase 3**: CLI (user-facing command)
- [ ] **Phase 4**: Claude Tools (AI integration)
- [ ] **Phase 5**: Unit Tests (verification)
- [ ] **Phase 6**: Documentation (usage guide)
- [ ] **Phase 7**: Live Integration Test (end-to-end)
- [ ] **Final**: Run CI (`make ci`) to verify everything passes
