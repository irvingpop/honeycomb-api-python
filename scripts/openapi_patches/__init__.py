"""OpenAPI spec patches for Honeycomb API.

This package provides modular, testable patches for the Honeycomb OpenAPI spec.
The patches ensure datamodel-codegen generates clean, usable class names.

Usage:
    from openapi_patches import ALL_PATCHES

    for patch in ALL_PATCHES:
        changes = patch(spec)
        if changes:
            print(f"Applied {patch.name}: {changes} changes")
"""

from .base import BasePatch, get_schemas
from .discriminator_restructuring import DISCRIMINATOR_RESTRUCTURING_PATCHES
from .enum_patches import ENUM_PATCHES
from .field_patches import FIELD_PATCHES
from .schema_extraction import SCHEMA_EXTRACTION_PATCHES
from .title_patches import TITLE_PATCHES

# All patches in recommended application order
ALL_PATCHES: list[BasePatch] = [
    # Title patches first (naming)
    *TITLE_PATCHES,
    # Enum patches (x-enum-varnames)
    *ENUM_PATCHES,
    # Field patches (required, defaults, patterns)
    *FIELD_PATCHES,
    # Schema extraction patches (inline -> named schemas)
    *SCHEMA_EXTRACTION_PATCHES,
    # Discriminator restructuring (must run AFTER schema extraction)
    *DISCRIMINATOR_RESTRUCTURING_PATCHES,
]

__all__ = [
    "BasePatch",
    "get_schemas",
    "ALL_PATCHES",
    "TITLE_PATCHES",
    "ENUM_PATCHES",
    "FIELD_PATCHES",
    "SCHEMA_EXTRACTION_PATCHES",
    "DISCRIMINATOR_RESTRUCTURING_PATCHES",
]
