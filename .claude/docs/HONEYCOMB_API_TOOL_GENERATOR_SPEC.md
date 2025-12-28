# Requirements: Tool Definition Generator for honeycomb-api-python

## Overview

Generate Claude-compatible tool definitions from the `honeycomb-api-python` library, enabling LLMs to create and manage Honeycomb resources (triggers, SLOs, boards, queries) via tool calls.

## Output Format

Each generated tool must conform to Claude's tool schema:

```json
{
  "name": "string (1-64 chars, ^[a-zA-Z0-9_-]+$)",
  "description": "string (detailed, 3-4+ sentences)",
  "input_schema": {
    "type": "object",
    "properties": { ... },
    "required": [ ... ]
  },
  "input_examples": [ ... ]
}
```

## Requirements

### R1: Tool Naming Convention

| Resource | Operation | Tool Name |
|----------|-----------|-----------|
| Trigger | Create | `honeycomb_create_trigger` |
| Trigger | List | `honeycomb_list_triggers` |
| Trigger | Get | `honeycomb_get_trigger` |
| Trigger | Update | `honeycomb_update_trigger` |
| Trigger | Delete | `honeycomb_delete_trigger` |
| SLO | Create | `honeycomb_create_slo` |
| SLO | List | `honeycomb_list_slos` |
| SLO | Get | `honeycomb_get_slo` |
| SLO | Update | `honeycomb_update_slo` |
| SLO | Delete | `honeycomb_delete_slo` |
| Burn Alert | Create | `honeycomb_create_burn_alert` |
| Burn Alert | List | `honeycomb_list_burn_alerts` |
| Burn Alert | Get | `honeycomb_get_burn_alert` |
| Burn Alert | Update | `honeycomb_update_burn_alert` |
| Burn Alert | Delete | `honeycomb_delete_burn_alert` |
| Board | Create | `honeycomb_create_board` |
| Board | List | `honeycomb_list_boards` |
| Board | Get | `honeycomb_get_board` |
| Board | Update | `honeycomb_update_board` |
| Board | Delete | `honeycomb_delete_board` |
| Query | Create | `honeycomb_create_query` |
| Query | Get | `honeycomb_get_query` |
| Query | Run | `honeycomb_run_query` |
| Query | Get Results | `honeycomb_get_query_results` |
| Dataset | Create | `honeycomb_create_dataset` |
| Dataset | List | `honeycomb_list_datasets` |
| Dataset | Get | `honeycomb_get_dataset` |
| Dataset | Update | `honeycomb_update_dataset` |
| Dataset | Delete | `honeycomb_delete_dataset` |
| Column | List | `honeycomb_list_columns` |
| Column | Get | `honeycomb_get_column` |
| Column | Create | `honeycomb_create_column` |
| Column | Update | `honeycomb_update_column` |
| Column | Delete | `honeycomb_delete_column` |
| Derived Column | Create | `honeycomb_create_derived_column` |
| Derived Column | List | `honeycomb_list_derived_columns` |
| Derived Column | Get | `honeycomb_get_derived_column` |
| Derived Column | Update | `honeycomb_update_derived_column` |
| Derived Column | Delete | `honeycomb_delete_derived_column` |
| Recipient | Create | `honeycomb_create_recipient` |
| Recipient | List | `honeycomb_list_recipients` |
| Recipient | Get | `honeycomb_get_recipient` |
| Recipient | Update | `honeycomb_update_recipient` |
| Recipient | Delete | `honeycomb_delete_recipient` |
| Marker | Create | `honeycomb_create_marker` |
| Marker | List | `honeycomb_list_markers` |
| Marker | Update | `honeycomb_update_marker` |
| Marker | Delete | `honeycomb_delete_marker` |
| Marker Setting | Create | `honeycomb_create_marker_setting` |
| Marker Setting | List | `honeycomb_list_marker_settings` |
| Marker Setting | Get | `honeycomb_get_marker_setting` |
| Marker Setting | Update | `honeycomb_update_marker_setting` |
| Marker Setting | Delete | `honeycomb_delete_marker_setting` |
| Query Annotation | Create | `honeycomb_create_query_annotation` |
| Query Annotation | List | `honeycomb_list_query_annotations` |
| Query Annotation | Get | `honeycomb_get_query_annotation` |
| Query Annotation | Update | `honeycomb_update_query_annotation` |
| Query Annotation | Delete | `honeycomb_delete_query_annotation` |
| Event | Send | `honeycomb_send_event` |
| Event | Send Batch | `honeycomb_send_events_batch` |

**Constraints:**
- Prefix all tools with `honeycomb_` for namespacing
- Use snake_case
- Max 64 characters
- Only `[a-zA-Z0-9_-]`

### R2: Description Quality

Each tool description MUST include:

1. **What it does** (1 sentence)
2. **When to use it** (1 sentence)
3. **Key parameters explained** (1-2 sentences)
4. **Important caveats/limitations** (if any)

**Example (good):**
```
Creates a new trigger (alert) in Honeycomb that fires when query results cross a threshold.
Use this when migrating Datadog monitors or creating new alerting rules.
Requires a dataset, query specification with calculations/filters, threshold operator and value,
and frequency (how often to evaluate). The trigger will send notifications to configured recipients
when the threshold is breached. Note: Recipients must already exist in Honeycomb.
```

**Example (bad):**
```
Creates a trigger.
```

### R3: Input Schema Generation

Generate JSON Schema from Pydantic models with:

#### R3.1: Type Mapping

| Python Type | JSON Schema |
|-------------|-------------|
| `str` | `{"type": "string"}` |
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `bool` | `{"type": "boolean"}` |
| `list[T]` | `{"type": "array", "items": {...}}` |
| `dict[str, T]` | `{"type": "object", "additionalProperties": {...}}` |
| `Optional[T]` | Include in properties, exclude from required |
| `Literal["a", "b"]` | `{"type": "string", "enum": ["a", "b"]}` |
| `Enum` | `{"type": "string", "enum": [...values...]}` |

#### R3.2: Field Descriptions

Extract from:
1. Pydantic `Field(description="...")`
2. Docstring `Args:` section
3. Type annotations with `Annotated[str, "description"]`

**Every field MUST have a description.** If not found in source, generate a sensible default or flag for manual review.

#### R3.3: Nested Objects

For complex types, generate nested `$defs` or inline object schemas:

```json
{
  "type": "object",
  "properties": {
    "threshold": {
      "type": "object",
      "description": "Threshold configuration for trigger firing",
      "properties": {
        "op": {
          "type": "string",
          "enum": [">", ">=", "<", "<="],
          "description": "Comparison operator"
        },
        "value": {
          "type": "number",
          "description": "Threshold value to compare against"
        }
      },
      "required": ["op", "value"]
    }
  }
}
```

#### R3.4: Required vs Optional

- Fields without defaults → `required`
- Fields with `Optional[T]` or `T | None` → not required
- Fields with default values → not required

### R4: Input Examples (Recommended)

Generate 2-3 examples per tool showing:
1. Minimal required fields only
2. Common use case with optional fields
3. Complex/advanced usage (if applicable)

```json
"input_examples": [
  {
    "environment": "production",
    "dataset": "api-logs",
    "name": "High Error Rate",
    "query": {
      "calculations": [{"op": "COUNT"}],
      "filters": [{"column": "status_code", "op": ">=", "value": 500}],
      "time_range": 900
    },
    "threshold": {"op": ">", "value": 100},
    "frequency": 900
  },
  {
    "environment": "production",
    "dataset": "api-logs",
    "name": "Slow P99 Latency",
    "query": {
      "calculations": [{"op": "P99", "column": "duration_ms"}],
      "time_range": 300
    },
    "threshold": {"op": ">", "value": 5000},
    "frequency": 300,
    "description": "Alert when P99 latency exceeds 5 seconds",
    "recipients": ["email:oncall@example.com"]
  }
]
```

### R5: Resources to Generate Tools For

**Priority 1 (Migration Critical):**

| Resource | Operations |
|----------|------------|
| Triggers | create, list, get, update, delete |
| SLOs | create, list, get, update, delete |
| Burn Alerts | create, list, get, update, delete |

**Priority 2 (Observability Infrastructure):**

| Resource | Operations |
|----------|------------|
| Boards | create, list, get, update, delete |
| Queries | create, get, run, get_results |
| Derived Columns | create, list, get, update, delete |
| Recipients | create, list, get, update, delete |

**Priority 3 (Full Coverage):**

| Resource | Operations |
|----------|------------|
| Datasets | create, list, get, update, delete |
| Columns | list, get, create, update, delete |
| Markers | create, list, update, delete |
| Marker Settings | create, list, get, update, delete |
| Query Annotations | create, list, get, update, delete |
| Events | send, send_batch |

### R6: Output Formats

Generate tool definitions in multiple formats:

#### R6.1: JSON File

```json
{
  "tools": [
    {
      "name": "honeycomb_create_trigger",
      "description": "...",
      "input_schema": { ... },
      "input_examples": [ ... ]
    }
  ],
  "version": "0.1.0",
  "generated_at": "2025-12-27T12:00:00Z"
}
```

#### R6.2: Python Module

```python
# honeycomb_tools.py
from typing import Any

HONEYCOMB_TOOLS: list[dict[str, Any]] = [
    {
        "name": "honeycomb_create_trigger",
        "description": "...",
        "input_schema": { ... },
    },
    ...
]

def get_tool(name: str) -> dict[str, Any] | None:
    """Get a tool definition by name."""
    return next((t for t in HONEYCOMB_TOOLS if t["name"] == name), None)

def get_all_tools() -> list[dict[str, Any]]:
    """Get all tool definitions."""
    return HONEYCOMB_TOOLS
```

#### R6.3: TypeScript Module (Optional)

```typescript
// honeycomb_tools.ts
export interface Tool {
  name: string;
  description: string;
  input_schema: object;
  input_examples?: object[];
}

export const HONEYCOMB_TOOLS: Tool[] = [
  {
    name: "honeycomb_create_trigger",
    description: "...",
    input_schema: { ... },
  },
  ...
];
```

### R7: Validation

The generator MUST validate:

1. **Tool names** match regex `^[a-zA-Z0-9_-]{1,64}$`
2. **Descriptions** are non-empty and ≥50 characters
3. **Input schemas** are valid JSON Schema draft-07
4. **Required fields** are listed in `required` array
5. **Examples** validate against the schema (if provided)

### R8: Generator CLI

```bash
# Generate all tools
python -m honeycomb_api.tools generate --output honeycomb_tools.json

# Generate specific resource
python -m honeycomb_api.tools generate --resource triggers --output triggers_tools.json

# Generate with examples
python -m honeycomb_api.tools generate --with-examples --output honeycomb_tools.json

# Validate existing definitions
python -m honeycomb_api.tools validate honeycomb_tools.json

# Generate Python module
python -m honeycomb_api.tools generate --format python --output honeycomb_tools.py
```

### R9: Integration with Anthropic SDK

The generated tools should work directly with Anthropic's SDK:

```python
from anthropic import Anthropic
from honeycomb_api.tools import HONEYCOMB_TOOLS

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    tools=HONEYCOMB_TOOLS,  # Direct usage
    messages=[
        {"role": "user", "content": "Create a trigger for high error rates in the api-logs dataset"}
    ]
)
```

### R10: Tool Execution Handler with Builder Integration

For complex resources (Boards, SLOs, Triggers, Queries), the executor uses the library's Builder pattern to enable **single-call creation** of resources that would otherwise require multiple API calls.

**Builder-Enabled Resources:**

| Resource | Builder | Orchestration Method | Creates Automatically |
|----------|---------|---------------------|----------------------|
| Board | `BoardBuilder` | `boards.create_from_bundle_async()` | Queries, Annotations, SLOs, Derived Columns |
| SLO | `SLOBuilder` | `slos.create_from_bundle_async()` | Derived Columns, Burn Alerts |
| Trigger | `TriggerBuilder` | `triggers.create_async()` | Embedded Query Spec |
| Query | `QueryBuilder` | `queries.create_async()` | Query with dataset scope |

**Benefits:**
- **Single tool call** - LLM says "create board with these charts" not "create query, then board"
- **No ID management** - LLM doesn't track intermediate query/annotation IDs
- **Hidden complexity** - Derived columns, query annotations created automatically

```python
# honeycomb_tool_handlers.py
from honeycomb import (
    HoneycombClient, QueryBuilder, BoardBuilder, SLOBuilder, TriggerBuilder
)
import json

async def execute_tool(
    client: HoneycombClient,
    tool_name: str,
    tool_input: dict,
) -> str:
    """Execute a Honeycomb tool and return the result as a string."""

    # === BUILDER-ENABLED RESOURCES ===

    if tool_name == "honeycomb_create_board":
        builder = BoardBuilder(tool_input["name"])
        if tool_input.get("layout") == "auto":
            builder.auto_layout()
        for panel in tool_input.get("panels", []):
            if panel["type"] == "query":
                qb = _build_query(panel)
                builder.query(qb, style=panel.get("style", "graph"))
            elif panel["type"] == "slo":
                sb = _build_slo(panel)
                builder.slo(sb)
        result = await client.boards.create_from_bundle_async(builder.build())
        return json.dumps(result.model_dump())

    elif tool_name == "honeycomb_create_slo":
        builder = _build_slo(tool_input)
        result = await client.slos.create_from_bundle_async(builder.build())
        return json.dumps({k: v.model_dump() for k, v in result.items()})

    elif tool_name == "honeycomb_create_trigger":
        builder = _build_trigger(tool_input)
        result = await client.triggers.create_async(
            dataset=tool_input["dataset"],
            trigger=builder.build()
        )
        return json.dumps(result.model_dump())

    elif tool_name == "honeycomb_run_query":
        builder = _build_query(tool_input)
        result = await client.query_results.create_and_run_async(builder)
        return json.dumps(result.model_dump())

    # === SIMPLE CRUD OPERATIONS ===

    elif tool_name == "honeycomb_list_triggers":
        result = await client.triggers.list_async(dataset=tool_input["dataset"])
        return json.dumps([t.model_dump() for t in result])

    # ... other tools

    raise ValueError(f"Unknown tool: {tool_name}")


def _build_query(data: dict) -> QueryBuilder:
    """Convert tool input to QueryBuilder."""
    qb = QueryBuilder(data.get("name", "Query")).dataset(data["dataset"])
    if "time_range" in data:
        qb.time_range(data["time_range"])
    for calc in data.get("calculations", []):
        op = calc["op"].lower()
        col = calc.get("column")
        if op == "count":
            qb.count()
        elif op == "avg":
            qb.avg(col)
        # ... other ops
    for f in data.get("filters", []):
        qb.filter(f["column"], f["op"], f.get("value"))
    for col in data.get("group_by", []):
        qb.group_by(col)
    return qb


def _build_slo(data: dict) -> SLOBuilder:
    """Convert tool input to SLOBuilder."""
    builder = SLOBuilder(data["name"]).dataset(data["dataset"])
    if "target_percentage" in data:
        builder.target_percentage(data["target_percentage"])
    sli = data["sli"]
    if "expression" in sli:
        builder.sli(sli["alias"], sli["expression"])
    else:
        builder.sli(sli["alias"])
    for ba in data.get("burn_alerts", []):
        if ba["type"] == "exhaustion_time":
            builder.exhaustion_time_alert(ba["threshold_minutes"])
        for r in ba.get("recipients", []):
            if r["type"] == "email":
                builder.email(r["target"])
    return builder


def _build_trigger(data: dict) -> TriggerBuilder:
    """Convert tool input to TriggerBuilder."""
    builder = TriggerBuilder(data["name"]).dataset(data["dataset"])
    query = data["query"]
    if "time_range" in query:
        builder.time_range(query["time_range"])
    for calc in query.get("calculations", []):
        if calc["op"].lower() == "count":
            builder.count()
        # ... single calculation only for triggers
    for f in query.get("filters", []):
        builder.filter(f["column"], f["op"], f.get("value"))
    threshold = data["threshold"]
    if threshold["op"] == ">":
        builder.threshold_gt(threshold["value"])
    if "frequency" in data:
        builder.frequency(data["frequency"])
    for r in data.get("recipients", []):
        if r["type"] == "email":
            builder.email(r["target"])
    return builder
```

---

## Example Generated Tool: `honeycomb_create_trigger`

```json
{
  "name": "honeycomb_create_trigger",
  "description": "Creates a new trigger (alert) in Honeycomb that fires when query results cross a specified threshold. Use this tool when migrating alerting rules from Datadog monitors or when setting up new alerts for error rates, latency spikes, or other anomalies. The trigger evaluates a query at the specified frequency and sends notifications to configured recipients when the threshold condition is met. Important: The query must include at least one calculation (COUNT, AVG, P99, etc.), and recipients must already exist in your Honeycomb team.",
  "input_schema": {
    "type": "object",
    "properties": {
      "environment": {
        "type": "string",
        "description": "The Honeycomb environment slug where the trigger will be created (e.g., 'production', 'staging')"
      },
      "dataset": {
        "type": "string",
        "description": "The dataset slug to query for this trigger (e.g., 'api-logs', 'frontend-traces')"
      },
      "name": {
        "type": "string",
        "description": "Human-readable name for the trigger, shown in alerts and the UI (e.g., 'High Error Rate - API')"
      },
      "description": {
        "type": "string",
        "description": "Optional longer description explaining what this trigger monitors and why"
      },
      "query": {
        "type": "object",
        "description": "The Honeycomb query specification that defines what data to evaluate",
        "properties": {
          "calculations": {
            "type": "array",
            "description": "Aggregation operations to perform. At least one required.",
            "items": {
              "type": "object",
              "properties": {
                "op": {
                  "type": "string",
                  "enum": ["COUNT", "SUM", "AVG", "MAX", "MIN", "P50", "P75", "P90", "P95", "P99", "P999", "COUNT_DISTINCT", "HEATMAP", "RATE_SUM", "RATE_AVG"],
                  "description": "The aggregation operation"
                },
                "column": {
                  "type": "string",
                  "description": "Column to aggregate (required for all ops except COUNT)"
                }
              },
              "required": ["op"]
            },
            "minItems": 1
          },
          "filters": {
            "type": "array",
            "description": "Optional filters to narrow down the data",
            "items": {
              "type": "object",
              "properties": {
                "column": {
                  "type": "string",
                  "description": "Column name to filter on"
                },
                "op": {
                  "type": "string",
                  "enum": ["=", "!=", ">", ">=", "<", "<=", "exists", "does-not-exist", "contains", "does-not-contain", "starts-with", "does-not-start-with", "in", "not-in"],
                  "description": "Filter operator"
                },
                "value": {
                  "description": "Value to compare against (type depends on column)"
                }
              },
              "required": ["column", "op"]
            }
          },
          "breakdowns": {
            "type": "array",
            "description": "Optional columns to group results by",
            "items": {"type": "string"}
          },
          "time_range": {
            "type": "integer",
            "description": "Time window in seconds to query (default: 900 = 15 minutes)",
            "default": 900
          }
        },
        "required": ["calculations"]
      },
      "threshold": {
        "type": "object",
        "description": "Condition that triggers the alert",
        "properties": {
          "op": {
            "type": "string",
            "enum": [">", ">=", "<", "<="],
            "description": "Comparison operator for threshold"
          },
          "value": {
            "type": "number",
            "description": "Threshold value that triggers the alert"
          },
          "exceeded_limit": {
            "type": "integer",
            "description": "Number of consecutive times threshold must be exceeded before firing (default: 1)",
            "default": 1
          }
        },
        "required": ["op", "value"]
      },
      "frequency": {
        "type": "integer",
        "description": "How often to evaluate the trigger in seconds (default: 900 = 15 minutes). Minimum: 60 seconds.",
        "default": 900,
        "minimum": 60
      },
      "recipients": {
        "type": "array",
        "description": "List of recipient IDs or notification targets (e.g., ['email:oncall@example.com', 'pagerduty:ABC123'])",
        "items": {"type": "string"}
      },
      "disabled": {
        "type": "boolean",
        "description": "If true, trigger is created but won't fire alerts (default: false)",
        "default": false
      }
    },
    "required": ["environment", "dataset", "name", "query", "threshold"]
  },
  "input_examples": [
    {
      "environment": "production",
      "dataset": "api-logs",
      "name": "High Error Rate",
      "query": {
        "calculations": [{"op": "COUNT"}],
        "filters": [{"column": "status_code", "op": ">=", "value": 500}],
        "time_range": 900
      },
      "threshold": {"op": ">", "value": 100}
    },
    {
      "environment": "production",
      "dataset": "api-logs",
      "name": "Slow P99 Latency",
      "description": "Alert when API P99 latency exceeds 5 seconds",
      "query": {
        "calculations": [{"op": "P99", "column": "duration_ms"}],
        "filters": [{"column": "service.name", "op": "=", "value": "api-gateway"}],
        "time_range": 300
      },
      "threshold": {"op": ">", "value": 5000},
      "frequency": 300,
      "recipients": ["email:oncall@example.com"]
    }
  ]
}
```

---

## Example Generated Tool: `honeycomb_create_slo`

```json
{
  "name": "honeycomb_create_slo",
  "description": "Creates a new Service Level Objective (SLO) in Honeycomb to track reliability targets over time. Use this when migrating SLOs from Datadog or establishing new reliability goals. An SLO requires a Service Level Indicator (SLI) defined as a calculated field expression that returns 1 for 'good' events and 0 for 'bad' events. The target is specified as a percentage (e.g., 99.9% = 999000 per million). Burn alerts can be attached separately to notify when error budget is depleting too quickly.",
  "input_schema": {
    "type": "object",
    "properties": {
      "environment": {
        "type": "string",
        "description": "The Honeycomb environment slug (e.g., 'production')"
      },
      "dataset": {
        "type": "string",
        "description": "The dataset slug containing the events to measure"
      },
      "name": {
        "type": "string",
        "description": "Human-readable name for the SLO (e.g., 'API Availability')"
      },
      "description": {
        "type": "string",
        "description": "Optional longer description of what this SLO measures and why"
      },
      "sli": {
        "type": "object",
        "description": "Service Level Indicator definition",
        "properties": {
          "alias": {
            "type": "string",
            "description": "Short name for the SLI column (e.g., 'is_successful')"
          },
          "expression": {
            "type": "string",
            "description": "Honeycomb calculated field expression returning 1 (good) or 0 (bad). Example: 'IF(LT($status_code, 400), 1, 0)'"
          }
        },
        "required": ["alias", "expression"]
      },
      "target_per_million": {
        "type": "integer",
        "description": "Target as parts per million. 999000 = 99.9%, 990000 = 99%, 999900 = 99.99%",
        "minimum": 0,
        "maximum": 1000000
      },
      "time_period_days": {
        "type": "integer",
        "description": "Rolling time window in days for SLO calculation (common: 7, 14, 30)",
        "enum": [7, 14, 30],
        "default": 30
      }
    },
    "required": ["environment", "dataset", "name", "sli", "target_per_million"]
  },
  "input_examples": [
    {
      "environment": "production",
      "dataset": "api-logs",
      "name": "API Success Rate",
      "sli": {
        "alias": "is_successful",
        "expression": "IF(LT($status_code, 500), 1, 0)"
      },
      "target_per_million": 999000,
      "time_period_days": 30
    },
    {
      "environment": "production",
      "dataset": "api-logs",
      "name": "Latency SLO",
      "description": "99th percentile latency under 500ms",
      "sli": {
        "alias": "is_fast",
        "expression": "IF(LTE($duration_ms, 500), 1, 0)"
      },
      "target_per_million": 990000,
      "time_period_days": 7
    }
  ]
}
```

---

## Implementation Approaches

### Option A: Introspection from Pydantic Models (Recommended)

```python
# In honeycomb-api-python/tools/generator.py

from pydantic import BaseModel
from typing import get_type_hints, get_origin, get_args, Callable, Any

def generate_tool_from_method(
    resource_name: str,
    method_name: str,
    method: Callable,
    input_model: type[BaseModel] | None = None,
) -> dict[str, Any]:
    """Generate a Claude tool definition from an API client method."""

    # Extract schema from Pydantic model
    if input_model:
        schema = input_model.model_json_schema()
    else:
        # Introspect from method signature
        schema = _schema_from_signature(method)

    # Build description from docstring
    description = _build_description(method.__doc__, resource_name, method_name)

    return {
        "name": f"honeycomb_{method_name}_{resource_name}",
        "description": description,
        "input_schema": schema,
    }
```

### Option B: Decorator-Based Registration

```python
# In honeycomb-api-python

from honeycomb_api.tools import register_tool

class TriggersResource:
    @register_tool(
        name="honeycomb_create_trigger",
        description="Creates a new trigger...",
        examples=[...],
    )
    async def create_async(self, dataset: str, trigger: TriggerCreate) -> Trigger:
        ...
```

### Option C: Separate Schema Definitions (Most Control)

```python
# In honeycomb-api-python/tools/schemas/triggers.py

TRIGGER_CREATE_TOOL = {
    "name": "honeycomb_create_trigger",
    "description": "...",
    "input_schema": {...},
    "input_examples": [...],
}

# Manually curated for quality, but kept in sync with Pydantic models via tests
```

---

## Recommendation

Use **Option A (Introspection) + Manual Description Override**:

1. Auto-generate schemas from Pydantic models (ensures type accuracy)
2. Allow manual description overrides via a config file or decorators (ensures quality descriptions)
3. Generate examples from test fixtures or manual curation
4. Validate generated schemas against test cases

This gives you:
- **Accuracy**: Schemas always match the actual API
- **Quality**: Descriptions can be hand-crafted for clarity
- **Maintainability**: Changes to models auto-propagate to tools

---

## Integration with Migration Tooling

Once tool definitions are generated, the migration-tooling project can use them:

```python
# backend/app/services/honeycomb_api.py

from honeycomb_api import HoneycombClient
from honeycomb_api.tools import HONEYCOMB_TOOLS, execute_tool

class HoneycombAPIService:
    """Service that uses generated tools for Honeycomb operations."""

    def __init__(self, api_key: str):
        self.client = HoneycombClient(api_key=api_key)

    def get_tools(self) -> list[dict]:
        """Return tool definitions for LLM."""
        return HONEYCOMB_TOOLS

    async def execute_tool_call(
        self,
        tool_name: str,
        tool_input: dict,
    ) -> str:
        """Execute a tool call from the LLM."""
        return await execute_tool(self.client, tool_name, tool_input)
```

This allows the translation service to:
1. Pass tool definitions to the LLM for structured output
2. Execute the resulting tool calls against the Honeycomb API
3. Return results to complete the migration workflow

---

## R11: Claude API Integration Tests (Eval Suite with DeepEval)

Reference implementation using [DeepEval](https://github.com/confident-ai/deepeval) to validate tool definitions against the real Claude API. DeepEval is Apache 2.0 licensed and runs fully standalone without any SaaS requirement.

### Why DeepEval

| Feature | Benefit |
|---------|---------|
| `ToolCorrectnessMetric` | Validates Claude selects the right tool |
| `ArgumentCorrectnessMetric` | Validates parameter quality and completeness |
| Pytest-native | Integrates with existing test suite |
| Local execution | No cloud dependency, runs offline |
| Ollama support | Can use local LLMs as evaluation judge |

### Test Categories

| Category | DeepEval Metric | What It Validates |
|----------|-----------------|------------------|
| Tool Selection | `ToolCorrectnessMetric` | Claude picks the correct tool |
| Parameter Quality | `ArgumentCorrectnessMetric` | Claude generates valid parameters |
| Schema Acceptance | Manual assertion | Claude parses tool definitions |
| End-to-End | Custom + Honeycomb API | Full loop execution |

### Optional Dependencies

```toml
# pyproject.toml
[project.optional-dependencies]
evals = [
    "deepeval>=1.0",
    "anthropic>=0.40.0",
]
```

### Example Test

```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import ToolCorrectnessMetric

def test_trigger_tool_selection(anthropic_client):
    result = call_claude_with_tools(
        anthropic_client,
        "Create a trigger for high error rates in api-logs"
    )

    test_case = LLMTestCase(
        input="Create a trigger for high error rates in api-logs",
        actual_output=result["text"],
        tools_called=[ToolCall(name=tc.name) for tc in result["tool_calls"]],
        expected_tools=[ToolCall(name="honeycomb_create_trigger")],
    )

    assert_test(test_case, [ToolCorrectnessMetric(threshold=0.9)])
```

### Running Tests

```bash
# Install eval dependencies
poetry install --extras evals

# Run all eval tests (requires both API keys)
ANTHROPIC_API_KEY=sk-ant-... HONEYCOMB_API_KEY=... \
    poetry run pytest tests/integration/test_claude_tools_eval.py -v

# Run with DeepEval's enhanced output
poetry run deepeval test run tests/integration/test_claude_tools_eval.py
```

### Fully Offline Mode

```python
# Use Ollama as local evaluation judge
from deepeval.models import OllamaModel

local_judge = OllamaModel(model="llama3.2")
metric = ToolCorrectnessMetric(model=local_judge, threshold=0.9)
```

See PLAN.md Phase 11.16 for detailed test implementation.
