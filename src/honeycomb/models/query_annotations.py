"""Pydantic models for Honeycomb Query Annotations."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QueryAnnotationSource(str, Enum):
    """Source of a query annotation."""

    QUERY = "query"  # Created via Query Annotations API
    BOARD = "board"  # Auto-created by board creation


class QueryAnnotationCreate(BaseModel):
    """Model for creating a new query annotation.

    Query Annotations add name and description metadata to queries
    for collaboration and documentation.
    """

    name: str = Field(description="Name for the query (1-320 chars)")
    query_id: str = Field(description="ID of the query this annotation describes")
    description: str | None = Field(
        default=None, description="Description of the query (max 1023 chars)"
    )

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {
            "name": self.name,
            "query_id": self.query_id,
        }

        if self.description:
            data["description"] = self.description

        return data


class QueryAnnotation(BaseModel):
    """A Honeycomb query annotation (response model).

    Query Annotations consist of a name and description associated
    with a query to add context when collaborating.
    """

    id: str = Field(description="Unique identifier")
    name: str = Field(description="Name for the query")
    query_id: str = Field(description="ID of the query this annotation describes")
    description: str | None = Field(default=None, description="Description of the query")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")
    source: QueryAnnotationSource | None = Field(
        default=None,
        description="Source of the annotation (query=manual, board=auto-created)",
    )

    model_config = {"extra": "allow"}
