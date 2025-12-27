# Integration Tests and Documentation Sync

This document describes how documentation examples are kept in sync with integration tests, ensuring all code examples in docs are tested against the real Honeycomb API.

## Problem Statement

Documentation code examples that aren't tested will drift from reality over time, leading to:
- Doc examples that don't actually work
- Duplicated maintenance burden
- No guarantee docs stay current with API changes

## Solution: Executable Documentation Examples

We use **mkdocs-include-markdown-plugin** to extract code sections from tested Python files into documentation. This creates a single source of truth where:

1. Code examples live in `docs/examples/*.py` with named sections
2. Documentation includes these sections via the plugin
3. Integration tests (`tests/integration/test_doc_examples.py`) run the examples

## Core Principles

### 1. Async-First Documentation

All documentation examples use async patterns only. Sync equivalents are auto-generated (future phase) to avoid duplication and drift.

**Rationale**: The sync methods are thin wrappers around async. Testing async validates the core logic; sync wrappers are mechanical.

### 2. Full Lifecycle Testing

Every integration test covers the complete resource lifecycle (5 actions):

```
list -> create -> get -> update -> delete
```

This ensures all CRUD operations work and prevents orphaned test resources.

### 3. No Illustrative Error Handling

Error handling examples are removed from resource documentation. If needed, create a single dedicated "Error Handling" guide with tested examples.

**Rationale**: Error handling patterns are generic across resources. Duplicating try/except blocks in every resource doc adds noise without value.

### 4. Resource Dependencies

Tests follow the dependency hierarchy from [DEPENDENCIES.md](.claude/skills/live-test/DEPENDENCIES.md):

```
Level 0: Environment, Dataset
Level 1: Columns (requires Dataset)
Level 2: Events (requires Dataset) -> can be queried
Level 3: Queries/QueryResults, Recipients
Level 4: Triggers, Boards, SLOs, Markers
Level 5: Burn Alerts (requires SLO)
Level 6: Service Map Dependencies (requires trace data)
```

## Architecture

```
docs/
├── usage/
│   ├── triggers.md           # Human-readable docs, includes snippets
│   ├── recipients.md
│   ├── derived_columns.md
│   └── ...
└── examples/                  # Standalone executable snippets
    ├── __init__.py
    ├── recipients/
    │   ├── __init__.py
    │   └── basic_recipient.py    # Full CRUD lifecycle
    ├── triggers/
    │   ├── __init__.py
    │   └── basic_trigger.py      # Full CRUD lifecycle
    └── ...

tests/
├── unit/                      # Existing unit tests (unchanged)
└── integration/
    ├── conftest.py            # Shared fixtures (dataset, columns, events, sli, slo)
    ├── test_doc_examples.py   # Runs all docs/examples/**/*.py
    └── test_*.py              # Additional integration tests
```

## Example File Format

Each example file covers the **full CRUD lifecycle** (5 actions) with named sections:

```python
# docs/examples/triggers/basic_trigger.py
"""Trigger CRUD examples."""
from __future__ import annotations

from honeycomb import HoneycombClient, TriggerBuilder, Trigger, TriggerCreate, TriggerThreshold

# start_example:list
async def list_triggers(client: HoneycombClient, dataset: str) -> list[Trigger]:
    """List all triggers in a dataset."""
    return await client.triggers.list_async(dataset)
# end_example:list


# start_example:create
async def create_trigger(client: HoneycombClient, dataset: str) -> str:
    """Create a trigger using TriggerBuilder."""
    trigger = (
        TriggerBuilder("High Error Rate")
        .dataset(dataset)
        .last_30_minutes()
        .count()
        .threshold_gt(100)
        .every_15_minutes()
        .disabled()
        .build()
    )
    created = await client.triggers.create_async(dataset, trigger)
    return created.id
# end_example:create


# start_example:get
async def get_trigger(client: HoneycombClient, dataset: str, trigger_id: str) -> Trigger:
    """Get a trigger by ID."""
    return await client.triggers.get_async(dataset, trigger_id)
# end_example:get


# start_example:update
async def update_trigger(
    client: HoneycombClient, dataset: str, trigger_id: str
) -> Trigger:
    """Update a trigger's threshold."""
    existing = await client.triggers.get_async(dataset, trigger_id)
    updated = TriggerCreate(
        name=existing.name,
        threshold=TriggerThreshold(op=existing.threshold.op, value=200.0),
        frequency=existing.frequency,
        query=existing.query,
    )
    return await client.triggers.update_async(dataset, trigger_id, updated)
# end_example:update


# start_example:delete
async def delete_trigger(client: HoneycombClient, dataset: str, trigger_id: str) -> None:
    """Delete a trigger."""
    await client.triggers.delete_async(dataset, trigger_id)
# end_example:delete


# TEST_ASSERTIONS
async def test_lifecycle(client: HoneycombClient, dataset: str, trigger_id: str) -> None:
    """Verify the full lifecycle worked."""
    trigger = await client.triggers.get_async(dataset, trigger_id)
    assert trigger.id == trigger_id
    assert trigger.disabled is True


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, trigger_id: str) -> None:
    """Clean up resources (called even on test failure)."""
    try:
        await client.triggers.delete_async(dataset, trigger_id)
    except Exception:
        pass  # Already deleted or doesn't exist
```

## Integration Test Pattern

Tests import example functions and run the **full lifecycle** (5 actions):

```python
# tests/integration/test_doc_examples.py
class TestTriggerExamples:
    """Test trigger examples - full CRUD lifecycle."""

    @pytest.mark.asyncio
    async def test_trigger_lifecycle(self, client: HoneycombClient, ensure_dataset: str) -> None:
        """Test list -> create -> get -> update -> delete lifecycle."""
        from docs.examples.triggers.basic_trigger import (
            list_triggers,
            create_trigger,
            get_trigger,
            update_trigger,
            delete_trigger,
        )

        # List (before create)
        initial_triggers = await list_triggers(client, ensure_dataset)
        initial_count = len(initial_triggers)

        # Create
        trigger_id = await create_trigger(client, ensure_dataset)
        try:
            # Get
            trigger = await get_trigger(client, ensure_dataset, trigger_id)
            assert trigger.id == trigger_id

            # Update
            updated = await update_trigger(client, ensure_dataset, trigger_id)
            assert updated.threshold.value == 200.0

            # List (after create - verify it appears)
            triggers = await list_triggers(client, ensure_dataset)
            assert len(triggers) == initial_count + 1
        finally:
            # Delete (always, even on failure)
            await delete_trigger(client, ensure_dataset, trigger_id)
```

## Fixture Hierarchy

```python
# tests/integration/conftest.py

@pytest.fixture(scope="session")
async def api_key() -> str:
    """Load API key from environment."""
    ...

@pytest.fixture
async def client(api_key: str) -> AsyncIterator[HoneycombClient]:
    """Create authenticated client."""
    ...

@pytest.fixture
async def ensure_dataset(client: HoneycombClient) -> str:
    """Create test dataset if needed."""
    ...

@pytest.fixture
async def ensure_columns(client: HoneycombClient, ensure_dataset: str) -> list[str]:
    """Send events to create columns used in examples."""
    ...

@pytest.fixture
async def ensure_sli(client: HoneycombClient, ensure_dataset: str, ensure_columns: list[str]) -> str:
    """Create derived column for SLI (required for SLO tests)."""
    ...

@pytest.fixture
async def ensure_slo(client: HoneycombClient, ensure_dataset: str, ensure_sli: str) -> str:
    """Create SLO (required for Burn Alert tests)."""
    ...

@pytest.fixture
async def ensure_events_queryable(client: HoneycombClient, ensure_dataset: str) -> None:
    """Send events and wait for them to be queryable (~30s)."""
    ...
```

## Resource Coverage Matrix

### Target: 50%+ of code blocks tested

| Resource | API Methods | Example File | Test Coverage | Status |
|----------|-------------|--------------|---------------|--------|
| **datasets** | list, get, create, update, delete | basic_dataset.py | Full CRUD | Done |
| **columns** | list, get, create, update, delete | basic_column.py | Full CRUD | Done |
| **events** | send, send_batch | basic_event.py | Send + Query | **TODO** |
| **queries** | create, get, delete | basic_query.py | Full lifecycle | Partial |
| **query_results** | create, get, run, create_and_run | basic_query.py | Run patterns | Partial |
| **recipients** | list, get, create, update, delete | basic_recipient.py | Full CRUD | Done |
| **triggers** | list, get, create, update, delete | basic_trigger.py | Full CRUD | Partial |
| **boards** | list, get, create, update, delete | basic_board.py | Full CRUD | Partial |
| **slos** | list, get, create, update, delete | basic_slo.py | Full CRUD | Partial |
| **burn_alerts** | list, get, create, update, delete | basic_burn_alert.py | Full CRUD | Partial |
| **markers** | list, create, update, delete + settings | basic_marker.py | Full CRUD | Partial |
| **derived_columns** | list, get, create, update, delete | basic_derived_column.py | Full CRUD | Done |
| **api_keys** | list, get, create, update, delete | basic_api_key.py | Full CRUD | **TODO** |
| **environments** | list, get, create, update, delete | basic_environment.py | Full CRUD | **TODO** |
| **service_map** | create, get, get_result | basic_service_map.py | Full lifecycle | **TODO** |

### Priority Order (by dependency level)

1. **Level 0**: datasets (done), environments (TODO - needs management key)
2. **Level 1**: columns (done)
3. **Level 2**: events (TODO - send + query validation)
4. **Level 3**: queries (partial), recipients (done)
5. **Level 4**: triggers, boards, slos, markers (all partial - need full CRUD)
6. **Level 5**: burn_alerts (partial - need full CRUD)
7. **Level 6**: service_map (TODO)
8. **Management**: api_keys (TODO - needs management key)

## Implementation Phases

### Phase 1: Complete Existing Resources (Add update/delete)

Expand existing example files to include full CRUD lifecycle:

- [ ] `triggers/basic_trigger.py` - Add get, update examples
- [ ] `boards/basic_board.py` - Add get, update, delete examples
- [ ] `slos/basic_slo.py` - Add get, update, delete examples
- [ ] `burn_alerts/basic_burn_alert.py` - Add get, update, delete examples
- [ ] `markers/basic_marker.py` - Add get, update, delete, settings examples
- [ ] `queries/basic_query.py` - Add get, delete examples
- [ ] `columns/basic_column.py` - Add get, update, delete examples

### Phase 2: Add Missing Resources

Create example files for resources with no coverage:

- [ ] `events/basic_event.py` - send, send_batch, then query to verify
- [ ] `api_keys/basic_api_key.py` - Full CRUD (requires management key fixture)
- [ ] `environments/basic_environment.py` - Full CRUD (requires management key fixture)
- [ ] `service_map/basic_service_map.py` - create request, poll for result, get

### Phase 3: Update Documentation

For each resource doc (`docs/usage/*.md`):

1. Remove sync usage sections (mark as "TODO: auto-generate")
2. Remove error handling examples
3. Replace inline code blocks with include directives
4. Ensure all includes point to tested example files

### Phase 4: Auto-generate Sync Examples (Future)

Create a script to generate sync equivalents from async examples:

```python
# scripts/generate_sync_examples.py
# Transforms:
#   async def create_trigger(...) -> str:
#       ... await client.triggers.create_async(...)
# Into:
#   def create_trigger_sync(...) -> str:
#       ... client.triggers.create(...)
```

## Events Lifecycle Testing

Events are special - they can't be deleted, but they CAN be verified via queries:

```python
# docs/examples/events/basic_event.py

# start_example:send_single
async def send_event(client: HoneycombClient, dataset: str) -> None:
    """Send a single event."""
    await client.events.send_async(
        dataset,
        data={"service": "api", "duration_ms": 45, "status": 200}
    )
# end_example:send_single


# start_example:send_batch
async def send_batch(client: HoneycombClient, dataset: str) -> None:
    """Send multiple events in a batch."""
    events = [
        {"service": "api", "endpoint": "/users", "duration_ms": 45},
        {"service": "api", "endpoint": "/orders", "duration_ms": 120},
    ]
    await client.events.send_batch_async(dataset, events)
# end_example:send_batch


# start_example:verify_via_query
async def verify_events(client: HoneycombClient, dataset: str) -> QueryResult:
    """Verify events were ingested by running a query."""
    import asyncio
    await asyncio.sleep(30)  # Wait for events to be queryable

    query, result = await client.query_results.create_and_run_async(
        dataset,
        QueryBuilder().last_10_minutes().count().build()
    )
    assert result.data.rows[0]["COUNT"] > 0
    return result
# end_example:verify_via_query
```

## Service Map Dependencies Testing

Service map requires trace data and async result polling:

```python
# docs/examples/service_map/basic_service_map.py

# start_example:create_request
async def create_service_map_request(
    client: HoneycombClient, dataset: str
) -> str:
    """Create a service map dependency request."""
    request_id = await client.service_map_dependencies.create_async(
        dataset=dataset,
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now(),
    )
    return request_id
# end_example:create_request


# start_example:poll_result
async def get_service_map_result(
    client: HoneycombClient, dataset: str, request_id: str
) -> ServiceMapResult:
    """Poll for service map result (async operation)."""
    import asyncio

    for _ in range(30):  # Poll for up to 30 seconds
        result = await client.service_map_dependencies.get_result_async(
            dataset, request_id
        )
        if result.complete:
            return result
        await asyncio.sleep(1)

    raise TimeoutError("Service map request did not complete")
# end_example:poll_result
```

## Running Tests

```bash
# Run all integration tests
poetry run pytest tests/integration/ -v

# Run only doc example tests
poetry run pytest tests/integration/test_doc_examples.py -v

# Run specific resource tests
poetry run pytest tests/integration/test_doc_examples.py::TestTriggerExamples -v

# Run with live API (requires credentials)
HONEYCOMB_API_KEY=xxx poetry run pytest tests/integration/ -v
```

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Code blocks tested | 37/189 (19.6%) | 95/189 (50%+) |
| Resources with full CRUD tests | 4/15 | 12/15 |
| Inline code blocks (untested) | 152 | <80 |
| Sync sections in docs | ~14 | 0 (removed) |
| Error handling sections | ~2 | 0 (removed) |

## File Naming Conventions

| Pattern | Purpose |
|---------|---------|
| `docs/examples/<resource>/basic_<resource>.py` | Main CRUD example file |
| `# start_example:<operation>` | Extractable section (list, create, get, update, delete) |
| `test_lifecycle()` | Verification function |
| `cleanup()` | Resource cleanup (idempotent) |

## References

- [DEPENDENCIES.md](.claude/skills/live-test/DEPENDENCIES.md) - Resource dependency graph
- [validate_docs_examples.py](scripts/validate_docs_examples.py) - Syntax validator
- [MkDocs Include Plugin](https://github.com/mondeja/mkdocs-include-markdown-plugin) - Plugin documentation
