# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

**For usage examples, API reference, and setup:** See [README.md](README.md)
**For architecture decisions and implementation plan:** See [PLAN.md](PLAN.md)

## Ground Rules
* Always be concise
* Always be candidly honest
* Don't use emoji
* The plan isn't perfect, question it but tell me if you want to deviate from it

## Development Commands

```bash
# Quick start
make install-dev              # Setup environment
make ci                       # Run full CI pipeline (format, lint, test, validate-docs)

# Individual commands
make format                   # Format with ruff
make check                    # Lint + typecheck
make test                     # Run all tests
make validate-docs            # Validate documentation code examples
make docs-serve               # Preview docs at http://127.0.0.1:8000

# Run specific tests
poetry run pytest tests/unit/test_queries.py -v
poetry run pytest tests/unit/test_queries.py::test_create_query -v
```

Run `make help` for full command list.

## Development Workflow

After implementing each phase item (new resource, feature, etc.), you MUST:

1. **Run CI and fix all issues**
   ```bash
   make ci  # Runs format, lint, typecheck, test, validate-docs
   ```
   All checks must pass before moving forward.

2. **Update documentation**
   - Add/update docstrings (Google-style) for all new public methods
   - Add usage examples to relevant `docs/**/*.md` files
   - Update [README.md](README.md) if adding major features

3. **Update live API tests**
   - Modify [scripts/test_live_api.py](scripts/test_live_api.py) for new/changed resources
   - Test against real API with `make test-live` (requires `HONEYCOMB_API_KEY`)

## Critical Architecture Points

### Hybrid Wrapper + Generated Code Pattern

```
honeycomb/              (public API - edit this)
├── client.py           HoneycombClient
├── resources/          Resource classes (Triggers, SLOs, etc.)
├── models/             Pydantic models
└── _generated/         Auto-generated code (NEVER EDIT)
```

**⚠️ NEVER edit `src/honeycomb/_generated/` - it's auto-generated from OpenAPI spec**

To regenerate: `openapi-python-client generate --path api.yaml --output-path src/honeycomb/_generated`

### Async-First Design

Every resource method has two variants:
- `method_async()` - Async version (primary)
- `method()` - Sync wrapper (uses `asyncio.run()` internally)

### Resource Pattern

All resources extend [BaseResource](src/honeycomb/resources/base.py) and follow consistent CRUD:
- `list()` / `list_async()`
- `get()` / `get_async()`
- `create()` / `create_async()`
- `update()` / `update_async()`
- `delete()` / `delete_async()`

**Dataset-scoped resources** require `dataset` parameter: Triggers, SLOs, Queries
**Environment-scoped resources** don't: Boards, Recipients

## Testing Pattern

All tests use `respx` to mock HTTP requests:

```python
async def test_example(client: HoneycombClient, mock_api: MockRouter):
    mock_api.get("https://api.honeycomb.io/1/triggers/dataset").respond(
        json=[{"id": "t1", "name": "Trigger"}]
    )
    triggers = await client.triggers.list_async(dataset="dataset")
    assert len(triggers) == 1
```

**Key fixtures** ([tests/conftest.py](tests/conftest.py)):
- `mock_api` - respx MockRouter
- `client` - HoneycombClient with test key

## Important Implementation Details

### Query Execution Has 3 Patterns

1. **Saved query** - Create, then run separately
2. **Ephemeral query** - Run without saving (`spec=` parameter)
3. **Create and run** - Convenience method that does both: `create_and_run_async()`

All run methods poll automatically with exponential backoff.

### Query Time Range Constraints

- **Trigger queries**: `time_range` ≤ 3600 seconds (enforced by API)
- **Regular queries**: No hard limit

### Documentation Validation

Code examples in `docs/**/*.md` are validated in CI via [scripts/validate_docs_examples.py](scripts/validate_docs_examples.py). Run with `make validate-docs`.

## Code Quality Config

- **Ruff**: Excludes `_generated/`, line length 100, Python 3.10+ target
- **Mypy**: Strict on `src/` (except `_generated/`), Pydantic plugin enabled
- **Pytest**: Async mode auto-enabled, respx for HTTP mocking
