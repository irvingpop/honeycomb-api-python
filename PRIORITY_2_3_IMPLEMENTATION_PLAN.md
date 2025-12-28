# Priority 2 & 3 Resources - Implementation Plan

## Overview

Expand Claude tool definitions from 15 to 58 tools, covering user-facing Honeycomb API resources.

**Current:** 15 tools (Priority 1: Triggers, SLOs, Burn Alerts)
**Target:** 58 tools (12 user-facing resources)
**Scope:** Focus on observability operations, exclude administrative/security-sensitive operations

## Scope Decisions

### ✅ Included Resources (12 total)
- **Priority 1:** Triggers, SLOs, Burn Alerts (15 tools) ✅
- **Priority 2:** Recipients, Boards, Queries, Derived Columns, Columns, Markers (33 tools)
- **Priority 3:** Datasets, Events, Service Map Dependencies (10 tools)

### ❌ Excluded Resources (4 total, 18 tools removed)

**Rationale for exclusions:**

1. **Query Results** (3 tools) - **Redundant functionality**
   - `honeycomb_run_query` already handles query execution and returns results
   - Separate create/get/poll operations add complexity without value
   - Single `run_query` tool is more intuitive for LLMs

2. **Query Annotations** (5 tools) - **Redundant functionality**
   - `honeycomb_create_query` can create annotations via `annotation_name` parameter
   - Separate annotation CRUD adds API surface without benefit
   - Annotations are internal metadata, not user-facing features

3. **API Keys** (5 tools) - **Security risk**
   - LLMs should NOT create, rotate, or delete API keys
   - Key management requires human oversight
   - Security-sensitive operation (keys grant API access)

4. **Environments** (5 tools) - **Administrative operation**
   - LLMs should NOT create or delete environments
   - Structural changes to team organization
   - Requires human decision-making

## Priority 2 Resources (Infrastructure - 33 tools)

**Resources:** Recipients (6), Boards (5), Queries (3), Derived Columns (5), Columns (5), Markers (9)

**Key Pattern:** Smart routing in create operations (like Priority 1)
- `honeycomb_create_board` - Routes to bundle if inline queries/SLOs present
- `honeycomb_create_query` - Routes to create_with_annotation if annotation_name present
- `honeycomb_create_slo` - Routes to bundle if burn_alerts or SLI expression present (already implemented)

### 1. Recipients (6 tools)

**Resource:** Environment-scoped notification targets

**Methods:**
- `honeycomb_list_recipients` - List all recipients
- `honeycomb_get_recipient` - Get specific recipient
- `honeycomb_create_recipient` - Create recipient (email, slack, pagerduty, webhook, msteams)
- `honeycomb_update_recipient` - Update recipient
- `honeycomb_delete_recipient` - Delete recipient
- `honeycomb_get_recipient_triggers` - List triggers using a recipient

**Complexity:** ⭐⭐ Medium
- Multiple recipient types (5 formats)
- Each type has different required fields
- Integration points: Used by triggers and burn alerts

**Builder:** `RecipientBuilder` (simple, no orchestration)

**Implementation Notes:**
- Schema must support union of recipient types (email, slack, pagerduty, webhook, msteams)
- Validation rules differ per type
- get_recipient_triggers returns raw dicts (not Trigger objects)

### 2. Boards (5 tools)

**Resource:** Environment-scoped dashboards

**Methods:**
- `honeycomb_list_boards` - List all boards
- `honeycomb_get_board` - Get specific board
- `honeycomb_create_board` - Create board (with inline queries/SLOs OR existing IDs)
- `honeycomb_update_board` - Update board
- `honeycomb_delete_board` - Delete board

**Complexity:** ⭐⭐⭐⭐ Very High
- Most complex resource
- Three panel types: query, SLO, text
- Layout options: auto vs manual (with x/y/w/h positions)
- Single tool accepts BOTH simple (existing IDs) AND complex (inline builders) patterns
- Executor intelligently routes: if inline queries/SLOs → use create_from_bundle_async()

**Builder:** `BoardBuilder` + `BoardBundle` (full orchestration)

**Builder Integration Required:**
- `_build_board()` - Convert tool input to BoardBuilder
- `_build_query()` - Convert query panel to QueryBuilder (NEW)
- Handle auto-layout vs manual-layout positioning
- Coordinate panel creation order

**Implementation Notes:**
- **Single tool, two execution paths** (like honeycomb_create_slo):
  ```python
  # Simple: Reference existing queries/SLOs by ID
  {
    "name": "Dashboard",
    "panels": [
      {"type": "query", "query_id": "q-123", "annotation_id": "ann-456"},
      {"type": "slo", "slo_id": "slo-789"}
    ]
  }

  # Complex: Inline query/SLO definitions (uses BoardBuilder)
  {
    "name": "Dashboard",
    "panels": [
      {
        "type": "query",
        "dataset": "api-logs",
        "calculations": [{"op": "COUNT"}],
        "time_range": 3600
      },
      {
        "type": "slo",
        "name": "Availability",
        "dataset": "api-logs",
        "target_per_million": 999000
      }
    ]
  }
  ```
- Executor checks: if any panel has inline definitions → use create_from_bundle_async()
- Manual layout requires position (x, y, width, height) for each panel
- Auto layout doesn't require positions

### 3. Queries (3 tools)

**Resource:** Dataset-scoped saved queries

**Methods:**
- `honeycomb_create_query` - Create saved query (with optional annotation)
- `honeycomb_get_query` - Get query by ID
- `honeycomb_run_query` - Create + execute query with polling

**Complexity:** ⭐⭐⭐ High
- Single create tool with two execution paths:
  - If `annotation_name` provided → create_with_annotation_async()
  - Otherwise → create_async()
- run_query does automatic polling with exponential backoff
- Returns query results, not just query object

**Builder:** `QueryBuilder` (100+ methods, already used in TriggerBuilder)

**Builder Integration Required:**
- `_build_query()` - Convert tool input to QueryBuilder (NEW)
- Support all query features:
  - Multiple calculations (unlike triggers which allow only 1)
  - Orders (sorting)
  - Havings (post-aggregation filters)
  - Limits
  - Absolute time ranges (start_time/end_time)

**Implementation Notes:**
- **Single create tool, smart routing** (like honeycomb_create_slo):
  ```python
  # Without annotation (simple)
  {
    "dataset": "api-logs",
    "calculations": [{"op": "COUNT"}],
    "time_range": 3600
  }

  # With annotation (creates both query + annotation)
  {
    "dataset": "api-logs",
    "annotation_name": "Error Count",  # Triggers create_with_annotation
    "calculations": [{"op": "COUNT"}],
    "time_range": 3600
  }
  ```
- QueryBuilder is much more powerful than TriggerBuilder subset
- Supports multiple calculations (triggers only support 1)
- No time_range limit (triggers limited to 3600s)
- Can have absolute time (start_time/end_time)

### 4. Derived Columns (5 tools)

**Resource:** Dataset or environment-scoped calculated fields

**Methods:**
- `honeycomb_list_derived_columns` - List with optional alias filter
- `honeycomb_get_derived_column` - Get specific column
- `honeycomb_create_derived_column` - Create with expression
- `honeycomb_update_derived_column` - Update expression
- `honeycomb_delete_derived_column` - Delete column

**Complexity:** ⭐⭐ Medium
- Can be dataset-scoped OR environment-wide (dataset="__all__")
- Expression syntax (Honeycomb query language)
- Used by SLOs as SLI definitions

**Builder:** `DerivedColumnBuilder` (simple)

**Implementation Notes:**
- list can filter by alias
- Expression validation is API-side only
- Environment-wide columns used across multiple datasets

### 5. Columns (5 tools)

**Resource:** Dataset-scoped column management

**Methods:**
- `honeycomb_list_columns` - List all columns
- `honeycomb_get_column` - Get column by ID
- `honeycomb_create_column` - Create column
- `honeycomb_update_column` - Update column metadata
- `honeycomb_delete_column` - Delete column

**Complexity:** ⭐ Low
- Simple CRUD
- Column types: string, integer, float, boolean
- Metadata: description, hidden flag

**Builder:** None (simple CRUD)

**Implementation Notes:**
- Different from derived columns (these are raw columns)
- Type is for schema definition, not validation

### 6. Markers (9 tools)

**Resource:** Dataset or environment-scoped deployment/event markers

**Methods (Markers):**
- `honeycomb_list_markers` - List markers
- `honeycomb_create_marker` - Create deployment marker
- `honeycomb_update_marker` - Update marker
- `honeycomb_delete_marker` - Delete marker

**Methods (Marker Settings):**
- `honeycomb_list_marker_settings` - List marker type configs
- `honeycomb_get_marker_setting` - Get setting
- `honeycomb_create_marker_setting` - Create marker type
- `honeycomb_update_marker_setting` - Update setting
- `honeycomb_delete_marker_setting` - Delete setting

**Complexity:** ⭐⭐ Medium
- Dual functionality: markers + settings
- Can be dataset-scoped or environment-wide (dataset="__all__")
- Settings define marker types with colors
- No GET for individual markers (only list)

**Builder:** `MarkerBuilder` (simple)

**Implementation Notes:**
- Two separate sub-resources in one
- Markers: deployment events with timestamps
- Settings: configuration for marker types (colors)

---

## Priority 3 Resources (Full Coverage - 10 tools)

**Resources:** Datasets (5), Events (2), Service Map Dependencies (3)

**Focus:** Core data operations and observability infrastructure

### 7. Datasets (5 tools)

**Resource:** Environment-scoped dataset management

**Methods:**
- `honeycomb_list_datasets` - List all datasets
- `honeycomb_get_dataset` - Get dataset by slug
- `honeycomb_create_dataset` - Create dataset
- `honeycomb_update_dataset` - Update dataset settings
- `honeycomb_delete_dataset` - Delete dataset

**Complexity:** ⭐ Low
- Simple CRUD
- Settings: description, expand_json, color

**Builder:** None

### 8. Events (2 tools)

**Resource:** Dataset-scoped data ingestion

**Methods:**
- `honeycomb_send_event` - Send single event
- `honeycomb_send_events_batch` - Send batch (preferred)

**Complexity:** ⭐⭐ Medium
- Batch sending with per-event status tracking
- Custom headers: X-Honeycomb-Event-Time, X-Honeycomb-Samplerate
- Single event returns empty 200
- Batch returns BatchEventResult list

**Builder:** None

**Implementation Notes:**
- Batch is preferred for production
- timestamp and samplerate are optional
- No read/update/delete (write-only)

### 9. Service Map Dependencies (3 tools)

**Resource:** Environment-scoped distributed tracing dependencies

**Methods:**
- `honeycomb_create_service_map_request` - Initiate async dependency query
- `honeycomb_get_service_map_result` - Get query results (with pagination)
- `honeycomb_query_service_dependencies` - Convenience method (create + poll)

**Complexity:** ⭐⭐⭐⭐ Very High
- Async query pattern (create request, poll results)
- Auto-pagination (up to 640 pages possible!)
- Can return up to 64,000 dependencies
- Time range filtering (absolute or relative)
- Service filtering by node name
- max_pages safety valve (default 640)

**Builder:** None

**Implementation Notes:**
- Polling with exponential backoff
- Trace-based service discovery
- Very large result sets possible
- Rate limiting critical (100 req/min)

---

## Implementation Strategy

### Phase A: Systematic Tool Generation

For each resource, follow this pattern:

1. **Audit Resource API**
   - Read resource class in `src/honeycomb/resources/*.py`
   - Document all methods (list, get, create, update, delete, etc.)
   - Identify special methods (create_from_bundle, pagination, etc.)
   - Note scoping (dataset, environment, team)

2. **Create Generator Functions**
   - Add to `src/honeycomb/tools/generator.py`
   - `generate_list_<resource>_tool()`
   - `generate_get_<resource>_tool()`
   - `generate_create_<resource>_tool()`
   - `generate_update_<resource>_tool()`
   - `generate_delete_<resource>_tool()`
   - Special methods as needed

3. **Write Hand-Crafted Descriptions**
   - Add to `src/honeycomb/tools/descriptions.py`
   - Follow quality requirements (what, when, params, caveats)
   - >= 50 characters
   - Emphasize when to use tool

4. **Create Examples (2-3 per tool)**
   - Minimal example (required fields only)
   - Common use case (with optional fields)
   - Advanced example (if applicable)

5. **Implement Builder Converters (if needed)**
   - Add to `src/honeycomb/tools/builders.py`
   - `_build_board()` for BoardBuilder
   - `_build_query()` for QueryBuilder
   - `_build_recipient()` for RecipientBuilder
   - `_build_marker()` for MarkerBuilder

6. **Implement Executor Handlers**
   - Add to `src/honeycomb/tools/executor.py`
   - `_execute_<operation>_<resource>()`
   - Handle special cases (pagination, polling, orchestration)

7. **Write Tests**
   - Completeness tests (100% feature coverage)
   - Unit tests (generator, executor, builders)
   - Integration tests (mock API calls)

8. **Update generate_all_tools()**
   - Add new tool generators to the list
   - Update resource filter in generate_tools_for_resource()

### Phase B: Builder Integration for Complex Resources

**Boards (Highest Priority)**

Requires comprehensive QueryBuilder support:

```python
def _build_query(data: dict) -> QueryBuilder:
    """Convert tool input to QueryBuilder.

    Must support features beyond TriggerBuilder:
    - Multiple calculations (triggers only allow 1)
    - Orders (sorting results)
    - Havings (post-aggregation filters)
    - Limits (result count)
    - Absolute time ranges (start_time/end_time)
    - All 12 calculation types
    - All 14 filter operators
    """
```

```python
def _build_board(data: dict) -> BoardBuilder:
    """Convert tool input to BoardBuilder.

    Handles:
    - Query panels (inline QueryBuilder or existing query_id)
    - SLO panels (inline SLOBuilder or existing slo_id)
    - Text panels (markdown content)
    - Auto vs manual layout
    - Preset filters
    - Tags
    - Panel ordering
    """
```

**Recipients**

Simple builder but needs type discrimination:

```python
def _build_recipient(data: dict) -> RecipientBuilder:
    """Convert tool input to RecipientBuilder.

    Handles 5 recipient types:
    - Email: {type: "email", target: "user@example.com"}
    - Slack: {type: "slack", target: "#channel", details: {...}}
    - PagerDuty: {type: "pagerduty", target: "routing-key", details: {severity}}
    - Webhook: {type: "webhook", target: "https://...", details: {...}}
    - MSTeams: {type: "msteams", target: "webhook-url"}
    """
```

---

## Implementation Order (Recommended)

### Batch 1: Simple CRUD (No Builders) - 10 tools
**Estimated Effort:** 1.5-2 hours

1. **Datasets** (5 tools) - ⭐ Low complexity
2. **Columns** (5 tools) - ⭐ Low complexity

**Rationale:** Get comfortable with the pattern, build momentum

### Batch 2: Medium Complexity with Simple Builders - 11 tools
**Estimated Effort:** 3-4 hours

4. **Derived Columns** (5 tools) - ⭐⭐ Medium
5. **Recipients** (6 tools) - ⭐⭐ Medium (type discrimination)

**Rationale:** Introduces builder patterns without orchestration complexity

### Batch 3: High Complexity with Orchestration - 8 tools
**Estimated Effort:** 5-6 hours

6. **Queries** (3 tools) - ⭐⭐⭐ High (QueryBuilder integration, smart routing for annotations)
7. **Boards** (5 tools) - ⭐⭐⭐⭐ Very High (full orchestration, smart routing for bundles)

**Dependencies:** Requires `_build_query()` implementation first

**Rationale:** Most complex resources, needs QueryBuilder fully working

### Batch 4: Special Patterns - 14 tools
**Estimated Effort:** 3-4 hours

7. **Markers + Settings** (9 tools) - ⭐⭐ Medium (dual resource)
8. **Events** (2 tools) - ⭐⭐ Medium (batch sending)
9. **Service Map Dependencies** (3 tools) - ⭐⭐⭐⭐ Very High (async + pagination)

**Rationale:** Special execution patterns (dual resources, batch operations, async queries)

---

## Technical Challenges

### Challenge 1: QueryBuilder Completeness

**Problem:** QueryBuilder has 67 methods, TriggerBuilder subset only uses ~20

**Solution:**
- Create comprehensive `_build_query()` that handles:
  - Multiple calculations (not just one)
  - All order operations
  - All having operations
  - Limit support
  - Absolute time ranges

**Test Strategy:**
- Extend completeness tests to verify ALL QueryBuilder methods
- Ensure every CalcOp, FilterOp, OrderDirection supported

### Challenge 2: BoardBuilder Orchestration

**Problem:** Most complex resource, coordinates multiple API calls

**Solution:**
- Implement `_build_board()` step by step:
  1. Start with simple board (no panels)
  2. Add text panels (easiest)
  3. Add query panels with QueryBuilder
  4. Add SLO panels with SLOBuilder
  5. Add layout handling (auto vs manual)

**Test Strategy:**
- Unit tests for each panel type separately
- Integration test for full board creation
- Test both layout modes

### Challenge 3: Pagination (Service Map Dependencies)

**Problem:** List operations may require multiple API calls (up to 640 pages!)

**Solution:**
- Executor handles pagination transparently
- Document max_pages parameter for Service Map
- Tool descriptions warn about potential request volume
- Rate limiting critical (100 requests/minute)

### Challenge 4: Async Patterns (Service Map)

**Problem:** Create request, poll for completion pattern

**Solution:**
- Executor implements polling with exponential backoff
- Tool parameters include poll_interval and timeout
- Document expected completion times

---

## Testing Strategy

### Completeness Tests (Must Pass Before Merging)

For each batch, create tests that verify 100% coverage:

```python
# test_tools_completeness.py additions

class TestQueryBuilderCompleteness:
    """Verify _build_query supports ALL QueryBuilder methods."""

    def test_all_query_features_supported(self):
        # Multiple calculations
        # Orders
        # Havings
        # Limits
        # Absolute time
        pass

class TestBoardBuilderCompleteness:
    """Verify _build_board supports all panel types and layouts."""
    pass

class TestRecipientTypesCompleteness:
    """Verify all 5 recipient types supported."""
    pass
```

### Unit Test Coverage Goals

| Test File | Target Tests | Current | Remaining |
|-----------|--------------|---------|-----------|
| test_tools_generator.py | 50 | 24 | +26 |
| test_tools_executor.py | 50 | 10 | +40 |
| test_tools_builders.py | 40 | 14 | +26 |
| test_tools_completeness.py | 30 | 14 | +16 |
| **Total** | **170** | **62** | **+108** |

### DeepEval Test Expansion

Add tool selection tests for each new resource:
- 6 tests per resource (list, get, create, update, delete, special)
- Total: ~48 new DeepEval test cases

---

## Code Structure Changes

### generator.py Growth

**Current:** ~650 lines (15 tools)
**Projected:** ~3,500 lines (80 tools)

**Mitigation:**
- Split into multiple files:
  - `generator/triggers.py`
  - `generator/slos.py`
  - `generator/boards.py`
  - etc.
- Keep `generator.py` as coordinator

### executor.py Growth

**Current:** ~300 lines (15 tools)
**Projected:** ~1,600 lines (80 tools)

**Mitigation:**
- Split into multiple files:
  - `executor/triggers.py`
  - `executor/slos.py`
  - etc.
- Keep `executor.py` as router

### builders.py Growth

**Current:** ~310 lines (2 builders)
**Projected:** ~800 lines (5-6 builders)

**Addition Needed:**
- `_build_query()` - ~200 lines (comprehensive)
- `_build_board()` - ~150 lines (orchestration)
- `_build_recipient()` - ~50 lines (type switching)
- `_build_marker()` - ~30 lines (simple)

---

## Success Criteria

### Per-Resource Checklist

For each resource, must have:

- [ ] All CRUD methods have tool definitions
- [ ] Hand-crafted descriptions (>= 50 chars)
- [ ] 2-3 examples per tool
- [ ] Generator functions implemented
- [ ] Executor handlers implemented
- [ ] Builder converters (if applicable)
- [ ] Completeness tests (100% coverage)
- [ ] Unit tests for executor
- [ ] Unit tests for builders
- [ ] Documentation updated

### Overall Success Metrics

- [ ] 80+ tool definitions generated
- [ ] All tools validate successfully
- [ ] 170+ unit tests passing
- [ ] 100% feature coverage for all resources
- [ ] DeepEval schema acceptance: 100%
- [ ] DeepEval tool selection: >= 85%
- [ ] Documentation complete for all resources
- [ ] CLI works for all resources

---

## Estimated Timeline

**Total Estimated Effort:** 12-15 hours (reduced from 17-22 hours)

| Phase | Resources | Tools | Effort | Dependencies |
|-------|-----------|-------|--------|--------------|
| Batch 1 | Datasets, Columns | 10 | 1.5-2h | None |
| Batch 2 | Derived Columns, Recipients | 11 | 3-4h | Batch 1 |
| Batch 3 | Queries, Boards | 8 | 5-6h | _build_query() |
| Batch 4 | Markers, Events, Service Map | 14 | 3-4h | Batch 3 |

**Total New Tools:** 43 (15 existing + 43 new = 58 total)

**Critical Path:** Batch 1 → Batch 2 → Batch 3 (QueryBuilder) → Batch 4

---

## Risk Mitigation

### Risk 1: QueryBuilder Complexity

**Mitigation:**
- Start with subset of QueryBuilder features
- Test incrementally
- Use completeness tests to track progress

### Risk 2: BoardBuilder Orchestration

**Mitigation:**
- Test each panel type separately first
- Start with simple boards (no panels)
- Add complexity gradually

### Risk 3: Test Suite Growth

**Mitigation:**
- Parallelize test execution (pytest-xdist)
- Split into fast/slow test suites
- Use markers to run subset during development

### Risk 4: Documentation Lag

**Mitigation:**
- Generate documentation from tool definitions
- Automate example generation where possible
- Keep examples in sync with schemas

---

## Next Actions

**Immediate (Start Batch 1):**
1. Create generator functions for Datasets (5 tools)
2. Create generator functions for Columns (5 tools)
3. Create generator functions for Query Annotations (5 tools)
4. Write descriptions for all 15
5. Implement executor handlers
6. Write completeness tests
7. Run unit tests

**Then (Batch 2):**
8. Implement Derived Columns (5 tools)
9. Implement Recipients (6 tools) with type discrimination
10. Create _build_recipient() converter

**Then (Batch 3 - Critical):**
11. Implement comprehensive _build_query()
12. Test all QueryBuilder features
13. Implement Queries tools (4 tools)
14. Implement _build_board()
15. Implement Boards tools (6 tools)

---

## Tracking Metrics

We'll track these metrics at each batch:

| Metric | Current | Target |
|--------|---------|--------|
| Tool Definitions | 15 | 58 |
| Resources Complete | 3/12 | 12/12 |
| Unit Tests | 65 | 140+ |
| Feature Coverage | 100% (P1) | 100% (all) |
| Documentation Pages | 1 | 1 (comprehensive) |

---

## Questions to Resolve

1. **Should we split generator.py and executor.py into multiple files now or later?**
   - Now: Better organization from the start
   - Later: Avoid premature splitting

2. **How comprehensive should QueryBuilder examples be?**
   - Minimal: Just show basic usage
   - Full: Show all 12 calculation types, all filter types

3. **Should we implement all special methods (create_with_annotation, create_and_run, etc.)?**
   - Yes: Complete coverage
   - No: Start with basic CRUD only

4. **Priority order: Complete P2 before P3, or implement by complexity?**
   - By priority: Finish P2 completely first
   - By complexity: Do all simple ones first (easier wins)

**Recommendation:** Implement by complexity (Batches 1-5) - provides incremental value and learning
