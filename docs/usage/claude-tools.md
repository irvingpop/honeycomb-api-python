# Claude Tool Definitions

Generate Claude-compatible tool definitions from the Honeycomb API Python client, enabling LLMs to create and manage Honeycomb resources via structured tool calls.

## Overview

The `honeycomb.tools` module provides:

1. **Tool Definitions** - JSON Schema definitions compatible with Claude's tool calling API
2. **Tool Executor** - Handler that executes tool calls against Honeycomb API
3. **Builder Integration** - Single-call resource creation with nested structures

**Current Coverage:** 15 Priority 1 tools (Triggers, SLOs, Burn Alerts)

## Quick Start

### Basic Usage with Anthropic SDK

```python
from anthropic import Anthropic
from honeycomb import HoneycombClient
from honeycomb.tools import HONEYCOMB_TOOLS, execute_tool

# Initialize clients
anthropic = Anthropic()  # Uses ANTHROPIC_API_KEY env var
honeycomb = HoneycombClient(api_key="your-key")

# System prompt that encourages tool use (RECOMMENDED)
system_prompt = (
    "You are a Honeycomb API automation assistant. "
    "When the user asks you to perform operations on Honeycomb resources, "
    "you MUST use the available tools rather than providing conversational responses. "
    "Always call the appropriate tool, even if some parameters are not explicitly specified - "
    "use reasonable defaults. "
    "Only respond conversationally if no appropriate tool is available."
)

# Call Claude with Honeycomb tools
response = anthropic.messages.create(
    model="claude-sonnet-4-5-20250929",  # Latest Claude Sonnet 4.5
    max_tokens=4096,
    tools=HONEYCOMB_TOOLS,  # Provides all 15 tools
    system=system_prompt,  # Encourages tool use
    messages=[
        {"role": "user", "content": "Create a high error rate trigger in api-logs"}
    ]
)

# Execute tool calls
async with honeycomb:
    for block in response.content:
        if block.type == "tool_use":
            result = await execute_tool(honeycomb, block.name, block.input)
            print(f"Result: {result}")
```

**Best Practices:**

1. **Always use a system prompt** - Dramatically improves tool selection (50% → 100% in testing)
2. **Use latest model** - `claude-sonnet-4-5-20250929` has better tool use support
3. **Be directive in prompts** - "Create trigger..." not "Can you create..."
4. **Include parameters** - Specify dataset, thresholds, IDs explicitly

## Available Tools

### Triggers (Alerts)

| Tool | Description |
|------|-------------|
| `honeycomb_list_triggers` | List all triggers in a dataset |
| `honeycomb_get_trigger` | Get specific trigger by ID |
| `honeycomb_create_trigger` | Create trigger with inline query spec |
| `honeycomb_update_trigger` | Update existing trigger |
| `honeycomb_delete_trigger` | Delete trigger |

### SLOs (Service Level Objectives)

| Tool | Description |
|------|-------------|
| `honeycomb_list_slos` | List all SLOs in a dataset |
| `honeycomb_get_slo` | Get specific SLO by ID |
| `honeycomb_create_slo` | Create SLO with optional derived columns and burn alerts |
| `honeycomb_update_slo` | Update existing SLO |
| `honeycomb_delete_slo` | Delete SLO |

### Burn Alerts (SLO Budget Alerts)

| Tool | Description |
|------|-------------|
| `honeycomb_list_burn_alerts` | List burn alerts for an SLO |
| `honeycomb_get_burn_alert` | Get specific burn alert by ID |
| `honeycomb_create_burn_alert` | Create exhaustion_time or budget_rate alert |
| `honeycomb_update_burn_alert` | Update existing burn alert |
| `honeycomb_delete_burn_alert` | Delete burn alert |

## Single-Call Resource Creation

The tool definitions support complex nested structures via Builder integration:

### Create Trigger with Inline Query

```python
# Claude can provide this in a single tool call:
{
  "dataset": "api-logs",
  "name": "High Error Rate",
  "query": {
    "time_range": 900,
    "calculations": [{"op": "COUNT"}],
    "filters": [{"column": "status_code", "op": ">=", "value": 500}]
  },
  "threshold": {"op": ">", "value": 100},
  "frequency": 900,
  "recipients": [
    {"type": "email", "target": "oncall@example.com"}
  ]
}
```

### Create SLO with Derived Column and Burn Alerts

```python
# Single tool call creates SLO + derived column + burn alerts:
{
  "dataset": "api-logs",
  "name": "API Availability",
  "sli": {
    "alias": "api_success",
    "expression": "IF(LT($status_code, 500), 1, 0)",  # Creates derived column
    "description": "Success rate"
  },
  "target_per_million": 999000,  # 99.9%
  "time_period_days": 30,
  "burn_alerts": [  # Creates burn alerts automatically
    {
      "alert_type": "exhaustion_time",
      "exhaustion_minutes": 60,
      "recipients": [{"type": "slack", "target": "#alerts"}]
    }
  ]
}
```

## Supported Features

### Query Calculations

All calculation types supported in triggers:

- `COUNT` - Count records
- `SUM`, `AVG`, `MIN`, `MAX` - Aggregations
- `COUNT_DISTINCT` - Unique values
- `P50`, `P90`, `P95`, `P99` - Percentiles
- `HEATMAP` - Distribution visualization
- `CONCURRENCY` - Concurrent requests

### Filter Operators

All filter types supported:

- Comparison: `=`, `!=`, `>`, `>=`, `<`, `<=`
- String: `starts-with`, `does-not-start-with`, `contains`, `does-not-contain`
- Existence: `exists`, `does-not-exist`
- Membership: `in`, `not-in`

### Recipient Types

Multiple notification formats:

```python
# ID-based (recommended)
{"id": "recip-123"}

# Inline email
{"type": "email", "target": "oncall@example.com"}

# Inline Slack
{"type": "slack", "target": "#alerts"}

# Inline PagerDuty
{"type": "pagerduty", "target": "routing-key", "details": {"severity": "critical"}}
```

## CLI Usage

Generate and validate tool definitions:

```bash
# Generate all tools to JSON
make generate-tools
# Creates: tools/honeycomb_tools.json

# Validate tool definitions
make validate-tools

# Generate specific resource only
python -m honeycomb.tools generate --resource triggers --output triggers.json

# Generate as Python module
python -m honeycomb.tools generate --format python --output definitions.py

# Validate custom definitions
python -m honeycomb.tools validate my_tools.json
```

## Testing

### Unit Tests

```bash
# Run all tool tests
poetry run pytest tests/unit/test_tools_*.py -v

# Completeness tests (ensure 100% feature coverage)
poetry run pytest tests/unit/test_tools_completeness.py -v
```

### DeepEval Integration Tests

Test tool definitions against the real Claude API:

```bash
# Install eval dependencies
poetry install --with evals

# Run schema acceptance tests
ANTHROPIC_API_KEY=sk-ant-... poetry run pytest \
    tests/integration/test_claude_tools_eval.py::TestToolSchemaAcceptance -v

# Run tool selection tests
ANTHROPIC_API_KEY=sk-ant-... poetry run pytest \
    tests/integration/test_claude_tools_eval.py::TestToolSelection -v

# Run parameter quality tests
ANTHROPIC_API_KEY=sk-ant-... poetry run pytest \
    tests/integration/test_claude_tools_eval.py::TestParameterQuality -v

# End-to-end tests (requires both APIs)
ANTHROPIC_API_KEY=sk-ant-... HONEYCOMB_API_KEY=... poetry run pytest \
    tests/integration/test_claude_tools_eval.py::TestEndToEnd -v -m live
```

## Architecture

### Tool Definition Structure

```json
{
  "name": "honeycomb_create_trigger",
  "description": "Creates a new trigger (alert)...",
  "input_schema": {
    "type": "object",
    "properties": {
      "dataset": {"type": "string", "description": "..."},
      "name": {"type": "string", "description": "..."}
    },
    "required": ["dataset", "name", "threshold"]
  }
}
```

### Execution Flow

```
Claude API Call
    ↓
Tool Selection
    ↓
Parameter Generation
    ↓
execute_tool()
    ↓
Builder Conversion (_build_trigger, _build_slo)
    ↓
Honeycomb API Call
    ↓
JSON Result
```

## Programmatic Access

```python
from honeycomb.tools import get_tool, list_tool_names, get_all_tools

# Get specific tool
tool = get_tool("honeycomb_create_trigger")
print(tool["description"])

# List all tool names
names = list_tool_names()
print(f"Available: {', '.join(names)}")

# Get all tools
all_tools = get_all_tools()
print(f"{len(all_tools)} tools available")
```

## Validation

All tool definitions are automatically validated:

- ✅ Tool names match `^[a-zA-Z0-9_-]{1,64}$`
- ✅ Descriptions >= 50 characters
- ✅ Input schemas are valid JSON Schema draft-07
- ✅ All properties have descriptions
- ✅ Required fields listed correctly

## Use Cases

### 1. Datadog to Honeycomb Migration

```python
# Use Claude to translate Datadog monitors to Honeycomb triggers
prompt = """
Convert this Datadog monitor to Honeycomb:
- Name: High 5xx Error Rate
- Metric: count of status:5xx
- Threshold: > 100 in last 15 minutes
- Dataset: api-logs
"""

response = anthropic.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    tools=HONEYCOMB_TOOLS,
    messages=[{"role": "user", "content": prompt}]
)

# Claude will call honeycomb_create_trigger with appropriate parameters
```

### 2. Autonomous Agent Workflows

```python
# Build agents that manage observability infrastructure
async def setup_service_monitoring(service_name: str):
    """Agent sets up complete monitoring for a service."""
    messages = [
        {
            "role": "user",
            "content": f"Set up monitoring for {service_name}: error rate trigger, "
            f"latency SLO at 99.9%, and burn alerts"
        }
    ]

    while True:
        response = anthropic.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            tools=HONEYCOMB_TOOLS,
            messages=messages
        )

        # Execute any tool calls
        for block in response.content:
            if block.type == "tool_use":
                result = await execute_tool(honeycomb, block.name, block.input)
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    }]
                })

        if response.stop_reason == "end_turn":
            break

    return response
```

### 3. Interactive CLI with LLM

```python
# Natural language CLI for Honeycomb operations
from anthropic import Anthropic

anthropic = Anthropic()

while True:
    user_input = input("honeycomb> ")

    response = anthropic.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        tools=HONEYCOMB_TOOLS,
        messages=[{"role": "user", "content": user_input}]
    )

    # Handle tool calls...
```

## Roadmap

### Completed (Phase 11 - Priority 1)
- ✅ Triggers, SLOs, Burn Alerts (15 tools)
- ✅ TriggerBuilder and SLOBuilder integration
- ✅ Comprehensive unit tests (65 tests)
- ✅ DeepEval integration tests
- ✅ CLI for generation and validation

### Planned
- **Priority 2** (~40 tools): Boards, Queries, Recipients, Derived Columns, Query Annotations, Columns, Markers
- **Priority 3** (~25 tools): Datasets, Events, API Keys, Environments, Service Map Dependencies
- **Full Builder Support**: BoardBuilder, QueryBuilder for complete orchestration

## See Also

- [Triggers Documentation](triggers.md) - Full trigger API reference
- [SLOs Documentation](slos.md) - SLO creation and management
- [Burn Alerts Documentation](burn_alerts.md) - Error budget alerting
- [Anthropic Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
