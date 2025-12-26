# Integration Tests and Documentation Sync Plan

This document outlines the design for keeping integration tests and documentation examples in sync, ensuring that all code examples in docs are tested against the real Honeycomb API.

## Problem Statement

Currently we have:
- **Documentation** (`docs/usage/*.md`) with code examples that may drift from reality
- **Unit tests** (`tests/unit/`) that mock the API but don't verify real behavior
- **Integration tests** (`tests/integration/`) that test against real API but duplicate doc examples

This leads to:
- Doc examples that don't actually work
- Duplicated maintenance burden
- No guarantee docs stay current with API changes

## Solution: Executable Documentation Examples

### Architecture Overview

```
docs/
├── usage/
│   ├── triggers.md           # Human-readable docs, includes snippets
│   ├── recipients.md
│   └── ...
└── examples/                  # NEW: Standalone executable snippets
    ├── __init__.py
    ├── triggers/
    │   ├── __init__.py
    │   ├── basic_trigger.py
    │   ├── trigger_with_filter.py
    │   ├── trigger_with_recipients.py
    │   └── trigger_crud.py
    ├── recipients/
    │   ├── __init__.py
    │   ├── email_recipient.py
    │   └── webhook_recipient.py
    ├── derived_columns/
    │   ├── __init__.py
    │   └── basic_derived_column.py
    └── queries/
        ├── __init__.py
        └── query_builder.py

tests/
├── unit/                      # Existing unit tests (unchanged)
└── integration/
    ├── conftest.py            # Shared fixtures (dataset, columns, events)
    ├── test_doc_examples.py   # NEW: Runs all docs/examples/**/*.py
    └── test_*.py              # Additional integration tests
```

### Example File Format

Each example file follows a standard structure:

```python
# docs/examples/triggers/basic_trigger.py
"""Basic trigger creation example.

This example demonstrates creating a simple count-based trigger
using the TriggerBuilder pattern.
"""
from __future__ import annotations

from honeycomb import HoneycombClient, TriggerBuilder

# EXAMPLE: basic_trigger_create
async def create_basic_trigger(client: HoneycombClient, dataset: str) -> str:
    """Create a simple count-based trigger.

    Args:
        client: Authenticated HoneycombClient
        dataset: Dataset slug to create trigger in

    Returns:
        The created trigger ID
    """
    trigger = (
        TriggerBuilder("High Request Count")
        .dataset(dataset)
        .last_30_minutes()
        .count()
        .threshold_gt(1000)
        .every_15_minutes()
        .disabled()  # Start disabled for safety
        .build()
    )

    created = await client.triggers.create_async(dataset, trigger)
    return created.id
# END_EXAMPLE


# TEST_ASSERTIONS (not included in docs)
async def test_assertions(client: HoneycombClient, dataset: str, trigger_id: str):
    """Verify the example worked correctly."""
    trigger = await client.triggers.get_async(dataset, trigger_id)
    assert trigger.name == "High Request Count"
    assert trigger.threshold.value == 1000
    assert trigger.disabled is True


# CLEANUP
async def cleanup(client: HoneycombClient, dataset: str, trigger_id: str):
    """Clean up resources created by example."""
    await client.triggers.delete_async(dataset, trigger_id)
```

### Documentation Inclusion

Docs reference examples using a custom include syntax:

```markdown
<!-- docs/usage/triggers.md -->

## Creating a Basic Trigger

Use the `TriggerBuilder` for a fluent API:

```python
{!examples/triggers/basic_trigger.py:basic_trigger_create!}
```

This creates a trigger that fires when the count exceeds 1000.
```

A preprocessor extracts the marked section at build time.

## Example Extraction Mechanism

### How It Works

The extraction happens during the MkDocs build process. There are three viable approaches:

### Option A: mkdocs-include-markdown-plugin (Recommended)

This existing MkDocs plugin supports extracting sections between markers.

**Installation:**
```bash
poetry add mkdocs-include-markdown-plugin --group dev
```

**mkdocs.yml:**
```yaml
plugins:
  - include-markdown:
      opening_tag: "{!"
      closing_tag: "!}"
```

**Example file markers:**
```python
# docs/examples/triggers/basic_trigger.py

# <!-- include: basic_trigger_create -->
trigger = (
    TriggerBuilder("High Request Count")
    .dataset(dataset)
    .last_30_minutes()
    .count()
    .threshold_gt(1000)
    .every_15_minutes()
    .build()
)
# <!-- end_include -->
```

**In markdown:**
```markdown
```python
{%
   include "../examples/triggers/basic_trigger.py"
   start="<!-- include: basic_trigger_create -->"
   end="<!-- end_include -->"
%}
```

### Option B: Custom Preprocessor Script (More Control)

A custom script that runs before MkDocs build, providing full control over extraction.

**scripts/extract_examples.py:**
```python
#!/usr/bin/env python3
"""Extract code examples from Python files into markdown snippets."""
from __future__ import annotations

import re
from pathlib import Path

EXAMPLES_DIR = Path("docs/examples")
SNIPPETS_DIR = Path("docs/_snippets")  # Generated, gitignored

# Pattern matches: # EXAMPLE: example_name ... # END_EXAMPLE
EXAMPLE_PATTERN = re.compile(
    r"# EXAMPLE: (\w+)\n(.*?)# END_EXAMPLE",
    re.DOTALL
)


def extract_examples(source_file: Path) -> dict[str, str]:
    """Extract all named examples from a Python file."""
    content = source_file.read_text()
    examples = {}

    for match in EXAMPLE_PATTERN.finditer(content):
        name = match.group(1)
        code = match.group(2)

        # Clean up the code:
        # - Remove leading/trailing blank lines
        # - Dedent to minimum indentation
        lines = code.strip().split("\n")
        if lines:
            # Find minimum indentation (excluding empty lines)
            min_indent = min(
                len(line) - len(line.lstrip())
                for line in lines if line.strip()
            )
            # Dedent all lines
            lines = [line[min_indent:] if len(line) > min_indent else line
                     for line in lines]

        examples[name] = "\n".join(lines)

    return examples


def process_all_examples():
    """Process all example files and generate snippets."""
    SNIPPETS_DIR.mkdir(parents=True, exist_ok=True)

    for py_file in EXAMPLES_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        examples = extract_examples(py_file)

        # Create snippet files
        rel_path = py_file.relative_to(EXAMPLES_DIR)
        for name, code in examples.items():
            snippet_path = SNIPPETS_DIR / rel_path.parent / f"{py_file.stem}_{name}.md"
            snippet_path.parent.mkdir(parents=True, exist_ok=True)
            snippet_path.write_text(f"```python\n{code}\n```\n")
            print(f"Generated: {snippet_path}")


if __name__ == "__main__":
    process_all_examples()
```

**In markdown (using standard include):**
```markdown
## Creating a Basic Trigger

Use the `TriggerBuilder` for a fluent API:

--8<-- "docs/_snippets/triggers/basic_trigger_basic_trigger_create.md"

This creates a trigger that fires when the count exceeds 1000.
```

**Build process:**
```bash
# Run before mkdocs build
python scripts/extract_examples.py
mkdocs build
```

### Option C: MkDocs Hook (Integrated)

A MkDocs hook that processes includes during the build.

**docs/hooks/example_include.py:**
```python
"""MkDocs hook for including example code snippets."""
from __future__ import annotations

import re
from pathlib import Path

INCLUDE_PATTERN = re.compile(r"\{!examples/([^:]+):(\w+)!\}")
EXAMPLE_PATTERN = re.compile(r"# EXAMPLE: (\w+)\n(.*?)# END_EXAMPLE", re.DOTALL)

_cache: dict[str, dict[str, str]] = {}


def extract_from_file(filepath: Path) -> dict[str, str]:
    """Extract all examples from a file, with caching."""
    key = str(filepath)
    if key not in _cache:
        content = filepath.read_text()
        _cache[key] = {}
        for match in EXAMPLE_PATTERN.finditer(content):
            name = match.group(1)
            code = match.group(2).strip()
            # Dedent
            lines = code.split("\n")
            if lines:
                min_indent = min(
                    (len(l) - len(l.lstrip()) for l in lines if l.strip()),
                    default=0
                )
                code = "\n".join(l[min_indent:] for l in lines)
            _cache[key][name] = code
    return _cache[key]


def on_page_markdown(markdown: str, page, config, files) -> str:
    """Process example includes in markdown."""
    docs_dir = Path(config["docs_dir"])

    def replace_include(match):
        filepath = docs_dir / "examples" / match.group(1)
        example_name = match.group(2)

        if not filepath.exists():
            return f"**ERROR: File not found: {filepath}**"

        examples = extract_from_file(filepath)
        if example_name not in examples:
            return f"**ERROR: Example '{example_name}' not found in {filepath}**"

        return examples[example_name]

    return INCLUDE_PATTERN.sub(replace_include, markdown)
```

**mkdocs.yml:**
```yaml
hooks:
  - docs/hooks/example_include.py
```

**In markdown:**
```markdown
```python
{!examples/triggers/basic_trigger.py:basic_trigger_create!}
```

### Option D: Sync Checker (Simplest)

Instead of extracting code, keep examples duplicated in both docs and test files, with a CI check that verifies they match. This is the simplest approach with the least tooling.

**How it works:**

1. Documentation has code blocks as usual (easy to write and preview)
2. Example files in `docs/examples/` have the same code with test harness
3. A validation script compares them and fails if they drift

**docs/usage/triggers.md (unchanged workflow):**
```markdown
## Creating a Basic Trigger

Use the `TriggerBuilder` for a fluent API:

```python
trigger = (
    TriggerBuilder("High Request Count")
    .dataset(dataset)
    .last_30_minutes()
    .count()
    .threshold_gt(1000)
    .every_15_minutes()
    .build()
)

created = await client.triggers.create_async(dataset, trigger)
```
```

**docs/examples/triggers/basic_trigger.py:**
```python
"""Basic trigger example - tested against live API."""
from honeycomb import HoneycombClient, TriggerBuilder

# EXAMPLE: basic_trigger_create
# DOCREF: docs/usage/triggers.md:35-47
trigger = (
    TriggerBuilder("High Request Count")
    .dataset(dataset)
    .last_30_minutes()
    .count()
    .threshold_gt(1000)
    .every_15_minutes()
    .build()
)

created = await client.triggers.create_async(dataset, trigger)
# END_EXAMPLE


async def run_example(client: HoneycombClient, dataset: str):
    """Execute the example and return created resource."""
    trigger = (
        TriggerBuilder("High Request Count")
        .dataset(dataset)
        .last_30_minutes()
        .count()
        .threshold_gt(1000)
        .every_15_minutes()
        .disabled()  # Disabled for testing
        .build()
    )
    return await client.triggers.create_async(dataset, trigger)


async def cleanup(client: HoneycombClient, dataset: str, trigger_id: str):
    await client.triggers.delete_async(dataset, trigger_id)
```

**scripts/validate_doc_sync.py:**
```python
#!/usr/bin/env python3
"""Verify that code examples in docs match their tested counterparts."""
from __future__ import annotations

import re
import sys
from pathlib import Path

EXAMPLE_PATTERN = re.compile(
    r"# EXAMPLE: (\w+)\n# DOCREF: ([^\n]+)\n(.*?)# END_EXAMPLE",
    re.DOTALL
)


def normalize_code(code: str) -> str:
    """Normalize code for comparison (strip whitespace, comments)."""
    lines = []
    for line in code.strip().split("\n"):
        # Remove trailing whitespace
        line = line.rstrip()
        # Skip empty lines and comments for comparison
        stripped = line.lstrip()
        if stripped and not stripped.startswith("#"):
            lines.append(line)
    return "\n".join(lines)


def extract_markdown_code_block(md_path: Path, start_line: int, end_line: int) -> str:
    """Extract code from a markdown file by line numbers."""
    lines = md_path.read_text().split("\n")
    # Adjust for 1-indexed line numbers, skip ```python and ```
    code_lines = lines[start_line:end_line-1]
    return "\n".join(code_lines)


def validate_sync() -> list[str]:
    """Check all examples match their doc references."""
    errors = []
    examples_dir = Path("docs/examples")

    for py_file in examples_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        content = py_file.read_text()

        for match in EXAMPLE_PATTERN.finditer(content):
            example_name = match.group(1)
            docref = match.group(2)  # e.g., "docs/usage/triggers.md:35-47"
            example_code = match.group(3)

            # Parse docref
            doc_path, line_range = docref.rsplit(":", 1)
            start, end = map(int, line_range.split("-"))
            doc_file = Path(doc_path)

            if not doc_file.exists():
                errors.append(f"{py_file}:{example_name} - Doc file not found: {doc_path}")
                continue

            doc_code = extract_markdown_code_block(doc_file, start, end)

            # Compare normalized versions
            if normalize_code(example_code) != normalize_code(doc_code):
                errors.append(
                    f"{py_file}:{example_name} - Code drift detected!\n"
                    f"  Example file and {docref} don't match.\n"
                    f"  Run: diff <(sed -n '{start},{end}p' {doc_path}) <(grep -A50 'EXAMPLE: {example_name}' {py_file})"
                )

    return errors


if __name__ == "__main__":
    errors = validate_sync()
    if errors:
        print("Code sync errors found:")
        for e in errors:
            print(f"\n{e}")
        sys.exit(1)
    print("All examples are in sync with documentation!")
    sys.exit(0)
```

**Benefits of Option D:**

1. **No tooling changes** - Docs are written normally with code blocks
2. **Easy to preview** - `mkdocs serve` works without preprocessing
3. **Explicit references** - `DOCREF:` makes the relationship clear
4. **Line-based comparison** - Easy to debug when things drift
5. **Gradual adoption** - Can add sync checking to existing docs incrementally

**Trade-offs:**

- Code is duplicated (but sync is enforced)
- Need to update two places when changing examples
- Line numbers in DOCREF can drift if docs are edited

### Recommendation

**Use Option D (Sync Checker)** for these reasons:

1. **Simplest to implement** - No new MkDocs plugins or hooks needed
2. **Familiar workflow** - Writers edit markdown normally, no special syntax
3. **Easy to preview** - `mkdocs serve` works without any preprocessing
4. **Gradual adoption** - Can add sync checking to existing docs one at a time
5. **Clear failure messages** - When sync fails, you know exactly which lines drifted
6. **Low maintenance** - No custom tooling to maintain beyond the sync checker script

The trade-off of maintaining code in two places is acceptable because:
- CI catches drift immediately
- The duplication is explicit and intentional
- Test files can have additional context (disabled flags, error handling) that shouldn't be in docs

### Validation Script (for Options A-C)

Regardless of approach, add validation to CI:

**scripts/validate_example_includes.py:**
```python
#!/usr/bin/env python3
"""Validate that all example includes resolve correctly."""
from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS_DIR = Path("docs")
EXAMPLES_DIR = DOCS_DIR / "examples"
INCLUDE_PATTERN = re.compile(r"\{!examples/([^:]+):(\w+)!\}")
EXAMPLE_PATTERN = re.compile(r"# EXAMPLE: (\w+)")

def get_available_examples() -> dict[str, set[str]]:
    """Scan example files for available example names."""
    available = {}
    for py_file in EXAMPLES_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        rel_path = str(py_file.relative_to(EXAMPLES_DIR))
        content = py_file.read_text()
        examples = set(EXAMPLE_PATTERN.findall(content))
        available[rel_path] = examples
    return available


def validate_includes() -> list[str]:
    """Find all broken includes in markdown files."""
    available = get_available_examples()
    errors = []

    for md_file in DOCS_DIR.rglob("*.md"):
        content = md_file.read_text()
        for match in INCLUDE_PATTERN.finditer(content):
            filepath = match.group(1)
            example_name = match.group(2)

            if filepath not in available:
                errors.append(f"{md_file}: File not found: examples/{filepath}")
            elif example_name not in available[filepath]:
                errors.append(
                    f"{md_file}: Example '{example_name}' not found in {filepath}. "
                    f"Available: {available[filepath]}"
                )

    return errors


def find_orphaned_examples() -> list[str]:
    """Find examples that are never included anywhere."""
    available = get_available_examples()
    used: set[tuple[str, str]] = set()

    for md_file in DOCS_DIR.rglob("*.md"):
        content = md_file.read_text()
        for match in INCLUDE_PATTERN.finditer(content):
            used.add((match.group(1), match.group(2)))

    orphans = []
    for filepath, examples in available.items():
        for example in examples:
            if (filepath, example) not in used:
                orphans.append(f"examples/{filepath}:{example}")

    return orphans


if __name__ == "__main__":
    errors = validate_includes()
    orphans = find_orphaned_examples()

    if errors:
        print("Broken includes:")
        for e in errors:
            print(f"  - {e}")

    if orphans:
        print("\nOrphaned examples (not included anywhere):")
        for o in orphans:
            print(f"  - {o}")

    if errors:
        sys.exit(1)

    print("All example includes are valid!")
    sys.exit(0)
```

### Test Runner

```python
# tests/integration/test_doc_examples.py
"""Run all documentation examples as integration tests."""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

import pytest

# Discover all example modules
EXAMPLES_PATH = Path(__file__).parent.parent.parent / "docs" / "examples"


def discover_examples():
    """Find all example modules with runnable functions."""
    examples = []
    for finder, name, ispkg in pkgutil.walk_packages([str(EXAMPLES_PATH)]):
        if not ispkg:
            examples.append(name)
    return examples


class TestDocExamples:
    """Test all documentation examples against live API."""

    @pytest.mark.asyncio
    async def test_triggers_basic(self, client, ensure_dataset, ensure_columns):
        """Test basic trigger example."""
        from docs.examples.triggers import basic_trigger

        trigger_id = await basic_trigger.create_basic_trigger(client, ensure_dataset)
        try:
            await basic_trigger.test_assertions(client, ensure_dataset, trigger_id)
        finally:
            await basic_trigger.cleanup(client, ensure_dataset, trigger_id)

    @pytest.mark.asyncio
    async def test_recipients_email(self, client):
        """Test email recipient example."""
        from docs.examples.recipients import email_recipient

        recipient_id = await email_recipient.create_email_recipient(client)
        try:
            await email_recipient.test_assertions(client, recipient_id)
        finally:
            await email_recipient.cleanup(client, recipient_id)

    # ... more tests for each example
```

### Fixture Dependencies (conftest.py)

Based on [DEPENDENCIES.md](.claude/skills/live-test/DEPENDENCIES.md), fixtures must be created in order:

```python
# tests/integration/conftest.py
"""Shared fixtures for integration tests."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from honeycomb import HoneycombClient


@pytest.fixture(scope="session")
def api_key() -> str:
    """Load API key from secrets."""
    secrets_file = Path(__file__).parent.parent.parent / ".claude" / "secrets" / "test.env"
    if secrets_file.exists():
        for line in secrets_file.read_text().splitlines():
            if line.startswith("export HONEYCOMB_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')

    key = os.environ.get("HONEYCOMB_API_KEY")
    if not key:
        pytest.skip("No API key available")
    return key


@pytest.fixture(scope="session")
def test_dataset() -> str:
    """Dataset name for integration tests."""
    return os.environ.get("HONEYCOMB_TEST_DATASET", "integration-test")


@pytest.fixture(scope="session")
def client(api_key: str) -> HoneycombClient:
    """Create async client for tests."""
    return HoneycombClient(api_key=api_key)


@pytest.fixture(scope="session")
def sync_client(api_key: str) -> HoneycombClient:
    """Create sync client for tests."""
    return HoneycombClient(api_key=api_key)


# Level 0: Dataset
@pytest.fixture(scope="session")
def ensure_dataset(client: HoneycombClient, test_dataset: str) -> str:
    """Ensure test dataset exists (Level 0)."""
    try:
        client.datasets.get(test_dataset)
    except Exception:
        client.datasets.create({"name": test_dataset, "slug": test_dataset})
    return test_dataset


# Level 1: Columns
@pytest.fixture(scope="session")
def ensure_columns(client: HoneycombClient, ensure_dataset: str) -> list[str]:
    """Create standard test columns (Level 1)."""
    columns = [
        {"key_name": "duration_ms", "type": "float"},
        {"key_name": "status_code", "type": "integer"},
        {"key_name": "service", "type": "string"},
        {"key_name": "endpoint", "type": "string"},
        {"key_name": "error", "type": "boolean"},
        {"key_name": "trace.trace_id", "type": "string"},
        {"key_name": "user_id", "type": "string"},
    ]
    created = []
    for col in columns:
        try:
            client.columns.create(ensure_dataset, col)
            created.append(col["key_name"])
        except Exception:
            pass  # Column may already exist
    return created


# Level 2: Events (with wait)
@pytest.fixture(scope="session")
def ensure_events(client: HoneycombClient, ensure_dataset: str, ensure_columns: list[str]) -> bool:
    """Send test events and wait for ingestion (Level 2)."""
    events = [
        {"service": "api", "endpoint": "/users", "duration_ms": 45.0, "status_code": 200},
        {"service": "api", "endpoint": "/users", "duration_ms": 120.0, "status_code": 200},
        {"service": "api", "endpoint": "/orders", "duration_ms": 1200.0, "status_code": 500, "error": True},
        {"service": "web", "endpoint": "/home", "duration_ms": 30.0, "status_code": 200},
    ]

    for event in events:
        client.events.create(ensure_dataset, event)

    # Wait for ingestion
    import time
    time.sleep(35)

    return True


# Fixture that requires data
@pytest.fixture
def with_data(ensure_events: bool) -> bool:
    """Marker fixture for tests that need queryable data."""
    return ensure_events
```

## Implementation Plan

### Phase 1: Fix Current Integration Tests (Immediate)

1. **Update conftest.py** with proper fixture hierarchy:
   - Add `ensure_columns` fixture
   - Add `ensure_events` fixture with 35-second wait
   - Update test dependencies

2. **Fix failing tests**:
   - Derived columns: Use expressions that reference created columns
   - Triggers with filters: Reference columns from `ensure_columns`

3. **Verify all 23 tests pass**

### Phase 2: Create Examples Directory Structure

1. **Create `docs/examples/` directory structure**:
   ```
   docs/examples/
   ├── __init__.py
   ├── triggers/
   ├── recipients/
   ├── derived_columns/
   ├── queries/
   └── slos/
   ```

2. **Migrate one example** (triggers/basic_trigger.py) as proof of concept

3. **Create test_doc_examples.py** to run example

### Phase 3: Migrate All Examples

For each resource type:

1. Extract existing code examples from `docs/usage/*.md`
2. Create corresponding `docs/examples/<resource>/*.py` files
3. Add test methods to `test_doc_examples.py`
4. Update markdown to include from example files

**Priority order** (based on complexity and usage):
1. Recipients (simple, no dataset dependency)
2. Triggers (most commonly used)
3. Derived Columns (new feature)
4. Queries (complex, multiple patterns)
5. SLOs (requires data)
6. Boards (environment-scoped)
7. Burn Alerts (requires SLO)

### Phase 4: Documentation Preprocessing

1. **Choose approach**:
   - Option A: MkDocs plugin (mkdocs-include-markdown-plugin)
   - Option B: Custom preprocessor script
   - Option C: Jinja2 templates

2. **Implement include syntax** for extracting example sections

3. **Update CI** to validate includes resolve correctly

### Phase 5: Validation and CI Integration

1. **Add validation script** (`scripts/validate_example_includes.py`):
   - Verify all `{!examples/...!}` references exist
   - Verify all example files have test coverage
   - Check for orphaned examples (not included anywhere)

2. **Update CI pipeline**:
   ```yaml
   - name: Validate doc examples
     run: poetry run python scripts/validate_example_includes.py

   - name: Run integration tests
     run: poetry run pytest tests/integration/ -v
     env:
       HONEYCOMB_API_KEY: ${{ secrets.HONEYCOMB_TEST_API_KEY }}
   ```

## File Naming Conventions

| Pattern | Purpose |
|---------|---------|
| `docs/examples/<resource>/<action>.py` | Main example file |
| `EXAMPLE: <name>` / `END_EXAMPLE` | Extractable section markers |
| `test_assertions()` | Verification function (not in docs) |
| `cleanup()` | Resource cleanup function |

## Testing Levels

| Test Type | Location | Purpose | When to Run |
|-----------|----------|---------|-------------|
| Unit tests | `tests/unit/` | Fast, mocked, catches regressions | Every commit |
| Doc validation | `scripts/validate_docs_examples.py` | Syntax check | Every commit |
| Integration tests | `tests/integration/` | Real API verification | PR merge, nightly |
| Example tests | `tests/integration/test_doc_examples.py` | Doc accuracy | PR merge, nightly |

## Migration Checklist

For each documentation page:

- [ ] Identify all code examples
- [ ] Create example files in `docs/examples/`
- [ ] Add markers for extractable sections
- [ ] Write test_assertions() and cleanup() functions
- [ ] Add test to test_doc_examples.py
- [ ] Update markdown to use include syntax
- [ ] Verify rendering in docs preview
- [ ] Run integration tests to verify

## Success Criteria

1. **All doc examples are tested** - Every code block in docs comes from a tested example file
2. **Single source of truth** - No duplicate code between docs and tests
3. **CI catches drift** - Broken examples fail the build
4. **Fast feedback** - Unit tests still run in seconds; integration tests run separately
5. **Easy maintenance** - Adding a new example is straightforward

## Open Questions

1. **Include syntax**: Use MkDocs plugin or custom solution?
2. **Session vs function scope**: Should fixtures be session-scoped (faster) or function-scoped (isolated)?
3. **Parallel execution**: Can integration tests run in parallel, or do they conflict?
4. **Cost management**: How to minimize API calls during testing?

## References

- [DEPENDENCIES.md](.claude/skills/live-test/DEPENDENCIES.md) - Resource dependency graph
- [validate_docs_examples.py](scripts/validate_docs_examples.py) - Existing syntax validator
- [MkDocs Include Plugin](https://github.com/mondeja/mkdocs-include-markdown-plugin) - Potential solution
