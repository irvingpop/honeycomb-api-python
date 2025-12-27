"""Query builder and shared query components for Honeycomb queries.

This module provides:
- Enums for query operations (CalcOp, FilterOp, OrderDirection, FilterCombination)
- Typed Pydantic models (Calculation, Filter, Order, Having)
- A fluent QueryBuilder for constructing queries
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from honeycomb.models.queries import QuerySpec
    from honeycomb.models.triggers import TriggerQuery


# =============================================================================
# Enums
# =============================================================================


class CalcOp(str, Enum):
    """Calculation operations for Honeycomb queries."""

    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    P001 = "P001"
    P01 = "P01"
    P05 = "P05"
    P10 = "P10"
    P25 = "P25"
    P50 = "P50"
    P75 = "P75"
    P90 = "P90"
    P95 = "P95"
    P99 = "P99"
    P999 = "P999"
    COUNT_DISTINCT = "COUNT_DISTINCT"
    CONCURRENCY = "CONCURRENCY"
    HEATMAP = "HEATMAP"
    RATE_AVG = "RATE_AVG"
    RATE_SUM = "RATE_SUM"
    RATE_MAX = "RATE_MAX"


class FilterOp(str, Enum):
    """Filter operations for Honeycomb queries."""

    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    STARTS_WITH = "starts-with"
    DOES_NOT_START_WITH = "does-not-start-with"
    CONTAINS = "contains"
    DOES_NOT_CONTAIN = "does-not-contain"
    EXISTS = "exists"
    DOES_NOT_EXIST = "does-not-exist"
    IN = "in"
    NOT_IN = "not-in"


class OrderDirection(str, Enum):
    """Order directions for query results."""

    ASCENDING = "ascending"
    DESCENDING = "descending"


class FilterCombination(str, Enum):
    """How to combine multiple filters."""

    AND = "AND"
    OR = "OR"


# =============================================================================
# Typed Models
# =============================================================================


class Calculation(BaseModel):
    """A calculation in a query.

    Examples:
        >>> Calculation(op=CalcOp.COUNT)
        >>> Calculation(op=CalcOp.P99, column="duration_ms")
        >>> Calculation(op="AVG", column="response_time", alias="avg_response")
    """

    op: CalcOp | str = Field(description="Calculation operation (COUNT, AVG, P99, etc.)")
    column: str | None = Field(default=None, description="Column to calculate on")
    alias: str | None = Field(default=None, description="Alias for the result column")

    def to_dict(self) -> dict[str, Any]:
        """Convert to API dict format."""
        op_value = self.op.value if isinstance(self.op, CalcOp) else self.op
        result: dict[str, Any] = {"op": op_value}
        if self.column is not None:
            result["column"] = self.column
        if self.alias is not None:
            result["alias"] = self.alias
        return result


class Filter(BaseModel):
    """A filter in a query.

    Examples:
        >>> Filter(column="status", op=FilterOp.EQUALS, value=200)
        >>> Filter(column="error", op=FilterOp.EXISTS, value=True)
        >>> Filter(column="service", op="in", value=["api", "web"])
    """

    column: str = Field(description="Column to filter on")
    op: FilterOp | str = Field(description="Filter operator (=, !=, >, <, contains, etc.)")
    value: Any = Field(description="Filter value")

    def to_dict(self) -> dict[str, Any]:
        """Convert to API dict format."""
        op_value = self.op.value if isinstance(self.op, FilterOp) else self.op
        return {"column": self.column, "op": op_value, "value": self.value}


class Order(BaseModel):
    """An ordering specification for query results.

    Examples:
        >>> Order(op=CalcOp.COUNT, order=OrderDirection.DESCENDING)
        >>> Order(op=CalcOp.AVG, column="duration_ms", order=OrderDirection.ASCENDING)
    """

    op: CalcOp | str = Field(description="Calculation to order by")
    column: str | None = Field(default=None, description="Column for the calculation")
    order: OrderDirection | str = Field(
        default=OrderDirection.DESCENDING, description="Sort direction"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to API dict format."""
        op_value = self.op.value if isinstance(self.op, CalcOp) else self.op
        order_value = self.order.value if isinstance(self.order, OrderDirection) else self.order
        result: dict[str, Any] = {"op": op_value, "order": order_value}
        if self.column is not None:
            result["column"] = self.column
        return result


class Having(BaseModel):
    """A having clause for post-aggregation filtering.

    Examples:
        >>> Having(calculate_op=CalcOp.COUNT, op=FilterOp.GREATER_THAN, value=100)
        >>> Having(calculate_op=CalcOp.AVG, column="duration_ms", op=">", value=500.0)
    """

    calculate_op: CalcOp | str = Field(description="Calculation to filter on")
    column: str | None = Field(default=None, description="Column for the calculation")
    op: FilterOp | str = Field(description="Comparison operator")
    value: float = Field(description="Threshold value")

    def to_dict(self) -> dict[str, Any]:
        """Convert to API dict format."""
        calc_op_value = (
            self.calculate_op.value if isinstance(self.calculate_op, CalcOp) else self.calculate_op
        )
        op_value = self.op.value if isinstance(self.op, FilterOp) else self.op
        result: dict[str, Any] = {
            "calculate_op": calc_op_value,
            "op": op_value,
            "value": self.value,
        }
        if self.column is not None:
            result["column"] = self.column
        return result


# =============================================================================
# QueryBuilder
# =============================================================================


class QueryBuilder:
    """Fluent builder for constructing QuerySpec objects.

    The builder provides a chainable API for constructing queries. Each method
    returns self, allowing method chaining. Call build() to get the final QuerySpec,
    or build_for_trigger() to get a TriggerQuery with validation.

    Examples:
        >>> # Simple count query
        >>> spec = QueryBuilder().last_1_hour().count().build()

        >>> # Complex query with multiple calculations
        >>> spec = (
        ...     QueryBuilder()
        ...     .last_24_hours()
        ...     .count()
        ...     .p99("duration_ms")
        ...     .avg("duration_ms")
        ...     .where("status", FilterOp.GREATER_THAN_OR_EQUAL, 500)
        ...     .breakdown("service", "endpoint")
        ...     .order_by_count()
        ...     .build()
        ... )

        >>> # Trigger query (validates time_range <= 3600)
        >>> trigger_query = (
        ...     QueryBuilder()
        ...     .last_30_minutes()
        ...     .p99("duration_ms")
        ...     .build_for_trigger()
        ... )
    """

    def __init__(self) -> None:
        """Initialize an empty query builder."""
        self._time_range: int | None = None
        self._start_time: int | None = None
        self._end_time: int | None = None
        self._granularity: int | None = None
        self._calculations: list[Calculation] = []
        self._filters: list[Filter] = []
        self._breakdowns: list[str] = []
        self._filter_combination: FilterCombination | None = None
        self._orders: list[Order] = []
        self._limit: int | None = None
        self._havings: list[Having] = []
        # Query annotation metadata (for board integration)
        self._annotation_name: str | None = None
        self._annotation_description: str | None = None

    # -------------------------------------------------------------------------
    # Time Methods - Custom
    # -------------------------------------------------------------------------

    def time_range(self, seconds: int) -> QueryBuilder:
        """Set the query time range in seconds (relative time).

        Note: Mutually exclusive with start_time()/end_time(). Setting this
        clears any absolute time range.

        Args:
            seconds: Time range in seconds (e.g., 3600 for 1 hour)

        Returns:
            self for chaining
        """
        self._time_range = seconds
        self._start_time = None  # Clear absolute time
        self._end_time = None
        return self

    def start_time(self, timestamp: int) -> QueryBuilder:
        """Set absolute start time as Unix timestamp.

        Note: Mutually exclusive with time_range(). Setting this clears any
        relative time range. Must be used with end_time().

        Args:
            timestamp: Start time as Unix timestamp (seconds since epoch)

        Returns:
            self for chaining
        """
        self._start_time = timestamp
        self._time_range = None  # Clear relative time
        return self

    def end_time(self, timestamp: int) -> QueryBuilder:
        """Set absolute end time as Unix timestamp.

        Note: Mutually exclusive with time_range(). Setting this clears any
        relative time range. Must be used with start_time().

        Args:
            timestamp: End time as Unix timestamp (seconds since epoch)

        Returns:
            self for chaining
        """
        self._end_time = timestamp
        self._time_range = None  # Clear relative time
        return self

    def absolute_time(self, start: int, end: int) -> QueryBuilder:
        """Set absolute start and end times as Unix timestamps.

        Convenience method equivalent to calling start_time(start).end_time(end).

        Note: Mutually exclusive with time_range(). Setting this clears any
        relative time range.

        Args:
            start: Start time as Unix timestamp
            end: End time as Unix timestamp

        Returns:
            self for chaining
        """
        self._start_time = start
        self._end_time = end
        self._time_range = None  # Clear relative time range
        return self

    def granularity(self, seconds: int) -> QueryBuilder:
        """Set the time granularity for bucketing results.

        Args:
            seconds: Granularity in seconds (e.g., 60 for 1-minute buckets)

        Returns:
            self for chaining
        """
        self._granularity = seconds
        return self

    # -------------------------------------------------------------------------
    # Time Methods - Presets (matching Honeycomb UI)
    # -------------------------------------------------------------------------

    def last_10_minutes(self) -> QueryBuilder:
        """Set time range to last 10 minutes (600 seconds)."""
        return self.time_range(600)

    def last_30_minutes(self) -> QueryBuilder:
        """Set time range to last 30 minutes (1800 seconds)."""
        return self.time_range(1800)

    def last_1_hour(self) -> QueryBuilder:
        """Set time range to last 1 hour (3600 seconds)."""
        return self.time_range(3600)

    def last_2_hours(self) -> QueryBuilder:
        """Set time range to last 2 hours (7200 seconds)."""
        return self.time_range(7200)

    def last_8_hours(self) -> QueryBuilder:
        """Set time range to last 8 hours (28800 seconds)."""
        return self.time_range(28800)

    def last_24_hours(self) -> QueryBuilder:
        """Set time range to last 24 hours (86400 seconds)."""
        return self.time_range(86400)

    def last_1_day(self) -> QueryBuilder:
        """Set time range to last 1 day (86400 seconds). Alias for last_24_hours()."""
        return self.time_range(86400)

    def last_7_days(self) -> QueryBuilder:
        """Set time range to last 7 days (604800 seconds)."""
        return self.time_range(604800)

    def last_14_days(self) -> QueryBuilder:
        """Set time range to last 14 days (1209600 seconds)."""
        return self.time_range(1209600)

    def last_28_days(self) -> QueryBuilder:
        """Set time range to last 28 days (2419200 seconds)."""
        return self.time_range(2419200)

    # -------------------------------------------------------------------------
    # Calculation Methods (additive - each call adds to the list)
    # -------------------------------------------------------------------------

    def calculate(
        self, op: CalcOp | str, column: str | None = None, alias: str | None = None
    ) -> QueryBuilder:
        """Add a calculation to the query.

        Args:
            op: Calculation operation (e.g., CalcOp.COUNT, "AVG")
            column: Column to calculate on (optional for COUNT)
            alias: Alias for the result column

        Returns:
            self for chaining
        """
        self._calculations.append(Calculation(op=op, column=column, alias=alias))
        return self

    def count(self, alias: str | None = None) -> QueryBuilder:
        """Add a COUNT calculation."""
        return self.calculate(CalcOp.COUNT, alias=alias)

    def sum(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add a SUM calculation on a column."""
        return self.calculate(CalcOp.SUM, column=column, alias=alias)

    def avg(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add an AVG calculation on a column."""
        return self.calculate(CalcOp.AVG, column=column, alias=alias)

    def min(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add a MIN calculation on a column."""
        return self.calculate(CalcOp.MIN, column=column, alias=alias)

    def max(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add a MAX calculation on a column."""
        return self.calculate(CalcOp.MAX, column=column, alias=alias)

    def count_distinct(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add a COUNT_DISTINCT calculation on a column."""
        return self.calculate(CalcOp.COUNT_DISTINCT, column=column, alias=alias)

    def p50(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add a P50 (median) calculation on a column."""
        return self.calculate(CalcOp.P50, column=column, alias=alias)

    def p90(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add a P90 calculation on a column."""
        return self.calculate(CalcOp.P90, column=column, alias=alias)

    def p95(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add a P95 calculation on a column."""
        return self.calculate(CalcOp.P95, column=column, alias=alias)

    def p99(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add a P99 calculation on a column."""
        return self.calculate(CalcOp.P99, column=column, alias=alias)

    def heatmap(self, column: str, alias: str | None = None) -> QueryBuilder:
        """Add a HEATMAP calculation on a column."""
        return self.calculate(CalcOp.HEATMAP, column=column, alias=alias)

    def concurrency(self, alias: str | None = None) -> QueryBuilder:
        """Add a CONCURRENCY calculation."""
        return self.calculate(CalcOp.CONCURRENCY, alias=alias)

    # -------------------------------------------------------------------------
    # Filter Methods
    # -------------------------------------------------------------------------

    def filter(self, column: str, op: FilterOp | str, value: Any) -> QueryBuilder:
        """Add a filter to the query.

        Args:
            column: Column to filter on
            op: Filter operator (e.g., FilterOp.EQUALS, ">=")
            value: Filter value

        Returns:
            self for chaining
        """
        self._filters.append(Filter(column=column, op=op, value=value))
        return self

    def where(self, column: str, op: FilterOp | str, value: Any) -> QueryBuilder:
        """Add a filter to the query. Alias for filter().

        Args:
            column: Column to filter on
            op: Filter operator (e.g., FilterOp.EQUALS, ">=")
            value: Filter value

        Returns:
            self for chaining
        """
        return self.filter(column, op, value)

    def where_equals(self, column: str, value: Any) -> QueryBuilder:
        """Add an equality filter.

        Args:
            column: Column to filter on
            value: Value to match

        Returns:
            self for chaining
        """
        return self.filter(column, FilterOp.EQUALS, value)

    def where_exists(self, column: str) -> QueryBuilder:
        """Add a filter for column existence.

        Args:
            column: Column that must exist

        Returns:
            self for chaining
        """
        return self.filter(column, FilterOp.EXISTS, True)

    # -------------------------------------------------------------------------
    # Filter Shortcuts (one method per operator)
    # -------------------------------------------------------------------------

    def eq(self, column: str, value: Any) -> QueryBuilder:
        """Filter where column equals value. Shortcut for where(column, FilterOp.EQUALS, value)."""
        return self.filter(column, FilterOp.EQUALS, value)

    def ne(self, column: str, value: Any) -> QueryBuilder:
        """Filter where column does not equal value. Shortcut for where(column, FilterOp.NOT_EQUALS, value)."""
        return self.filter(column, FilterOp.NOT_EQUALS, value)

    def gt(self, column: str, value: Any) -> QueryBuilder:
        """Filter where column > value. Shortcut for where(column, FilterOp.GREATER_THAN, value)."""
        return self.filter(column, FilterOp.GREATER_THAN, value)

    def gte(self, column: str, value: Any) -> QueryBuilder:
        """Filter where column >= value. Shortcut for where(column, FilterOp.GREATER_THAN_OR_EQUAL, value)."""
        return self.filter(column, FilterOp.GREATER_THAN_OR_EQUAL, value)

    def lt(self, column: str, value: Any) -> QueryBuilder:
        """Filter where column < value. Shortcut for where(column, FilterOp.LESS_THAN, value)."""
        return self.filter(column, FilterOp.LESS_THAN, value)

    def lte(self, column: str, value: Any) -> QueryBuilder:
        """Filter where column <= value. Shortcut for where(column, FilterOp.LESS_THAN_OR_EQUAL, value)."""
        return self.filter(column, FilterOp.LESS_THAN_OR_EQUAL, value)

    def starts_with(self, column: str, value: str) -> QueryBuilder:
        """Filter where column starts with value."""
        return self.filter(column, FilterOp.STARTS_WITH, value)

    def does_not_start_with(self, column: str, value: str) -> QueryBuilder:
        """Filter where column does not start with value."""
        return self.filter(column, FilterOp.DOES_NOT_START_WITH, value)

    def contains(self, column: str, value: str) -> QueryBuilder:
        """Filter where column contains value."""
        return self.filter(column, FilterOp.CONTAINS, value)

    def does_not_contain(self, column: str, value: str) -> QueryBuilder:
        """Filter where column does not contain value."""
        return self.filter(column, FilterOp.DOES_NOT_CONTAIN, value)

    def exists(self, column: str) -> QueryBuilder:
        """Filter where column exists."""
        return self.filter(column, FilterOp.EXISTS, True)

    def does_not_exist(self, column: str) -> QueryBuilder:
        """Filter where column does not exist."""
        return self.filter(column, FilterOp.DOES_NOT_EXIST, True)

    def is_in(self, column: str, values: list[Any]) -> QueryBuilder:
        """Filter where column is in a list of values."""
        return self.filter(column, FilterOp.IN, values)

    def not_in(self, column: str, values: list[Any]) -> QueryBuilder:
        """Filter where column is not in a list of values."""
        return self.filter(column, FilterOp.NOT_IN, values)

    def filter_with(self, combination: FilterCombination | str) -> QueryBuilder:
        """Set how multiple filters are combined.

        Args:
            combination: FilterCombination.AND or FilterCombination.OR

        Returns:
            self for chaining
        """
        if isinstance(combination, str):
            self._filter_combination = FilterCombination(combination)
        else:
            self._filter_combination = combination
        return self

    # -------------------------------------------------------------------------
    # Grouping Methods
    # -------------------------------------------------------------------------

    def breakdown(self, *columns: str) -> QueryBuilder:
        """Add columns to group results by.

        Args:
            *columns: Column names to group by

        Returns:
            self for chaining
        """
        self._breakdowns.extend(columns)
        return self

    def group_by(self, *columns: str) -> QueryBuilder:
        """Add columns to group results by. Alias for breakdown().

        Args:
            *columns: Column names to group by

        Returns:
            self for chaining
        """
        return self.breakdown(*columns)

    # -------------------------------------------------------------------------
    # Ordering Methods
    # -------------------------------------------------------------------------

    def order_by(
        self,
        op: CalcOp | str,
        direction: OrderDirection | str = OrderDirection.DESCENDING,
        column: str | None = None,
    ) -> QueryBuilder:
        """Add an ordering specification.

        Args:
            op: Calculation to order by
            direction: Sort direction (default: descending)
            column: Column for the calculation (if applicable)

        Returns:
            self for chaining
        """
        self._orders.append(Order(op=op, column=column, order=direction))
        return self

    def order_by_count(
        self, direction: OrderDirection | str = OrderDirection.DESCENDING
    ) -> QueryBuilder:
        """Order results by COUNT.

        Args:
            direction: Sort direction (default: descending)

        Returns:
            self for chaining
        """
        return self.order_by(CalcOp.COUNT, direction)

    # -------------------------------------------------------------------------
    # Result Limiting
    # -------------------------------------------------------------------------

    def limit(self, n: int) -> QueryBuilder:
        """Set the maximum number of results.

        Args:
            n: Maximum number of results (max 1000 for saved queries)

        Returns:
            self for chaining
        """
        self._limit = n
        return self

    # -------------------------------------------------------------------------
    # Having Methods
    # -------------------------------------------------------------------------

    def having(
        self,
        calculate_op: CalcOp | str,
        op: FilterOp | str,
        value: float,
        column: str | None = None,
    ) -> QueryBuilder:
        """Add a having clause for post-aggregation filtering.

        Args:
            calculate_op: Calculation to filter on
            op: Comparison operator
            value: Threshold value
            column: Column for the calculation (if applicable)

        Returns:
            self for chaining
        """
        self._havings.append(Having(calculate_op=calculate_op, column=column, op=op, value=value))
        return self

    # -------------------------------------------------------------------------
    # Annotation (for board integration)
    # -------------------------------------------------------------------------

    def annotate(self, name: str, description: str | None = None) -> QueryBuilder:
        """Add annotation metadata for board integration.

        When creating a query with annotation, you can use it directly in
        BoardBuilder without needing to separately create a query annotation.

        Args:
            name: Name for the query (1-320 chars)
            description: Optional description (max 1023 chars)

        Example:
            >>> query = (
            ...     QueryBuilder()
            ...     .last_1_hour()
            ...     .count()
            ...     .annotate("Request Count", "Total requests over time")
            ... )
        """
        self._annotation_name = name
        self._annotation_description = description
        return self

    def get_annotation_name(self) -> str | None:
        """Get the annotation name if set."""
        return self._annotation_name

    def get_annotation_description(self) -> str | None:
        """Get the annotation description if set."""
        return self._annotation_description

    def has_annotation(self) -> bool:
        """Check if this query has annotation metadata."""
        return self._annotation_name is not None

    # -------------------------------------------------------------------------
    # Build Methods
    # -------------------------------------------------------------------------

    def build(self) -> QuerySpec:
        """Build a QuerySpec from the builder state.

        Returns:
            A QuerySpec configured with the builder's settings

        Raises:
            ValueError: If only one of start_time/end_time is set (must use both)
        """
        # Import here to avoid circular imports
        from honeycomb.models.queries import QuerySpec

        # Validate absolute time: if either is set, both must be set
        has_start = self._start_time is not None
        has_end = self._end_time is not None
        if has_start != has_end:
            raise ValueError(
                "Both start_time and end_time must be set together. "
                "Use time_range() for relative time queries."
            )

        return QuerySpec(
            time_range=self._time_range,
            start_time=self._start_time,
            end_time=self._end_time,
            granularity=self._granularity,
            calculations=self._calculations if self._calculations else None,
            filters=self._filters if self._filters else None,
            breakdowns=self._breakdowns if self._breakdowns else None,
            filter_combination=self._filter_combination,
            orders=self._orders if self._orders else None,
            limit=self._limit,
            havings=self._havings if self._havings else None,
        )

    def build_for_trigger(self) -> TriggerQuery:
        """Build a TriggerQuery from the builder state.

        TriggerQuery has additional constraints:
        - time_range must be <= 3600 seconds (1 hour)
        - No absolute time support
        - No orders, havings, or limit

        Returns:
            A TriggerQuery configured with the builder's settings

        Raises:
            ValueError: If time_range > 3600 or absolute time is set
        """
        # Import here to avoid circular imports
        from honeycomb.models.triggers import TriggerQuery

        if self._start_time is not None or self._end_time is not None:
            raise ValueError("TriggerQuery does not support absolute time ranges")

        if self._time_range is not None and self._time_range > 3600:
            raise ValueError(
                f"TriggerQuery time_range must be <= 3600 seconds (1 hour), got {self._time_range}"
            )

        return TriggerQuery(
            time_range=self._time_range if self._time_range is not None else 3600,
            granularity=self._granularity,
            calculations=self._calculations if self._calculations else None,
            filters=self._filters if self._filters else None,
            breakdowns=self._breakdowns if self._breakdowns else None,
            filter_combination=self._filter_combination,
        )
