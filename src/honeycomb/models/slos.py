"""Pydantic models for Honeycomb SLOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SLI(BaseModel):
    """Service Level Indicator configuration."""

    alias: str | None = Field(default=None, description="Alias for the SLI")


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
