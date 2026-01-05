#!/usr/bin/env python3
"""
Patch Honeycomb OpenAPI spec to fix issues that prevent client generation.

This script applies fixes documented in OPENAPI_FIXES.md to make the spec
compatible with openapi-python-client.

NOTE: API Key permissions issue (Issue 6 in OPENAPI_FIXES.md) is NOT patched here
because we hand-craft those models. The OpenAPI spec appears to use incorrect
field names ('api_key_access' instead of 'permissions') but since we don't use
the generated client for v2 API keys, we've worked around it by using the
correct field names directly in our models.

Usage:
    ./scripts/patch-openapi.py [--input api.yaml] [--output api.yaml]
"""

import argparse
import shutil
import sys
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    """Load YAML file preserving order."""
    with open(path) as f:
        return yaml.safe_load(f)


def save_yaml(data: dict, path: Path) -> None:
    """Save YAML file with proper formatting."""
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def fix_array_without_items(schema: dict, path: str = "") -> int:
    """
    Fix arrays that are missing 'items' definition.
    Returns count of fixes applied.
    """
    fixes = 0

    if isinstance(schema, dict):
        # Check if this is an array without items
        if schema.get("type") == "array" and "items" not in schema and "prefixItems" not in schema:
            # Infer items type from example if available
            example = schema.get("example", [])
            if example and isinstance(example, list) and len(example) > 0:
                first_item = example[0]
                if isinstance(first_item, str):
                    schema["items"] = {"type": "string"}
                elif isinstance(first_item, int):
                    schema["items"] = {"type": "integer"}
                elif isinstance(first_item, float):
                    schema["items"] = {"type": "number"}
                elif isinstance(first_item, bool):
                    schema["items"] = {"type": "boolean"}
                elif isinstance(first_item, dict):
                    schema["items"] = {"type": "object"}
                else:
                    schema["items"] = {"type": "string"}  # fallback
            else:
                # Default to string if no example
                schema["items"] = {"type": "string"}
            print(f"  Fixed array without items at: {path}")
            fixes += 1

        # Recurse into nested structures
        for key, value in schema.items():
            if isinstance(value, dict):
                fixes += fix_array_without_items(value, f"{path}.{key}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        fixes += fix_array_without_items(item, f"{path}.{key}[{i}]")

    return fixes


def fix_allof_with_default(schema: dict, path: str = "") -> int:
    """
    Fix allOf that incorrectly combines $ref with default value.
    Returns count of fixes applied.
    """
    fixes = 0

    if isinstance(schema, dict):
        # Check for allOf with $ref and default
        if "allOf" in schema and isinstance(schema["allOf"], list):
            allof_items = schema["allOf"]
            has_ref = any("$ref" in item for item in allof_items if isinstance(item, dict))
            has_default = any("default" in item for item in allof_items if isinstance(item, dict))

            if has_ref and has_default and len(allof_items) == 2:
                # Extract just the $ref, drop the default (it's usually documented)
                ref_item = next(
                    (item for item in allof_items if isinstance(item, dict) and "$ref" in item),
                    None,
                )
                if ref_item:
                    # Replace allOf with just the $ref
                    del schema["allOf"]
                    schema["$ref"] = ref_item["$ref"]
                    print(f"  Fixed allOf with default at: {path}")
                    fixes += 1

        # Recurse into nested structures
        for key, value in schema.items():
            if isinstance(value, dict):
                fixes += fix_allof_with_default(value, f"{path}.{key}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        fixes += fix_allof_with_default(item, f"{path}.{key}[{i}]")

    return fixes


def fix_type_with_allof(schema: dict, schema_name: str = "") -> int:
    """
    Fix schemas that have both 'type: object' and 'allOf' at the same level.
    Returns count of fixes applied.
    """
    fixes = 0

    # Check for type + allOf at same level
    if (
        isinstance(schema, dict)
        and "type" in schema
        and "allOf" in schema
        and schema.get("type") == "object"
    ):
        allof = schema.get("allOf", [])
        properties = schema.get("properties", {})

        if properties:
            # Move properties into allOf as a new item
            del schema["type"]
            new_item = {"type": "object", "properties": properties}
            if "properties" in schema:
                del schema["properties"]

            # Append to allOf
            allof.append(new_item)
            schema["allOf"] = allof
            print(f"  Fixed type+allOf at: {schema_name}")
            fixes += 1

    return fixes


def fix_readonly_allof(schema: dict, path: str = "") -> int:
    """
    Fix allOf that combines $ref with readOnly (invalid pattern).
    Returns count of fixes applied.
    """
    fixes = 0

    if isinstance(schema, dict):
        # Check for property with allOf containing just a $ref, plus readOnly at same level
        if "allOf" in schema and "readOnly" in schema:
            allof = schema.get("allOf", [])
            if len(allof) == 1 and isinstance(allof[0], dict) and "$ref" in allof[0]:
                # Replace allOf with just $ref
                ref = allof[0]["$ref"]
                del schema["allOf"]
                schema["$ref"] = ref
                print(f"  Fixed readOnly+allOf at: {path}")
                fixes += 1

        # Recurse into nested structures
        for key, value in schema.items():
            if isinstance(value, dict):
                fixes += fix_readonly_allof(value, f"{path}.{key}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        fixes += fix_readonly_allof(item, f"{path}.{key}[{i}]")

    return fixes


def extract_inline_objects(spec: dict) -> int:
    """
    Extract inline object definitions to named schemas to avoid duplicate model names.
    Returns count of fixes applied.
    """
    fixes = 0
    schemas = spec.get("components", {}).get("schemas", {})

    # Fix JSONAPIError.errors[].source - extract to named schema
    if "JSONAPIError" in schemas:
        jsonapi_error = schemas["JSONAPIError"]
        errors_prop = jsonapi_error.get("properties", {}).get("errors", {})
        items = errors_prop.get("items", {})
        source_prop = items.get("properties", {}).get("source", {})

        if source_prop and "properties" in source_prop and "$ref" not in source_prop:
            # Create new schema for source
            schemas["JSONAPIErrorSource"] = {
                "type": "object",
                "description": "Source of a JSON:API error",
                "properties": source_prop.get("properties", {}),
            }
            # Replace inline with reference
            items["properties"]["source"] = {"$ref": "#/components/schemas/JSONAPIErrorSource"}
            print("  Extracted JSONAPIError.errors[].source to JSONAPIErrorSource")
            fixes += 1

    return fixes


def remove_problematic_titles(spec: dict) -> int:
    """
    Remove 'title' fields from allOf items that cause duplicate model names.
    Returns count of fixes applied.
    """
    fixes = 0
    schemas = spec.get("components", {}).get("schemas", {})

    # These schemas have title fields in allOf that cause duplicate names
    problematic_schemas = [
        "ExhaustionTimeBurnAlertListResponse",
        "ExhaustionTimeBurnAlertDetailResponse",
        "BudgetRateBurnAlertListResponse",
        "BudgetRateBurnAlertDetailResponse",
        "CreateExhaustionTimeBurnAlertRequest",
        "CreateBudgetRateBurnAlertRequest",
        "UpdateExhaustionTimeBurnAlertRequest",
        "UpdateBudgetRateBurnAlertRequest",
    ]

    for schema_name in problematic_schemas:
        if schema_name in schemas:
            schema = schemas[schema_name]
            if "allOf" in schema:
                for item in schema["allOf"]:
                    if isinstance(item, dict) and "title" in item:
                        del item["title"]
                        print(f"  Removed title from {schema_name} allOf item")
                        fixes += 1

    return fixes


def apply_all_fixes(spec: dict) -> int:
    """Apply all fixes to the OpenAPI spec."""
    total_fixes = 0

    print("Fixing arrays without items...")
    schemas = spec.get("components", {}).get("schemas", {})
    for name, schema in schemas.items():
        total_fixes += fix_array_without_items(schema, f"schemas.{name}")

    print("\nFixing allOf with default values...")
    for name, schema in schemas.items():
        total_fixes += fix_allof_with_default(schema, f"schemas.{name}")

    print("\nFixing type+allOf at same level...")
    for name, schema in schemas.items():
        total_fixes += fix_type_with_allof(schema, name)

    print("\nFixing readOnly+allOf patterns...")
    for name, schema in schemas.items():
        total_fixes += fix_readonly_allof(schema, f"schemas.{name}")

    print("\nExtracting inline objects...")
    total_fixes += extract_inline_objects(spec)

    print("\nRemoving problematic titles...")
    total_fixes += remove_problematic_titles(spec)

    return total_fixes


def main():
    parser = argparse.ArgumentParser(description="Patch Honeycomb OpenAPI spec")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("api.yaml"),
        help="Input OpenAPI spec file (default: api.yaml)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file (default: overwrite input)",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        default=False,
        help="Create backup of original file",
    )
    parser.add_argument(
        "--no-backup",
        dest="backup",
        action="store_false",
        help="Do not create backup (useful when input != output)",
    )
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or input_path

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Create backup
    if args.backup and output_path == input_path:
        backup_path = input_path.with_suffix(".yaml.original")
        if not backup_path.exists():
            shutil.copy(input_path, backup_path)
            print(f"Created backup: {backup_path}")

    print(f"Loading {input_path}...")
    spec = load_yaml(input_path)

    print("\nApplying fixes to OpenAPI spec...")
    total_fixes = apply_all_fixes(spec)

    print(f"\nSaving to {output_path}...")
    save_yaml(spec, output_path)

    print(f"\nDone! Applied {total_fixes} fixes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
