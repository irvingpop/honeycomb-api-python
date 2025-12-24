#!/usr/bin/env python3
"""Validate that documentation examples are syntactically correct."""

import ast
import sys
from pathlib import Path


def extract_python_code_blocks(markdown_file: Path) -> list[tuple[int, str]]:
    """Extract Python code blocks from markdown file.

    Handles both regular code blocks and Material tabbed code blocks.
    """
    code_blocks = []
    in_code_block = False
    current_block = []
    block_start_line = 0
    block_indent = 0

    with open(markdown_file) as f:
        for line_num, line in enumerate(f, 1):
            if line.strip().startswith("```python"):
                in_code_block = True
                block_start_line = line_num + 1
                current_block = []
                # Detect indentation level (for Material tabs)
                block_indent = len(line) - len(line.lstrip())
            elif line.strip() == "```" and in_code_block:
                in_code_block = False
                if current_block:
                    # De-indent the code block if it was indented (Material tabs)
                    dedented = []
                    for code_line in current_block:
                        if code_line.startswith(" " * block_indent):
                            dedented.append(code_line[block_indent:])
                        elif code_line.strip() == "":
                            dedented.append("")
                        else:
                            dedented.append(code_line)
                    code_blocks.append((block_start_line, "\n".join(dedented)))
            elif in_code_block:
                current_block.append(line.rstrip())

    return code_blocks


def validate_syntax(code: str, file_path: Path, line_num: int) -> bool:
    """Validate Python syntax."""
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}:{line_num + e.lineno - 1}")
        print(f"   {e.msg}")
        print(f"   Line: {e.text}")
        return False


def main():
    """Validate all documentation examples."""
    docs_dir = Path("docs")

    if not docs_dir.exists():
        print("❌ docs/ directory not found")
        return 1

    errors = 0
    total_blocks = 0

    for md_file in docs_dir.rglob("*.md"):
        code_blocks = extract_python_code_blocks(md_file)

        if not code_blocks:
            continue

        print(f"\n📄 Checking {md_file.relative_to(docs_dir)}...")

        for line_num, code in code_blocks:
            total_blocks += 1
            if not validate_syntax(code, md_file, line_num):
                errors += 1
                print(f"   Code block starting at line {line_num}")
            else:
                print(f"   ✓ Code block at line {line_num}")

    print(f"\n{'=' * 60}")
    if errors == 0:
        print(f"✅ All {total_blocks} code blocks have valid syntax!")
        return 0
    else:
        print(f"❌ Found {errors} syntax errors in {total_blocks} code blocks")
        return 1


if __name__ == "__main__":
    sys.exit(main())
