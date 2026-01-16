# MCP Server for Claude Desktop

The Honeycomb API SDK includes an MCP (Model Context Protocol) server that exposes Honeycomb tools to Claude Desktop and other MCP-compatible clients.

## Quick Start

No installation required! Use [uv](https://docs.astral.sh/uv/#installation) (recommended) or [pipx](https://pipx.pypa.io/stable/#install-pipx) to run the MCP server directly.

### Claude Desktop

Add the Honeycomb MCP server to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

**Using uvx (recommended):**

```json
{
  "mcpServers": {
    "honeycomb": {
      "command": "uvx",
      "args": ["--from", "honeycomb-api[mcp]", "hny-mcp"],
      "env": {
        "HONEYCOMB_API_KEY": "your-environment-api-key"
      }
    }
  }
}
```

**Using pipx:**

```json
{
  "mcpServers": {
    "honeycomb": {
      "command": "pipx",
      "args": ["run", "--spec", "honeycomb-api[mcp]", "hny-mcp"],
      "env": {
        "HONEYCOMB_API_KEY": "your-environment-api-key"
      }
    }
  }
}
```

After saving, restart Claude Desktop. You should see "honeycomb" in the MCP servers list.

### Claude Code (CLI)

Add the MCP server to your Claude Code configuration.

**Edit `~/.claude/settings.json`** (or `.claude/settings.local.json` for project-specific):

**Using uvx (recommended):**

```json
{
  "mcpServers": {
    "honeycomb": {
      "command": "uvx",
      "args": ["--from", "honeycomb-api[mcp]", "hny-mcp"],
      "env": {
        "HONEYCOMB_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Using pipx:**

```json
{
  "mcpServers": {
    "honeycomb": {
      "command": "pipx",
      "args": ["run", "--spec", "honeycomb-api[mcp]", "hny-mcp"],
      "env": {
        "HONEYCOMB_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Cursor

Add the MCP server to Cursor's configuration.

**Edit `~/.cursor/mcp.json`:**

**Using uvx (recommended):**

```json
{
  "honeycomb": {
    "command": "uvx",
    "args": ["--from", "honeycomb-api[mcp]", "hny-mcp"],
    "env": {
      "HONEYCOMB_API_KEY": "your-api-key"
    }
  }
}
```

**Using pipx:**

```json
{
  "honeycomb": {
    "command": "pipx",
    "args": ["run", "--spec", "honeycomb-api[mcp]", "hny-mcp"],
    "env": {
      "HONEYCOMB_API_KEY": "your-api-key"
    }
  }
}
```

### Start Using Honeycomb Tools

Once configured, you can ask Claude to interact with Honeycomb:

- "What datasets do I have in Honeycomb?"
- "List all triggers in the api-logs dataset"
- "Create an SLO for my checkout service with 99.9% availability"
- "Search for columns related to HTTP status codes"

## How It Works

### Meta-Tools Architecture

By default, the MCP server exposes **2 meta-tools** instead of all 69 individual tools. This reduces token usage and context overhead:

1. **`honeycomb_discover_tools`**: Discover available tools and their parameters
2. **`honeycomb_call_tool`**: Execute any Honeycomb tool by name

Claude will automatically:
1. Call `honeycomb_discover_tools` to find the right tool
2. Call `honeycomb_call_tool` to execute it

### Tool Categories

Tools are organized into these categories:

| Category | API | Description | Example Tools |
|----------|-----|-------------|---------------|
| `auth` | v1 | Authentication info | `honeycomb_get_auth` |
| `datasets` | v1 | Dataset management | `honeycomb_list_datasets`, `honeycomb_create_dataset` |
| `triggers` | v1 | Alert triggers | `honeycomb_list_triggers`, `honeycomb_create_trigger` |
| `slos` | v1 | Service Level Objectives | `honeycomb_list_slos`, `honeycomb_create_slo` |
| `burn_alerts` | v1 | SLO burn alerts | `honeycomb_list_burn_alerts` |
| `queries` | v1 | Query execution | `honeycomb_run_query`, `honeycomb_create_query` |
| `boards` | v1 | Dashboards | `honeycomb_list_boards`, `honeycomb_create_board` |
| `columns` | v1 | Dataset columns | `honeycomb_list_columns` |
| `discovery` | v1 | Environment exploration | `honeycomb_search_columns`, `honeycomb_get_environment_summary` |
| `environments` | v2* | Team environments | `honeycomb_list_environments`, `honeycomb_create_environment` |
| `api_keys` | v2* | API key management | `honeycomb_list_api_keys`, `honeycomb_create_api_key` |

*v2 tools require both `HONEYCOMB_MANAGEMENT_KEY` and `HONEYCOMB_MANAGEMENT_SECRET`. If not configured, these tools are automatically hidden.

## Configuration Options

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HONEYCOMB_API_KEY` | Yes* | Environment-scoped API key (for v1 API tools) |
| `HONEYCOMB_MANAGEMENT_KEY` | No** | Management key ID (for v2 API tools) |
| `HONEYCOMB_MANAGEMENT_SECRET` | No** | Management key secret (for v2 API tools) |
| `HONEYCOMB_MCP_NATIVE_TOOLS` | No | Set to `1` to expose all tools directly |

*Required for most operations (datasets, triggers, SLOs, queries, etc.)

**Required only for team-level operations (managing environments and API keys). If not provided, these 10 tools are automatically hidden.

### Native Tools Mode (Advanced)

If you prefer to expose all 69 tools directly instead of using meta-tools, add `HONEYCOMB_MCP_NATIVE_TOOLS=1`:

```json
{
  "mcpServers": {
    "honeycomb": {
      "command": "uvx",
      "args": ["--from", "honeycomb-api[mcp]", "hny-mcp"],
      "env": {
        "HONEYCOMB_API_KEY": "your-api-key",
        "HONEYCOMB_MCP_NATIVE_TOOLS": "1"
      }
    }
  }
}
```

This can be useful for future MCP deferred loading support, but uses more tokens.

## Development / Testing

For local development or testing unreleased versions, use `poetry run`:

```json
{
  "mcpServers": {
    "honeycomb-dev": {
      "command": "poetry",
      "args": ["run", "python", "-m", "honeycomb.mcp"],
      "cwd": "/path/to/honeycomb-api-python",
      "env": {
        "HONEYCOMB_API_KEY": "your-test-api-key"
      }
    }
  }
}
```

**Important**: The `cwd` parameter must point to your local clone of the repository.

## Example Conversations

### Investigating Datasets

> **You**: What datasets do I have?
>
> **Claude**: Let me check your Honeycomb datasets.
> *[Calls honeycomb_discover_tools, then honeycomb_call_tool with honeycomb_list_datasets]*
>
> You have 5 datasets:
> - api-logs (production API traffic)
> - frontend-events (user interactions)
> - ...

### Creating Alerts

> **You**: Create a trigger that alerts when error rate exceeds 5% in api-logs
>
> **Claude**: I'll create that trigger for you.
> *[Calls honeycomb_call_tool with honeycomb_create_trigger]*
>
> Created trigger "High Error Rate" in api-logs dataset. It will alert when error rate exceeds 5%.

### Exploring Data

> **You**: What columns are available related to HTTP status?
>
> **Claude**: *[Calls honeycomb_call_tool with honeycomb_search_columns]*
>
> Found these HTTP status-related columns:
> - `http.status_code` (integer) - HTTP response status
> - `http.status_class` (string) - Status class (2xx, 4xx, 5xx)
> - ...

## Troubleshooting

### Server Not Starting

1. Verify `uvx` or `pipx` is installed and in your PATH
2. Check environment variables are set in your MCP configuration
3. Test manually: `uvx --from honeycomb-api[mcp] hny-mcp` (should show error about interactive mode)

### Authentication Errors

- Ensure `HONEYCOMB_API_KEY` is set in the MCP configuration
- Verify the key has appropriate permissions
- For v2 tools (environments, api_keys), both `HONEYCOMB_MANAGEMENT_KEY` and `HONEYCOMB_MANAGEMENT_SECRET` are required

### Tools Not Appearing

1. Restart Claude Desktop/Claude Code after config changes
2. Check MCP config file syntax is valid JSON
3. Verify `uvx` or `pipx` is working: `uvx --version` or `pipx --version`
4. Check MCP server logs (typically in Claude Desktop logs)

## API Reference

For detailed information about individual tools and their parameters, see:

- [Triggers](triggers.md)
- [SLOs](slos.md)
- [Queries](queries.md)
- [Datasets](datasets.md)
- [Boards](boards.md)
