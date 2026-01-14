#!/usr/bin/env python3
"""Patch api.yaml for stable datamodel-codegen output.

This script applies patches to the Honeycomb OpenAPI spec to ensure
datamodel-codegen generates clean, usable class names instead of
auto-numbered names (Type1, Details1, AttributesAttributes1, etc.).

The patches are organized into modules:
- title_patches: Add titles to inline schemas
- enum_patches: Add x-enum-varnames for readable operator names
- field_patches: Fix required fields, patterns, defaults
- schema_extraction: Extract inline schemas to named schemas

Usage:
    ./scripts/patch_openapi_spec.py api.yaml api-patched.yaml
"""

import argparse
import sys
from pathlib import Path

import yaml

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from openapi_patches import ALL_PATCHES


def apply_patches(spec: dict) -> int:
    """Apply all patches to the OpenAPI spec.

    Args:
        spec: The OpenAPI spec as a dictionary. Modified in place.

    Returns:
        Total count of changes made across all patches.
    """
    total_patches = 0

    for patch in ALL_PATCHES:
        changes = patch(spec)
        total_patches += changes

    return total_patches


def main() -> int:
    """Patch api.yaml with all configured patches."""
    parser = argparse.ArgumentParser(
        description="Patch api.yaml for datamodel-codegen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", type=Path, help="Input api.yaml file")
    parser.add_argument("output", type=Path, help="Output patched api.yaml file")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed patch information"
    )
    args = parser.parse_args()

    print(f"Loading {args.input}...")
    with open(args.input) as f:
        spec = yaml.safe_load(f)

    print(f"Applying {len(ALL_PATCHES)} patches...")
    total_changes = apply_patches(spec)

    print(f"\nWriting {args.output}...")
    with open(args.output, "w") as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n[check] Applied patches with {total_changes} total changes")
    print(f"  Input:  {args.input}")
    print(f"  Output: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
