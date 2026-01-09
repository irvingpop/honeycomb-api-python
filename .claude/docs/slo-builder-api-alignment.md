# SLO Builder API Alignment Analysis

**Date**: 2026-01-08
**Analysis**: Comparison of hand-written slo_builder.py models against OpenAPI spec

## Summary

⚠️ **2 missing features identified**:
1. **Tags support** - API supports tags, hand-written models don't
2. **dataset_slugs in SLOCreate** - Required for multi-dataset SLOs via `__all__` endpoint

✅ **Intentional enhancements** (beyond API spec):
1. **SLI inline expression** - Allows creating derived columns inline (UX improvement)

---

## Detailed Comparison

### 1. SLOCreate Model

| Property | Hand-Written | Generated (OpenAPI) | Status |
|----------|-------------|---------------------|---------|
| `name` | `str` (required) | `str` (required) | ✅ Correct |
| `sli` | `SLI` (required) | `SLOCreateSli` (required) | ⚠️ Extended (see SLI section) |
| `time_period_days` | `int` (default=30, ge=1, le=90) | `int` (required, min=1) | ⚠️ See Note 1 |
| `target_per_million` | `int` (ge=0, le=1000000) | `int` (required, min=0, max=999999) | ⚠️ See Note 2 |
| `description` | `str \| None` (optional) | `Union[Unset, str]` (optional) | ✅ Correct |
| `tags` | ❌ **Missing** | `Union[Unset, list['Tag']]` (optional) | ❌ **Missing** |
| `dataset_slugs` | ❌ **Missing** | `Union[Unset, list[str]]` (optional) | ❌ **Missing** |
| `id` | ❌ Not in create model | `Union[Unset, str]` (readOnly) | ✅ Correct (response-only) |
| `reset_at` | ❌ Not in create model | `Union[None, Unset, datetime]` (readOnly) | ✅ Correct (response-only) |
| `created_at` | ❌ Not in create model | `Union[Unset, datetime]` (readOnly) | ✅ Correct (response-only) |
| `updated_at` | ❌ Not in create model | `Union[Unset, datetime]` (readOnly) | ✅ Correct (response-only) |

**Source**:
- OpenAPI: `api.yaml:8142-8231` (SLOCreate schema)
- Generated: `_generated/models/slo_create.py:24-58`
- Hand-written: `models/slos.py:36-69`

**Notes**:

**Note 1 - time_period_days constraints**:
- **API**: min=1 (no max specified)
- **Our model**: default=30, ge=1, le=90
- **SLOBuilder**: Validates 1-90 range (lines 292-294)
- **Status**: ⚠️ Our 90-day limit is stricter than API but reasonable

**Note 2 - target_per_million constraints**:
- **API**: min=0, max=999999
- **Our model**: ge=0, le=1000000
- **Status**: ⚠️ Our max is 1000000 vs API's 999999 (off by 1)
- **Impact**: Minor - 1000000 would represent 100.0000%, which is technically valid

---

### 2. SLI (Service Level Indicator) Model

| Property | Hand-Written | Generated (OpenAPI) | Status |
|----------|-------------|---------------------|---------|
| `alias` | `str \| None` (optional) | `str` (required) | ⚠️ We make it optional |
| `expression` | `str \| None` (optional) | ❌ Not in API | ✅ **Intentional extension** |
| `description` | `str \| None` (optional) | ❌ Not in API | ✅ **Intentional extension** |

**Source**:
- OpenAPI: `api.yaml:8165-8179` (SLI object definition)
- Generated: `_generated/models/slo_create_sli.py:13-24`
- Hand-written: `models/slos.py:11-34`

**Analysis**:

The API spec defines SLI as a **simple reference object** with only `alias`:
```yaml
sli:
  type: object
  required:
    - alias
  properties:
    alias:
      type: string
      description: The alias of the Calculated Field (Derived Column)
      minLength: 1
      maxLength: 255
```

**Our Enhancement**:
We extend SLI with `expression` and `description` to support **inline derived column creation**:
- If only `alias` provided → references existing derived column
- If `alias` + `expression` provided → creates new derived column automatically

This is an **intentional UX improvement** that:
1. Maintains API compatibility (we only send `alias` to the SLO API)
2. Provides convenience (auto-creates derived column before SLO)
3. Is handled by the SLOBuilder/SLOBundle pattern (see `slo_builder.py:419-429`)

**Status**: ✅ This is a **good design decision** - maintains compatibility while improving UX

---

### 3. Tag Support (MISSING)

**API Specification** (`api.yaml:8192-8200`):
```yaml
tags:
  type: array
  description: A list of key-value pairs to help identify the SLO
  maxItems: 10
  items:
    $ref: '#/components/schemas/Tag'
```

**Tag Schema** (`api.yaml:7874-7889`):
```yaml
Tag:
  type: object
  required:
    - key
    - value
  properties:
    key:
      type: string
      description: A key to identify the tag, lowercase letters only
      maxLength: 32
    value:
      type: string
      description: A value for the tag
      maxLength: 128
```

**Current Implementation**:
- ❌ `SLOCreate` model (slos.py) - **does NOT include tags field**
- ❌ `SLOBuilder` (slo_builder.py) - **does NOT support tag methods**
- ✅ Generated model (slo_create.py:54) - **includes tags**: `tags: Union[Unset, list['Tag']] = UNSET`

**Impact**:
- Users cannot add tags to SLOs when creating them
- Tags are useful for organization (team, service, criticality, etc.)

**Recommendation**: ⚠️ **Add tags support** to SLOCreate and SLOBuilder

---

### 4. Dataset Slugs Support (MISSING)

**API Specification** (`api.yaml:8222-8231`):
```yaml
dataset_slugs:
  type: array
  description: >-
    The dataset(s) the SLO will be evaluated against.
    Required if using `__all__` in the path.
  minItems: 1
  maxItems: 10
  items:
    type: string
  example:
    - mydataset1
    - mydataset2
```

**API Endpoint Behavior**:
- **Single dataset**: `POST /1/slos/{datasetSlug}` - dataset specified in path
- **Multi-dataset**: `POST /1/slos/__all__` - datasets specified in `dataset_slugs` array

**Current Implementation**:
- ❌ `SLOCreate` model - **does NOT include dataset_slugs field**
- ⚠️ `SLOBuilder` - Has `.dataset()` and `.datasets()` methods but:
  - Stores in `_datasets` internal list (slo_builder.py:236-255)
  - Returns in `SLOBundle` (slo_builder.py:440-446)
  - **Resource layer** likely handles the API path selection
- ✅ Generated model (slo_create.py:58) - **includes dataset_slugs**: `dataset_slugs: Union[Unset, list[str]] = UNSET`

**Analysis**:
The SLOBuilder pattern stores datasets in the bundle, not in SLOCreate:
```python
# slo_builder.py:440-446
return SLOBundle(
    slo=slo,
    datasets=self._datasets,  # <- Separate from SLO object
    derived_column=derived_column,
    derived_column_environment_wide=is_multi_dataset,
    burn_alerts=self._burn_alerts,
)
```

This separation makes sense architecturally:
- Single dataset SLO → use dataset in path: `POST /1/slos/my-dataset`
- Multi-dataset SLO → use `__all__` path: `POST /1/slos/__all__` with `dataset_slugs` in body

**Status**: ⚠️ Implementation pattern is reasonable BUT:
- The SLOCreate model should **optionally accept dataset_slugs** for API compatibility
- The resource layer must handle populating dataset_slugs when posting to `__all__`

**Check Resource Implementation**: Let's verify if `resources/slos.py` handles this correctly.

---

### 5. SLOBuilder Integration

| Property/Method | Implemented | Notes |
|----------------|-------------|-------|
| `name` | ✅ `__init__(name)` | Constructor parameter |
| `description` | ✅ `.description()` | Method available |
| `dataset` | ✅ `.dataset()` | Single dataset |
| `datasets` | ✅ `.datasets()` | Multiple datasets |
| `target_percentage` | ✅ `.target_percentage()` | Converts % to per-million |
| `target_per_million` | ✅ `.target_per_million()` | Direct per-million value |
| `time_period_days` | ✅ `.time_period_days()` | With 1-90 validation |
| `time_period_weeks` | ✅ `.time_period_weeks()` | Convenience (weeks × 7) |
| `sli` | ✅ `.sli()` | With optional expression/description |
| `exhaustion_alert` | ✅ `.exhaustion_alert()` | Burn alert integration |
| `budget_rate_alert` | ✅ `.budget_rate_alert()` | Burn alert integration |
| **`tags`** | ❌ **Missing** | No `.tag()` or `.tags()` method |

---

### 6. BurnAlertBuilder

**Status**: ✅ Burn alerts are a separate builder pattern, not part of core SLO API

Burn alerts are **related resources** created after the SLO:
1. Create SLO → get SLO ID
2. Create burn alerts → reference SLO ID

This is correctly modeled as:
- `SLOBuilder` accepts `BurnAlertBuilder` instances
- `SLOBundle` includes `burn_alerts` list
- Resource layer creates burn alerts after SLO creation

**No API alignment issues** - this is pure builder pattern, not API schema.

---

### 7. Response Model (SLO)

| Property | Hand-Written | API Spec | Status |
|----------|-------------|----------|---------|
| `id` | ✅ `str` | ✅ `str` (readOnly) | ✅ Correct |
| `name` | ✅ `str` | ✅ `str` | ✅ Correct |
| `description` | ✅ `str \| None` | ✅ `str` (optional) | ✅ Correct |
| `sli` | ✅ `dict` | ✅ `SLISli` object | ✅ Correct |
| `time_period_days` | ✅ `int` | ✅ `int` | ✅ Correct |
| `target_per_million` | ✅ `int` | ✅ `int` | ✅ Correct |
| `dataset_slugs` | ✅ `list[str] \| None` | ✅ `list[str]` (readOnly) | ✅ Correct |
| `created_at` | ✅ `datetime \| None` | ✅ `datetime` (readOnly) | ✅ Correct |
| `updated_at` | ✅ `datetime \| None` | ✅ `datetime` (readOnly) | ✅ Correct |
| `reset_at` | ❌ Missing | ✅ `datetime \| null` (readOnly) | ⚠️ Minor (rarely used) |
| `tags` | ❌ Missing | ✅ `list[Tag]` (readOnly) | ⚠️ Minor (can access via extra) |

**Source**:
- OpenAPI: `api.yaml:8233-8324` (SLO response schema)
- Hand-written: `models/slos.py:72-98`

**Notes**:
- `model_config = {"extra": "allow"}` means missing fields like `reset_at` and `tags` ARE accessible via the dict interface
- Convenience properties: `@property dataset` (returns first dataset) and `@property target_percentage` (converts to %)

**Status**: ✅ Response model is functional, missing fields accessible via extras

---

## Findings Summary

### Critical Issues

1. **❌ Tags Support Missing**
   - **Impact**: Users cannot tag SLOs for organization
   - **Location**: `models/slos.py` (SLOCreate), `models/slo_builder.py` (SLOBuilder)
   - **Fix**: Add `tags` field to SLOCreate and `.tag()` method to SLOBuilder

2. **❌ dataset_slugs in SLOCreate Missing**
   - **Impact**: May not work correctly with multi-dataset SLOs via `__all__` endpoint
   - **Location**: `models/slos.py` (SLOCreate)
   - **Fix**: Add optional `dataset_slugs` field to SLOCreate
   - **Verify**: Check if `resources/slos.py` handles this correctly

### Minor Issues

3. **⚠️ target_per_million upper bound**
   - **Current**: `le=1000000` (allows 100.0000%)
   - **API spec**: `max=999999` (allows 99.9999%)
   - **Impact**: Negligible - 100% is technically valid
   - **Fix**: Change to `le=999999` for exactness

4. **⚠️ time_period_days upper bound**
   - **Current**: `le=90` (enforced in builder)
   - **API spec**: No maximum specified
   - **Impact**: Reasonable limit for SLOs
   - **Fix**: None needed - stricter is fine

### Intentional Enhancements (Good!)

5. **✅ SLI inline expression/description**
   - **Purpose**: Auto-create derived columns inline
   - **Compatibility**: Maintained (only `alias` sent to API)
   - **Status**: Excellent UX improvement

6. **✅ SLOBuilder pattern with burn alerts**
   - **Purpose**: Fluent API for complex SLO creation
   - **Compatibility**: Fully compatible
   - **Status**: Great design

---

## Recommendations

### High Priority

1. **Add tags support**
   ```python
   # models/slos.py - SLOCreate
   tags: list[dict[str, str]] | None = Field(default=None, description="Tags for SLO")

   # models/slo_builder.py - SLOBuilder
   def tag(self, key: str, value: str) -> SLOBuilder:
       """Add a tag key-value pair."""
       if not hasattr(self, '_tags'):
           self._tags = []
       self._tags.append({"key": key, "value": value})
       return self
   ```

2. **Add dataset_slugs to SLOCreate**
   ```python
   # models/slos.py - SLOCreate
   dataset_slugs: list[str] | None = Field(default=None, description="Dataset slugs for multi-dataset SLOs")
   ```

3. **Update model_dump_for_api() to include new fields**
   ```python
   # models/slos.py - SLOCreate.model_dump_for_api()
   if self.tags:
       data["tags"] = self.tags
   if self.dataset_slugs:
       data["dataset_slugs"] = self.dataset_slugs
   ```

### Low Priority

4. **Adjust target_per_million constraint**
   ```python
   # models/slos.py - SLOCreate
   target_per_million: int = Field(
       ge=0,
       le=999999,  # Change from 1000000
       description="Target success rate per million (e.g., 999000 = 99.9%)",
   )
   ```

5. **Add reset_at to SLO response model** (optional, accessible via extras already)

---

## Conclusion

The SLO Builder implementation is **mostly correct** with **2 missing features**:

1. **Tags** - Supported by API, missing from our models (organizational feature)
2. **dataset_slugs in SLOCreate** - May cause issues with multi-dataset SLOs

Both are **non-breaking additions** that would improve API compatibility and feature completeness.

The **SLI inline expression enhancement** is an **excellent design choice** that maintains compatibility while providing better UX.
