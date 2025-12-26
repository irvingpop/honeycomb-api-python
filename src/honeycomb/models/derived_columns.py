"""Pydantic models and builder for Honeycomb Derived Columns (Calculated Fields)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from typing_extensions import Self


class DerivedColumnCreate(BaseModel):
    """Model for creating a derived column (calculated field).

    Derived columns (also called Calculated Fields) allow you to run queries
    based on the value of an expression that is calculated from the fields in an event.
    """

    alias: str = Field(description="Name of the derived column")
    expression: str = Field(
        description="Expression to calculate the value. See https://docs.honeycomb.io/reference/derived-column-formula/"
    )
    description: str | None = Field(default=None, description="Human-readable description")

    def model_dump_for_api(self) -> dict[str, Any]:
        """Serialize for API request."""
        data = {"alias": self.alias, "expression": self.expression}
        if self.description:
            data["description"] = self.description
        return data


class DerivedColumn(BaseModel):
    """A derived column (calculated field) response model."""

    id: str = Field(description="Unique identifier")
    alias: str = Field(description="Name of the derived column")
    expression: str = Field(description="Expression to calculate the value")
    description: str | None = Field(default=None, description="Human-readable description")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}


class DerivedColumnBuilder:
    """Builder for derived columns.

    Example:
        >>> dc = (
        ...     DerivedColumnBuilder("request_success")
        ...     .expression("IF(LT($status_code, 400), 1, 0)")
        ...     .description("1 if request succeeded, 0 otherwise")
        ...     .build()
        ... )
        >>> await client.derived_columns.create_async(dataset="api-logs", derived_column=dc)
    """

    def __init__(self, alias: str):
        """Initialize builder with column alias.

        Args:
            alias: Name of the derived column.
        """
        self._alias = alias
        self._expression: str | None = None
        self._description: str | None = None

    def expression(self, expr: str) -> Self:
        """Set the expression for the derived column.

        Args:
            expr: Expression to calculate the value.
                See https://docs.honeycomb.io/reference/derived-column-formula/

        Returns:
            Self for method chaining.
        """
        self._expression = expr
        return self

    def description(self, desc: str) -> Self:
        """Set the description.

        Args:
            desc: Human-readable description.

        Returns:
            Self for method chaining.
        """
        self._description = desc
        return self

    def build(self) -> DerivedColumnCreate:
        """Build DerivedColumnCreate object.

        Returns:
            DerivedColumnCreate object ready for API submission.

        Raises:
            ValueError: If expression is not set.
        """
        if not self._expression:
            raise ValueError("Expression is required")
        return DerivedColumnCreate(
            alias=self._alias, expression=self._expression, description=self._description
        )
