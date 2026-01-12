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

**Core Dataset Resources** (originally planned):

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

**Additional Resources** (discovered during Phase 3):

| Model | File | Priority | Notes |
|-------|------|----------|-------|
| BurnAlert | burn_alerts.py | Medium | SLO burn alerts |
| DerivedColumn | derived_columns.py | Medium | Calculated fields |
| QueryAnnotation | query_annotations.py | Medium | Query annotations |
| Event | events.py | Low | Event sending (BatchEvent) |
| ServiceMapDependency | service_map_dependencies.py | Low | Service map |
| ApiKey | api_keys.py | Low | Management API |
| Environment | environments.py | Low | Management API |
| Auth | auth.py | Low | Response-only, no Create |

**Utility Models** (may not need migration):

| Model | File | Notes |
|-------|------|-------|
| Tool Inputs | tool_inputs.py | PositionInput, ChartSettings, etc. - used internally |
| Tags Mixin | tags_mixin.py | Mixin class for tags |
| Builders | *_builder.py | Keep separate from models |

**Total**: 16 main model files + 8 additional resources = 24 model files to evaluate

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

### 3.3 Generated Model Name Mapping

**Phase 2 Complete**: Generated 285 models successfully.

Mapping of hand-written models to generated base classes:

| Our Model | Generated Base | Type | Notes |
|-----------|---------------|------|-------|
| **ColumnCreate** | CreateColumn | Create | Direct extend |
| **Column** | Column | Response | Extends CreateColumn in generated |
| **DatasetCreate** | DatasetCreationPayload | Create | Different name |
| **Dataset** | Dataset | Response | Direct extend |
| **MarkerCreate** | MarkerCreateRequest | Create | Wrapped in Data13 structure - needs investigation |
| **Marker** | Marker | Response | Direct extend |
| **RecipientCreate** | Complex | Create | Discriminated union per type (Email/Slack/etc) |
| **Recipient** | Recipient | Response | RootModel discriminated union |
| **TriggerCreate** | CreateTriggerRequest | Create | RootModel union of TriggerWithInlineQuery \| TriggerWithQueryReference |
| **Trigger** | TriggerResponse | Response | Extends both inline and reference variants |
| **SLOCreate** | SLOCreate | Create | ✓ EXACT MATCH |
| **SLO** | SLO | Response | ✓ EXACT MATCH |
| **QuerySpec** | Query | Create | Different name |
| **BoardCreate** | Board | Create/Response | Same model for both (has optional id/links) |

**Additional Resources**:

| Our Model | Generated Base | Type | Notes |
|-----------|---------------|------|-------|
| **BurnAlertCreate** | CreateExhaustionTimeBurnAlertRequest / CreateBudgetRateBurnAlertRequest | Create | Discriminated union by alert_type |
| **BurnAlert** | ExhaustionTimeBurnAlert / BudgetRateBurnAlert | Response | Discriminated union |
| **DerivedColumnCreate** | CalculatedField (no Create variant) | Create | May need wrapper |
| **DerivedColumn** | CalculatedField | Response | Direct extend |
| **QueryAnnotationCreate** | QueryAnnotation (no Create variant) | Create | May need wrapper |
| **QueryAnnotation** | QueryAnnotation | Response | Same model for create+response |
| **ApiKeyCreate** | ApiKeyCreateRequest | Create | Direct extend |
| **ApiKey** | ApiKeyAccess | Response | Different name |
| **EnvironmentCreate** | CreateEnvironmentRequest | Create | Direct extend |
| **Environment** | Environment | Response | Direct extend |
| **BatchEvent** | BatchEvent | Input | ✓ EXACT MATCH |
| **ServiceMapDependencyRequestCreate** | CreateMapDependenciesRequest | Create | Direct extend |

**Key Findings**:
- **Perfect matches**: SLO, BatchEvent ✓
- Most Create models have different naming conventions (CreateX vs XCreate)
- Some models use discriminated unions (Trigger, Recipient, BurnAlert)
- Marker uses nested Data structure
- Board/QueryAnnotation use single model for create+response
- **Total models found**: 24 resources (16 original + 8 additional)

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

## Phase 4 Progress

**Core Resources (4/8 complete)**:
- ✓ Columns, Datasets, Markers, Recipients
- Pending: SLOs, Triggers, Queries, Boards

**Additional Resources (6/8 complete)**:
- ✓ Events, Auth, ApiKeys, Environments, BurnAlerts (refactored properly), DerivedColumns
- Pending: QueryAnnotations, ServiceMapDependencies

**Total: 10/16 resources migrated**

---

## Phase 4: Model Migration Details

### 4.1 Columns - COMPLETED ✓

**Date**: 2026-01-11

#### Final Implementation

**File**: [src/honeycomb/models/columns.py](../../src/honeycomb/models/columns.py) - **22 lines** (down from 60)

```python
from honeycomb._generated_models import Column as _ColumnGenerated
from honeycomb._generated_models import CreateColumn as _CreateColumnGenerated
from honeycomb._generated_models import CreateColumnColumnType

ColumnType = CreateColumnColumnType  # Re-export generated enum

class ColumnCreate(_CreateColumnGenerated):
    pass

class Column(_ColumnGenerated):
    pass
```

**That's it!** No custom fields, no custom serialization, just extends and re-exports.

#### Solution Path

**Problem Discovered**: 88 auto-generated numbered classes (Type1, Data1, etc.)

**Solution Applied**:
1. ✓ Patch api.yaml with `title:` fields for inline schemas ([patch_api_yaml_for_dmcg.py](../../scripts/patch_api_yaml_for_dmcg.py))
2. ✓ Use `--naming-strategy full-path` flag
3. ✓ Use `--use-title-as-name` flag
4. ✓ **Result**: 88 → 5 unused numbered classes (94% reduction)

**Patches Applied**:
- `CreateColumn.type` → Title: "ColumnType" → Generated as `CreateColumnColumnType`
- 6 recipient `details` objects → Titles added → Generated as `{Type}RecipientDetails`

#### Decisions Made

**1. Use Generated Enums Directly** (Breaking Change Accepted)
- Changed: `ColumnType.STRING` → `ColumnType.string` (lowercase)
- Rationale: Pre-1.0 version, breaking changes allowed per CLAUDE.md
- Updated: 8 usages (7 tests, 1 CLI)

**2. Remove `model_dump_for_api()`**
- Use Pydantic's `model_dump(mode="json", exclude_none=True)` instead
- Rationale: Generated models serialize correctly, no custom logic needed
- Simpler, less code to maintain

**3. Fully Extend Generated Models**
- No field overrides, no custom logic
- Just thin wrappers for documentation and future extensibility

#### Validation Passed

- ✓ 937/937 unit tests pass
- ✓ 4/4 column serialization snapshot tests pass
- ✓ Mypy clean
- ✓ Live API test passed (create + delete)
- ✓ Code reduced from 60 → 22 lines (63% reduction)

#### Scope of Auto-Generated Name Problem

**⚠️ MAJOR DISCOVERY**: The problem is much larger than just enums!

**Total auto-generated numbered classes**: **88 classes**

| Pattern | Count | Examples | Impact |
|---------|-------|----------|--------|
| **Type** | 19 | Type1 (ColumnType), Type8-12 (RecipientType × 5) | **HIGH** - Enums |
| **Attributes** | 17 | Attributes1-17 (nested attribute objects) | **HIGH** - Nested models |
| **Data** | 15 | Data1-15 (wrapper objects) | **HIGH** - Request wrappers |
| **Links** | 6 | Links1-6 (HAL/HATEOAS links) | Medium |
| **Details** | 5 | Details1-5 (recipient details?) | Medium |
| **Relationships** | 4 | Relationships1-4 (JSONAPI relationships) | Medium |
| **Status** | 2 | Status1-2 | Low |
| Others | 20 | Slo1-3, Settings1-2, Dataset1, etc. | Low-Medium |

**Critical Issues**:
1. RecipientType duplicated as Type8-12 (5 times!)
2. 15 Data wrapper objects (Data1-15)
3. 17 Attributes objects (Attributes1-17)
4. **Total**: 88 unstable class names across entire codebase

**Root Cause**: OpenAPI spec uses inline/anonymous schema definitions without titles. When datamodel-codegen encounters these, it auto-generates numbered names.

#### Solution Found! 🎉

**datamodel-codegen has `--naming-strategy full-path` flag!**

Discovered via [Issue #2822](https://github.com/koxudaxi/datamodel-code-generator/issues/2822) and [Issue #796](https://github.com/koxudaxi/datamodel-code-generator/issues/796).

**Test Results**:

| Metric | Without flag | With `--naming-strategy full-path` | Improvement |
|--------|-------------|-----------------------------------|-------------|
| **Auto-numbered classes** | 88 | 12 | **86% reduction!** |
| **Type1-19 enums** | 19 | 5 (Type1-5 for RecipientType variants) | **74% reduction** |
| **Data1-15 wrappers** | 15 | 0 | **100% eliminated!** |
| **Attributes1-17** | 17 | 0 | **100% eliminated!** |
| **Links1-6** | 6 | 0 | **100% eliminated!** |

**Combined with patching**, we achieved even better results:

| Improvement | Before | After |
|-------------|--------|-------|
| Numbered classes | 88 | 5 (unused) |
| Details1-5 | 5 | 0 (now PagerDutyRecipientDetails, etc.) |
| Type1 for ColumnType | Yes | No (now CreateColumnColumnType) |

**Examples of improved names**:
- Type1 → **CreateColumnColumnType** ✓
- Details1 → **PagerDutyRecipientDetails** ✓
- Data13 → **UpdatePipelineConfigurationRolloutRequestData** ✓
- Attributes7 → **CreatePipelineHealthRecordRequestDataAttributes** ✓

**Remaining 5 numbered classes** (Type1-5): Unused dead code - RecipientType duplicates that are never referenced. Safe to ignore.

### 4.2 Datasets - COMPLETED ✓

**Date**: 2026-01-11

**File**: [src/honeycomb/models/datasets.py](../../src/honeycomb/models/datasets.py) - **35 lines** (down from 94, 63% reduction)

#### Key Discovery: Verify Against Live API, Not Tests

**Problem Found**: Spec says `DatasetUpdatePayload` has `required: ["description", "expand_json_depth"]`

**Live API Test** (using curl):
```bash
# Partial update with ONLY description works!
curl -X PUT .../datasets/slug -d '{"description": "Updated"}'
# ✓ API accepts it (spec was wrong)
```

**Solution**: Patched spec to remove `required` from DatasetUpdatePayload

**Result**: Fully vanilla models, no custom serialization needed
- `DatasetCreate` → extends `DatasetCreationPayload` (pass only)
- `DatasetUpdate` → extends `DatasetUpdatePayload` (one field description override for tools)
- `Dataset` → extends generated `Dataset` (pass only)

**Updated Resources**: Use API structure directly with `settings: {delete_protected: bool}`
- Removed custom `model_dump_for_api()` with flat delete_protected
- Use `DatasetUpdatePayloadSettings` as API expects

**Validation**: ✓ 936/936 unit tests, ✓ Mypy clean, ✓ Live API tested

#### Migration Ground Rules (Updated)

**For all remaining model migrations**:

1. **Test against live API first** - Use `curl` to verify actual API behavior before assuming anything
2. **Patch spec when wrong** - If spec contradicts API (like DatasetUpdate required fields), patch it
3. **Keep models vanilla** - Match API structure exactly, no "convenience" abstractions
4. **Move nice UX to builders** - Flat fields, friendlier interfaces belong in builders or CLI, not base models
5. **Minimal overrides** - Only add field overrides when required (e.g., tool schema descriptions)
6. **Use Pydantic serialization** - `model_dump(mode="json", exclude_none=True, exclude_defaults=True)`
7. **Just pass** - Models should be thin wrappers unless adding custom methods (builders, etc.)

### 4.3 Recipients - COMPLETED ✓

- Re-exported discriminated union structure (6 types)
- Added `get_recipient_class()` helper
- extra="forbid" patch for LLM validation

#### Migration Pattern

```python
# Step 1: Find generated model names
grep "^class.*Foo" src/honeycomb/_generated_models.py

# Step 2: Test live API with curl (verify behavior)
curl -X POST .../resource -d '{"field": "value"}'

# Step 3: Implement
from honeycomb._generated_models import FooCreate as _FooCreateGenerated
from honeycomb._generated_models import FooEnum

FooEnum = FooEnum  # Re-export if needed

class FooCreate(_FooCreateGenerated):
    pass  # Or add builders/custom methods only
```

## Final Infrastructure

**Generation Workflow**:
1. `api.yaml` (source spec from Honeycomb)
2. → `patch_api_yaml_for_dmcg.py` (8 patches applied)
3. → `.api-patched.yaml` (temporary, gitignored)
4. → `datamodel-codegen` with flags
5. → `src/honeycomb/_generated_models.py` (288 models)

**Patches Applied** (14 total):
1. `CreateColumn.type` → Title: "ColumnType"
2-7. Recipient `details` → Titles: "PagerDutyRecipientDetails", etc. (6 patches)
8. `DatasetUpdatePayload` → Remove `required` (spec bug: UPDATE should allow partial)
9-14. Recipient `details` → additionalProperties: false (6 patches for LLM validation)

**Key Flags**:
- `--naming-strategy full-path` - Parent-prefixed names
- `--use-title-as-name` - Use title fields for class names
- `--formatters ruff-format ruff-check` - Consistent formatting

**Result**:
- 88 numbered classes → 5 unused dead code
- Stable, semantic class names (CreateColumnColumnType, PagerDutyRecipientDetails, etc.)
- Single command: `make generate-models`

## Notes

- **mypy errors**: 26 errors in generated code are expected and excluded via pyproject.toml
- **Single file**: All 288 models in one file (split mode creates confusing numbered files)
- **Deterministic**: `--disable-timestamp` + stable naming ensures clean git diffs
- **Breaking changes**: Enum names changed to lowercase (ColumnType.string vs STRING) - acceptable pre-1.0
- **No custom serialization**: Use Pydantic's `model_dump(mode="json", exclude_none=True)`
- **Minimal wrappers**: Models are just `pass` statements unless custom methods needed
