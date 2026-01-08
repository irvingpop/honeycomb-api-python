"""Tests for model validation with extra="forbid" configuration."""

import pytest
from pydantic import ValidationError

from honeycomb.models.boards import BoardViewFilter
from honeycomb.models.query_builder import (
    CalcOp,
    Calculation,
    Filter,
    FilterOp,
    Having,
    Order,
    OrderDirection,
)


class TestCalculationValidation:
    """Test Calculation model validation."""

    def test_accepts_valid_fields(self):
        """Test that valid fields are accepted."""
        calc = Calculation(op=CalcOp.COUNT)
        assert calc.op == CalcOp.COUNT

    def test_accepts_string_enum_coercion(self):
        """Test that string values are coerced to enum."""
        calc = Calculation(op="COUNT")
        assert calc.op == CalcOp.COUNT
        assert isinstance(calc.op, CalcOp)

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Calculation(op=CalcOp.COUNT, invalid_field="test")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestFilterValidation:
    """Test Filter model validation."""

    def test_accepts_valid_fields(self):
        """Test that valid fields are accepted."""
        filt = Filter(column="status", op=FilterOp.EQUALS, value=200)
        assert filt.op == FilterOp.EQUALS

    def test_accepts_string_enum_coercion(self):
        """Test that string values are coerced to enum."""
        filt = Filter(column="status", op="=", value=200)
        assert filt.op == FilterOp.EQUALS
        assert isinstance(filt.op, FilterOp)

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Filter(column="status", op=FilterOp.EQUALS, value=200, chart_type="line")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestOrderValidation:
    """Test Order model validation."""

    def test_accepts_valid_fields(self):
        """Test that valid fields are accepted."""
        order = Order(op=CalcOp.COUNT)
        assert order.op == CalcOp.COUNT
        assert order.order == OrderDirection.DESCENDING

    def test_accepts_string_enum_coercion(self):
        """Test that string values are coerced to enum."""
        order = Order(op="COUNT", order="ascending")
        assert order.op == CalcOp.COUNT
        assert order.order == OrderDirection.ASCENDING
        assert isinstance(order.op, CalcOp)
        assert isinstance(order.order, OrderDirection)

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Order(op=CalcOp.COUNT, extra_param="invalid")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestHavingValidation:
    """Test Having model validation."""

    def test_accepts_valid_fields(self):
        """Test that valid fields are accepted."""
        having = Having(calculate_op=CalcOp.COUNT, op=FilterOp.GREATER_THAN, value=100)
        assert having.calculate_op == CalcOp.COUNT
        assert having.op == FilterOp.GREATER_THAN

    def test_accepts_string_enum_coercion(self):
        """Test that string values are coerced to enum."""
        having = Having(calculate_op="COUNT", op=">", value=100)
        assert having.calculate_op == CalcOp.COUNT
        assert having.op == FilterOp.GREATER_THAN
        assert isinstance(having.calculate_op, CalcOp)
        assert isinstance(having.op, FilterOp)

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Having(calculate_op=CalcOp.COUNT, op=FilterOp.GREATER_THAN, value=100, unknown="field")

        error = exc_info.value
        assert "extra_forbidden" in str(error)


class TestBoardViewFilterValidation:
    """Test BoardViewFilter model validation."""

    def test_accepts_valid_fields(self):
        """Test that valid fields are accepted."""
        filt = BoardViewFilter(column="status", operation=FilterOp.EQUALS, value="active")
        assert filt.operation == FilterOp.EQUALS

    def test_accepts_string_enum_coercion(self):
        """Test that string values are coerced to enum."""
        filt = BoardViewFilter(column="status", operation="=", value="active")
        assert filt.operation == FilterOp.EQUALS
        assert isinstance(filt.operation, FilterOp)

    def test_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BoardViewFilter(
                column="status", operation=FilterOp.EQUALS, value="active", extra="field"
            )

        error = exc_info.value
        assert "extra_forbidden" in str(error)
