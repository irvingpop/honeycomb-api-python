# Breaking Changes: DMCG Migration (v0.5.x → v0.6.x)

**Date**: 2026-01-13
**Related**: [2026-01-11-DMCG-migration.md](2026-01-11-DMCG-migration.md)

This document details all breaking changes introduced by the datamodel-code-generator migration.

## Summary

The v0.6.x release migrates from hand-written Pydantic models to generated models from the OpenAPI spec. This provides better API alignment and field validation, but introduces breaking changes in:

1. Enum member naming (UPPERCASE → lowercase) - 7 enums affected
2. Model class renames - 5 models renamed
3. **Model structure changes** - flat → nested objects
   - Auth: `team_name` → `team.name`, `environment_name` → `environment.name`
   - Dataset: `delete_protected` → `settings.delete_protected`
   - BurnAlert: `slo_id` → `slo.id`, `slo` dict → typed object
   - SLO: `sli` dict → typed `SLOSli` object
4. Field type changes (str/dict → typed objects) - Auth.type enum, api_key_access object
5. Nested JSON:API structures - Datasets, Environments, API Keys
6. Removed `model_dump_for_api()` methods - all Create models affected
7. Union types for polymorphic models - Triggers, Recipients, Burn Alerts
8. QuerySpec field types - requires generated types or QueryBuilder

---

## 1. Model & Class Renames

| Before (v0.5.x) | After (v0.6.x) | Notes |
|-----------------|----------------|-------|
| `AuthInfo` | `Auth` | v1 auth response |
| `AuthInfoV2` | `AuthV2Response` | Management key auth |
| `SLI` | `SLOCreateSli` | SLI configuration object |
| `TriggerQuery` | *removed* | Use `QuerySpec` instead |
| `BurnAlertRecipient` | `NotificationRecipient` | Also aliased as `BurnAlertRecipient` |

---

## 2. Enum Member Case Changes (UPPERCASE → lowercase)

All enums now use **lowercase** member names to match API values directly.

### ColumnType

```python
# Before
ColumnType.STRING
ColumnType.INTEGER
ColumnType.FLOAT
ColumnType.BOOLEAN

# After
ColumnType.string
ColumnType.integer
ColumnType.float
ColumnType.boolean
```

### RecipientType

```python
# Before
RecipientType.EMAIL
RecipientType.SLACK
RecipientType.PAGERDUTY
RecipientType.WEBHOOK
RecipientType.MSTEAMS
RecipientType.MSTEAMS_WORKFLOW

# After
RecipientType.email
RecipientType.slack
RecipientType.pagerduty
RecipientType.webhook
RecipientType.msteams
RecipientType.msteams_workflow
```

### TriggerAlertType

```python
# Before
TriggerAlertType.ON_CHANGE
TriggerAlertType.ON_TRUE

# After
TriggerAlertType.on_change
TriggerAlertType.on_true
```

### EnvironmentColor

```python
# Before
EnvironmentColor.BLUE
EnvironmentColor.GREEN
EnvironmentColor.LIGHT_BLUE
EnvironmentColor.LIGHT_GREEN
# etc.

# After
EnvironmentColor.blue
EnvironmentColor.green
EnvironmentColor.lightBlue
EnvironmentColor.lightGreen
# etc.
```

### ServiceMapNodeType

```python
# Before
ServiceMapNodeType.SERVICE

# After
ServiceMapNodeType.service
```

### ServiceMapDependencyRequestStatus

```python
# Before
ServiceMapDependencyRequestStatus.PENDING
ServiceMapDependencyRequestStatus.READY
ServiceMapDependencyRequestStatus.ERROR

# After
ServiceMapDependencyRequestStatus.pending
ServiceMapDependencyRequestStatus.ready
ServiceMapDependencyRequestStatus.error
```

### QueryAnnotationSource

```python
# Before
QueryAnnotationSource.QUERY
QueryAnnotationSource.BOARD

# After
QueryAnnotationSource.query
QueryAnnotationSource.board
```

### Unchanged

`TriggerThresholdOp` remains UPPERCASE:
- `TriggerThresholdOp.GREATER_THAN`
- `TriggerThresholdOp.GREATER_THAN_OR_EQUAL`
- `TriggerThresholdOp.LESS_THAN`
- `TriggerThresholdOp.LESS_THAN_OR_EQUAL`

---

## 3. Auth Model Changes

### Structure Changed: Flat → Nested

The Auth model changed from flat fields to nested objects:

```python
# Before
auth.id
auth.type  # str: "configuration" or "ingest"
auth.team_name
auth.team_slug
auth.environment_name
auth.environment_slug
auth.api_key_access  # dict[str, Any]
auth.time_to_live

# After
auth.id
auth.type  # AuthType enum
auth.team.name
auth.team.slug
auth.environment.name
auth.environment.slug
auth.api_key_access  # AuthApiKeyAccess object
auth.time_to_live
```

### Type Changed: str → Enum

The `type` field is now a typed enum. Direct string comparison no longer works:

```python
# Before (worked)
if auth.type == "configuration":
    ...

# After - BROKEN (comparing enum to str returns False)
if auth.type == "configuration":  # Always False!
    ...

# After - correct approaches
if auth.type.value == "configuration":  # Compare to value
    ...

if auth.type == AuthType.configuration:  # Compare to enum (preferred)
    ...
```

### api_key_access Changed: dict → Typed Object

```python
# Before
auth.api_key_access["events"]
auth.api_key_access["queries"]

# After
auth.api_key_access.events
auth.api_key_access.queries
auth.api_key_access.triggers
# etc.
```

---

## 4. Datasets

### Response Structure Changed: delete_protected → settings.delete_protected

```python
# Before
dataset.delete_protected  # bool - flat field
dataset.expand_json_depth  # int - flat field

# After
dataset.settings.delete_protected  # bool - nested in settings object
dataset.expand_json_depth  # int - still at root level (unchanged)
```

### DatasetUpdate Requires Nested Structure

```python
# Before
update = DatasetUpdate(delete_protected=True)
payload = update.model_dump_for_api()

# After
from honeycomb._generated_models import DatasetUpdatePayloadSettings

update = DatasetUpdate(
    settings=DatasetUpdatePayloadSettings(delete_protected=True)
)
payload = update.model_dump(mode="json", exclude_none=True)
```

---

## 5. Burn Alerts

### Model Structure Changes

| Before | After |
|--------|-------|
| `BurnAlertCreate` (single model) | Union: `CreateExhaustionTimeBurnAlertRequest \| CreateBudgetRateBurnAlertRequest` |
| `BurnAlert` (single model) | `BurnAlertDetailResponse` (RootModel) |
| `BurnAlertRecipient` | `NotificationRecipient` |

### Response Structure Changed: slo_id → slo.id

```python
# Before
burn_alert.slo_id  # str - direct field
burn_alert.slo     # dict | None - SLO details as dict

# After
burn_alert.slo     # ExhaustionTimeBurnAlertListResponseSlo object
burn_alert.slo.id  # str - access via object
```

**Note**: Property accessors hide the RootModel complexity, so `burn_alert.slo` works directly (no need for `.root.slo`).

### Creating Burn Alerts

```python
# Before
alert = BurnAlertCreate(
    alert_type=BurnAlertType.EXHAUSTION_TIME,
    slo_id="slo123",
    exhaustion_minutes=60,
    recipients=[BurnAlertRecipient(id="r1")]
)

# After
from honeycomb.models import (
    CreateExhaustionTimeBurnAlertRequest,
    CreateExhaustionTimeBurnAlertRequestSlo,
    NotificationRecipient,
)

alert = CreateExhaustionTimeBurnAlertRequest(
    slo=CreateExhaustionTimeBurnAlertRequestSlo(id="slo123"),
    exhaustion_minutes=60,
    recipients=[NotificationRecipient(id="r1")]
)
```

**Note**: `BurnAlertType.EXHAUSTION_TIME` still works - the enum has both UPPERCASE and lowercase aliases for backward compatibility.

### Accessing Response Fields

Response models use property accessors to hide RootModel complexity:

```python
# Both work the same
alert.id
alert.alert_type
alert.exhaustion_minutes
```

---

## 6. Boards

### Panel Types

```python
# Before
board = BoardCreate(
    name="My Board",
    panels=[{"type": "query", "query_panel": {...}}]
)

# After
from honeycomb.models import BoardCreate, QueryPanel

board = BoardCreate(
    name="My Board",
    panels=[QueryPanel(type="query", query_panel=...)]
)
```

### BoardViewFilter Operation Enum

```python
# Before
from honeycomb.models import FilterOp
BoardViewFilter(column="status", operation=FilterOp.EQUALS, value="active")

# After
from honeycomb.models import BoardViewFilterOperation
BoardViewFilter(column="status", operation=BoardViewFilterOperation.EQUALS, value="active")
```

---

## 7. Triggers

### TriggerCreate is Now a Union Type

```python
# Before
trigger = TriggerCreate(
    name="High Latency",
    query=TriggerQuery(time_range=3600, calculations=[...]),
    threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100),
    frequency=300,
)

# After - use specific type
from honeycomb.models import TriggerWithInlineQuery, TriggerThreshold, QuerySpec

trigger = TriggerWithInlineQuery(
    name="High Latency",
    query=QuerySpec(time_range=3600, calculations=[...]),
    threshold=TriggerThreshold(op=TriggerThresholdOp.GREATER_THAN, value=100),
    frequency=300,
)
```

### TriggerQuery Removed

Use `QuerySpec` instead of `TriggerQuery`:

```python
# Before
from honeycomb.models import TriggerQuery
query = TriggerQuery(time_range=3600, calculations=[...])

# After
from honeycomb.models import QuerySpec
query = QuerySpec(time_range=3600, calculations=[...])
```

---

## 8. SLOs

### SLI → SLOCreateSli

```python
# Before
from honeycomb.models import SLI
slo = SLOCreate(
    name="API Availability",
    sli=SLI(alias="success_rate"),
    time_period_days=30,
    target_per_million=999000,
)

# After - string alias (recommended, auto-converted)
slo = SLOCreate(
    name="API Availability",
    sli="success_rate",
    time_period_days=30,
    target_per_million=999000,
)

# After - explicit SLOCreateSli
from honeycomb.models import SLOCreateSli
slo = SLOCreate(
    name="API Availability",
    sli=SLOCreateSli(alias="success_rate"),
    time_period_days=30,
    target_per_million=999000,
)
```

### Response Structure Changed: sli from dict → typed object

```python
# Before
slo.sli  # dict like {"alias": "success_rate", "expression": "..."}
slo.sli["alias"]

# After
slo.sli  # SLOSli object
slo.sli.alias
```

---

## 9. API Keys

### ApiKeyType Enum Changed

```python
# Before
ApiKeyType.INGEST
ApiKeyType.CONFIGURATION

# After - enum has different values
ApiKeyType.api_keys  # Single value for JSON:API type field
```

### Creating API Keys

The structure now matches JSON:API format:

```python
# Before
key = ApiKeyCreate(
    name="My Key",
    key_type=ApiKeyType.CONFIGURATION,
    environment_id="env123",
)

# After - use typed key models
from honeycomb.models import (
    ApiKeyCreate,
    ConfigurationKey,
    ConfigurationKeyPermissions,
)
# Structure matches JSON:API - see generated models for full schema
```

### Response Access

Property accessors hide JSON:API nesting:

```python
# Both before and after work the same
key.name
key.key_type
key.environment_id
key.disabled
key.permissions
```

---

## 10. Environments

### EnvironmentColor Enum

```python
# Before
EnvironmentColor.RED
EnvironmentColor.LIGHT_BLUE

# After
EnvironmentColor.red
EnvironmentColor.lightBlue
```

### Creating Environments

```python
# Before
env = EnvironmentCreate(name="Production", color=EnvironmentColor.RED)

# After - structure matches JSON:API
from honeycomb.models import EnvironmentCreate  # alias for CreateEnvironmentRequest
# Use lowercase color string or enum
env = EnvironmentCreate(
    data=CreateEnvironmentRequestData(
        type="environments",
        attributes=CreateEnvironmentRequestDataAttributes(
            name="Production",
            color="red"  # or EnvironmentColor.red
        )
    )
)
```

### Response Access

Property accessors hide JSON:API nesting:

```python
# Both before and after work the same
env.name
env.color
env.slug
env.delete_protected
```

---

## 11. Recipients

### RecipientCreate is Now a Union Type

```python
# Before
recipient = RecipientCreate(
    type=RecipientType.EMAIL,
    details=EmailRecipientDetails(email_address="user@example.com")
)

# After - use specific recipient type
from honeycomb.models import EmailRecipient, EmailRecipientDetails

recipient = EmailRecipient(
    type="email",  # or RecipientType.email
    details=EmailRecipientDetails(email_address="user@example.com")
)
```

### Available Recipient Types

- `EmailRecipient`
- `SlackRecipient`
- `PagerDutyRecipient`
- `WebhookRecipient`
- `MSTeamsRecipient`
- `MSTeamsWorkflowRecipient`

### Helper Function

```python
from honeycomb.models import get_recipient_class, RecipientType

# Get the right class for a type
cls = get_recipient_class(RecipientType.email)  # Returns EmailRecipient
cls = get_recipient_class("slack")  # Returns SlackRecipient
```

---

## 12. Queries

### QuerySpec Field Types

`QuerySpec` now extends the generated `Query` model. Fields that previously accepted both typed models and dicts now require generated types:

```python
# Before - dicts worked
QuerySpec(calculations=[{"op": "COUNT"}])
QuerySpec(filters=[{"column": "status", "op": "=", "value": 200}])

# After - use generated types or QueryBuilder
from honeycomb.models import QuerySpec, QueryBuilder

# Option 1: Use QueryBuilder (recommended)
spec = QuerySpec.builder().count().filter("status", "=", 200).build()

# Option 2: Use generated types directly
from honeycomb._generated_models import QueryCalculation, QueryFilter
spec = QuerySpec(
    calculations=[QueryCalculation(op="COUNT")],
    filters=[QueryFilter(column="status", op="=", value=200)]
)
```

### Query Response Model

The `Query` response model is largely unchanged but now includes `extra="allow"` for forward compatibility.

---

## 13. Query Annotations

### QueryAnnotationSource Enum

```python
# Before
QueryAnnotationSource.QUERY
QueryAnnotationSource.BOARD

# After
QueryAnnotationSource.query
QueryAnnotationSource.board
```

### model_dump_for_api() Removed

```python
# Before
payload = annotation.model_dump_for_api()

# After
payload = annotation.model_dump(mode="json", exclude_none=True)
```

---

## 14. Derived Columns

### model_dump_for_api() Removed

```python
# Before
payload = derived_column.model_dump_for_api()

# After
payload = derived_column.model_dump(mode="json", exclude_none=True)
```

### New Export

```python
# New convenience alias for list responses
from honeycomb.models import DerivedColumnList  # alias for CalculatedFieldList
```

---

## 15. Events

### BatchEvent.model_dump_for_api() Removed

```python
# Before
event = BatchEvent(data={"field": "value"}, time="2024-01-01T00:00:00Z")
payload = event.model_dump_for_api()

# After
payload = event.model_dump(mode="json", exclude_none=True)
```

---

## 16. Markers

### model_dump_for_api() Removed

Both `MarkerCreate` and `MarkerSettingCreate` had custom serialization methods:

```python
# Before
marker = MarkerCreate(message="Deploy v1.2", type="deploy")
payload = marker.model_dump_for_api()

setting = MarkerSettingCreate(type="deploy", color="#F96E11")
payload = setting.model_dump_for_api()

# After
payload = marker.model_dump(mode="json", exclude_none=True)
payload = setting.model_dump(mode="json", exclude_none=True)
```

---

## 17. Service Map Dependencies

### Enum Case Changes

```python
# Before
ServiceMapNodeType.SERVICE
ServiceMapDependencyRequestStatus.PENDING
ServiceMapDependencyRequestStatus.READY
ServiceMapDependencyRequestStatus.ERROR

# After
ServiceMapNodeType.service
ServiceMapDependencyRequestStatus.pending
ServiceMapDependencyRequestStatus.ready
ServiceMapDependencyRequestStatus.error
```

### model_dump_for_api() Removed

```python
# Before
request = ServiceMapDependencyRequestCreate(time_range=7200)
payload = request.model_dump_for_api()

# After
payload = request.model_dump(mode="json", exclude_none=True)
```

---

## 18. Serialization Changes (All Models)

All custom `model_dump_for_api()` methods have been removed. Use Pydantic's standard serialization:

```python
# Before
payload = model.model_dump_for_api()

# After
payload = model.model_dump(mode="json", exclude_none=True)

# Or for excluding defaults too
payload = model.model_dump(mode="json", exclude_none=True, exclude_defaults=True)
```

---

## Quick Migration Checklist

- [ ] **Enum case**: Search for UPPERCASE enum members → change to lowercase
  - `ColumnType`, `RecipientType`, `TriggerAlertType`, `EnvironmentColor`
  - `ServiceMapNodeType`, `ServiceMapDependencyRequestStatus`, `QueryAnnotationSource`
- [ ] **Auth model structure**: Update field access patterns
  - `auth.team_name` → `auth.team.name`
  - `auth.team_slug` → `auth.team.slug`
  - `auth.environment_name` → `auth.environment.name`
  - `auth.environment_slug` → `auth.environment.slug`
  - `auth.api_key_access["key"]` → `auth.api_key_access.key`
- [ ] **Auth type checks**: `auth.type == "string"` → `auth.type.value == "string"` or compare to enum
- [ ] **Dataset structure**: `dataset.delete_protected` → `dataset.settings.delete_protected`
- [ ] **BurnAlert structure**: `burn_alert.slo_id` → `burn_alert.slo.id`
- [ ] **SLO structure**: `slo.sli["alias"]` → `slo.sli.alias` (dict → typed object)
- [ ] **Model renames**: `AuthInfo` → `Auth`, `SLI` → `SLOCreateSli`, `TriggerQuery` → `QuerySpec`
- [ ] **Nested structures**: `DatasetUpdate(delete_protected=...)` → `DatasetUpdate(settings=...)`
- [ ] **Serialization**: `.model_dump_for_api()` → `.model_dump(mode="json", exclude_none=True)`
  - Affects: all Create models, BatchEvent, BoardViewFilter
- [ ] **Union types**: Use specific types like `TriggerWithInlineQuery`, `EmailRecipient`, etc.
- [ ] **Board filter enum**: `FilterOp` → `BoardViewFilterOperation`
- [ ] **QuerySpec fields**: Use `QueryBuilder` or generated types instead of dicts

---

## Why These Changes?

1. **API Alignment**: Generated models match the OpenAPI spec exactly
2. **Type Safety**: Enums provide compile-time checking
3. **Field Validation**: Generated models include `Field(ge=, le=, min_length=)` constraints
4. **Maintainability**: Single source of truth (api.yaml) reduces drift
5. **Simplicity**: No custom serialization logic to maintain

See [2026-01-11-DMCG-migration.md](2026-01-11-DMCG-migration.md) for full migration details.
