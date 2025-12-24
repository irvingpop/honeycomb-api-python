"""Pydantic models for Honeycomb Queries."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QuerySpec(BaseModel):
    """Query specification for creating queries."""

    time_range: int = Field(description="Query time range in seconds")
    granularity: int | None = Field(default=None, description="Time granularity in seconds")
    calculations: list[dict] | None = Field(default=None, description="Calculations to perform")
    filters: list[dict] | None = Field(default=None, description="Query filters")
    breakdowns: list[str] | None = Field(default=None, description="Columns to group by")
    filter_combination: str | None = Field(
        default=None, description="How to combine filters (AND/OR)"
    )
    orders: list[dict] | None = Field(default=None, description="Result ordering")
    limit: int | None = Field(default=None, description="Result limit")
    havings: list[dict] | None = Field(default=None, description="Having clauses")

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data: dict[str, Any] = {"time_range": self.time_range}

        if self.granularity is not None:
            data["granularity"] = self.granularity
        if self.calculations:
            data["calculations"] = self.calculations
        if self.filters:
            data["filters"] = self.filters
        if self.breakdowns:
            data["breakdowns"] = self.breakdowns
        if self.filter_combination:
            data["filter_combination"] = self.filter_combination
        if self.orders:
            data["orders"] = self.orders
        if self.limit is not None:
            data["limit"] = self.limit
        if self.havings:
            data["havings"] = self.havings

        return data


class Query(BaseModel):
    """A Honeycomb query (response model)."""

    id: str = Field(description="Unique identifier")
    query_json: dict = Field(description="Query specification")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}


class QueryResult(BaseModel):
    """Results from a query execution.

    Note: data will be None if the query is still processing.
    Poll until data is not None to get the complete results.
    """

    data: list[dict] | None = Field(default=None, description="Query result rows (None if pending)")
    links: dict | None = Field(default=None, description="Pagination links")

    model_config = {"extra": "allow"}
