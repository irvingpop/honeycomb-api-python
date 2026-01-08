# Tool Schema Validation Refactor

**Date:** 2026-01-07
**Status:** Planning (Revised)

## Problem Statement

External program generated invalid board tool call with nested structure:
```json
{
  "inline_query_panels": [{
    "name": "CPU",
    "query": {"dataset": "...", "calculations": [...]},  // Invalid nesting
    "chart_type": "line"  // Not in schema
  }]
}
```

**Result:** All 15 query panels created with identical empty specs → duplicate QueryIDs → API error: `A query with the same QueryID can only be added to a board once.`

## Root Cause Analysis

### Why It Happened

1. **No `additionalProperties: false` constraint** - Schema allowed undefined properties
2. **No runtime validation** - Builder silently ignored invalid properties
3. **Schema-builder mismatch** - SLO tool examples use `burn_alerts` but schema doesn't define it

### Current Architecture Issues

| Component | Issue | Impact |
|-----------|-------|--------|
| **Existing Models** | `Calculation`, `Filter`, `Order`, `Having` accept `Enum \| str` | No type constraint in schema |
| **Existing Models** | No `extra="forbid"` config | No `additionalProperties: false` |
| **SLO Tool** | Missing `burn_alerts`, `datasets`, `target_percentage` from schema | Examples work but will fail with validation |
| **Board Tool** | Position uses tuple, API uses named fields | Schema mismatch with API |
| **All Tools** | No `additionalProperties: false` on nested objects | Claude can add arbitrary fields |
| **Builders** | No property validation | Silently ignores schema violations |

## Solution Overview

### Simplified Approach: Fix Existing Models + Create Minimal New Models

Instead of creating duplicate "strict" models, we will:

1. **Fix existing Pydantic models** - Remove `| str` flexibility, add `extra="forbid"`
2. **Create new models only where needed** - Position, QueryPanel, BoardTool, SLOTool inputs
3. **Use Pydantic schema generation** - Replace hand-coded schemas with `model_json_schema()`
4. **Validate in builders** - Use `model_validate()` for runtime validation

### Why This Works

Pydantic automatically coerces string values to enum members for `str, Enum` types:

```python
class FilterOp(str, Enum):
    EQUALS = "="
    CONTAINS = "contains"

# If we change Filter.op from `FilterOp | str` to just `FilterOp`:
Filter(op=FilterOp.EQUALS, ...)     # Works (enum object)
Filter(op="=", ...)                  # Works (Pydantic coerces "=" → FilterOp.EQUALS)
Filter(op="contains", ...)           # Works (Pydantic coerces)
Filter(op="EQUALS", ...)             # FAILS (name, not value - but nobody does this)
```

**Impact:** All existing code using enum values as strings (`"COUNT"`, `"="`, `"contains"`) continues to work.

## Phase 1: Fix Existing Models

### 1.1 Update query_builder.py Models

**File:** `src/honeycomb/models/query_builder.py`

**Changes:**

```python
# BEFORE
class Calculation(BaseModel):
    op: CalcOp | str = Field(...)
    column: str | None = None
    alias: str | None = None

# AFTER
class Calculation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    op: CalcOp = Field(description="Calculation operation (COUNT, AVG, P99, etc.)")
    column: str | None = Field(default=None, description="Column to calculate on")
    alias: str | None = Field(default=None, description="Alias for the result column")
```

**All models to update:**

| Model | Current `op` Type | New Type | Add `extra="forbid"` |
|-------|-------------------|----------|---------------------|
| `Calculation` | `CalcOp \| str` | `CalcOp` | Yes |
| `Filter` | `FilterOp \| str` | `FilterOp` | Yes |
| `Order` | `CalcOp \| str`, `OrderDirection \| str` | `CalcOp`, `OrderDirection` | Yes |
| `Having` | `CalcOp \| str`, `FilterOp \| str` | `CalcOp`, `FilterOp` | Yes |

### 1.2 Update boards.py Models

**File:** `src/honeycomb/models/boards.py`

**Changes:**

```python
# BEFORE
class BoardViewFilter(BaseModel):
    column: str
    operation: FilterOp  # Already enum-only, good!
    value: Any | None = None

# AFTER
class BoardViewFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: str = Field(description="Column name to filter on")
    operation: FilterOp = Field(description="Filter operation")
    value: Any | None = Field(default=None, description="Filter value")
```

**Schema output for FilterOp:**
```json
"operation": {
  "enum": ["=", "!=", ">", ">=", "<", "<=", "starts-with", "contains", "exists", ...]
}
```

Pydantic uses the **string values** (not Python names) automatically.

## Phase 2: Create New Tool Input Models

### 2.1 Position Model (API-Native Structure)

**Current:** `tuple[int, int, int, int]` (doesn't match API)

**API expects:**
```json
{
  "x_coordinate": 0,
  "y_coordinate": 0,
  "height": 6,
  "width": 8
}
```

**New model:**

```python
# src/honeycomb/models/tool_inputs.py

class PositionInput(BaseModel):
    """Panel position on the board grid."""
    model_config = ConfigDict(extra="forbid")

    x_coordinate: int = Field(ge=0, description="X position on grid")
    y_coordinate: int = Field(ge=0, description="Y position on grid")
    width: int = Field(ge=1, le=24, description="Panel width (1-24)")
    height: int = Field(ge=1, le=24, description="Panel height (1-24)")
```

**Breaking change:** Update `BoardBuilder.query()` to accept `PositionInput | None` instead of `tuple`.

### 2.2 Query Panel Input

```python
class QueryPanelInput(BaseModel):
    """Query panel specification for board tool input."""
    model_config = ConfigDict(extra="forbid")

    # Panel metadata
    name: str = Field(description="Panel/query name")
    description: str | None = Field(default=None, description="Panel description")
    style: Literal["graph", "table", "combo"] = Field(
        default="graph", description="Panel display style"
    )
    visualization: dict[str, Any] | None = Field(
        default=None, description="Visualization settings"
    )
    position: PositionInput | None = Field(
        default=None, description="Panel position for manual layout"
    )

    # Query specification (flat, NOT nested)
    dataset: str | None = Field(default=None, description="Dataset slug (None = environment-wide)")
    time_range: int | None = Field(default=None, description="Time range in seconds")
    start_time: int | None = Field(default=None, description="Absolute start time (Unix timestamp)")
    end_time: int | None = Field(default=None, description="Absolute end time (Unix timestamp)")
    granularity: int | None = Field(default=None, description="Time granularity in seconds")
    calculations: list[Calculation] | None = Field(default=None, description="Calculations to perform")
    filters: list[Filter] | None = Field(default=None, description="Query filters")
    breakdowns: list[str] | None = Field(default=None, description="Columns to group by")
    filter_combination: FilterCombination | None = Field(default=None, description="How to combine filters")
    orders: list[Order] | None = Field(default=None, description="Result ordering")
    limit: int | None = Field(default=None, description="Result limit")
    havings: list[Having] | None = Field(default=None, description="Having clauses")
```

**Key:** Uses typed models (`Calculation`, `Filter`, etc.) directly - NOT `dict[str, Any]`.

### 2.3 SLO Tool Input

**Design decision:** Only expose `target_percentage` in schema. Remove `target_nines` entirely.

```python
class SLIInput(BaseModel):
    """SLI specification for tool input."""
    model_config = ConfigDict(extra="forbid")

    alias: str = Field(description="Column alias for the SLI")
    expression: str | None = Field(default=None, description="Derived column expression (creates column if provided)")
    description: str | None = Field(default=None, description="SLI description")


class BurnAlertInput(BaseModel):
    """Burn alert specification for inline creation."""
    model_config = ConfigDict(extra="forbid")

    alert_type: Literal["exhaustion_time", "budget_rate"] = Field(description="Alert type")
    description: str | None = Field(default=None, description="Alert description")
    exhaustion_minutes: int | None = Field(default=None, description="Minutes until budget exhaustion (for exhaustion_time)")
    budget_rate_window_minutes: int | None = Field(default=None, description="Window size (for budget_rate)")
    budget_rate_decrease_threshold_per_million: int | None = Field(default=None, description="Threshold (for budget_rate)")
    recipients: list[RecipientInput] | None = Field(default=None, description="Alert recipients")


class SLOToolInput(BaseModel):
    """Complete SLO tool input."""
    model_config = ConfigDict(extra="forbid")

    # Required
    name: str = Field(description="SLO name")
    sli: SLIInput = Field(description="SLI specification")

    # Optional metadata
    description: str | None = Field(default=None, description="SLO description")

    # Dataset(s)
    dataset: str | None = Field(default=None, description="Single dataset slug")
    datasets: list[str] | None = Field(default=None, description="Multiple dataset slugs")

    # Target - only target_percentage exposed (most intuitive)
    target_percentage: float = Field(
        description="Target as percentage (e.g., 99.9 for 99.9%)"
    )

    # Time period
    time_period_days: int = Field(
        default=30,
        description="SLO time period in days (typically 7, 14, or 30)"
    )

    # Inline burn alerts
    burn_alerts: list[BurnAlertInput] | None = Field(
        default=None, description="Burn alerts to create with the SLO"
    )
```

**Note:** `target_nines` removed entirely. Builder converts `target_percentage` to `target_per_million` internally.

### 2.4 Recipient Input

```python
class RecipientInput(BaseModel):
    """Recipient specification (shared across triggers, SLOs, burn alerts)."""
    model_config = ConfigDict(extra="forbid")

    # Either reference existing recipient by ID...
    id: str | None = Field(default=None, description="Existing recipient ID")

    # ...OR create inline with type + target
    type: Literal["email", "webhook"] | None = Field(
        default=None, description="Recipient type (for inline creation)"
    )
    target: str | None = Field(
        default=None, description="Recipient target (email address or webhook URL)"
    )
```

**Note:** Only `email` and `webhook` are testable without external integrations.

### 2.5 Board Tool Input

```python
class TextPanelInput(BaseModel):
    """Text/markdown panel for boards."""
    model_config = ConfigDict(extra="forbid")

    content: str = Field(description="Markdown content")
    position: PositionInput | None = Field(default=None, description="Panel position")


class SLOPanelInput(BaseModel):
    """Inline SLO panel for boards."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="SLO name")
    description: str | None = Field(default=None, description="SLO description")
    dataset: str = Field(description="Dataset slug")
    sli: SLIInput = Field(description="SLI specification")
    target_percentage: float = Field(description="Target as percentage")
    time_period_days: int = Field(default=30, description="Time period in days")
    position: PositionInput | None = Field(default=None, description="Panel position")


class TagInput(BaseModel):
    """Tag for boards."""
    model_config = ConfigDict(extra="forbid")

    key: str = Field(description="Tag key")
    value: str = Field(description="Tag value")


class PresetFilterInput(BaseModel):
    """Preset filter for boards."""
    model_config = ConfigDict(extra="forbid")

    column: str = Field(description="Column to filter on")
    alias: str = Field(description="Display alias")


class BoardViewInput(BaseModel):
    """Board view with filters."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="View name")
    filters: list[BoardViewFilter] | None = Field(
        default=None, description="View filters"
    )


class BoardToolInput(BaseModel):
    """Complete board tool input."""
    model_config = ConfigDict(extra="forbid")

    # Board metadata
    name: str = Field(description="Board name")
    description: str | None = Field(default=None, description="Board description")
    layout_generation: Literal["auto", "manual"] = Field(
        default="auto", description="Layout mode"
    )

    # Panels
    inline_query_panels: list[QueryPanelInput] | None = Field(
        default=None, description="Query panels to create"
    )
    inline_slo_panels: list[SLOPanelInput] | None = Field(
        default=None, description="SLO panels to create"
    )
    text_panels: list[TextPanelInput] | None = Field(
        default=None, description="Text/markdown panels"
    )
    slo_panels: list[str] | None = Field(
        default=None, description="Existing SLO IDs to add"
    )

    # Board features
    tags: list[TagInput] | None = Field(default=None, description="Board tags")
    preset_filters: list[PresetFilterInput] | None = Field(
        default=None, description="Preset filter columns"
    )
    views: list[BoardViewInput] | None = Field(
        default=None, description="Named views with filters"
    )
```

## Phase 3: Update BoardBuilder

### 3.1 Update Position Handling

**File:** `src/honeycomb/models/board_builder.py`

```python
# BEFORE
def query(
    self,
    qb_or_id: QueryBuilder | str,
    position: tuple[int, int, int, int] | None = None,  # OLD
    ...
) -> BoardBuilder:

# AFTER
from honeycomb.models.tool_inputs import PositionInput

def query(
    self,
    qb_or_id: QueryBuilder | str,
    position: PositionInput | None = None,  # NEW
    ...
) -> BoardBuilder:
```

**Also update** `QueryBuilderPanel` dataclass to use `PositionInput`.

### 3.2 Remove target_nines from SLOBuilder

**File:** `src/honeycomb/models/slo_builder.py`

```python
# DELETE this method entirely
def target_nines(self, nines: int) -> SLOBuilder:
    """REMOVED - Use target_percentage instead."""
    ...
```

Keep `target_percentage()` and `target_per_million()` (latter for API compatibility).

## Phase 4: Update Generator

### 4.1 Replace Hand-Coded Schemas

**File:** `src/honeycomb/tools/generator.py`

```python
# BEFORE (hand-coded)
schema["properties"]["inline_query_panels"] = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "calculations": {...},  # 50+ lines
        }
    }
}

# AFTER (Pydantic-powered)
from honeycomb.models.tool_inputs import BoardToolInput

def generate_create_board_tool() -> dict[str, Any]:
    schema = BoardToolInput.model_json_schema()
    # Add descriptions, examples, etc.
    return create_tool_definition(
        name="honeycomb_create_board",
        description=get_description("honeycomb_create_board"),
        input_schema=schema,
        input_examples=[...],
    )
```

### 4.2 Update SLO Tool Schema

```python
# BEFORE
base_schema = generate_schema_from_model(SLOCreate)  # Incomplete

# AFTER
from honeycomb.models.tool_inputs import SLOToolInput
schema = SLOToolInput.model_json_schema()  # Complete
```

## Phase 5: Update Builders with Pydantic Validation

**File:** `src/honeycomb/tools/builders.py`

**Note:** The `confidence` and `notes` metadata fields are stripped in `executor.py` (line 90) **before** data reaches the builders. The tool input models do NOT need to include these fields.

```python
# BEFORE (no validation)
def _build_board(data: dict[str, Any]) -> BoardBuilder:
    builder = BoardBuilder(data["name"])  # KeyError if missing
    for query_panel in data.get("inline_query_panels", []):
        qb = QueryBuilder(query_panel["name"])
        # Silent failures on unknown properties...

# AFTER (Pydantic validation)
from honeycomb.models.tool_inputs import BoardToolInput

def _build_board(data: dict[str, Any]) -> BoardBuilder:
    validated = BoardToolInput.model_validate(data)  # Raises ValidationError

    builder = BoardBuilder(validated.name)
    if validated.description:
        builder.description(validated.description)

    for panel in validated.inline_query_panels or []:
        qb = QueryBuilder(panel.name)
        if panel.dataset:
            qb.dataset(panel.dataset)
        if panel.time_range:
            qb.time_range(panel.time_range)
        for calc in panel.calculations or []:
            qb.calculate(calc.op, calc.column, calc.alias)
        # ... type-safe access throughout
        builder.query(qb, style=panel.style, position=panel.position)

    return builder
```

## Implementation Checklist

### Phase 1: Fix Existing Models
- [ ] Update `Calculation` - remove `| str`, add `extra="forbid"`
- [ ] Update `Filter` - remove `| str`, add `extra="forbid"`
- [ ] Update `Order` - remove `| str`, add `extra="forbid"`
- [ ] Update `Having` - remove `| str`, add `extra="forbid"`
- [ ] Update `BoardViewFilter` - add `extra="forbid"`
- [ ] Run tests to verify coercion still works

### Phase 2: Create Tool Input Models
- [ ] Create `src/honeycomb/models/tool_inputs.py`
- [ ] Define `PositionInput` (API-native structure)
- [ ] Define `RecipientInput`
- [ ] Define `SLIInput`, `BurnAlertInput`
- [ ] Define `QueryPanelInput` (using typed models, not dicts)
- [ ] Define `SLOToolInput` (with `target_percentage` only)
- [ ] Define `TextPanelInput`, `SLOPanelInput`, `TagInput`, `PresetFilterInput`, `BoardViewInput`
- [ ] Define `BoardToolInput`
- [ ] Write unit tests for all models

### Phase 3: Update BoardBuilder
- [ ] Update `BoardBuilder.query()` to accept `PositionInput`
- [ ] Update `QueryBuilderPanel` dataclass
- [ ] Remove `SLOBuilder.target_nines()` method
- [ ] Update any code using tuple positions

### Phase 4: Update Generator
- [ ] Replace board schema generation with `BoardToolInput.model_json_schema()`
- [ ] Replace SLO schema generation with `SLOToolInput.model_json_schema()`
- [ ] Remove manual `additionalProperties: false` additions
- [ ] Regenerate tools JSON
- [ ] Validate all tool definitions

### Phase 5: Update Builders
- [ ] Update `_build_board()` with `BoardToolInput.model_validate()`
- [ ] Update `_build_slo()` with `SLOToolInput.model_validate()`
- [ ] Update `_build_trigger()` if needed
- [ ] Remove any manual property validation code
- [ ] Update tests to expect Pydantic validation errors

### Phase 6: Update Documentation
- [ ] Update `docs/usage/boards.md` - Change position from tuple to `PositionInput` object
- [ ] Update `docs/usage/slos.md` - Remove `target_nines` from method table
- [ ] Update `docs/examples/boards/builder_board.py` - Use `PositionInput` for positions
- [ ] Update `docs/examples/slos/builder_slo.py` - Replace `target_nines(3)` with `target_percentage(99.9)`
- [ ] Run `make validate-docs` to verify all code examples still work
- [ ] Update any docstrings in modified files

### Phase 7: Update Integration Tests
- [ ] Update `tests/integration/test_claude_tools_eval.py` - Verify eval test cases use valid schemas
- [ ] Update `tests/integration/test_claude_tools_live.py` - Verify live tests use valid schemas
- [ ] Run integration tests to verify Claude tool calls work end-to-end

#### Test Case Updates Required
- [ ] `test_cases/boards.py`: Update `board_create_inline_slo` - change `target_nines` assertion to `target_percentage`
- [ ] `test_cases/slos.py`: Update `target_per_million` assertions to use `target_percentage`

#### New Test Cases to Add
**SLOs (`test_cases/slos.py`):**
- [ ] `slo_with_burn_alerts` - SLO with inline burn alert creation (exhaustion_time + budget_rate)
- [ ] `slo_delete` - Delete SLO by ID
- [ ] `slo_update` - Update existing SLO

**Boards (`test_cases/boards.py`):**
- [ ] `board_manual_layout` - Board with manual layout using PositionInput (x_coordinate, y_coordinate, width, height)
- [ ] `board_with_preset_filters` - Board with preset filter columns
- [ ] `board_update` - Update existing board

**Triggers (`test_cases/triggers.py`):**
- [ ] `trigger_with_recipients` - Trigger with inline recipient creation (email/webhook)
- [ ] `trigger_update` - Update existing trigger

### Phase 8: Final Validation
- [ ] Run full test suite (`make test`)
- [ ] Run CI pipeline (`make ci`)
- [ ] Test error messages are clear
- [ ] Verify schema constraints work (test with invalid input)
- [ ] Run live tests if possible (`/live-test`)

## Breaking Changes Summary

| Change | Impact | Migration |
|--------|--------|-----------|
| Position: tuple → PositionInput | BoardBuilder.query() signature | Use `PositionInput(x_coordinate=0, y_coordinate=0, width=8, height=6)` |
| Remove target_nines | SLOBuilder method removed | Use `target_percentage(99.9)` instead |
| Enum-only in models | `op="EQUALS"` fails (name vs value) | Use `op="="` or `op=FilterOp.EQUALS` |
| extra="forbid" | Unknown fields rejected | Remove invalid fields from input |

## Expected Error Messages

### Before (Silent Failure)
```
Input: {"name": "CPU", "query": {...}, "chart_type": "line"}
Result: Empty query spec → duplicate QueryIDs → cryptic API error
```

### After (Clear Pydantic Error)
```
Input: {"name": "CPU", "query": {...}, "chart_type": "line"}
Error: ValidationError: 2 validation errors for QueryPanelInput
  query
    Extra inputs are not permitted [type=extra_forbidden]
  chart_type
    Extra inputs are not permitted [type=extra_forbidden]
```

## File Structure

```
src/honeycomb/models/
├── tool_inputs.py          # NEW: Pydantic models for tool inputs
├── query_builder.py        # MODIFIED: Remove | str, add extra="forbid"
├── boards.py               # MODIFIED: Add extra="forbid" to BoardViewFilter
├── board_builder.py        # MODIFIED: Use PositionInput
├── slo_builder.py          # MODIFIED: Remove target_nines
└── triggers.py             # No changes needed

src/honeycomb/tools/
├── generator.py            # MODIFIED: Use Pydantic schema generation
├── builders.py             # MODIFIED: Use Pydantic validation
└── schemas.py              # No changes needed

tests/unit/
├── test_tool_inputs.py     # NEW: Test tool input models
├── test_query_builder.py   # UPDATE: Verify enum coercion
└── test_tools_builders.py  # UPDATE: Expect Pydantic errors

tests/integration/
├── test_claude_tools_eval.py   # UPDATE: Verify eval tests use valid schemas
├── test_claude_tools_live.py   # UPDATE: Verify live tests use valid schemas
└── test_cases/
    ├── boards.py               # UPDATE: Check for tuple positions
    └── slos.py                 # UPDATE: Check for target_nines

docs/
├── usage/
│   ├── boards.md           # MODIFIED: PositionInput instead of tuple
│   └── slos.md             # MODIFIED: Remove target_nines
└── examples/
    ├── boards/
    │   └── builder_board.py  # MODIFIED: PositionInput, remove target_nines
    └── slos/
        └── builder_slo.py    # MODIFIED: target_percentage instead of target_nines
```

## Success Criteria

- [ ] All existing tests pass (enum coercion works)
- [ ] Schema shows enum values (`"="`, `"COUNT"`) not names (`"EQUALS"`, `"COUNT"`)
- [ ] All nested objects have `additionalProperties: false`
- [ ] Invalid nested structures rejected with clear errors
- [ ] SLO schema includes `burn_alerts`, `target_percentage`
- [ ] Position uses API-native structure
- [ ] No `target_nines` in schema or builder
- [ ] CI passes
- [ ] All 67 tool definitions validate
- [ ] `make validate-docs` passes (all documentation examples work)
- [ ] No references to `target_nines` or tuple positions in docs

## References

- [query_builder.py](src/honeycomb/models/query_builder.py) - Calculation, Filter, Order, Having models
- [boards.py](src/honeycomb/models/boards.py) - BoardViewFilter model
- [board_builder.py](src/honeycomb/models/board_builder.py) - BoardBuilder, position handling
- [slo_builder.py](src/honeycomb/models/slo_builder.py) - SLOBuilder, target methods
- [generator.py](src/honeycomb/tools/generator.py) - Tool schema generation
- [builders.py](src/honeycomb/tools/builders.py) - Tool input to Builder conversion
