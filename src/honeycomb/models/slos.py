"""Pydantic models for Honeycomb SLOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SLI(BaseModel):
    """Service Level Indicator configuration.

    The SLI references a derived column by alias. You can either:
    1. Reference an existing derived column: just provide alias
    2. Create a new derived column inline: provide alias + expression

    When expression is provided, a new derived column will be created automatically
    before the SLO is created.
    """

    alias: str | None = Field(
        default=None, description="Alias for the derived column (existing or new)"
    )
    expression: str | None = Field(
        default=None,
        description="If provided, creates a new derived column with this expression. "
        "If omitted, uses an existing derived column with the given alias.",
    )
    description: str | None = Field(
        default=None,
        description="Description for the new derived column (only used when expression is provided)",
    )


class SLOCreate(BaseModel):
    """Model for creating a new SLO."""

    name: str = Field(description="Human-readable name for the SLO")
    description: str | None = Field(default=None, description="Longer description")
    sli: SLI = Field(description="SLI configuration")
    time_period_days: int = Field(
        default=30,
        ge=1,
        le=90,
        description="Time period for the SLO in days (1-90)",
    )
    target_per_million: int = Field(
        ge=0,
        le=1000000,
        description="Target success rate per million (e.g., 999000 = 99.9%)",
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {
            "name": self.name,
            "sli": {},
            "time_period_days": self.time_period_days,
            "target_per_million": self.target_per_million,
        }

        if self.description:
            data["description"] = self.description

        if self.sli.alias:
            data["sli"]["alias"] = self.sli.alias

        return data


class SLO(BaseModel):
    """A Honeycomb SLO (response model)."""

    id: str = Field(description="Unique identifier")
    name: str = Field(description="Human-readable name")
    description: str | None = Field(default=None, description="Longer description")
    sli: dict = Field(description="SLI configuration")
    time_period_days: int = Field(description="Time period in days")
    target_per_million: int = Field(description="Target per million")
    dataset_slugs: list[str] | None = Field(default=None, description="Datasets this SLO spans")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}

    @property
    def dataset(self) -> str | None:
        """Return the first dataset slug for convenience (SLOs can span multiple datasets)."""
        if self.dataset_slugs and len(self.dataset_slugs) > 0:
            return self.dataset_slugs[0]
        return None
