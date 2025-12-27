# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

| Resource | Purpose |
|----------|---------|
| [README.md](README.md) | Usage examples, API reference, setup |
| [PLAN.md](PLAN.md) | Architecture decisions, implementation plan |
| [api.yaml](api.yaml) | OpenAPI spec (source of truth for API) |

## Ground Rules

- Always be concise
- Always be candidly honest
- Don't use emoji
- The plan isn't perfect, question it but tell me if you want to deviate from it
- Don't pipe test output to `head` or `tail`
- Don't read files using bash tools, use your native built-in tools instead
- Recipient integrations: Only email/webhook testable - no slack/pagerduty/msteams configured
- All builders follow pattern: Builder → Bundle → create_from_bundle_async() (except Marker/Recipient which are simple)
- Breaking changes are acceptable before version 1.0
- Don't leave dead code lying around - either clean it up or add comments for future cleanup tasks

## Agents

Use these specialized agents for complex tasks:

| Agent | When to Use |
|-------|-------------|
| `live-tester` | "Test against the real API", "Verify this works in production" |
| `honeycomb-reviewer` | "Review my changes", "Check code quality before commit" |
| `resource-implementer` | "Add a new resource", "Implement the Pipelines API" |
| `test-fixer` | "Fix the failing tests", "Debug this test failure" |
| `api-explorer` | "What endpoints exist for X?", "What fields are required?" |

Invoke explicitly: "Use the `live-tester` agent to verify this works"

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/ci` | Run full CI pipeline |
| `/check` | Quick lint + typecheck |
| `/test <path>` | Run specific tests |
| `/live-test` | Run live API tests (requires credentials) |
| `/docs-serve` | Preview documentation |

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

After implementing changes, you MUST:

1. **Run CI**: `make ci` (or `/ci`) - all checks must pass
2. **Update docs**: Docstrings + `docs/usage/*.md` examples
3. **Test live API**: Use `live-tester` agent or `/live-test` for real API verification

For new resources, use the `resource-implementer` agent which handles the full checklist.

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

## Live API Testing Credentials

For testing against the real Honeycomb API:

1. Copy `.envrc.example` to `.envrc` and add your management key
2. Run `direnv allow`
3. The `live-tester` agent will create test environments automatically

Credentials are stored securely:
- `.envrc` - Your management key (gitignored)
- `.claude/secrets/` - Generated test API keys (gitignored)

See [.claude/skills/live-test/SKILL.md](.claude/skills/live-test/SKILL.md) for details.
