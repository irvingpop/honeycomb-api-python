
# DeepEval Test Architecture

## Overview

Scalable, data-driven architecture for testing all 58 Claude tools across 12 Honeycomb API resources.

**Key Principle:** Separate test data from test execution logic

## Architecture

```
tests/integration/
├── eval_test_cases.py           # Test data (prompts + expected outputs)
└── test_claude_tools_eval.py    # Test execution logic (generic)
```

### File Responsibilities

**eval_test_cases.py** - Test Case Registry
- Contains arrays of test case dicts per resource
- Each test case: id, description, prompt, expected_tool, expected_params, assertion_checks
- Easy to add new cases - just append to array
- No test execution logic

**test_claude_tools_eval.py** - Generic Test Runner
- Loads test cases from registry
- Parameterized tests execute all cases
- Two test modes: fast (basic assertions) + slow (LLM evaluation)
- No hardcoded prompts - all data-driven

## Test Case Structure

```python
{
    "id": "trigger_p99_percentile",  # Unique ID for test case
    "description": "P99 calculation (not COUNT)",  # Human-readable description
    "prompt": "Create a trigger...",  # Natural language prompt
    "expected_tool": "honeycomb_create_trigger",  # Tool that should be called
    "expected_params": {  # Expected parameters (partial match)
        "dataset": "api-logs",
        "query": {
            "calculations": [{"op": "P99", "column": "duration"}]
        },
    },
    "assertion_checks": [  # Custom Python expressions
        "params['query']['calculations'][0]['op'] == 'P99'",
        "params['threshold']['value'] > 0",
    ],
}
```

## Adding New Test Cases

### Step 1: Add to eval_test_cases.py

```python
DATASETS_TEST_CASES = [
    # ... existing cases ...
    {
        "id": "dataset_update_description",
        "description": "Update dataset description",
        "prompt": "Update the description of dataset 'api-logs' to 'Updated description'",
        "expected_tool": "honeycomb_update_dataset",
        "expected_params": {
            "dataset": "api-logs",
            "description": "Updated description",
        },
        "assertion_checks": [],
    },
]
```

### Step 2: Run Tests

```bash
# Tests automatically pick up new case
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k dataset_update_description
```

**That's it!** No need to modify test execution logic.

## Test Modes

### Mode 1: Basic Assertions (Fast)

**Test:** `test_argument_basic_assertions`
**Speed:** ~1 second per test case
**Validation:**
- Checks expected_params match (partial)
- Runs assertion_checks expressions
- No LLM evaluation

**Use:** During development, quick smoke tests

### Mode 2: LLM Evaluation (Slow)

**Test:** `test_argument_with_llm_eval`
**Speed:** ~10 seconds per test case
**Validation:**
- Uses ArgumentCorrectnessMetric (Claude evaluates semantic correctness)
- Catches subtle errors that basic assertions miss
- More robust validation

**Use:** Before commits, comprehensive validation

## Running Tests

### All Tests (Full Validation)

```bash
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v
```

### Fast Mode Only (Development)

```bash
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k basic
```

### LLM Evaluation Only (Pre-Commit)

```bash
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k llm_eval
```

### Specific Resource

```bash
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k triggers
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k slos
```

### Specific Test Case

```bash
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k trigger_p99_percentile
```

## Coverage Goals

### Current Coverage (Phase 11)

| Resource | Tools | Test Cases |
|----------|-------|------------|
| Triggers | 5 | 8 |
| SLOs | 5 | 5 |
| Burn Alerts | 5 | 3 |
| **Total** | **15** | **16** |

### Target Coverage (All Phases)

| Resource | Tools | Target Test Cases | Status |
|----------|-------|-------------------|--------|
| Triggers | 5 | 10 | ⬆️ Expand |
| SLOs | 5 | 8 | ⬆️ Expand |
| Burn Alerts | 5 | 5 | ⬆️ Expand |
| Datasets | 5 | 8 | 🔜 Add |
| Columns | 5 | 8 | 🔜 Add |
| Derived Columns | 5 | 8 | 🔜 Add |
| Recipients | 6 | 10 | 🔜 Add |
| Queries | 3 | 8 | 🔜 Add |
| Boards | 5 | 12 | 🔜 Add |
| Markers | 9 | 12 | 🔜 Add |
| Events | 2 | 4 | 🔜 Add |
| Service Map | 3 | 6 | 🔜 Add |
| **Total** | **58** | **~100** | |

**Target:** ~100 test cases covering all tools and major parameter variations

## Test Case Design Guidelines

### 1. Coverage Per Tool

For each tool, create test cases covering:
- **Basic operation** (minimal required fields)
- **Common use case** (with optional fields)
- **Edge cases** (unusual but valid inputs)
- **Parameter variations** (different filter ops, calc types, etc.)

Example for `honeycomb_create_trigger`:
1. Basic COUNT trigger
2. P99 percentile trigger
3. Multiple filters (AND conditions)
4. String filter operators (contains, starts-with)
5. EXISTS filter
6. Complex threshold operators
7. Different time ranges
8. With recipients

### 2. Expected Parameters

Use **partial matching** - only specify params you want to validate:

```python
# Good: Only check what matters for this test
"expected_params": {
    "dataset": "api-logs",
    "threshold": {"op": ">", "value": 100},
}

# Bad: Over-specifying makes tests brittle
"expected_params": {
    "dataset": "api-logs",
    "name": "Exact Name",
    "description": "Exact description",
    "query": { /* full object */ },
    "threshold": {"op": ">", "value": 100},
    "frequency": 900,
    "recipients": [],
    ...
}
```

### 3. Assertion Checks

Use for dynamic/complex validations:

```python
"assertion_checks": [
    # Check list length
    "len(params['recipients']) >= 1",

    # Check value ranges
    "999000 <= params['target_per_million'] <= 1000000",

    # Check presence
    "'expression' in params['sli'] or 'alias' in params['sli']",

    # Check type
    "isinstance(params['data'], dict)",
]
```

### 4. Naming Convention

**Test ID format:** `{resource}_{operation}_{variant}`

Examples:
- `trigger_create_basic` - Basic trigger creation
- `trigger_create_p99` - Trigger with P99 calculation
- `slo_create_inline_expression` - SLO with inline derived column
- `board_create_with_bundle` - Board with inline queries

## Scaling to 58 Tools

### Adding a New Resource

Example: Adding Datasets (5 tools)

**1. Add test cases to eval_test_cases.py:**

```python
DATASETS_TEST_CASES = [
    {
        "id": "dataset_create_basic",
        "description": "Create dataset with minimal fields",
        "prompt": "Create a dataset named 'logs'",
        "expected_tool": "honeycomb_create_dataset",
        "expected_params": {"name": "logs"},
        "assertion_checks": [],
    },
    {
        "id": "dataset_create_with_settings",
        "description": "Create dataset with description and color",
        "prompt": "Create a dataset named 'api-logs' with description 'Production API' and blue color",
        "expected_tool": "honeycomb_create_dataset",
        "expected_params": {
            "name": "api-logs",
            "description": "Production API",
            "settings": {"color": "blue"},
        },
        "assertion_checks": [],
    },
    # ... 6 more test cases (list, get, update, delete, variations)
]

# Add to registry
ALL_TEST_CASES_BY_RESOURCE = {
    # ... existing ...
    "datasets": DATASETS_TEST_CASES,  # ← Add this line
}
```

**2. Run tests:**

```bash
# Automatically includes new cases
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v
```

**Effort:** ~30 minutes to add 8 test cases per resource

### Batch Addition Strategy

**Phase 1: Simple Resources (Datasets, Columns)** - 16 test cases
- Copy existing patterns
- Minimal complexity
- Quick wins

**Phase 2: Medium Resources (Derived Columns, Recipients)** - 18 test cases
- Type discrimination (recipients)
- Expression syntax (derived columns)

**Phase 3: Complex Resources (Queries, Boards)** - 20 test cases
- Multiple parameter variations
- Bundle vs simple patterns
- Orchestration cases

**Phase 4: Special Resources (Markers, Events, Service Map)** - 22 test cases
- Dual resources (markers + settings)
- Batch operations (events)
- Async patterns (service map)

**Total:** ~76 test cases (beyond initial 16)

## Performance Optimization

### Parallel Test Execution

```bash
# Run with pytest-xdist (8 workers)
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -n 8
```

**Impact:**
- Serial: ~100 tests × 10 sec = 16 minutes
- Parallel (8 workers): ~2-3 minutes

### Selective Test Execution

```bash
# Fast smoke test (basic assertions only)
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k basic

# LLM eval for changed resource only
direnv exec . poetry run pytest tests/integration/test_claude_tools_eval.py -v -k "triggers and llm_eval"
```

## Maintenance

### Updating Test Cases

When tool schemas change:

1. Update test case in `eval_test_cases.py`
2. Re-run tests
3. No changes to test execution logic needed

### Adding New Assertions

```python
# Add new assertion type to existing test case
{
    "id": "trigger_create_basic",
    # ... existing fields ...
    "assertion_checks": [
        "params['threshold']['value'] >= 100",  # ← Add new assertion
    ],
}
```

### Debugging Failed Tests

Test IDs make it easy to identify failures:

```
FAILED test_argument_basic_assertions[trigger_p99_percentile]
       ↓
Find in eval_test_cases.py: id="trigger_p99_percentile"
       ↓
Update prompt or expected_params
       ↓
Re-run specific test
```

## Metrics

### Test Execution Time

| Test Mode | Per Case | Total (100 cases) | Parallelized (8x) |
|-----------|----------|-------------------|-------------------|
| Basic assertions | ~1 sec | ~2 min | ~15 sec |
| LLM evaluation | ~10 sec | ~17 min | ~2 min |
| **Both** | ~11 sec | ~18 min | ~2.5 min |

### Coverage Metrics

Track these per resource:
- **Tool coverage:** % of tools with test cases
- **Parameter coverage:** % of parameters tested
- **Variation coverage:** % of parameter variations tested (e.g., all CalcOps)

**Goal:** 100% tool coverage, 80%+ parameter coverage

## Comparison: Old vs New Architecture

### Old Architecture (test_claude_tools_eval.py)

```python
class TestParameterQuality:
    def test_trigger_params_with_argument_correctness(self, client, model):
        prompt = "Create a trigger..."  # ← Hardcoded
        result = call_claude(client, prompt)
        # ... test logic ...

    def test_slo_params_with_argument_correctness(self, client, model):
        prompt = "Create an SLO..."  # ← Hardcoded
        result = call_claude(client, prompt)
        # ... test logic ...

    # 50 more methods...
```

**Problems:**
- Hardcoded prompts in test methods
- Difficult to see all test cases at once
- Adding new case requires new method
- Can't easily bulk-update test data
- Test logic mixed with test data

### New Architecture (test_claude_tools_eval.py + eval_test_cases.py)

```python
# eval_test_cases.py (DATA)
TRIGGERS_TEST_CASES = [
    {"id": "...", "prompt": "...", ...},
    {"id": "...", "prompt": "...", ...},
    # ... 100 test cases
]

# test_claude_tools_eval.py (LOGIC)
class TestArgumentCorrectness:
    @pytest.mark.parametrize("test_case", get_all_test_cases(), ids=lambda tc: tc["id"])
    def test_argument_basic_assertions(self, client, test_case):
        # Generic logic - works for ALL test cases
```

**Benefits:**
- All test cases visible in one file
- Easy to add/modify test cases
- Bulk operations (update all triggers tests at once)
- Test logic remains constant as cases grow
- Clear separation of concerns

## Future Enhancements

### 1. YAML/JSON Test Cases

Move test cases to YAML for easier editing:

```yaml
# tests/integration/test_data/triggers.yaml
- id: trigger_basic_count
  description: Basic COUNT trigger
  prompt: Create a trigger...
  expected_tool: honeycomb_create_trigger
  expected_params:
    dataset: api-logs
    threshold:
      op: ">"
      value: 100
```

### 2. Test Case Generation

Auto-generate test cases from tool schemas:

```bash
# Generate skeleton test cases for new resource
python -m honeycomb.tools generate-test-cases --resource datasets
```

### 3. Coverage Reports

Track which parameters have test coverage:

```bash
# Show coverage gaps
python -m honeycomb.tools test-coverage-report
```

Output:
```
Triggers:
  ✅ 100% tool coverage (5/5)
  ✅ 85% parameter coverage
  ❌ Missing: exceeded_limit parameter
  ❌ Missing: breakdowns parameter

SLOs:
  ✅ 100% tool coverage (5/5)
  ⚠️  70% parameter coverage
  ❌ Missing: datasets array (multi-dataset SLOs)
```

### 4. Regression Testing

Store actual tool call outputs for regression detection:

```python
# tests/integration/test_data/baselines/trigger_basic_count.json
{
    "prompt": "Create a trigger...",
    "actual_tool_call": {
        "name": "honeycomb_create_trigger",
        "input": { /* actual parameters */ }
    },
    "deepeval_score": 0.95,
    "timestamp": "2025-12-28T10:30:00Z"
}
```

Compare new runs against baselines to detect regressions.

## Migration Path

### Implementation Complete

- ✅ Data-driven architecture implemented
- ✅ 26 test cases covering Priority 1 resources
- ✅ Framework ready to scale to 100+ test cases
- ✅ All tests using Claude for evaluation (no OpenAI dependency)

## Best Practices

### Writing Good Test Cases

**DO:**
- Use directive prompts ("Create...", "List...", "Delete...")
- Specify all required parameters in prompt
- Test parameter variations (not just happy path)
- Use partial matching in expected_params (only check what matters)
- Add descriptive test IDs

**DON'T:**
- Write vague prompts ("Help me with triggers")
- Over-specify expected_params (makes tests brittle)
- Duplicate test cases (one test per variation)
- Hardcode values that might change (API URLs, etc.)

### Organizing Test Cases

Group by operation within resource:

```python
TRIGGERS_TEST_CASES = [
    # Create operations (variations)
    {"id": "trigger_create_basic", ...},
    {"id": "trigger_create_p99", ...},
    {"id": "trigger_create_multi_filter", ...},

    # List operations
    {"id": "trigger_list", ...},

    # Get operations
    {"id": "trigger_get", ...},

    # Update operations
    {"id": "trigger_update_name", ...},
    {"id": "trigger_update_threshold", ...},

    # Delete operations
    {"id": "trigger_delete", ...},
]
```

### Parameter Coverage Strategy

For create operations, test:
- **Required parameters:** All combinations
- **Optional parameters:** At least one test case per parameter
- **Parameter variations:** All enum values, edge cases

Example: Burn Alerts
- 2 alert types → 2 test cases minimum
- Optional recipients → 1 test case with recipients
- Optional description → 1 test case with description
- **Total:** 5 test cases for full coverage

## Example: Complete Resource Test Suite

```python
# eval_test_cases.py
QUERIES_TEST_CASES = [
    # Create operations
    {
        "id": "query_create_minimal",
        "prompt": "Create a query in dataset 'logs' that counts requests",
        "expected_tool": "honeycomb_create_query",
        "expected_params": {"dataset": "logs"},
        "assertion_checks": ["params['query']['calculations'][0]['op'] == 'COUNT'"],
    },
    {
        "id": "query_create_with_filters",
        "prompt": "Create a query in 'logs' counting requests where status >= 500",
        "expected_tool": "honeycomb_create_query",
        "expected_params": {"dataset": "logs"},
        "assertion_checks": ["'filters' in params['query']"],
    },
    {
        "id": "query_create_multi_calc",
        "prompt": "Create a query in 'logs' that shows COUNT, AVG, and P99 of duration",
        "expected_tool": "honeycomb_create_query",
        "expected_params": {"dataset": "logs"},
        "assertion_checks": ["len(params['query']['calculations']) >= 3"],
    },
    {
        "id": "query_create_with_annotation",
        "prompt": "Create a query in 'logs' with annotation name 'Error Rate'",
        "expected_tool": "honeycomb_create_query",
        "expected_params": {"dataset": "logs", "annotation_name": "Error Rate"},
        "assertion_checks": [],
    },
    # Read operations
    {
        "id": "query_get",
        "prompt": "Get query q-123 from dataset 'logs'",
        "expected_tool": "honeycomb_get_query",
        "expected_params": {"dataset": "logs", "query_id": "q-123"},
        "assertion_checks": [],
    },
    # Execute operations
    {
        "id": "query_run",
        "prompt": "Run a query in 'logs' counting requests in last hour",
        "expected_tool": "honeycomb_run_query",
        "expected_params": {"dataset": "logs"},
        "assertion_checks": [],
    },
]
```

**Result:** 6 test cases × 2 test modes = 12 test executions per resource

## Success Metrics

### Per-Resource Checklist

For each resource, validate:
- ✅ Test cases for all tools (100% tool coverage)
- ✅ Test cases for common parameter variations (80%+ param coverage)
- ✅ All basic assertion tests passing
- ✅ All LLM evaluation tests passing
- ✅ Test IDs are descriptive and unique
- ✅ Prompts are clear and directive

### Overall Success Metrics

- ✅ 58/58 tools have test coverage (100%)
- ✅ ~100 test cases total
- ✅ 80%+ parameter coverage across all tools
- ✅ All tests passing in < 3 minutes (parallelized)
- ✅ Easy to add new test cases (< 5 minutes per case)
