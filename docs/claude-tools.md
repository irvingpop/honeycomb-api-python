# Claude Tool Definitions for Honeycomb API

Honeycomb Python SDK provides 67 Claude-compatible tool definitions that enable LLMs to create and manage Honeycomb resources via structured tool calls.

## Overview

The `honeycomb.tools` module provides:
- **67 tool definitions** covering 14 Honeycomb API resources
- **JSON schemas** for automatic parameter validation
- **Hand-crafted descriptions** for optimal LLM tool selection
- **Execution handlers** that call Honeycomb API with orchestration

## Quick Start

### Basic Usage

```python
from anthropic import Anthropic
from honeycomb.tools import HONEYCOMB_TOOLS, execute_tool
from honeycomb import HoneycombClient

# Initialize clients
anthropic_client = Anthropic(api_key="your-anthropic-key")
honeycomb_client = HoneycombClient(api_key="your-honeycomb-key")

# Call Claude with Honeycomb tools
response = anthropic_client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["advanced-tool-use-2025-11-20"],  # Recommended for better tool selection
    tools=HONEYCOMB_TOOLS,
    messages=[
        {"role": "user", "content": "Create a trigger for high error rates in api-logs"}
    ]
)

# Execute the tool call
for block in response.content:
    if block.type == "tool_use":
        result = await execute_tool(
            client=honeycomb_client,
            tool_name=block.name,
            tool_input=block.input
        )
        print(f"Result: {result}")
```

### Multi-Turn Conversation

```python
messages = []
user_message = "Set up monitoring for my API service"
messages.append({"role": "user", "content": user_message})

while True:
    response = anthropic_client.beta.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        betas=["advanced-tool-use-2025-11-20"],
        tools=HONEYCOMB_TOOLS,
        messages=messages,
    )

    # Add assistant response to conversation
    messages.append({"role": "assistant", "content": response.content})

    # Check if Claude is done
    if response.stop_reason == "end_turn":
        # Extract final text response
        text = " ".join(b.text for b in response.content if hasattr(b, "text"))
        print(f"Claude: {text}")
        break

    # Execute tool calls
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = await execute_tool(
                client=honeycomb_client,
                tool_name=block.name,
                tool_input=block.input
            )
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })

    # Add tool results to conversation
    messages.append({"role": "user", "content": tool_results})
```

## Available Tools

### Alerting & SLOs (15 tools)

**Triggers (5):** `list_triggers`, `get_trigger`, `create_trigger`, `update_trigger`, `delete_trigger`
- Create alerts when query results cross thresholds
- Inline query specification with filters, calculations

**SLOs (5):** `list_slos`, `get_slo`, `create_slo`, `update_slo`, `delete_slo`
- Track service reliability targets
- Inline derived column creation for SLI

**Burn Alerts (5):** `list_burn_alerts`, `get_burn_alert`, `create_burn_alert`, `update_burn_alert`, `delete_burn_alert`
- Alert when SLO error budget depletes

### Data Management (21 tools)

**Datasets (5):** `list_datasets`, `get_dataset`, `create_dataset`, `update_dataset`, `delete_dataset`

**Columns (5):** `list_columns`, `get_column`, `create_column`, `update_column`, `delete_column`

**Derived Columns (5):** `list_derived_columns`, `get_derived_column`, `create_derived_column`, `update_derived_column`, `delete_derived_column`
- Computed metrics from event fields
- Expression language: `IF()`, `LT()`, `GTE()`, etc.

**Recipients (6):** `list_recipients`, `get_recipient`, `create_recipient`, `update_recipient`, `delete_recipient`, `get_recipient_triggers`
- Notification targets: email, Slack, PagerDuty, webhooks

### Analysis & Visualization (16 tools)

**Queries (3):** `create_query`, `get_query`, `run_query`
- `run_query` creates + executes + polls automatically
- Supports all query features: calculations, filters, breakdowns, orders, havings, limits

**Boards (5):** `list_boards`, `get_boards`, `create_board`, `update_board`, `delete_board`
- **Inline panel creation** - queries, SLOs, and text panels in one operation
- Auto or manual layout

**Markers (4):** `list_markers`, `create_marker`, `update_marker`, `delete_marker`
- Annotate deployments, incidents, config changes

**Marker Settings (5):** `list_marker_settings`, `get_marker_setting`, `create_marker_setting`, `update_marker_setting`, `delete_marker_setting`
- Type-to-color mappings for markers

### Data Ingestion & Discovery (3 tools)

**Events (2):** `send_event`, `send_batch_events`
- Batch sending preferred for production

**Service Map (1):** `query_service_map`
- Discover service dependencies from traces
- Automatic create + poll + paginate

## Advanced Features

### Inline Orchestration

Many tools support creating nested resources in a single call:

#### Board with Inline Query Panels

```python
response = anthropic_client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["advanced-tool-use-2025-11-20"],
    tools=HONEYCOMB_TOOLS,
    messages=[{
        "role": "user",
        "content": """
        Create a board named 'API Health Dashboard' with auto-layout.
        Add two query panels:
        1. 'Error Count' from api-logs showing COUNT of errors (status_code >= 500) over 1 hour
        2. 'P99 Latency' from api-logs showing P99 of duration_ms over 1 hour
        """
    }]
)

# Claude will call honeycomb_create_board with inline_query_panels
# Execution creates queries, annotations, and board automatically
```

#### SLO with Inline Derived Column

```python
response = anthropic_client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["advanced-tool-use-2025-11-20"],
    tools=HONEYCOMB_TOOLS,
    messages=[{
        "role": "user",
        "content": """
        Create an SLO named 'API Availability' in api-logs with 99.9% target over 30 days.
        Create a NEW derived column inline with alias 'success_rate' and
        expression IF(LT($status_code, 400), 1, 0)
        """
    }]
)

# Claude will call honeycomb_create_slo with inline SLI expression
# Execution creates derived column, then SLO
```

### Environment-Wide Operations

Use `"__all__"` for operations across all datasets:

```python
# Environment-wide query
messages=[{
    "role": "user",
    "content": "Run a query showing total errors across all datasets in the past hour"
}]
# Claude uses dataset: "__all__"

# Environment-wide derived column
messages=[{
    "role": "user",
    "content": "Create an environment-wide derived column named 'is_error' with expression IF(GTE($status_code, 500), 1, 0)"
}]
# Creates derived column available in all datasets
```

## Tool Execution

### Async Execution (Recommended)

```python
from honeycomb.tools import execute_tool
from honeycomb import HoneycombClient

async with HoneycombClient(api_key="...") as client:
    # Execute tool call from Claude
    result = await execute_tool(
        client=client,
        tool_name="honeycomb_create_trigger",
        tool_input={
            "dataset": "api-logs",
            "name": "High Error Rate",
            "query": {
                "time_range": 900,
                "calculations": [{"op": "COUNT"}],
                "filters": [{"column": "status_code", "op": ">=", "value": 500}]
            },
            "threshold": {"op": ">", "value": 100},
            "frequency": 900
        }
    )

    # Result is JSON string
    import json
    trigger = json.loads(result)
    print(f"Created trigger: {trigger['id']}")
```

### Sync Execution

```python
with HoneycombClient(api_key="...", sync=True) as client:
    # Sync execution not yet supported in execute_tool
    # Use async client for now
    pass
```

## Best Practices

### 1. Use Directive Prompts

**Good:**
```python
"Create a trigger in api-logs that alerts when error count > 100"
```

**Better:**
```python
"Create a trigger named 'High Errors' in dataset 'api-logs' that fires when COUNT of requests with status_code >= 500 exceeds 100, checking every 15 minutes"
```

### 2. Leverage Inline Creation

Instead of multiple tool calls:
```python
# ❌ Inefficient - 3 tool calls
"Create a derived column for errors"
"Create an SLO using that derived column"
"Create a burn alert for that SLO"
```

Do it in one:
```python
# ✅ Efficient - 1 tool call
"Create an SLO with inline derived column and burn alert"
```

### 3. Specify Datasets Explicitly

**Ambiguous:**
```python
"Show me error rates"
```

**Clear:**
```python
"Run a query in dataset 'production' showing error rates"
```

### 4. Use Advanced Tool Use Beta

Always include the beta for better tool selection with 67 tools:

```python
response = client.beta.messages.create(
    betas=["advanced-tool-use-2025-11-20"],  # Improves tool selection
    tools=HONEYCOMB_TOOLS,
    # ... other parameters like model, max_tokens, messages, etc.
)
```

## Error Handling

```python
from honeycomb.exceptions import HoneycombAPIError
import json

try:
    result = await execute_tool(
        client=client,
        tool_name=block.name,
        tool_input=block.input
    )
    data = json.loads(result)
    print(f"Success: {data}")

except HoneycombAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Status: {e.status_code}")

except ValueError as e:
    print(f"Unknown tool: {e}")
```

### Orchestrated Operations

These tools coordinate multiple API calls:

**`honeycomb_create_board`**
- Creates queries with annotations
- Creates SLOs with derived columns
- Assembles all panels
- Creates board

**`honeycomb_create_slo`**
- Creates derived column (if expression provided)
- Creates SLO
- Creates burn alerts (if provided)

**`honeycomb_create_trigger`**
- Creates trigger with inline query

**`honeycomb_run_query`**
- Creates query
- Creates query result
- Polls for completion
- Returns results

**`honeycomb_query_service_map`**
- Creates dependency request
- Polls for completion
- Paginates through all results (up to 64K dependencies)
- Returns dependencies

## Tool Selection Guidelines

Claude selects tools based on:

1. **Description keywords** - "Use this when..."
2. **Parameter schemas** - Required vs optional fields
3. **Examples** (internal) - Patterns showing usage

### How Descriptions Guide Selection

The descriptions use directive language:

```
"IMPORTANT: Use this tool (not honeycomb_create_derived_column) when creating an SLO"
```

This overcomes Claude's training knowledge and ensures correct tool selection even with 67 options.

## Customization

### Filter Available Tools

```python
from honeycomb.tools import get_all_tools

# Only provide alerting tools
ALERTING_TOOLS = [
    t for t in get_all_tools()
    if any(x in t["name"] for x in ["trigger", "slo", "burn_alert"])
]

response = client.beta.messages.create(
    tools=ALERTING_TOOLS,  # Subset of tools
    # ... other parameters
)
```

### Add Custom System Prompt

```python
CUSTOM_SYSTEM = """
You are a Honeycomb observability engineer assistant.
When creating alerts, always use appropriate recipients.
When creating SLOs, always add burn alerts for early warning.
Prefer environment-wide queries when comparing across services.
"""

response = client.beta.messages.create(
    system=CUSTOM_SYSTEM,
    tools=HONEYCOMB_TOOLS,
    # ... other parameters
)
```

## Testing

The SDK includes comprehensive test suite:

```bash
# Run all tool validation tests
poetry run pytest tests/integration/test_claude_tools_eval.py -v

# Test specific resource
poetry run pytest tests/integration/test_claude_tools_eval.py -v -k triggers

# Fast tests only (no LLM evaluation)
poetry run pytest tests/integration/test_claude_tools_eval.py -v -k "tool_selection"
```

## Troubleshooting

### Tool Not Found Error

```python
# Error: Unknown tool: honeycomb_list_foo
# Solution: Check tool name matches exactly

from honeycomb.tools import list_tool_names
print(list_tool_names())  # See all available tools
```

### Incorrect Parameters

```python
# Error: Missing required parameter 'dataset'
# Solution: Improve prompt specificity

# ❌ Vague
"Create a trigger"

# ✅ Specific
"Create a trigger in dataset 'api-logs'"
```

### Tool Selection Issues

If Claude selects the wrong tool, improve the prompt:

```python
# ❌ Ambiguous
"Create something to calculate errors"

# ✅ Explicit
"Create an SLO (not just a derived column) with inline error calculation"
```

## API Reference

### Tool Structure

Each tool in `HONEYCOMB_TOOLS` contains:

```python
{
    "name": "honeycomb_create_trigger",
    "description": "Creates a new trigger...",  # Hand-crafted guidance
    "input_schema": {                          # JSON Schema
        "type": "object",
        "properties": {
            "dataset": {"type": "string", "description": "..."},
            "name": {"type": "string", "description": "..."},
            # ... more properties
            "confidence": {...},  # Metadata field (see below)
            "notes": {...},       # Metadata field (see below)
        },
        "required": ["dataset", "name"]  # ... and more required fields
    }
}
```

### Confidence and Notes Metadata

Every tool includes two optional metadata fields that allow Claude to express its reasoning:

**`confidence`** (string, optional):
- `"high"` - Certain this matches user intent and will succeed
- `"medium"` - Likely correct but some uncertainty
- `"low"` - Uncertain but best available option
- `"none"` - Guessing or placeholder value

**`notes`** (object, optional):
Structured reasoning with four optional categories (arrays of single-sentence strings):

```python
{
    "notes": {
        "decisions": ["Chose COUNT over AVG for error rate"],
        "concerns": ["Time range may be too short for accurate results"],
        "assumptions": ["Assuming status_code column exists in dataset"],
        "questions": ["I would be more confident if I knew the expected error baseline"]
    }
}
```

**Important**: These fields are for downstream applications to observe Claude's reasoning. They are automatically stripped before API calls - Honeycomb API never sees them.

**Example with metadata**:

```python
# Claude's tool call includes reasoning metadata
tool_input = {
    "dataset": "api-logs",
    "name": "High Error Rate",
    "threshold": {"op": ">", "value": 100},
    "frequency": 900,
    "confidence": "medium",
    "notes": {
        "decisions": ["Used COUNT for simple error counting"],
        "assumptions": ["Assuming status_code column indicates HTTP status"],
    }
}

# Downstream app can inspect Claude's reasoning
confidence = tool_input.get("confidence", "none")
notes = tool_input.get("notes", {})

if confidence in ("low", "none"):
    print(f"Low confidence: {notes}")  # Review before executing

# execute_tool() automatically strips metadata before API call
result = await execute_tool(client, "honeycomb_create_trigger", tool_input)
```

### Execution Handler

```python
async def execute_tool(
    client: HoneycombClient,
    tool_name: str,
    tool_input: dict[str, Any]
) -> str:
    """
    Args:
        client: Async-capable HoneycombClient
        tool_name: Tool name (e.g., "honeycomb_create_trigger")
        tool_input: Parameters from Claude

    Returns:
        JSON string with result

    Raises:
        ValueError: Unknown tool
        HoneycombAPIError: API call failed
    """
```

## Examples Repository

See the `examples/` directory in the repository for complete examples:

- `examples/boards/builder_board.py` - Complex board creation with inline panels
- `examples/triggers/builder_trigger.py` - Trigger creation patterns
- `examples/slos/builder_slo.py` - SLO with inline derived column

## Tool Inventory

Full list of 67 tools available via:

```python
from honeycomb.tools import list_tool_names
print("\n".join(list_tool_names()))
```

Output:
```
honeycomb_create_board
honeycomb_create_burn_alert
honeycomb_create_column
honeycomb_create_dataset
honeycomb_create_derived_column
honeycomb_create_marker
honeycomb_create_marker_setting
honeycomb_create_query
honeycomb_create_recipient
honeycomb_create_slo
honeycomb_create_trigger
honeycomb_delete_board
... (67 total)
```

## Learn More

- [Getting Started](getting-started/quickstart.md) - SDK installation and setup
- [Usage Guides](usage/triggers.md) - Resource-specific guides
- [API Reference](api/client.md) - Complete API documentation
- [Anthropic Tool Use Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) - General tool use guide
