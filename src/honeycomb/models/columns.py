"""Pydantic models for Honeycomb Columns."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ColumnType(str, Enum):
    """Column data types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"


class ColumnCreate(BaseModel):
    """Model for creating a new column."""

    key_name: str = Field(description="Name of the column")
    type: ColumnType = Field(
        default=ColumnType.STRING, description="Type of data the column contains"
    )
    description: str | None = Field(default=None, description="Column description")
    hidden: bool = Field(
        default=False,
        description="If true, column is excluded from autocomplete and raw data field lists",
    )

    def model_dump_for_api(self) -> dict:
        """Serialize for API request."""
        data = {
            "key_name": self.key_name,
            "type": self.type.value,
            "hidden": self.hidden,
        }
        if self.description:
            data["description"] = self.description
        return data


class Column(BaseModel):
    """A Honeycomb column (response model)."""

    id: str = Field(description="Unique identifier")
    key_name: str = Field(description="Name of the column")
    type: ColumnType = Field(description="Type of data the column contains")
    description: str | None = Field(default=None, description="Column description")
    hidden: bool = Field(default=False, description="Whether column is hidden")
    last_written: datetime | None = Field(
        default=None, description="Timestamp when column was last written to"
    )
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}
