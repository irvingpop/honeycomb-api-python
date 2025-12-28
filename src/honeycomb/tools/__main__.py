"""CLI for Honeycomb tool definition generator.

Usage:
    python -m honeycomb.tools generate --output tools.json
    python -m honeycomb.tools generate --resource triggers --output triggers.json
    python -m honeycomb.tools validate tools.json
    python -m honeycomb.tools generate --format python --output definitions.py
"""

import argparse
import json
import sys
from pathlib import Path

from honeycomb.tools.descriptions import validate_description
from honeycomb.tools.generator import (
    export_tools_json,
    export_tools_python,
    generate_all_tools,
    generate_tools_for_resource,
)
from honeycomb.tools.schemas import validate_schema, validate_tool_name


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate tool definitions.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Generate tools
        if args.resource:
            tools = generate_tools_for_resource(args.resource)
            print(f"Generated {len(tools)} tool definitions for resource '{args.resource}'")
        else:
            tools = generate_all_tools()
            print(f"Generated {len(tools)} tool definitions")

        # Export to file
        output_path = args.output
        if args.format == "json":
            export_tools_json(tools, output_path)
            print(f"Exported to JSON: {output_path}")
        elif args.format == "python":
            export_tools_python(tools, output_path)
            print(f"Exported to Python module: {output_path}")
        else:
            print(f"Error: Unknown format '{args.format}'", file=sys.stderr)
            return 1

        return 0

    except Exception as e:
        print(f"Error generating tools: {e}", file=sys.stderr)
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate tool definitions from a file.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Load tools from file
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            return 1

        with open(path) as f:
            data = json.load(f)

        # Extract tools list
        if isinstance(data, dict) and "tools" in data:
            tools = data["tools"]
        elif isinstance(data, list):
            tools = data
        else:
            print("Error: Invalid format. Expected {'tools': [...]} or [...]", file=sys.stderr)
            return 1

        # Validate each tool
        errors = []
        for i, tool in enumerate(tools):
            tool_name = tool.get("name", f"<tool {i}>")

            # Validate name
            try:
                validate_tool_name(tool_name)
            except ValueError as e:
                errors.append(f"{tool_name}: {e}")

            # Validate description
            description = tool.get("description")
            if description:
                try:
                    validate_description(description)
                except ValueError as e:
                    errors.append(f"{tool_name}: {e}")
            else:
                errors.append(f"{tool_name}: Missing description")

            # Validate schema
            schema = tool.get("input_schema")
            if schema:
                try:
                    validate_schema(schema)
                except ValueError as e:
                    errors.append(f"{tool_name}: Schema error: {e}")
            else:
                errors.append(f"{tool_name}: Missing input_schema")

        # Report results
        if errors:
            print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        else:
            print(f"✓ Validation passed for {len(tools)} tool definitions")
            return 0

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.file}: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error validating tools: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Honeycomb API tool definition generator for Claude",
        prog="python -m honeycomb.tools",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate tool definitions",
    )
    gen_parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output file path",
    )
    gen_parser.add_argument(
        "--resource",
        "-r",
        choices=["triggers", "slos", "burn_alerts"],
        help="Generate tools for specific resource only",
    )
    gen_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "python"],
        default="json",
        help="Output format (default: json)",
    )

    # Validate command
    val_parser = subparsers.add_parser(
        "validate",
        help="Validate tool definitions from file",
    )
    val_parser.add_argument(
        "file",
        help="Path to tool definitions file (JSON)",
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to command handler
    if args.command == "generate":
        return cmd_generate(args)
    elif args.command == "validate":
        return cmd_validate(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
