# Tool Call Debugging Skill

Systematic process for debugging Claude tool call failures that pass client-side validation but fail on the Honeycomb API.

**IMPORTANT:** All test scripts should be created in `/tmp/`, NOT in this skill directory.

## When to Use

- Tool call passes Pydantic validation but API returns 400/422 error
- Error message: "A query with the same QueryID can only be added to a board once"
- Suspicion of missing field mappings or silent data loss
- Need to verify tool input → builder → API flow

## Debugging Process

### Phase 1: Analyze the Error

1. **Capture the exact error message**
   - Full API error text
   - HTTP status code (400, 422, etc.)
   - Tool name and full input JSON

2. **Identify error category**
   - Duplicate resources (same QueryID, same email, etc.)
   - Validation errors (invalid field values)
   - Missing required fields
   - Constraint violations

### Phase 2: Validate Tool Input

Check if client-side validation catches the error:

```python
from honeycomb.models.tool_inputs import BoardToolInput  # or TriggerToolInput, SLOToolInput
from pydantic import ValidationError

try:
    validated = BoardToolInput.model_validate(tool_input)
    print("✓ Validation passed - error is NOT caught client-side")
    print("→ Need to add validation or fix field mapping")
except ValidationError as e:
    print("✓ Validation caught it - error message:")
    print(e.errors()[0]["msg"])
```

### Phase 3: Trace Field Mapping

Check if tool input fields are properly mapped to builders:

```python
from honeycomb.tools.builders import _build_board
from honeycomb.validation.boards import generate_query_signature

# Build from tool input
builder = _build_board(tool_input)
bundle = builder.build()

# Inspect each query panel
for i, qb_panel in enumerate(bundle.query_builder_panels, 1):
    qb = qb_panel.builder
    spec = qb.build()
    api_payload = spec.model_dump_for_api()

    print(f"Panel {i}: {qb.get_name()}")
    print(f"  Tool input granularity: {tool_input['inline_query_panels'][i-1].get('granularity')}")
    print(f"  Spec granularity: {spec.granularity}")
    print(f"  API payload granularity: {api_payload.get('granularity', 'OMITTED')}")
    print(f"  Signature: {hash(generate_query_signature(validated.inline_query_panels[i-1]))}")
```

**Look for:**
- Fields present in tool_input but missing from spec
- Fields present in tool_input but not in API payload
- Duplicate signatures indicating same QueryID

### Phase 4: Live API Testing

Test against real API to understand actual behavior.

**Step 1:** Use the template or create your own script in `/tmp/`:

```bash
# Copy the template
cp .claude/skills/tool-call-debug/template_live_test.py /tmp/test_my_tool.py

# Or create from scratch in /tmp/ (NOT in .claude/skills/!)
```

**Step 2:** Edit `/tmp/test_my_tool.py` with your test data:

```python
# /tmp/test_my_tool.py
import asyncio
from honeycomb import HoneycombClient
from honeycomb.tools import execute_tool

async def test_live():
    async with HoneycombClient(api_key=api_key) as client:
        dataset = "test-dataset"

        # Send events to create dataset/columns
        events = [
            {"column1": "value1", "column2": 123, ...},
            {"column1": "value2", "column2": 456, ...},
        ]
        for event in events:
            await client.events.send_async(dataset, data=event)

        await asyncio.sleep(3)  # Wait for ingestion

        # Execute tool
        try:
            result = await execute_tool(client, "honeycomb_create_board", tool_input)
            print("✓ Success")
        except Exception as e:
            print(f"✗ Failed: {e}")

            # Analyze error
            if "same QueryID" in str(e):
                print("→ Duplicate QueryID (validator should catch this)")
            elif "field" in str(e).lower():
                print("→ Field mapping issue (check builder code)")

asyncio.run(test_live())
```

**Step 3:** Run the test:

```bash
direnv exec . poetry run python /tmp/test_my_tool.py
```

### Phase 5: Add Validation

**For duplicate detection errors:**

Add to appropriate `ToolInput` model validator:

```python
@model_validator(mode="after")
def validate_no_duplicates(self) -> Self:
    """Detect duplicates before API call."""
    from honeycomb.validation.boards import validate_no_duplicate_query_panels

    if self.inline_query_panels:
        validate_no_duplicate_query_panels(self.inline_query_panels)

    return self
```

**For constraint violations:**

Add shared validator:

```python
# src/honeycomb/validation/triggers.py
def validate_trigger_no_heatmap(calc_op: str) -> None:
    if calc_op.upper() == "HEATMAP":
        raise ValueError("Triggers don't support HEATMAP")

# Use in TriggerToolInput
@model_validator(mode="after")
def validate_constraints(self) -> Self:
    validate_trigger_no_heatmap(self.query.calculations[0].op.value)
    return self
```

### Phase 6: Fix Field Mapping

**For missing field handling:**

1. Find the builder function: `_build_board()`, `_build_trigger()`, or `_build_slo()`
2. Add missing field:

```python
# Before
for breakdown in query_panel.breakdowns or []:
    qb.group_by(breakdown)

# After - add missing granularity
for breakdown in query_panel.breakdowns or []:
    qb.group_by(breakdown)

if query_panel.granularity:  # ← ADD THIS
    qb.granularity(query_panel.granularity)
```

3. Create field coverage test:

```python
def test_granularity_is_preserved():
    """Regression test for granularity field."""
    tool_input = {
        "name": "Test",
        "inline_query_panels": [{
            "name": "Test Panel",
            "dataset": "test",
            "time_range": 3600,
            "granularity": 120,  # Must be preserved
            "calculations": [{"op": "COUNT"}],
        }]
    }

    builder = _build_board(tool_input)
    bundle = builder.build()
    spec = bundle.query_builder_panels[0].builder.build()

    assert spec.granularity == 120, "granularity was lost!"
```

### Phase 7: Prevent Future Regressions

Create comprehensive field coverage test:

```python
def test_all_fields_are_mapped():
    """Test that ALL tool input fields are mapped to builder.

    Prevents regressions where new fields are added but not handled.
    """
    tool_input = {
        "name": "Complete Test",
        "inline_query_panels": [{
            # Include EVERY possible field
            "name": "Complete",
            "dataset": "test",
            "time_range": 3600,
            "granularity": 60,
            "calculations": [{"op": "COUNT"}],
            "filters": [{"column": "status", "op": "=", "value": 1}],
            "filter_combination": "AND",
            "breakdowns": ["service"],
            "orders": [{"op": "COUNT", "order": "descending"}],
            "limit": 100,
            "havings": [{"calculate_op": "COUNT", "op": ">", "value": 10}],
            "calculated_fields": [{"name": "test", "expression": "1"}],
            "compare_time_offset_seconds": 86400,
        }]
    }

    builder = _build_board(tool_input)
    spec = builder.build().query_builder_panels[0].builder.build()

    # Assert every field is set
    assert spec.granularity == 60, "granularity not set!"
    assert spec.filter_combination == "AND", "filter_combination not set!"
    assert spec.havings is not None, "havings not set!"
    # ... etc for all fields
```

## Common Error Patterns

### Pattern: Duplicate QueryID

**Symptom:** `[400] A query with the same QueryID can only be added to a board once`

**Root Cause:** Tool input has panels with identical query specs but different visualization

**Solution:**
1. Add duplicate detection to `BoardToolInput.validate_no_duplicate_queries()`
2. Use `generate_query_signature()` to compare query specs
3. Ignore visualization-only fields (orders, limit, chart_type, granularity defaults)

### Pattern: Missing Field Mapping

**Symptom:** Field in tool input but not in created query/trigger/SLO

**Root Cause:** `_build_X()` function doesn't handle the field

**Solution:**
1. Add field handling to builder function
2. Create field coverage test to prevent regression
3. Verify with live API test

### Pattern: Invalid Constraint

**Symptom:** Field value allowed by tool but rejected by API

**Root Cause:** Missing cross-field validation

**Solution:**
1. Add shared validator to `src/honeycomb/validation/`
2. Use in both ToolInput model and Builder class
3. Add tests for the constraint

## Testing Checklist

After fixing:

- [ ] Unit tests pass (`make test`)
- [ ] Field coverage test exists for the fixed field
- [ ] Live API test verifies the fix works
- [ ] Lint/typecheck clean (`make check`)
- [ ] Tool schemas regenerated (`make generate-tools`)
- [ ] Validation test covers the error case
- [ ] Commit message documents the bug and fix

## File Locations

**Validation:**
- `src/honeycomb/validation/boards.py` - Board duplicate detection
- `src/honeycomb/validation/triggers.py` - Trigger constraints
- `src/honeycomb/validation/slos.py` - SLO constraints

**Tool Inputs:**
- `src/honeycomb/models/tool_inputs.py` - TriggerToolInput, SLOToolInput, BoardToolInput

**Builders:**
- `src/honeycomb/tools/builders.py` - _build_board(), _build_trigger(), _build_slo()

**Field Coverage Tests:**
- `tests/unit/test_board_builder_field_coverage.py`
- `tests/unit/test_trigger_builder_field_coverage.py`
- `tests/unit/test_slo_builder_field_coverage.py`

## Example: Full Debugging Session

```bash
# 1. Reproduce error
direnv exec . poetry run python << 'EOF'
from honeycomb import HoneycombClient
from honeycomb.tools import execute_tool
# ... execute tool, capture error
EOF

# 2. Test validation
poetry run python << 'EOF'
from honeycomb.models.tool_inputs import BoardToolInput
BoardToolInput.model_validate(tool_input)  # Does it catch the error?
EOF

# 3. Trace field mapping
poetry run python << 'EOF'
from honeycomb.tools.builders import _build_board
builder = _build_board(tool_input)
# Inspect what fields are set
EOF

# 4. Add validation or fix mapping
# Edit src/honeycomb/validation/ or src/honeycomb/tools/builders.py

# 5. Add field coverage test
# Edit tests/unit/test_*_field_coverage.py

# 6. Verify fix
make check
poetry run pytest tests/unit/test_*_field_coverage.py -v

# 7. Test live
direnv exec . poetry run python /tmp/test_live.py
```

## Tips

- **Create all test scripts in `/tmp/`** - Never create scripts in `.claude/skills/` directory
- **Always send events first** to create datasets/columns for live testing
- **Wait 2-3 seconds** after sending events for ingestion
- **Check validator catches it** before assuming it's a field mapping bug
- **Inspect API payloads** to see what's actually being sent
- **Generate signatures** to understand QueryID generation
- **Test with minimal data** first, then expand to full tool call
- **Create regression tests** immediately after finding the bug
- **Use shared validators** for reusable validation logic

## Success Criteria

✅ Client-side validation catches the error before API call
✅ Field coverage test prevents regression
✅ Live API test confirms the fix works
✅ Error message guides Claude to fix the input
✅ All tests pass
