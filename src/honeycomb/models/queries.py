"""Pydantic models for Honeycomb Queries."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, field_validator

from honeycomb.models.query_builder import (
    VALID_COMPARE_OFFSETS,
    Calculation,
    Filter,
    FilterCombination,
    Having,
    Order,
)

if TYPE_CHECKING:
    from honeycomb.models.query_builder import QueryBuilder


def _normalize_calculation(calc: Calculation | dict[str, Any]) -> dict[str, Any]:
    """Convert a Calculation or dict to API dict format."""
    if isinstance(calc, Calculation):
        return calc.to_dict()
    return calc


def _normalize_filter(filt: Filter | dict[str, Any]) -> dict[str, Any]:
    """Convert a Filter or dict to API dict format."""
    if isinstance(filt, Filter):
        return filt.to_dict()
    return filt


def _normalize_order(order: Order | dict[str, Any]) -> dict[str, Any]:
    """Convert an Order or dict to API dict format."""
    if isinstance(order, Order):
        return order.to_dict()
    return order


def _normalize_having(having: Having | dict[str, Any]) -> dict[str, Any]:
    """Convert a Having or dict to API dict format."""
    if isinstance(having, Having):
        return having.to_dict()
    return having


def _normalize_filter_combination(combo: FilterCombination | str | None) -> str | None:
    """Convert a FilterCombination or string to API format."""
    if combo is None:
        return None
    if isinstance(combo, FilterCombination):
        return combo.value
    return combo


class QuerySpec(BaseModel):
    """Query specification for creating queries.

    Accepts both typed models and dicts for flexibility:
        >>> # Using dicts (backward compatible)
        >>> QuerySpec(calculations=[{"op": "COUNT"}])

        >>> # Using typed models
        >>> from honeycomb import Calculation, CalcOp
        >>> QuerySpec(calculations=[Calculation(op=CalcOp.COUNT)])

        >>> # Using the builder
        >>> QuerySpec.builder().count().last_1_hour().build()
    """

    time_range: int | None = Field(default=None, description="Query time range in seconds")
    start_time: int | None = Field(default=None, description="Absolute start time (Unix timestamp)")
    end_time: int | None = Field(default=None, description="Absolute end time (Unix timestamp)")
    granularity: int | None = Field(default=None, description="Time granularity in seconds")
    calculations: list[Calculation | dict[str, Any]] | None = Field(
        default=None, description="Calculations to perform"
    )
    filters: list[Filter | dict[str, Any]] | None = Field(default=None, description="Query filters")
    breakdowns: list[str] | None = Field(default=None, description="Columns to group by")
    filter_combination: FilterCombination | str | None = Field(
        default=None, description="How to combine filters (AND/OR)"
    )
    orders: list[Order | dict[str, Any]] | None = Field(default=None, description="Result ordering")
    limit: int | None = Field(
        default=None,
        description="Result limit (max 1000 for saved queries, 10K when using disable_series=True)",
    )
    havings: list[Having | dict[str, Any]] | None = Field(
        default=None, description="Having clauses"
    )
    calculated_fields: list[dict[str, str]] | None = Field(
        default=None,
        description="Inline calculated fields (derived columns) for this query",
    )
    compare_time_offset_seconds: int | None = Field(
        default=None,
        description="Compare against historical data offset by N seconds "
        "(1800, 3600, 7200, 28800, 86400, 604800, 2419200, 15724800)",
    )

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int | None) -> int | None:
        """Validate that limit doesn't exceed 1000 for saved queries."""
        if v is not None and v > 1000:
            raise ValueError(
                "limit cannot exceed 1000 for saved queries. "
                "The 10K limit comes from disable_series=True when executing the query. "
                "Remove limit from QuerySpec or use limit <= 1000."
            )
        return v

    @field_validator("compare_time_offset_seconds")
    @classmethod
    def validate_compare_time_offset(cls, v: int | None) -> int | None:
        """Validate that compare_time_offset_seconds is a valid offset value."""
        if v is not None and v not in VALID_COMPARE_OFFSETS:
            raise ValueError(
                f"Invalid compare_time_offset_seconds: {v}. "
                f"Must be one of: {sorted(VALID_COMPARE_OFFSETS)}"
            )
        return v

    @classmethod
    def builder(cls) -> QueryBuilder:
        """Create a QueryBuilder for fluent query construction.

        Returns:
            A new QueryBuilder instance

        Example:
            >>> spec = QuerySpec.builder().count().last_1_hour().build()
        """
        from honeycomb.models.query_builder import QueryBuilder

        return QueryBuilder()

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request, normalizing typed models to dicts."""
        data: dict[str, Any] = {}

        # Time range (either relative or absolute)
        if self.time_range is not None:
            data["time_range"] = self.time_range
        if self.start_time is not None:
            data["start_time"] = self.start_time
        if self.end_time is not None:
            data["end_time"] = self.end_time

        if self.granularity is not None:
            data["granularity"] = self.granularity
        if self.calculations:
            data["calculations"] = [_normalize_calculation(c) for c in self.calculations]
        if self.filters:
            data["filters"] = [_normalize_filter(f) for f in self.filters]
        if self.breakdowns:
            data["breakdowns"] = self.breakdowns
        if self.filter_combination:
            data["filter_combination"] = _normalize_filter_combination(self.filter_combination)
        if self.orders:
            data["orders"] = [_normalize_order(o) for o in self.orders]
        if self.limit is not None:
            data["limit"] = self.limit
        if self.havings:
            data["havings"] = [_normalize_having(h) for h in self.havings]
        if self.calculated_fields:
            data["calculated_fields"] = self.calculated_fields
        if self.compare_time_offset_seconds is not None:
            data["compare_time_offset_seconds"] = self.compare_time_offset_seconds

        return data


class Query(BaseModel):
    """A Honeycomb query (response model)."""

    id: str = Field(description="Unique identifier")
    query_annotation_id: str | None = Field(
        default=None,
        description="Annotation ID for referencing this query in boards (returned by API but not in spec)",
    )
    query_json: dict | None = Field(default=None, description="Query specification")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}


class QueryResultData(BaseModel):
    """Query result data container."""

    series: list[dict] | None = Field(default=None, description="Timeseries data")
    results: list[dict] | None = Field(default=None, description="Query result rows (wrapped)")
    total_by_aggregate: dict | None = Field(default=None, description="Total values by aggregate")
    total_by_aggregate_series: list[dict] | None = Field(
        default=None, description="Timeseries totals by aggregate"
    )
    other_by_aggregate: dict | None = Field(default=None, description="Other group aggregates")

    model_config = {"extra": "allow"}

    @property
    def rows(self) -> list[dict]:
        """Get unwrapped result rows.

        The API returns results as [{"data": {...values...}}, ...].
        This property unwraps them to just [{...values...}, ...] for easier access.

        Returns:
            List of result row dicts with breakdown and calculation values.
        """
        if not self.results:
            return []
        return [row.get("data", row) for row in self.results]


class QueryResult(BaseModel):
    """Results from a query execution.

    Note: data will be None if the query is still processing.
    Poll until data is not None to get the complete results.
    """

    id: str | None = Field(default=None, description="Query result ID")
    complete: bool | None = Field(default=None, description="Whether query is complete")
    data: QueryResultData | None = Field(
        default=None, description="Query result data (None if pending)"
    )
    links: dict | None = Field(default=None, description="UI and pagination links")

    model_config = {"extra": "allow"}
