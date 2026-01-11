# Migration Plan: datamodel-code-generator Integration

**Status**: Ready to implement
**Decision**: STRONG GO
**Date**: 2026-01-11

## Executive Summary

Replace the current openapi-python-client generated code with datamodel-code-generator models. This eliminates the complex patching workflow and provides native Pydantic v2 models with full field constraints.

### Key Benefits

| Before (openapi-python-client) | After (datamodel-code-generator) |
|-------------------------------|----------------------------------|
| Requires `patch-openapi.py` (400+ lines) | No patching needed |
| attrs-based models | Native Pydantic v2 |
| No field constraints | Full `Field(ge=, le=, min_length=)` |
| Complex regeneration workflow | Simple one-command regeneration |
| Hand-written models duplicate spec | Hand-written extends generated |

## Phase 0: Establish Baseline (Before Any Changes)

Given low unit test coverage, **live API testing is our primary safety net**.

### 0.1 Run live tests and capture baseline

Before changing ANY code:

```bash
# Run full live test suite and save output
/live-test 2>&1 | tee .claude/docs/pre-migration-baseline.log
```

### 0.2 Document current state

Create `.claude/docs/pre-migration-baseline.md` documenting:

| Resource | CRUD Works? | Builders Work? | Notes |
|----------|-------------|----------------|-------|
| Columns | ? | N/A | |
| Datasets | ? | N/A | |
| Markers | ? | N/A | |
| Recipients | ? | N/A | |
| SLOs | ? | ? | |
| Triggers | ? | ? | |
| Queries | ? | N/A | create/run |
| Boards | ? | ? | |

### 0.3 Create serialization snapshot tests

Create `tests/unit/test_serialization_snapshots.py` to capture "golden" payloads BEFORE migration:

```python
"""Ensure migrated models produce identical API payloads.

These tests capture the CURRENT serialization behavior. After migration,
models must produce identical output to avoid breaking API compatibility.
"""
import pytest
from honeycomb.models.triggers import TriggerCreate
from honeycomb.models.slos import SLOCreate
# ... etc

class TestTriggerSerialization:
    """Trigger serialization must not change after migration."""

    def test_basic_trigger_payload(self):
        trigger = TriggerCreate(
            name="Test",
            query=QuerySpec(...),
            threshold=Threshold(op=">", value=100),
            frequency=300,
        )
        payload = trigger.model_dump(exclude_unset=True, by_alias=True)
        # Snapshot the exact structure
        assert payload == {
            "name": "Test",
            "query": {...},
            "threshold": {"op": ">", "value": 100},
            "frequency": 300,
        }

    def test_builder_produces_same_payload(self):
        trigger = TriggerCreate.builder()...build()
        payload = trigger.model_dump_for_api()
        # Must match expected structure
        ...
```

**Phase 0 exit criteria:**
- [ ] Live test baseline captured
- [ ] Current state documented
- [ ] Serialization snapshot tests written and passing

## Phase 1: Generation Infrastructure

### 1.0 Remove unused generated code

The `src/honeycomb/_generated/` directory (from openapi-python-client) is not used. Delete it:

```bash
rm -rf src/honeycomb/_generated/
```

### 1.1 Create generation script

**File**: `scripts/generate_models.sh`

```bash
#!/bin/bash
set -e

# Generate Pydantic v2 models from Honeycomb OpenAPI spec
# Usage: ./scripts/generate_models.sh [--fetch]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

SPEC_FILE="$PROJECT_ROOT/api.yaml"
OUTPUT_FILE="$PROJECT_ROOT/src/honeycomb/_generated_models.py"

# Optionally fetch fresh spec
if [[ "$1" == "--fetch" ]]; then
    echo "Fetching fresh OpenAPI spec..."
    curl -sS -o "$SPEC_FILE" https://api.honeycomb.io/api.yaml
    echo "Spec downloaded: $(wc -c < "$SPEC_FILE" | tr -d ' ') bytes"
fi

echo "Generating models from $SPEC_FILE..."

datamodel-codegen \
  --input "$SPEC_FILE" \
  --input-file-type openapi \
  --output "$OUTPUT_FILE" \
  --output-model-type pydantic_v2.BaseModel \
  --use-schema-description \
  --field-constraints \
  --use-double-quotes \
  --target-python-version 3.10 \
  --collapse-root-models \
  --reuse-model \
  --use-default-kwarg \
  --disable-timestamp

echo "Generated: $OUTPUT_FILE"
echo "  $(grep -c '^class ' "$OUTPUT_FILE") models"
echo "  $(wc -l < "$OUTPUT_FILE" | tr -d ' ') lines"
```

### 1.2 Add Makefile targets

```makefile
# In Makefile

generate-models:
	@./scripts/generate_models.sh

generate-models-fresh:
	@./scripts/generate_models.sh --fetch

check-models-sync:
	@echo "Checking if generated models are in sync..."
	@./scripts/generate_models.sh
	@git diff --exit-code src/honeycomb/_generated_models.py || \
		(echo "ERROR: Generated models out of sync! Run 'make generate-models'" && exit 1)
	@echo "Models are in sync."
```

### 1.3 Update CI workflow

Add to `.github/workflows/ci.yml`:

```yaml
- name: Check generated models sync
  run: make check-models-sync
```

## Phase 2: Initial Generation

### 2.1 Generate models

```bash
# Make script executable
chmod +x scripts/generate_models.sh

# Generate (using existing api.yaml)
./scripts/generate_models.sh
```

### 2.2 Verify generation

```bash
# Syntax check
poetry run python -m py_compile src/honeycomb/_generated_models.py

# Import check
poetry run python -c "from honeycomb._generated_models import *; print('OK')"

# Count models
grep -c '^class ' src/honeycomb/_generated_models.py
# Expected: ~282 models
```

### 2.3 Confirm mypy exclusion works

The project already has this configured:

```toml
# pyproject.toml
[[tool.mypy.overrides]]
module = "honeycomb._generated.*"
ignore_errors = true
```

Verify with:
```bash
poetry run mypy src/honeycomb/
# Should pass without errors from _generated_models.py
```

## Phase 3: Model Migration Strategy

### 3.1 Identify models to migrate

Current hand-written models in `src/honeycomb/models/`:

| Model | File | Priority | Notes |
|-------|------|----------|-------|
| Query/QuerySpec | queries.py | High | Complex, many fields |
| Trigger | triggers.py | High | Uses builders |
| SLO | slos.py | High | Uses builders |
| Board | boards.py | Medium | Complex nested structure |
| Column | columns.py | Medium | Simple CRUD |
| Dataset | datasets.py | Medium | Simple |
| Marker | markers.py | Low | Simple |
| Recipient | recipients.py | Low | Simple |

### 3.2 Migration pattern

**Before** (hand-written from scratch):
```python
# src/honeycomb/models/slos.py
class SLO(BaseModel):
    id: str | None = None
    name: str = Field(description="...")
    sli: SLI = Field(description="...")
    # ... manually maintained fields

    def model_dump_for_api(self) -> dict[str, Any]:
        # Custom serialization
        ...
```

**After** (extending generated base):
```python
# src/honeycomb/models/slos.py
from honeycomb._generated_models import SLO as _SLOGenerated

class SLO(_SLOGenerated):
    """SLO with custom methods for API interaction."""

    def model_dump_for_api(self) -> dict[str, Any]:
        """Custom serialization for API requests."""
        ...

    @classmethod
    def builder(cls) -> SLOBuilder:
        """Fluent builder interface."""
        return SLOBuilder()
```

### 3.3 Handle naming conflicts

The generated models may have different names than our hand-written ones:

| Our Name | Generated Name | Resolution |
|----------|---------------|------------|
| SLO | SLO | Match |
| SLI | Sli1 | Alias in import |
| Query | Query | Match |
| QuerySpec | QuerySpec | Match |
| Trigger | BaseTrigger / Trigger | Check which to extend |

Mapping will be documented as we migrate each model.

## Phase 4: Incremental Migration

### 4.1 Migration order

1. **Columns** (simplest, good test case)
2. **Datasets** (simple, few custom methods)
3. **Markers** (simple)
4. **Recipients** (simple)
5. **SLOs** (has builders, good test of pattern)
6. **Triggers** (has builders)
7. **Queries** (most complex)
8. **Boards** (complex nested structure)

### 4.2 Per-model migration checklist

For each model:

- [ ] Identify generated base class name in `_generated_models.py`
- [ ] Update import to extend generated base
- [ ] Remove duplicate field definitions (keep only custom fields if any)
- [ ] Keep custom methods (builders, model_dump_for_api, etc.)
- [ ] Verify serialization snapshot test passes
- [ ] Run unit tests: `make test`
- [ ] Run lint/typecheck: `make check`
- [ ] **GATE: Run live tests for this resource** - Must pass before proceeding

### 4.3 Validation gate per model

```bash
# After each model migration - ALL must pass before proceeding
make test                           # Unit tests
make check                          # Lint + typecheck
/live-test --resource <resource>    # Live API validation

# Example for Columns migration:
/live-test --resource columns
```

**Do NOT proceed to next model if live tests fail.** Fix issues first.

## Phase 5: Cleanup

### 5.1 Files to remove

After all models migrated and tests pass:

- [ ] `scripts/patch-openapi.py` - No longer needed
- [ ] `.claude/docs/openapi-spec-updates.md` - Obsolete workflow

### 5.2 Files to update

- [ ] `Makefile` - Remove old generation targets, add new ones
- [ ] `CLAUDE.md` - Update regeneration instructions
- [ ] `README.md` - Update if mentions generated code
- [ ] `pyproject.toml` - Remove openapi-python-client if not needed elsewhere

## Phase 6: Documentation

### 6.1 Update CLAUDE.md

Add section:

```markdown
### Generated Models

Models are generated from the OpenAPI spec using datamodel-code-generator:

```bash
# Regenerate models (uses existing api.yaml)
make generate-models

# Fetch fresh spec and regenerate
make generate-models-fresh
```

**Never edit `src/honeycomb/_generated_models.py`** - it's auto-generated.

Hand-written models in `src/honeycomb/models/` extend the generated bases
and add custom logic (builders, serialization methods, etc.).
```

### 6.2 Add header to generated file

The generated file should have a clear header (datamodel-codegen adds one automatically):

```python
# generated by datamodel-codegen:
#   filename:  api.yaml
#   version:   0.52.2

# DO NOT EDIT - This file is auto-generated from the Honeycomb OpenAPI spec.
# To regenerate: make generate-models
# To update spec: make generate-models-fresh
```

## Phase 7: Final Validation

By this point, each model has already been validated via live tests in Phase 4. This phase is the final comprehensive check.

### 7.1 Full CI pipeline

```bash
make ci  # format, lint, typecheck, all tests
```

### 7.2 Full live API test suite

```bash
/live-test  # All resources, not just individual ones
```

### 7.3 Compare to baseline

```bash
# Compare live test results to pre-migration baseline
# Any regressions should have been caught in Phase 4, but verify:
diff .claude/docs/pre-migration-baseline.log <(make live-test 2>&1)
```

### 7.4 Final checklist

- [ ] All serialization snapshot tests pass
- [ ] All unit tests pass
- [ ] All live tests pass (same or better than baseline)
- [ ] No regressions from Phase 0 baseline
- [ ] CI pipeline green

## Implementation Sequence

| Phase | Description | Gate |
|-------|-------------|------|
| Phase 0 | Establish baseline | Live tests captured, snapshot tests written |
| Phase 1 | Generation infrastructure | Script works, generates valid models |
| Phase 2 | Initial generation | Models import and typecheck |
| Phase 3 | Migration strategy | Name mapping documented |
| Phase 4 | Incremental migration | Each model passes live tests before next |
| Phase 5 | Cleanup | Old files removed |
| Phase 6 | Documentation | CLAUDE.md updated |
| Phase 7 | Final validation | All tests match or exceed baseline |

## Rollback Plan

If issues are found after migration:

1. Generated models are additive - old code still works
2. Can revert individual model migrations independently
3. Keep old patch-openapi.py until fully validated
4. Git history preserves all previous states

## Success Criteria

- [ ] All unit tests pass
- [ ] All live tests pass
- [ ] CI pipeline passes
- [ ] No patching scripts needed
- [ ] Regeneration is single command
- [ ] Documentation updated
- [ ] CLAUDE.md reflects new workflow

## Notes

- **mypy errors**: 26 errors in generated code are expected and excluded via pyproject.toml
- **Single file**: All 282 models in one file (split mode creates confusing numbered files)
- **Deterministic**: `--disable-timestamp` ensures clean git diffs
- **No breaking changes**: Public API unchanged - only internal model inheritance changes
