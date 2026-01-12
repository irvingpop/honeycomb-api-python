"""Pydantic models for Honeycomb SLOs."""

from __future__ import annotations

from typing import Any

from pydantic import field_validator

from honeycomb._generated_models import (
    SLO as _SLOGenerated,
)
from honeycomb._generated_models import (
    SLOCreate as _SLOCreateGenerated,
)
from honeycomb._generated_models import (
    SLOCreateSli,
    SLOSli,
    Tag,
)

# Re-export generated types for public API
__all__ = ["SLOCreate", "SLO", "SLOCreateSli", "SLOSli", "Tag"]


class SLOCreate(_SLOCreateGenerated):
    """Model for creating a new SLO.

    Extends the generated SLOCreate model from the OpenAPI spec.
    The sli field accepts either a string alias or an SLOCreateSli object.

    Example (string alias):
        >>> slo = SLOCreate(
        ...     name="API Availability",
        ...     sli="success_rate",
        ...     time_period_days=30,
        ...     target_per_million=999000,
        ... )

    Example (explicit SLOCreateSli):
        >>> slo = SLOCreate(
        ...     name="API Availability",
        ...     sli=SLOCreateSli(alias="success_rate"),
        ...     time_period_days=30,
        ...     target_per_million=999000,
        ... )
    """

    @field_validator("sli", mode="before")
    @classmethod
    def _convert_sli_string(cls, v: Any) -> SLOCreateSli:
        """Allow passing SLI alias as a string for convenience."""
        if isinstance(v, str):
            return SLOCreateSli(alias=v)
        return v


class SLO(_SLOGenerated):
    """A Honeycomb SLO (response model).

    Extends the generated SLO model with convenience properties.
    """

    @property
    def dataset(self) -> str | None:
        """Return the dataset to use for API operations.

        For multi-dataset SLOs, returns "__all__" (required for API operations).
        For single-dataset SLOs, returns the dataset slug.

        Returns:
            "__all__" for multi-dataset SLOs, single slug for single-dataset, None if unset.
        """
        if not self.dataset_slugs:
            return None
        if len(self.dataset_slugs) > 1:
            return "__all__"
        return self.dataset_slugs[0]

    @property
    def datasets(self) -> list[str]:
        """Return the list of datasets this SLO spans.

        Returns:
            List of dataset slugs (empty list if unset).
        """
        return self.dataset_slugs or []

    @property
    def target_percentage(self) -> float:
        """Convert target_per_million to percentage for display.

        Example:
            >>> slo.target_per_million = 999000
            >>> slo.target_percentage
            99.9

        Returns:
            Target as a percentage (e.g., 99.9 for 99.9%).
        """
        return self.target_per_million / 10000
