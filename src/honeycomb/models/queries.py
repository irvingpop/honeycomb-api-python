"""Pydantic models for Honeycomb Queries."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

from honeycomb._generated_models import (
    Query as _QueryGenerated,
)
from honeycomb._generated_models import (
    QueryResultDetails as _QueryResultGenerated,
)
from honeycomb._generated_models import (
    QueryResultDetailsData as _QueryResultDataGenerated,
)
from honeycomb.models.query_builder import VALID_COMPARE_OFFSETS

if TYPE_CHECKING:
    from honeycomb.models.query_builder import QueryBuilder


class QuerySpec(_QueryGenerated):
    """Query specification for creating queries.

    Extends generated Query with custom validators and builder factory.

    NOTE: Use QueryBuilder for constructing queries. Direct instantiation
    requires generated types (QueryCalculation, QueryFilter, etc.).

    Example:
        >>> QuerySpec.builder().count().last_1_hour().build()
    """

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


class QueryResultData(_QueryResultDataGenerated):
    """Query result data with convenient accessors.

    Extends generated QueryResultDetailsData with property accessors
    for easier access to result rows.
    """

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
        # Generated model uses QueryResultsData objects with .data field
        return [row.data if row.data is not None else {} for row in self.results]


class QueryResult(_QueryResultGenerated):
    """Query execution result with accessors.

    Extends generated QueryResultDetails with enhanced data property
    that uses our QueryResultData type with .rows accessor.

    Note: data will be None if the query is still processing.
    Poll until data is not None to get the complete results.
    """

    model_config = {"extra": "allow"}

    # Override data to use our enhanced type
    data: QueryResultData | None = None
