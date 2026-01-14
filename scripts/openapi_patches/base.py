"""Base class for OpenAPI spec patches.

This module provides the abstract base class that all patches inherit from,
enabling testable, composable patches for the Honeycomb OpenAPI spec.
"""

from abc import ABC, abstractmethod
from typing import Any


class BasePatch(ABC):
    """Abstract base class for OpenAPI spec patches.

    Each patch should:
    1. Have a descriptive name and description
    2. Check if it applies to the given spec
    3. Apply the patch and return the count of changes made

    Example usage:
        class MyPatch(BasePatch):
            name = "My Patch"
            description = "Adds a title to FooSchema"

            def applies_to(self, spec: dict) -> bool:
                return "FooSchema" in spec.get("components", {}).get("schemas", {})

            def apply(self, spec: dict) -> int:
                schemas = spec["components"]["schemas"]
                schemas["FooSchema"]["title"] = "Foo"
                return 1
    """

    name: str  # Human-readable name for logging
    description: str  # What this patch does

    @abstractmethod
    def applies_to(self, spec: dict[str, Any]) -> bool:
        """Check if this patch should be applied to the given spec.

        Args:
            spec: The OpenAPI spec as a dictionary.

        Returns:
            True if this patch applies to the spec, False otherwise.
        """
        ...

    @abstractmethod
    def apply(self, spec: dict[str, Any]) -> int:
        """Apply the patch to the spec.

        Args:
            spec: The OpenAPI spec as a dictionary. Modified in place.

        Returns:
            The number of changes made (for logging purposes).
        """
        ...

    def __call__(self, spec: dict[str, Any]) -> int:
        """Apply the patch if it applies to the spec.

        This allows patches to be used as callables.

        Returns:
            The number of changes made, or 0 if the patch doesn't apply.
        """
        if self.applies_to(spec):
            return self.apply(spec)
        return 0


def get_schemas(spec: dict[str, Any]) -> dict[str, Any]:
    """Get the schemas dict from an OpenAPI spec, creating it if needed.

    Args:
        spec: The OpenAPI spec dictionary.

    Returns:
        The components/schemas dictionary.
    """
    return spec.setdefault("components", {}).setdefault("schemas", {})
