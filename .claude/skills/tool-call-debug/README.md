# Tool Call Debug Skill

Systematic debugging process for Claude tool call failures.

## Quick Reference

When a tool call passes validation but fails on the API:

```bash
# 1. Check if validator catches it
poetry run python -c "from honeycomb.models.tool_inputs import BoardToolInput; BoardToolInput.model_validate({...})"

# 2. Trace field mapping
poetry run python -c "from honeycomb.tools.builders import _build_board; builder = _build_board({...}); print(builder.build())"

# 3. Test against live API
direnv exec . poetry run python /tmp/test_live.py

# 4. Add field coverage test
# Edit tests/unit/test_*_field_coverage.py

# 5. Verify
make check && poetry run pytest tests/unit/test_*_field_coverage.py -v
```

## Common Fixes

**Duplicate QueryID:**
- Add `validate_no_duplicate_query_panels()` to model validator

**Missing field mapping:**
- Add field handling to `_build_board()` / `_build_trigger()` / `_build_slo()`
- Example: `if query_panel.granularity: qb.granularity(query_panel.granularity)`

**Invalid constraint:**
- Add shared validator to `src/honeycomb/validation/`
- Use in both ToolInput and Builder

## Examples

This skill was created from debugging sessions that fixed:
- Missing `granularity` field → duplicate QueryID errors
- Missing `filter_combination` field → silent data loss
- Missing `havings` field → silent data loss
- Missing `tags` field in SLOs → silent data loss
- HEATMAP allowed in triggers → API rejection

See [SKILL.md](SKILL.md) for full process documentation.
