"""Pydantic models and builder for Honeycomb Derived Columns (Calculated Fields)."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing_extensions import Self

from honeycomb._generated_models import CalculatedField as _CalculatedFieldGenerated
from honeycomb._generated_models import CalculatedFieldList


# Response model - extends generated
class DerivedColumn(_CalculatedFieldGenerated):
    """A derived column (calculated field) response model.

    Extends generated CalculatedField.
    """

    pass


# For creates, we need a simpler model without id/timestamps
class DerivedColumnCreate(BaseModel):
    """Model for creating a derived column."""

    alias: str = Field(description="Name of the derived column", max_length=255)
    expression: str = Field(
        description="Expression to calculate the value. See https://docs.honeycomb.io/reference/derived-column-formula/"
    )
    description: str | None = Field(default=None, description="Human-readable description")


# List response
DerivedColumnList = CalculatedFieldList


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
