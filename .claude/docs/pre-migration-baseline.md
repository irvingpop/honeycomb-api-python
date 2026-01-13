# Pre-Migration Baseline - DMCG Migration

**Date**: 2026-01-11
**Purpose**: Document current state before migrating to datamodel-code-generator

## Test Results Summary

All tests completed successfully with NO failures.

### Resource Status

| Resource | CRUD Works? | Builders Work? | Notes |
|----------|-------------|----------------|-------|
| Columns | ✓ Yes | N/A | Create + delete successful |
| Datasets | ✓ Yes | N/A | List (63 datasets) + get successful |
| Markers | ✓ Yes | N/A | Create + delete successful |
| Recipients | ✓ Yes | N/A | Create (email type) + delete successful |
| SLOs | Not tested | Not tested | Not included in test_live_api.py |
| Triggers | ✓ Yes | ✓ Yes | Full CRUD works. QueryBuilder pattern successful |
| Queries | Not tested | Not tested | Not included in test_live_api.py |
| Boards | ✓ Partial | Not tested | List works (5 boards found), CRUD not tested |
| Events | ✓ Yes | N/A | Single + batch send successful (3 events accepted) |

### Additional Features Tested

| Feature | Status | Notes |
|---------|--------|-------|
| Sync Client | ✓ Working | All sync wrappers functioning correctly |
| Rate Limiting | ✓ Working | Hit rate limit at 169 requests, automatic retry works |
| Retry Logic | ✓ Working | Correctly waits ~49s before retrying, respects Retry-After header |

### Test Environment

- **Dataset**: integration-test
- **Total datasets**: 63
- **Columns in test dataset**: 14
- **Existing triggers**: 0 (created/deleted during test)
- **Existing markers**: 0 (created/deleted during test)
- **Existing recipients**: 3 (email, email, webhook)
- **Existing boards**: 5

### Key Observations

1. **Triggers**: Full lifecycle works perfectly
   - Create with QueryBuilder (fluent API)
   - Get by ID
   - Update (threshold, name changes)
   - Delete + verification

2. **Events**: Both patterns work
   - Single event send
   - Batch send (3 events accepted)

3. **Rate Limiting**: Robust implementation
   - Triggers at 169 rapid requests
   - Automatic retry with exponential backoff
   - Respects Retry-After header (49s)
   - Successful retry after wait period

4. **Sync/Async**: Both clients work
   - Async client (primary)
   - Sync wrapper (delegates to async)

### Not Tested

The following resources were not included in test_live_api.py:

- SLOs (with builders)
- Queries (create/run operations)
- Burn Alerts
- Full Board CRUD (only list tested)

### Baseline Log

Full test output saved to: `.claude/docs/pre-migration-baseline.log`

### Serialization Snapshots

Comprehensive serialization snapshots captured to disk for diff comparison:

**Location**: `.claude/serialization-snapshots/pre-migration/`

**Files captured**: 30 JSON files across 8 model categories

| Category | Files | Examples |
|----------|-------|----------|
| Triggers | 4 | minimal, full_featured, saved_query, complex_filters |
| Columns | 6 | All types (string, integer, float, boolean), with_description, hidden |
| Markers | 5 | minimal, with_start_time, time_range, with_url, setting |
| Recipients | 5 | email, slack, pagerduty, webhook (minimal & with_headers) |
| Datasets | 2 | minimal, with_description |
| Queries | 2 | simple, complex |
| SLOs | 3 | simple, with_expression, multi_dataset |
| Boards | 3 | minimal, with_description, with_panels |

**Usage after migration**:
```bash
# Re-run the snapshot script to post-migration/ directory
poetry run python scripts/capture_serialization_snapshots.py

# Compare snapshots
diff -r .claude/serialization-snapshots/pre-migration/ \
        .claude/serialization-snapshots/post-migration/
```

### Exit Criteria Met

- [x] Live test baseline captured
- [x] Current state documented (this file)
- [x] Serialization snapshot tests written and passing (24 tests, all pass)
- [x] Serialization snapshots captured to disk (30 JSON files)

## Next Steps

Proceed to Phase 1: Generation Infrastructure
