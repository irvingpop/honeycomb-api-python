# Trigger Builder API Alignment Analysis

**Date**: 2026-01-08
**Analysis**: Comparison of hand-written trigger_builder.py models against OpenAPI spec

## Summary

⚠️ **2 missing features identified**:
1. **evaluation_schedule_type** - API supports time-window evaluation scheduling
2. **evaluation_schedule** - API supports restricting when triggers run (days of week + time window)

✅ **All core features present**:
- Threshold configuration (op, value, exceeded_limit)
- Alert types (on_change, on_true)
- Frequency configuration
- Baseline details for dynamic thresholds
- Tags support
- Recipients integration

---

## Detailed Comparison

### 1. TriggerCreate Model

| Property | Hand-Written | Generated (OpenAPI) | Status |
|----------|-------------|---------------------|---------|
| `name` | `str` (required) | `str` (optional in API) | ✅ Stricter is fine |
| `description` | `str \| None` (optional) | `Union[Unset, str]` (optional) | ✅ Correct |
| `query` | `TriggerQuery \| None` (optional) | `TriggerWithInlineQueryQuery` (optional) | ✅ Correct |
| `query_id` | `str \| None` (optional) | Not in inline variant | ✅ Correct |
| `threshold` | `TriggerThreshold` (required) | `BaseTriggerThreshold` (optional) | ✅ Stricter is fine |
| `frequency` | `int` (default=900, ge=60, le=86400) | `int` (optional, min=60, max=86400, multipleOf=60, default=900) | ✅ Correct |
| `alert_type` | `TriggerAlertType` (default=ON_CHANGE) | `BaseTriggerAlertType` (default=ON_CHANGE) | ✅ Correct |
| `disabled` | `bool` (default=False) | `bool` (default=False) | ✅ Correct |
| `recipients` | `list[dict] \| None` (optional) | `list[NotificationRecipient]` (optional) | ✅ Correct |
| `tags` | `list[dict[str, str]] \| None` (optional) | `list[Tag]` (optional, max=10) | ✅ Correct |
| `baseline_details` | `dict[str, Any] \| None` (optional) | `BaseTriggerBaselineDetailsType0` (optional) | ✅ Correct |
| `evaluation_schedule_type` | ❌ **Missing** | `BaseTriggerEvaluationScheduleType` (optional) | ❌ **Missing** |
| `evaluation_schedule` | ❌ **Missing** | `BaseTriggerEvaluationSchedule` (optional) | ❌ **Missing** |
| `triggered` | ❌ Not in create model | `bool` (readOnly) | ✅ Correct (response-only) |

**Source**:
- OpenAPI: `api.yaml:7890-8137` (BaseTrigger + TriggerWithInlineQuery)
- Generated: `_generated/models/trigger_with_inline_query.py:34-96`
- Hand-written: `models/triggers.py:102-179`

**Missing Fields Analysis**:

**evaluation_schedule_type** and **evaluation_schedule**:
- Allow restricting when triggers run (e.g., only during business hours, only on weekdays)
- **evaluation_schedule_type**: enum of `frequency` (default) or `window`
- **evaluation_schedule**: object with `window` containing:
  - `days_of_week`: array of weekday names (sunday-saturday)
  - `start_time`: HH:mm UTC format
  - `end_time`: HH:mm UTC format

**Impact**: Users cannot schedule triggers to run only during specific time windows

---

### 2. TriggerQuery Model (Inline Query for Triggers)

| Property | Hand-Written | API Spec | Status |
|----------|-------------|----------|---------|
| `time_range` | `int` (default=900, ge=300, le=3600) | `int` (min=300, max=**3600**) | ✅ Correct |
| `granularity` | `int \| None` (optional) | `int` (optional) | ✅ Correct |
| `calculations` | `list[Calculation]` (default=[COUNT]) | array (optional) | ✅ Correct |
| `filters` | `list[Filter] \| None` (optional) | array (optional) | ✅ Correct |
| `breakdowns` | `list[str] \| None` (optional) | array (optional) | ✅ Correct |
| `filter_combination` | `FilterCombination \| str \| None` | string (optional) | ✅ Correct |

**Source**:
- OpenAPI: `api.yaml:8111-8122` (TriggerWithInlineQuery.query)
- Generated: `_generated/models/trigger_with_inline_query_query.py`
- Hand-written: `models/triggers.py:50-76`

**Key Constraint**: Triggers have **max time_range of 3600 seconds (1 hour)** vs regular queries which have no limit.

**Status**: ✅ Perfect alignment - our model correctly enforces the 3600 second limit

---

### 3. TriggerThreshold Model

| Property | Hand-Written | Generated (OpenAPI) | Status |
|----------|-------------|---------------------|---------|
| `op` | `TriggerThresholdOp` (required) | `BaseTriggerThresholdOp` (required) | ✅ Correct |
| `value` | `float` (required) | `number` (required) | ✅ Correct |
| `exceeded_limit` | `int \| None` (optional) | `int` (optional, min=1, max=5, default=1) | ✅ Correct |

**Source**:
- OpenAPI: `api.yaml:7973-7992`
- Generated: `_generated/models/base_trigger_threshold.py`
- Hand-written: `models/triggers.py:35-42`

**Threshold Operators** (all 4 operators present):
- `>` (GREATER_THAN)
- `>=` (GREATER_THAN_OR_EQUAL)
- `<` (LESS_THAN)
- `<=` (LESS_THAN_OR_EQUAL)

**Status**: ✅ Perfect alignment

---

### 4. TriggerBuilder Methods vs API Features

| API Feature | Builder Method | Status |
|-------------|----------------|---------|
| **Basic Config** | | |
| `name` | `__init__(name)` | ✅ |
| `description` | `.description()` | ✅ |
| `disabled` | `.disabled()` | ✅ |
| **Scope** | | |
| Dataset-scoped | `.dataset()` | ✅ |
| Environment-wide | `.environment_wide()` | ✅ |
| **Query** (via QueryBuilder) | | |
| `time_range` | `.time_range()`, `.last_*()` presets | ✅ |
| `granularity` | `.granularity()` | ✅ |
| `calculations` | `.count()`, `.avg()`, `.p99()`, etc. | ✅ |
| `filters` | `.filter()`, `.where()`, `.where_*()` | ✅ |
| `breakdowns` | `.breakdown()`, `.group_by()` | ✅ |
| `filter_combination` | `.filter_with()` | ✅ |
| **Threshold** | | |
| Comparison threshold | `.threshold_gt()`, `.threshold_gte()`, `.threshold_lt()`, `.threshold_lte()` | ✅ |
| Exceeded limit | `.exceeded_limit(times)` | ✅ |
| **Alert Behavior** | | |
| `alert_type` | `.alert_on_change()`, `.alert_on_true()` | ✅ |
| `frequency` | `.frequency()`, `.every_minute()`, `.every_5_minutes()`, etc. | ✅ |
| **Baseline** | | |
| Baseline comparison | `.baseline_1h()`, `.baseline_1d()`, `.baseline_7d()`, `.baseline_28d()` | ✅ |
| Baseline type | `.baseline_percentage()`, `.baseline_value()` | ✅ |
| **Organization** | | |
| `tags` | `.tag()` (via TagsMixin) | ✅ |
| **Recipients** | | |
| All recipient types | `.email()`, `.slack()`, `.pagerduty()`, etc. (via RecipientMixin) | ✅ |
| **Scheduling** | | |
| `evaluation_schedule_type` | ❌ **Missing** | ❌ **Missing** |
| `evaluation_schedule` | ❌ **Missing** | ❌ **Missing** |

---

### 5. Evaluation Schedule (Missing Feature)

**API Specification** (`api.yaml:7993-8062`):

```yaml
evaluation_schedule_type:
  type: string
  enum: [frequency, window]
  default: frequency
  description: >
    The schedule type used by the trigger.
    - frequency: trigger runs at the specified frequency (default)
    - window: trigger runs at frequency, but only within the time window
             specified in evaluation_schedule

evaluation_schedule:
  type: object
  required:
    - window
  properties:
    window:
      type: object
      required:
        - days_of_week
        - start_time
        - end_time
      properties:
        days_of_week:
          type: array
          items:
            enum: [sunday, monday, tuesday, wednesday, thursday, friday, saturday]
          minItems: 1
          maxItems: 7
          example: [monday, tuesday, wednesday, thursday, friday]
        start_time:
          type: string
          pattern: ^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$
          example: "09:00"
        end_time:
          type: string
          pattern: ^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$
          example: "17:00"
```

**Example Use Case**:
"Only check this trigger during business hours (9am-5pm) on weekdays"

```python
{
  "evaluation_schedule_type": "window",
  "evaluation_schedule": {
    "window": {
      "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
      "start_time": "09:00",
      "end_time": "17:00"
    }
  }
}
```

**Current Implementation**:
- ❌ `TriggerCreate` - does NOT include these fields
- ❌ `TriggerBuilder` - does NOT support scheduling methods
- ✅ `Trigger` (response model) - HAS `evaluation_schedule_type` field (line 203)
- ❌ `Trigger` (response model) - does NOT have `evaluation_schedule` field

**Impact**: Users cannot schedule triggers to run only during specific time windows

---

### 6. Baseline Details

**API Specification** (`api.yaml:8063-8110`):

```yaml
baseline_details: oneOf
  - type: object  # Configuration
    required:
      - offset_minutes
      - type
    properties:
      offset_minutes:
        type: integer
        enum: [60, 1440, 10080, 40320]
        # 60 = 1 hour, 1440 = 1 day, 10080 = 7 days, 40320 = 28 days
      type:
        type: string
        enum: ["percentage", "value"]
        # percentage: (baseline - current) / baseline
        # value: baseline - current
  - type: object  # Empty object {} clears baseline
    properties: {}
```

**Current Implementation**:
- ✅ `TriggerCreate` - HAS `baseline_details: dict[str, Any] | None` (line 125-128)
- ✅ `TriggerBuilder` - HAS baseline methods:
  - `.baseline_1h()`, `.baseline_1d()`, `.baseline_7d()`, `.baseline_28d()`
  - `.baseline_percentage()`, `.baseline_value()`
- ✅ Serialized in `model_dump_for_api()` (line 176-177)

**Status**: ✅ Baseline support is complete and correctly implemented

---

### 7. Trigger Response Model (Trigger)

| Property | Hand-Written | API Spec | Status |
|----------|-------------|----------|---------|
| `id` | ✅ `str` | ✅ `str` (readOnly) | ✅ Correct |
| `name` | ✅ `str` | ✅ `str` | ✅ Correct |
| `description` | ✅ `str \| None` | ✅ `str` (optional) | ✅ Correct |
| `dataset_slug` | ✅ `str` | ✅ `str` (readOnly) | ✅ Correct |
| `threshold` | ✅ `TriggerThreshold` | ✅ `BaseTriggerThreshold` | ✅ Correct |
| `frequency` | ✅ `int` | ✅ `int` | ✅ Correct |
| `query` | ✅ `dict \| None` | ✅ `object` (optional) | ✅ Correct |
| `query_id` | ✅ `str \| None` | ✅ `str` (optional) | ✅ Correct |
| `disabled` | ✅ `bool` | ✅ `bool` | ✅ Correct |
| `triggered` | ✅ `bool` (default=False) | ✅ `bool` (readOnly) | ✅ Correct |
| `alert_type` | ✅ `str` (default="on_change") | ✅ enum (default=ON_CHANGE) | ✅ Correct |
| `recipients` | ✅ `list[dict] \| None` | ✅ `list[NotificationRecipient]` | ✅ Correct |
| `tags` | ✅ `list[dict[str, str]] \| None` | ✅ `list[Tag]` (max=10) | ✅ Correct |
| `baseline_details` | ✅ `dict[str, Any] \| None` | ✅ `BaseTriggerBaselineDetails` | ✅ Correct |
| `evaluation_schedule_type` | ✅ `str \| None` | ✅ enum (frequency\|window) | ✅ Correct |
| `evaluation_schedule` | ❌ **Missing** | ✅ `BaseTriggerEvaluationSchedule` | ⚠️ Accessible via extras |
| `created_at` | ✅ `datetime \| None` | ✅ `datetime` (readOnly) | ✅ Correct |
| `updated_at` | ✅ `datetime \| None` | ✅ `datetime` (readOnly) | ✅ Correct |

**Source**:
- OpenAPI: `api.yaml:7890-8110` (BaseTrigger schema)
- Hand-written: `models/triggers.py:182-212`

**Notes**:
- Response model is complete except `evaluation_schedule`
- `model_config = {"extra": "allow"}` means `evaluation_schedule` IS accessible via dict interface
- Response model correctly includes readOnly fields (`id`, `dataset_slug`, `triggered`)

**Status**: ✅ Response model functional, missing field accessible via extras

---

### 8. TriggerQuery Constraints vs Regular Queries

| Property | TriggerQuery | QuerySpec | Notes |
|----------|--------------|-----------|-------|
| `time_range` | max **3600** (1 hour) | No limit | Trigger-specific constraint |
| `calculations` | Default [COUNT], validated to 1 | Multiple allowed | Trigger limitation |
| `orders` | ❌ Not supported | ✅ Supported | Triggers don't need ordering |
| `limit` | ❌ Not supported | ✅ Supported | Triggers don't need limits |
| `havings` | ❌ Not supported | ✅ Supported | Triggers don't support HAVING |
| `start_time`/`end_time` | ❌ Not supported | ✅ Supported | Triggers use relative time only |

**TriggerBuilder Validation** (`trigger_builder.py:436-442`):
```python
if time_range > 3600:
    raise ValueError(
        "Trigger queries must have time_range <= 3600 seconds (1 hour). "
        f"Got {time_range} seconds. "
        "For longer time ranges, use regular queries, not triggers."
    )
```

**Status**: ✅ Correctly enforced

---

### 9. Threshold Configuration

#### TriggerThresholdOp Enum

| Operator | Hand-Written | Generated (OpenAPI) | Status |
|----------|-------------|---------------------|---------|
| `>` | ✅ GREATER_THAN | ✅ VALUE_0 | ✅ Correct |
| `>=` | ✅ GREATER_THAN_OR_EQUAL | ✅ VALUE_1 | ✅ Correct |
| `<` | ✅ LESS_THAN | ✅ VALUE_2 | ✅ Correct |
| `<=` | ✅ LESS_THAN_OR_EQUAL | ✅ VALUE_3 | ✅ Correct |

**Source**:
- OpenAPI: `api.yaml:7993-8001`
- Generated: `_generated/models/base_trigger_threshold_op.py`
- Hand-written: `models/triggers.py:19-26`

**Status**: ✅ All 4 operators present

#### Exceeded Limit

**API Constraint**: integer, min=1, max=5, default=1
**Our Implementation**: `int | None` (optional), validated 1-5 in builder

**Status**: ✅ Correct (our default is None which becomes API's default of 1)

---

### 10. Baseline Details Schema

**API Structure** (`api.yaml:8063-8110`):

```yaml
baseline_details: oneOf
  - type: object
    required: [offset_minutes, type]
    properties:
      offset_minutes:
        enum: [60, 1440, 10080, 40320]
      type:
        enum: ["percentage", "value"]
  - type: object (empty)  # {} clears baseline
```

**TriggerBuilder Implementation** (`trigger_builder.py:305-390`):

Has 6 helper methods:
- `.baseline_1h()`, `.baseline_1d()`, `.baseline_7d()`, `.baseline_28d()` - Set offset
- `.baseline_percentage()`, `.baseline_value()` - Set comparison type

**Status**: ✅ Full baseline support with validated offset values

---

### 11. Tags Support

**API Specification**: max 10 tags, Tag object with required `key` and `value`

**Current Implementation**:
- ✅ `TriggerCreate` - HAS `tags` field (line 122-124)
- ✅ `TriggerBuilder` - HAS `.tag()` method via `TagsMixin`
- ✅ Serialized in `model_dump_for_api()` (line 173-174)

**Status**: ✅ Tags fully supported

---

### 12. Alert Type and Frequency

#### Alert Type

**API Values**: `on_change` (default) | `on_true`

**Current Implementation**:
- ✅ Enum with both values (triggers.py:28-32)
- ✅ Builder methods: `.alert_on_change()`, `.alert_on_true()` (trigger_builder.py:285-303)

**Status**: ✅ Correct

#### Frequency

**API Constraints**: min=60, max=86400, multipleOf=60, default=900

**Current Implementation**:
- ✅ Default=900 (triggers.py:108-113)
- ✅ Validation ge=60, le=86400 (triggers.py:108-113)
- ⚠️ NOT validating multipleOf=60 (must be divisible by 60)

**Status**: ⚠️ Minor - missing multipleOf=60 validation

---

## Findings Summary

### Missing Features

1. **❌ evaluation_schedule_type and evaluation_schedule**
   - **Impact**: Users cannot restrict triggers to specific time windows (e.g., business hours only)
   - **Location**: `models/triggers.py` (TriggerCreate), `models/trigger_builder.py` (TriggerBuilder)
   - **API Support**: Full support for day-of-week + time-of-day windowing
   - **Priority**: Low - advanced feature, not commonly used

2. **⚠️ frequency multipleOf=60 validation**
   - **Impact**: Users could set invalid frequencies (e.g., 61 seconds)
   - **Location**: `models/triggers.py` TriggerCreate field validator
   - **API Constraint**: Must be multiple of 60
   - **Priority**: Low - API will reject invalid values anyway

### Correctly Implemented Features

1. ✅ **Time range constraint** (max 3600 for triggers)
2. ✅ **Threshold configuration** (op, value, exceeded_limit)
3. ✅ **Alert types** (on_change, on_true)
4. ✅ **Baseline details** (full support with validated offsets)
5. ✅ **Tags support** (via TagsMixin)
6. ✅ **Recipients** (via RecipientMixin)
7. ✅ **All query fields** (calculations, filters, breakdowns, filter_combination)
8. ✅ **Disabled flag**

### Intentional Differences (Good!)

1. **Stricter requirements**: `name` and `threshold` made required (API marks as optional)
   - Makes SDK clearer - these are effectively required for meaningful triggers
2. **Builder pattern**: Extends QueryBuilder with trigger-specific validation
   - Enforces time_range <= 3600
   - Validates frequency 60-86400
   - Validates exceeded_limit 1-5
   - Prevents absolute time ranges (start_time/end_time)
3. **Single calculation**: Builder validates only one calculation (trigger limitation)

---

## Recommendations

### Optional (Low Priority)

1. **Add evaluation_schedule support** (if time-window scheduling is needed)
   ```python
   # models/triggers.py - TriggerCreate
   evaluation_schedule_type: Literal["frequency", "window"] | None = Field(default=None)
   evaluation_schedule: dict[str, Any] | None = Field(default=None)

   # models/trigger_builder.py - TriggerBuilder
   def schedule_window(
       self,
       days_of_week: list[str],
       start_time: str,
       end_time: str
   ) -> Self:
       """Restrict trigger to specific time window."""
       self._evaluation_schedule_type = "window"
       self._evaluation_schedule = {
           "window": {
               "days_of_week": days_of_week,
               "start_time": start_time,
               "end_time": end_time
           }
       }
       return self
   ```

2. **Add frequency multipleOf=60 validation**
   ```python
   # models/triggers.py - TriggerCreate
   @field_validator("frequency")
   @classmethod
   def validate_frequency_multiple(cls, v: int) -> int:
       if v % 60 != 0:
           raise ValueError(f"Frequency must be a multiple of 60, got {v}")
       return v
   ```

3. **Add evaluation_schedule to Trigger response model** (for completeness, already accessible via extras)

---

## Conclusion

The Trigger Builder implementation is **highly complete** with only **2 optional features missing**:

1. **evaluation_schedule** - Time-window scheduling (advanced feature)
2. **frequency multipleOf=60 validation** - Minor validation gap

Both are **low priority** as they're advanced features or API-enforced anyway.

The trigger builder correctly implements:
- ✅ All core trigger functionality
- ✅ Proper time_range constraints (max 3600)
- ✅ Threshold configuration with exceeded_limit
- ✅ Baseline dynamic thresholds
- ✅ Tags and recipients
- ✅ Alert types and frequency

The builder pattern provides excellent UX with strong validation while maintaining full API compatibility.
