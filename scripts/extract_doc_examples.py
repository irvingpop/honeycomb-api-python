#!/usr/bin/env python3
"""Extract inline code blocks from documentation and convert to tested examples.

This script:
1. Scans all markdown files in docs/ for Python code blocks
2. Extracts code blocks that are NOT already include directives
3. Groups CRUD operations (create/read/update/delete) into single example files
4. Generates test scaffolding for all examples

Usage:
    python scripts/extract_doc_examples.py --analyze         # Show what would be extracted
    python scripts/extract_doc_examples.py --extract         # Extract to example files
    python scripts/extract_doc_examples.py --generate-tests  # Generate test file
    python scripts/extract_doc_examples.py --all             # Do everything
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# Patterns
INCLUDE_PATTERN = re.compile(r"^\s*\{%\s*include", re.MULTILINE)
ASYNC_WITH_CLIENT = re.compile(r"async\s+with\s+HoneycombClient")
SYNC_WITH_CLIENT = re.compile(r"with\s+HoneycombClient.*sync\s*=\s*True")

# Resources and their parameters
RESOURCE_CONFIG = {
    "triggers": {"params": "dataset: str", "scope": "dataset"},
    "queries": {"params": "dataset: str", "scope": "dataset"},
    "query_results": {"params": "dataset: str", "scope": "dataset"},
    "slos": {"params": "dataset: str", "scope": "dataset"},
    "burn_alerts": {"params": "dataset: str", "scope": "dataset"},
    "columns": {"params": "dataset: str", "scope": "dataset"},
    "datasets": {"params": "", "scope": "environment"},
    "markers": {"params": "dataset: str", "scope": "dataset"},
    "derived_columns": {"params": "dataset: str", "scope": "dataset"},
    "boards": {"params": "", "scope": "environment"},
    "recipients": {"params": "", "scope": "environment"},
    "events": {"params": "dataset: str", "scope": "dataset"},
    "environments": {"params": "", "scope": "environment"},
    "api_keys": {"params": "", "scope": "environment"},
    "service_map": {"params": "", "scope": "environment"},
}

# Files/sections to skip (illustrative only, not testable)
SKIP_FILES = {
    "advanced/retry-config.md",  # Configuration examples
    "advanced/error-handling.md",  # Error handling patterns
    "advanced/async-sync.md",  # Sync/async comparison
    "api/client.md",  # Client configuration
    "api/exceptions.md",  # Exception reference
    "getting-started/installation.md",  # Installation commands
    "getting-started/authentication.md",  # Auth patterns
}


@dataclass
class CodeBlock:
    """Represents an extracted code block."""

    file_path: Path
    line_start: int
    line_end: int
    code: str
    is_async: bool
    is_sync: bool
    is_include: bool
    tab_context: str | None
    section_title: str | None
    indent_level: int = 0

    @property
    def is_standalone(self) -> bool:
        """Check if this is a standalone snippet (has client creation)."""
        return bool(ASYNC_WITH_CLIENT.search(self.code) or SYNC_WITH_CLIENT.search(self.code))

    @property
    def resource_type(self) -> str | None:
        """Infer the resource type from the code."""
        for resource in RESOURCE_CONFIG.keys():
            pattern = rf"client\.{resource}\."
            if re.search(pattern, self.code):
                return resource
        return None

    @property
    def operation_type(self) -> str | None:
        """Infer the operation type from the code."""
        ops = [
            ("create_and_run", ".create_and_run"),
            ("create", ".create"),
            ("list", ".list"),
            ("get", ".get"),
            ("update", ".update"),
            ("delete", ".delete"),
            ("run", ".run"),
            ("send", ".send"),
        ]
        for op_name, pattern in ops:
            if pattern in self.code:
                return op_name
        return None

    @property
    def is_testable(self) -> bool:
        """Check if this block represents testable code."""
        # Must have a resource and operation
        if not self.resource_type or not self.operation_type:
            return False
        # Skip pure snippet examples (no actual API call pattern)
        if "..." in self.code and self.code.count("...") > 2:
            return False
        return True

    @property
    def variant(self) -> str:
        """Get variant name (async/sync)."""
        if self.tab_context:
            return self.tab_context.lower()
        if self.is_sync:
            return "sync"
        return "async"


@dataclass
class DocFile:
    """Represents a documentation file with its code blocks."""

    path: Path
    blocks: list[CodeBlock] = field(default_factory=list)

    @property
    def inline_blocks(self) -> list[CodeBlock]:
        return [b for b in self.blocks if not b.is_include]

    @property
    def testable_blocks(self) -> list[CodeBlock]:
        return [b for b in self.inline_blocks if b.is_testable]


def extract_code_blocks(md_file: Path) -> list[CodeBlock]:
    """Extract all Python code blocks from a markdown file."""
    blocks = []
    lines = md_file.read_text().splitlines()

    in_code_block = False
    current_block_lines: list[str] = []
    block_start_line = 0
    block_indent = 0
    tab_context = None
    last_heading = None

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("#"):
            last_heading = stripped.lstrip("#").strip()

        if stripped.startswith('=== "Async"'):
            tab_context = "Async"
        elif stripped.startswith('=== "Sync"'):
            tab_context = "Sync"

        if stripped.startswith("```python"):
            in_code_block = True
            block_start_line = i + 1
            current_block_lines = []
            block_indent = len(line) - len(line.lstrip())
            i += 1
            continue

        if stripped == "```" and in_code_block:
            in_code_block = False
            dedented = []
            for code_line in current_block_lines:
                if code_line.startswith(" " * block_indent):
                    dedented.append(code_line[block_indent:])
                elif code_line.strip() == "":
                    dedented.append("")
                else:
                    dedented.append(code_line)

            code = "\n".join(dedented)
            is_include = bool(INCLUDE_PATTERN.search(code))

            blocks.append(
                CodeBlock(
                    file_path=md_file,
                    line_start=block_start_line,
                    line_end=i,
                    code=code,
                    is_async="async " in code or "await " in code,
                    is_sync=bool(SYNC_WITH_CLIENT.search(code)),
                    is_include=is_include,
                    tab_context=tab_context if block_indent > 0 else None,
                    section_title=last_heading,
                    indent_level=block_indent,
                )
            )

            if block_indent == 0:
                tab_context = None

            i += 1
            continue

        if in_code_block:
            current_block_lines.append(line)

        i += 1

    return blocks


def analyze_docs(docs_dir: Path) -> list[DocFile]:
    """Analyze all documentation files."""
    doc_files = []

    for md_file in sorted(docs_dir.rglob("*.md")):
        if "examples" in md_file.parts:
            continue

        rel_path = str(md_file.relative_to(docs_dir))
        if rel_path in SKIP_FILES:
            continue

        blocks = extract_code_blocks(md_file)
        if blocks:
            doc_files.append(DocFile(path=md_file, blocks=blocks))

    return doc_files


def print_analysis(doc_files: list[DocFile], docs_dir: Path) -> None:
    """Print analysis of code blocks."""
    total_inline = 0
    total_testable = 0
    total_include = 0

    # Group by resource for summary
    resource_ops: dict[str, set[str]] = defaultdict(set)

    print("\n" + "=" * 70)
    print("DOCUMENTATION CODE BLOCK ANALYSIS")
    print("=" * 70)

    for doc_file in doc_files:
        rel_path = doc_file.path.relative_to(docs_dir)
        inline = doc_file.inline_blocks
        testable = doc_file.testable_blocks
        includes = [b for b in doc_file.blocks if b.is_include]

        if not inline and not includes:
            continue

        print(f"\n{rel_path}")
        print("-" * len(str(rel_path)))

        if includes:
            print(f"  Already using includes: {len(includes)}")
            total_include += len(includes)

        if testable:
            print(f"  Testable blocks: {len(testable)}")
            total_testable += len(testable)

            for block in testable:
                resource = block.resource_type
                op = block.operation_type
                variant = f" [{block.variant}]"
                resource_ops[resource].add(op)
                print(f"    Line {block.line_start}: {resource}.{op}{variant}")

        skipped = len(inline) - len(testable)
        if skipped > 0:
            print(f"  Skipped (illustrative): {skipped}")

        total_inline += len(inline)

    print("\n" + "=" * 70)
    print("EXTRACTION PLAN BY RESOURCE")
    print("=" * 70)

    for resource in sorted(resource_ops.keys()):
        ops = sorted(resource_ops[resource])
        print(f"\n{resource}/")
        print(f"  Operations: {', '.join(ops)}")
        print(f"  -> docs/examples/{resource}/extracted_{resource}.py")

    print("\n" + "=" * 70)
    print(f"SUMMARY:")
    print(f"  Include directives (already done): {total_include}")
    print(f"  Testable blocks to extract: {total_testable}")
    print(f"  Illustrative blocks (skipped): {total_inline - total_testable}")
    print("=" * 70)


def extract_inner_code(block: CodeBlock) -> str:
    """Extract the inner code from a standalone block, removing client wrapper."""
    code = block.code.strip()

    if not block.is_standalone:
        return code

    lines = code.split("\n")
    inner_lines = []
    in_with = False
    with_indent = 0

    for line in lines:
        if ASYNC_WITH_CLIENT.search(line) or SYNC_WITH_CLIENT.search(line):
            in_with = True
            with_indent = len(line) - len(line.lstrip()) + 4
            continue
        if in_with:
            if line.strip() and len(line) - len(line.lstrip()) < with_indent and not line.strip().startswith("#"):
                in_with = False
            else:
                if line.startswith(" " * with_indent):
                    inner_lines.append(line[with_indent:])
                elif line.strip() == "":
                    inner_lines.append("")
                else:
                    inner_lines.append(line)

    return "\n".join(inner_lines).strip() if inner_lines else code


def generate_example_file(resource: str, blocks: list[CodeBlock]) -> str:
    """Generate an example file for a resource with all CRUD operations."""

    config = RESOURCE_CONFIG.get(resource, {"params": "dataset: str", "scope": "dataset"})
    extra_params = config["params"]

    # Collect unique operations (prefer async versions)
    ops_by_type: dict[str, CodeBlock] = {}
    for block in blocks:
        op = block.operation_type
        key = f"{op}_{block.variant}"

        # Prefer async version, but keep sync if that's all we have
        if key not in ops_by_type:
            ops_by_type[key] = block
        elif block.variant == "async" and ops_by_type[key].variant == "sync":
            ops_by_type[key] = block

    # Generate imports based on what we need
    imports = ["from __future__ import annotations", "", "from honeycomb import HoneycombClient"]

    # Generate functions
    functions = []
    test_assertions = []

    for key, block in sorted(ops_by_type.items()):
        op = block.operation_type
        variant = block.variant
        func_name = f"{op}_{variant}" if variant == "sync" else op

        inner_code = extract_inner_code(block)

        # Build function signature
        params = ["client: HoneycombClient"]
        if extra_params:
            params.append(extra_params)

        param_str = ", ".join(params)

        # Determine return type from code analysis
        return_type = "None"
        if f"{resource} =" in inner_code or "result =" in inner_code or "query =" in inner_code:
            return_type = "Any"

        # Indent code
        indented = "\n".join("    " + line if line.strip() else "" for line in inner_code.split("\n"))

        # Generate async or sync function
        async_prefix = "async " if variant == "async" else ""

        func = f'''
# start_example:{func_name}
{async_prefix}def {func_name}({param_str}) -> {return_type}:
    """{'Async ' if variant == 'async' else ''}{op.replace('_', ' ').title()} {resource}.

    Source: {block.file_path.name}:{block.line_start}
    """
{indented}
# end_example:{func_name}
'''
        functions.append(func.strip())

        # Generate test assertion
        if op in ("create", "list", "get"):
            test_assertions.append(f"    # Test {func_name}: verify it runs without error")

    content = f'''"""Extracted examples for {resource}.

These examples were auto-extracted from documentation.
Run integration tests to verify they work against the live API.
"""

{chr(10).join(imports)}

{"".join(functions)}


# TEST_ASSERTIONS
async def test_examples(client: HoneycombClient{", dataset: str" if extra_params else ""}) -> None:
    """Run basic validation on extracted examples."""
{chr(10).join(test_assertions) if test_assertions else "    pass"}


# CLEANUP
async def cleanup(client: HoneycombClient{", dataset: str" if extra_params else ""}) -> None:
    """Clean up any resources created by examples."""
    pass
'''
    return content


def generate_test_file(doc_files: list[DocFile]) -> str:
    """Generate a test file that runs all extracted examples."""

    # Group by resource
    resource_blocks: dict[str, list[CodeBlock]] = defaultdict(list)
    for doc_file in doc_files:
        for block in doc_file.testable_blocks:
            resource = block.resource_type
            if resource:
                resource_blocks[resource].append(block)

    test_classes = []
    for resource in sorted(resource_blocks.keys()):
        blocks = resource_blocks[resource]
        ops = {b.operation_type for b in blocks}

        config = RESOURCE_CONFIG.get(resource, {"params": "dataset: str", "scope": "dataset"})
        needs_dataset = bool(config["params"])

        class_name = "".join(word.title() for word in resource.split("_"))

        fixture_param = "ensure_dataset: str" if needs_dataset else ""
        dataset_arg = ", ensure_dataset" if needs_dataset else ""

        test_methods = []
        for op in sorted(ops):
            method = f'''
    @pytest.mark.asyncio
    async def test_{op}(self, client: HoneycombClient{", " + fixture_param if fixture_param else ""}) -> None:
        """Test {op} operation for {resource}."""
        from docs.examples.{resource}.extracted_{resource} import {op}
        # await {op}(client{dataset_arg})
        pass  # TODO: Enable after manual review
'''
            test_methods.append(method)

        test_class = f'''
class TestExtracted{class_name}:
    """Tests for extracted {resource} examples."""
{"".join(test_methods)}
'''
        test_classes.append(test_class)

    content = f'''"""Auto-generated tests for extracted documentation examples.

These tests verify that code examples in documentation actually work.
Each test imports from docs/examples/<resource>/extracted_<resource>.py
"""

from __future__ import annotations

import pytest

from honeycomb import HoneycombClient

{"".join(test_classes)}
'''
    return content


def main():
    parser = argparse.ArgumentParser(description="Extract documentation code examples")
    parser.add_argument("--analyze", action="store_true", help="Analyze and show extraction plan")
    parser.add_argument("--extract", action="store_true", help="Extract code blocks to example files")
    parser.add_argument("--generate-tests", action="store_true", help="Generate test scaffolding")
    parser.add_argument("--all", action="store_true", help="Do all operations")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files")

    args = parser.parse_args()

    if args.all:
        args.analyze = args.extract = args.generate_tests = True

    if not any([args.analyze, args.extract, args.generate_tests]):
        args.analyze = True

    docs_dir = Path("docs")
    examples_dir = docs_dir / "examples"
    tests_dir = Path("tests/integration")

    if not docs_dir.exists():
        print("Error: docs/ directory not found")
        return 1

    doc_files = analyze_docs(docs_dir)

    if args.analyze:
        print_analysis(doc_files, docs_dir)

    if args.extract:
        print("\n" + "=" * 70)
        print("EXTRACTING CODE BLOCKS")
        print("=" * 70)

        resource_blocks: dict[str, list[CodeBlock]] = defaultdict(list)
        for doc_file in doc_files:
            for block in doc_file.testable_blocks:
                resource = block.resource_type
                if resource:
                    resource_blocks[resource].append(block)

        for resource, blocks in sorted(resource_blocks.items()):
            content = generate_example_file(resource, blocks)
            file_path = examples_dir / resource / f"extracted_{resource}.py"

            print(f"\n{file_path}")
            print(f"  Operations: {', '.join(sorted({b.operation_type for b in blocks}))}")
            print(f"  Blocks: {len(blocks)}")

            if not args.dry_run:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                print("  Written!")
            else:
                print("  (dry run - not written)")

    if args.generate_tests:
        print("\n" + "=" * 70)
        print("GENERATING TEST FILE")
        print("=" * 70)

        content = generate_test_file(doc_files)
        test_file = tests_dir / "test_extracted_examples.py"

        print(f"\n{test_file}")

        if not args.dry_run:
            test_file.write_text(content)
            print("  Written!")
        else:
            print("  (dry run - not written)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
