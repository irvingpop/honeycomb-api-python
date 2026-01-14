# OpenAPI Spec Patches

This package contains patches applied to the Honeycomb OpenAPI spec before model generation.
These patches ensure `datamodel-code-generator` produces clean, usable Python class names.

## Why Patches Are Needed

The Honeycomb API spec has several patterns that cause `datamodel-code-generator` to generate
suboptimal class names:

1. **Inline schemas without titles** - Generate numbered names like `Type1`, `Details1`
2. **Operator symbols in enums** - Generate unusable names like `field_` for `=`
3. **Incorrect field requirements** - Don't match actual API behavior
4. **Validation pattern mismatches** - Regex patterns that don't match real API keys

## Patch Categories

### Title Patches (`title_patches.py`)

Add `title` fields to inline schemas so `--use-title-as-name` works correctly.

| Patch | Problem | Solution |
|-------|---------|----------|
| `CreateColumnTypeTitlePatch` | Column type enum unnamed | Add title `ColumnType` |
| `RecipientDetailsTitlePatch` | Recipient details unnamed | Add `{Type}RecipientDetails` titles |
| `RecipientDetailsAdditionalPropertiesPatch` | LLMs hallucinate extra fields | Add `additionalProperties: false` |
| `UpdateBudgetRateBurnAlertTitlePatch` | Title conflicts with another schema | Change to `UpdateBudgetRateBurnAlert` |
| `BoardViewFilterOperationTitlePatch` | Filter operation enum unnamed | Add title `BoardViewFilterOperation` |
| `ApiKeyRequestTitlesPatch` | Request schema titles conflict | Change to `*Update` variants |

### Enum Patches (`enum_patches.py`)

Add `x-enum-varnames` for readable enum member names.

| Patch | Problem | Solution |
|-------|---------|----------|
| `FilterOpEnumPatch` | `=` becomes `field_` | Add `EQUALS`, `NOT_EQUALS`, etc. |
| `HavingOpEnumPatch` | Same as FilterOp subset | Add readable comparison names |
| `TriggerThresholdOpEnumPatch` | Trigger ops unnamed | Add `GREATER_THAN`, etc. |
| `BoardViewFilterOperationEnumPatch` | Board filter ops unnamed | Same as FilterOp |

### Field Patches (`field_patches.py`)

Fix field requirements, patterns, and defaults.

| Patch | Problem | Solution |
|-------|---------|----------|
| `DatasetUpdatePayloadOptionalPatch` | All fields required | Remove `required` for partial updates |
| `BatchEventDataRequiredPatch` | `data` not required | Add to required (can't send empty event) |
| `BurnAlertRecipientsOptionalPatch` | Recipients required in builders | Make optional for testing/builders |
| `QueryDefaultsPatch` | Bogus timestamp defaults | Remove example values used as defaults |
| `ApiKeyIdPatternsPatch` | `hcxik_` pattern wrong | Fix to `hc[a-z]ik_` for real keys |

### Schema Extraction Patches (`schema_extraction.py`)

Extract inline schemas from `allOf` patterns to named schemas.

| Patch | Problem | Solution |
|-------|---------|----------|
| `ApiKeySecretExtractionPatch` | Inline secret in allOf | Extract to `ApiKeySecret` |
| `BurnAlertListSloExtractionPatch` | Inline slo in list responses | Extract to `BurnAlertListSlo` |
| `BurnAlertDetailRecipientsExtractionPatch` | Inline recipients in detail responses | Extract to `BurnAlertDetailRecipients` |

### Discriminator Restructuring Patches (`discriminator_restructuring.py`)

Restructure nested `allOf(oneOf)` patterns to clean `oneOf` discriminators.

| Patch | Problem | Before | After |
|-------|---------|--------|-------|
| `ApiKeyCreateAttributesRestructuringPatch` | Nested allOf wrapping oneOf discriminator | `AttributesAttributes`, `AttributesAttributes1` | `IngestKeyCreateAttributes`, `ConfigurationKeyCreateAttributes` |

## Remaining Numbered Classes

After all patches, only 5 numbered enum classes remain:

| Class | Cause | Status |
|-------|-------|--------|
| `Type1`-`Type5` | Duplicate recipient type enums in response schemas | **Dead code** - Not referenced anywhere |

These are harmless dead code that can be ignored. They could be eliminated with:
1. Post-processing to remove unused classes
2. Upstream spec fix to use shared RecipientType enum
3. Datamodel-codegen improvement to detect duplicate enums

## Classes Fixed

The following numbered classes have been **eliminated** and replaced with clean names:

| Old Name | New Name | Notes |
|----------|----------|-------|
| `AttributesAttributes` | `IngestKeyCreateAttributes` | API key create with secret |
| `AttributesAttributes1` | `ConfigurationKeyCreateAttributes` | Config key create with secret |
| `BudgetRate1` | `BudgetRateListResponse` | Budget rate alert list response |
| `ExhaustionTime1` | `ExhaustionTimeDetailResponse` | Exhaustion time alert detail response |

## Adding New Patches

1. Identify the problematic schema in `api.yaml`
2. Choose the appropriate patch category
3. Create a new class inheriting from `BasePatch`:

```python
class MyPatch(BasePatch):
    name = "Human-readable name"
    description = "What this patch does"

    def applies_to(self, spec: dict[str, Any]) -> bool:
        """Return True if this patch should be applied."""
        schemas = get_schemas(spec)
        return "MySchema" in schemas

    def apply(self, spec: dict[str, Any]) -> int:
        """Apply the patch, return number of changes."""
        schemas = get_schemas(spec)
        # Make changes...
        print(f"  [check] Applied my patch")
        return 1
```

4. Add the patch instance to the module's `*_PATCHES` list
5. Add a test case in `tests/unit/test_openapi_patches.py`

## Usage

The patches are applied automatically by `scripts/generate_models.sh`:

```bash
make generate-models        # Apply patches and regenerate
make generate-models-fresh  # Fetch fresh spec first
```

To apply patches manually:

```bash
poetry run python scripts/patch_openapi_spec.py api.yaml .api-patched.yaml
```
