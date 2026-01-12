"""Pydantic models for Honeycomb Environments (v2 team-scoped).

Re-exports generated models that match JSON:API structure exactly.
"""

from collections.abc import Sequence

from pydantic import Field

from honeycomb._generated_models import (
    CreateEnvironmentRequest,
    EnvironmentAttributesColor,
    EnvironmentColor,
    PaginationLinks,
    UpdateEnvironmentRequest,
)
from honeycomb._generated_models import (
    Environment as _EnvironmentGenerated,
)
from honeycomb._generated_models import (
    EnvironmentListResponse as _EnvironmentListResponseGenerated,
)
from honeycomb._generated_models import (
    EnvironmentResponse as _EnvironmentResponseGenerated,
)


class Environment(_EnvironmentGenerated):
    """Environment object with property accessors to hide JSON:API structure.

    Extends generated Environment to provide convenient access to nested attributes
    without requiring .attributes.field.
    """

    @property
    def name(self) -> str:
        """Get environment name from attributes."""
        return self.attributes.name

    @property
    def description(self) -> str:
        """Get environment description from attributes."""
        return self.attributes.description

    @property
    def color(self) -> EnvironmentColor | EnvironmentAttributesColor:
        """Get environment color from attributes."""
        return self.attributes.color

    @property
    def slug(self) -> str:
        """Get environment slug from attributes."""
        return self.attributes.slug

    @property
    def delete_protected(self) -> bool:
        """Get delete protection status from attributes.settings."""
        return self.attributes.settings.delete_protected


class EnvironmentResponse(_EnvironmentResponseGenerated):
    """Environment response wrapping the Environment with property accessors."""

    data: Environment = Field(...)


class EnvironmentListResponse(_EnvironmentListResponseGenerated):
    """Environment list response wrapping Environments with property accessors."""

    data: Sequence[Environment] = Field(...)  # type: ignore[assignment]
    links: PaginationLinks | None = None


# Convenience type aliases
EnvironmentCreate = CreateEnvironmentRequest
EnvironmentUpdate = UpdateEnvironmentRequest

__all__ = [
    "CreateEnvironmentRequest",
    "Environment",
    "EnvironmentColor",
    "EnvironmentCreate",  # Convenience alias
    "EnvironmentUpdate",  # Convenience alias
    "EnvironmentListResponse",
    "EnvironmentResponse",
    "UpdateEnvironmentRequest",
]
