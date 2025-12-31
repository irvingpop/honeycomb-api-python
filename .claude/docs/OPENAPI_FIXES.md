# Honeycomb OpenAPI Spec Fixes

This document describes issues in the Honeycomb API OpenAPI spec (`api.yaml`) that prevent `openapi-python-client` from generating a complete client, and the fixes applied.

## Results Summary

After applying patches, generation improved significantly:

| Metric | Before Patches | After Patches |
|--------|----------------|---------------|
| Generated Python files | 359 | 395 |
| SLO endpoints | 3 (missing create/update) | 5 (full CRUD) |
| Query endpoints | 1 (missing create) | 2 (create + get) |
| Query Result endpoints | 0 (broken) | 2 (create + get) |

### Remaining Issues (Low Priority)

These schemas still fail but are not critical for our use case:
- `JSONAPIError` / `RateLimitedJSONAPI` - Error response schemas (we handle errors manually)
- `BudgetRateBurnAlertDetailResponse` - BurnAlert detail (partial functionality)
- `ApiKeyCreateResponse` - v2 API key creation response (FIELD NAME MISMATCH - see Issue 6)
- `IngestKeyRequest` / `ConfigurationKeyRequest` - Key management requests (FIELD NAME MISMATCH - see Issue 6)

## Issues Fixed by Patch Script

The Honeycomb OpenAPI spec (v3.1.0) has several issues that cause `openapi-python-client` to fail on certain schemas:

| Issue Type | Affected Schemas | Impact |
|------------|------------------|--------|
| Arrays without `items` | SLO, SLOCreate, SLOHistoryRequest, AuthV2Response | SLO endpoints not generated |
| Invalid `allOf` with defaults | Query.calculations.op | Query create endpoint not generated |
| `allOf` + `type` at same level | QueryResultsSeries, QueryResultDetails | Query result models not generated |
| Duplicate model names | RateLimitedJSONAPI, BurnAlert variants | Error models and BurnAlert endpoints broken |

## Detailed Issues & Fixes

### Issue 1: Arrays Without `items` Definition

**Problem:** OpenAPI 3.1 requires arrays to have `items` or `prefixItems` defined.

**Affected locations:**
- `SLOCreate.dataset_slugs` (line ~7291)
- `SLO.dataset_slugs` (line ~7372)
- `SLOHistoryRequest.ids` (line ~7441)
- `AuthV2Response.data.attributes.scopes` (line ~8725)

**Fix:** Add `items: { type: string }` to each array definition.

```yaml
# Before
dataset_slugs:
  type: array
  minItems: 1
  maxItems: 10

# After
dataset_slugs:
  type: array
  items:
    type: string
  minItems: 1
  maxItems: 10
```

### Issue 2: Invalid `allOf` with Default Values

**Problem:** The Query schema uses `allOf` to combine a `$ref` with a `default` value, which is invalid OpenAPI.

**Location:** `Query.properties.calculations.items.properties.op` (line ~6326)

```yaml
# Before (invalid)
op:
  allOf:
    - $ref: "#/components/schemas/QueryOp"
    - default: "COUNT"

# After (valid - just use the ref, default is documented)
op:
  $ref: "#/components/schemas/QueryOp"
```

### Issue 3: `allOf` Combined with `type: object` at Same Level

**Problem:** Having both `type: object` and `allOf` at the same level causes parsing ambiguity.

**Affected schemas:**
- `QueryResultsSeries` (line ~6651)
- `QueryResultDetails.query` (line ~6668)

```yaml
# Before (QueryResultsSeries)
QueryResultsSeries:
  type: object
  allOf:
    - $ref: "#/components/schemas/QueryResultsData"
  properties:
    time:
      type: string

# After (proper allOf extension)
QueryResultsSeries:
  allOf:
    - $ref: "#/components/schemas/QueryResultsData"
    - type: object
      properties:
        time:
          type: string
```

### Issue 4: Duplicate Model Names from `allOf` Chains

**Problem:** When schemas use `allOf` to extend other schemas that have inline object definitions, the generator creates duplicate model names.

**Affected schemas:**
- `RateLimitedJSONAPI` → extends `JSONAPIError` which has `errors[].source` inline object
- `ExhaustionTimeBurnAlertDetailResponse` → chain of `allOf` references with `title` fields

**Fix for RateLimitedJSONAPI:** Extract the inline `source` object to a named schema:

```yaml
# Add new schema
JSONAPIErrorSource:
  type: object
  readOnly: true
  properties:
    pointer:
      type: string
    header:
      type: string
    parameter:
      type: string

# Update JSONAPIError to reference it
JSONAPIError:
  properties:
    errors:
      items:
        properties:
          source:
            $ref: "#/components/schemas/JSONAPIErrorSource"
```

**Fix for BurnAlert schemas:** Remove duplicate `title` fields that cause name collisions.

### Issue 5: Complex Union Types (BurnAlerts)

**Problem:** The BurnAlert schemas use `oneOf` with discriminator mappings that reference schemas with complex `allOf` chains, causing the generator to create duplicate nested models.

**Affected schemas:**
- `BurnAlertListResponse`
- `BurnAlertDetailResponse`
- `UpdateBurnAlertRequest`
- `ExhaustionTimeBurnAlertDetailResponse`
- `BudgetRateBurnAlertListResponse`

**Fix:** Flatten the inheritance hierarchy by inlining properties instead of using deep `allOf` chains.

### Issue 6: API Key Permissions Field Name Mismatch (CRITICAL BUG)

**Problem:** The OpenAPI spec and actual API behavior have a critical discrepancy for API key permissions.

**Actual API behavior (verified via live testing):**
- **Request field name**: `permissions` (NOT `api_key_access`)
- **Response field name**: `permissions` (NOT `api_key_access`)
- **Permission field names**: snake_case with prefixes:
  - `create_datasets` (NOT `createDatasets`)
  - `send_events` (NOT `events`)
  - `manage_markers` (NOT `markers`)
  - `manage_triggers` (NOT `triggers`)
  - `manage_boards` (NOT `boards`)
  - `run_queries` (NOT `queries`)
  - `manage_columns` (NOT `columns`)
  - `manage_slos` (NOT `slos`)
  - `manage_recipients` (NOT `recipients`)
  - `manage_privateBoards` (NOT `privateBoards`)
  - Plus: `read_service_maps`, `visible_team_members`

**Live testing results:**
```json
// Request with "permissions" - WORKS ✅
{
  "attributes": {
    "permissions": {
      "create_datasets": true,
      "send_events": true,
      "manage_triggers": true
    }
  }
}
// Response includes all permissions with actual values

// Request with "api_key_access" - IGNORED ❌
{
  "attributes": {
    "api_key_access": {
      "events": true,
      "createDatasets": true
    }
  }
}
// Results in key with ALL permissions set to false!
```

**Impact:**
- Configuration keys created without the correct `permissions` field have NO permissions
- Tools/documentation using `api_key_access` will create non-functional keys
- This is a CRITICAL issue for v2 API usage

**Workaround for our implementation:**
- Use `permissions` field name in request/response models
- Use snake_case with `manage_` prefix for permission names
- Document the correct format in tool descriptions

**Should be reported to Honeycomb:**
- OpenAPI spec needs to document `permissions` field correctly
- Field names should match actual API behavior
- This affects all API key management integrations

## Applying Fixes

Run the patch script:

```bash
./scripts/patch-openapi.py
```

This will:
1. Copy `api.yaml` to `api.yaml.original` (backup)
2. Apply all fixes to create `api.yaml` (patched version)
3. The patched file is used for client generation

## Regenerating After Upstream Updates

When Honeycomb updates their API spec:

```bash
# 1. Fetch new spec
curl -o api.yaml https://api.honeycomb.io/api.yaml

# 2. Apply patches
./scripts/patch-openapi.py

# 3. Regenerate client
./scripts/generate-client.sh
```

## Reporting Upstream

These issues should be reported to Honeycomb. Key points:

### OpenAPI 3.1 Compliance Issues:
- Arrays need `items` defined (OpenAPI 3.1 requirement)
- `allOf` cannot be used to add defaults to `$ref`
- Inline objects in arrays should be extracted to named schemas to avoid code generation issues

### Critical API Behavior Mismatch (Issue 6):
- **API Key Permissions Field**: Spec likely uses `api_key_access` but actual API requires `permissions`
- **Permission Names**: Spec may use camelCase/simple names but API requires snake_case with prefixes
  - Correct: `create_datasets`, `send_events`, `manage_triggers`, `manage_boards`, `run_queries`, `manage_columns`, `manage_slos`, `manage_recipients`, `manage_privateBoards`
  - Wrong: `createDatasets`, `events`, `triggers`, `boards`, `queries`, `columns`, `slos`, `recipients`, `privateBoards`
- **Impact**: Configuration keys created with wrong field names will have ZERO permissions
- **Verification**: Live API testing confirms `permissions` field with snake_case names works correctly
