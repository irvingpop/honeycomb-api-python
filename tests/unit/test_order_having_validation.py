"""Unit tests for Order and Having column validation."""

import pytest
from pydantic import ValidationError

from honeycomb.models.query_builder import CalcOp, FilterOp, Having, Order, OrderDirection


class TestOrderColumnValidation:
    """Test Order column requirement validation."""

    def test_order_count_without_column(self):
        """COUNT can be used without column."""
        order = Order(op=CalcOp.COUNT, order=OrderDirection.DESCENDING)
        assert order.op == CalcOp.COUNT
        assert order.column is None

    def test_order_concurrency_without_column(self):
        """CONCURRENCY can be used without column."""
        order = Order(op=CalcOp.CONCURRENCY, order=OrderDirection.ASCENDING)
        assert order.op == CalcOp.CONCURRENCY
        assert order.column is None

    def test_order_avg_without_column_rejected(self):
        """AVG requires column."""
        with pytest.raises(ValidationError, match="column required for op 'AVG'"):
            Order(op=CalcOp.AVG, order=OrderDirection.DESCENDING)

    def test_order_sum_without_column_rejected(self):
        """SUM requires column."""
        with pytest.raises(ValidationError, match="column required for op 'SUM'"):
            Order(op=CalcOp.SUM, order=OrderDirection.ASCENDING)

    def test_order_p99_without_column_rejected(self):
        """P99 requires column."""
        with pytest.raises(ValidationError, match="column required for op 'P99'"):
            Order(op=CalcOp.P99)

    def test_order_avg_with_column_succeeds(self):
        """AVG with column succeeds."""
        order = Order(op=CalcOp.AVG, column="duration_ms", order=OrderDirection.DESCENDING)
        assert order.op == CalcOp.AVG
        assert order.column == "duration_ms"
        assert order.order == OrderDirection.DESCENDING

    def test_order_p99_with_column_succeeds(self):
        """P99 with column succeeds."""
        order = Order(op=CalcOp.P99, column="latency", order=OrderDirection.ASCENDING)
        assert order.op == CalcOp.P99
        assert order.column == "latency"
        assert order.order == OrderDirection.ASCENDING

    def test_order_to_dict_with_column(self):
        """Order with column converts to dict correctly."""
        order = Order(op=CalcOp.AVG, column="cpu", order=OrderDirection.DESCENDING)
        result = order.to_dict()
        assert result == {"op": "AVG", "column": "cpu", "order": "descending"}

    def test_order_to_dict_without_column(self):
        """Order without column converts to dict correctly."""
        order = Order(op=CalcOp.COUNT, order=OrderDirection.ASCENDING)
        result = order.to_dict()
        assert result == {"op": "COUNT", "order": "ascending"}
        assert "column" not in result


class TestHavingColumnValidation:
    """Test Having column requirement validation."""

    def test_having_count_without_column(self):
        """COUNT can be used without column."""
        having = Having(calculate_op=CalcOp.COUNT, op=FilterOp.GREATER_THAN, value=100)
        assert having.calculate_op == CalcOp.COUNT
        assert having.column is None

    def test_having_concurrency_without_column(self):
        """CONCURRENCY can be used without column."""
        having = Having(calculate_op=CalcOp.CONCURRENCY, op=FilterOp.LESS_THAN, value=50)
        assert having.calculate_op == CalcOp.CONCURRENCY
        assert having.column is None

    def test_having_avg_without_column_rejected(self):
        """AVG requires column."""
        with pytest.raises(ValidationError, match="column required for calculate_op 'AVG'"):
            Having(calculate_op=CalcOp.AVG, op=FilterOp.GREATER_THAN, value=500)

    def test_having_sum_without_column_rejected(self):
        """SUM requires column."""
        with pytest.raises(ValidationError, match="column required for calculate_op 'SUM'"):
            Having(calculate_op=CalcOp.SUM, op=FilterOp.LESS_THAN_OR_EQUAL, value=1000)

    def test_having_p95_without_column_rejected(self):
        """P95 requires column."""
        with pytest.raises(ValidationError, match="column required for calculate_op 'P95'"):
            Having(calculate_op=CalcOp.P95, op=FilterOp.GREATER_THAN, value=200)

    def test_having_avg_with_column_succeeds(self):
        """AVG with column succeeds."""
        having = Having(
            calculate_op=CalcOp.AVG, column="duration_ms", op=FilterOp.GREATER_THAN, value=500.0
        )
        assert having.calculate_op == CalcOp.AVG
        assert having.column == "duration_ms"
        assert having.op == FilterOp.GREATER_THAN
        assert having.value == 500.0

    def test_having_p99_with_column_succeeds(self):
        """P99 with column succeeds."""
        having = Having(
            calculate_op=CalcOp.P99, column="latency", op=FilterOp.LESS_THAN, value=100.0
        )
        assert having.calculate_op == CalcOp.P99
        assert having.column == "latency"
        assert having.op == FilterOp.LESS_THAN
        assert having.value == 100.0

    def test_having_to_dict_with_column(self):
        """Having with column converts to dict correctly."""
        having = Having(calculate_op=CalcOp.AVG, column="cpu", op=FilterOp.GREATER_THAN, value=80.0)
        result = having.to_dict()
        assert result == {
            "calculate_op": "AVG",
            "column": "cpu",
            "op": ">",
            "value": 80.0,
        }

    def test_having_to_dict_without_column(self):
        """Having without column converts to dict correctly."""
        having = Having(calculate_op=CalcOp.COUNT, op=FilterOp.GREATER_THAN, value=1000.0)
        result = having.to_dict()
        assert result == {"calculate_op": "COUNT", "op": ">", "value": 1000.0}
        assert "column" not in result


class TestFilterValueValidation:
    """Test Filter value requirement validation."""

    def test_exists_without_value(self):
        """EXISTS can be used without value."""
        from honeycomb.models.query_builder import Filter, FilterOp

        f = Filter(column="error", op=FilterOp.EXISTS)
        assert f.op == FilterOp.EXISTS
        assert f.value is None
        assert f.to_dict() == {"column": "error", "op": "exists"}

    def test_does_not_exist_without_value(self):
        """DOES_NOT_EXIST can be used without value."""
        from honeycomb.models.query_builder import Filter, FilterOp

        f = Filter(column="field", op=FilterOp.DOES_NOT_EXIST)
        assert f.value is None
        assert f.to_dict() == {"column": "field", "op": "does-not-exist"}

    def test_exists_with_value_true_cleaned(self):
        """EXISTS with value=True is automatically cleaned (value set to None)."""
        from honeycomb.models.query_builder import Filter, FilterOp

        f = Filter(column="error", op=FilterOp.EXISTS, value=True)
        # Value should be cleaned to None by validator
        assert f.value is None
        # Should not appear in dict
        assert f.to_dict() == {"column": "error", "op": "exists"}

    def test_does_not_exist_with_value_false_cleaned(self):
        """DOES_NOT_EXIST with value=False is automatically cleaned."""
        from honeycomb.models.query_builder import Filter, FilterOp

        f = Filter(column="field", op=FilterOp.DOES_NOT_EXIST, value=False)
        assert f.value is None
        assert f.to_dict() == {"column": "field", "op": "does-not-exist"}

    def test_equals_requires_value(self):
        """EQUALS and other operators keep their value."""
        from honeycomb.models.query_builder import Filter, FilterOp

        f = Filter(column="status", op=FilterOp.EQUALS, value=200)
        assert f.value == 200
        assert f.to_dict() == {"column": "status", "op": "=", "value": 200}

    def test_in_operator_with_list_value(self):
        """IN operator with list value works correctly."""
        from honeycomb.models.query_builder import Filter, FilterOp

        f = Filter(column="service", op=FilterOp.IN, value=["api", "web"])
        assert f.value == ["api", "web"]
        assert f.to_dict() == {"column": "service", "op": "in", "value": ["api", "web"]}


class TestQueryBuilderWithOrdersAndHavings:
    """Test QueryBuilder integration with orders and havings."""

    def test_order_by_with_column(self):
        """order_by() with column works correctly."""
        from honeycomb.models.query_builder import QueryBuilder

        qb = QueryBuilder().order_by(CalcOp.AVG, OrderDirection.DESCENDING, column="duration_ms")
        spec = qb.build()
        assert len(spec.orders) == 1
        assert spec.orders[0].op == CalcOp.AVG
        assert spec.orders[0].column == "duration_ms"
        assert spec.orders[0].order == OrderDirection.DESCENDING

    def test_having_with_column(self):
        """having() with column works correctly."""
        from honeycomb.models.query_builder import QueryBuilder

        qb = QueryBuilder().having(CalcOp.AVG, FilterOp.GREATER_THAN, 500.0, column="duration_ms")
        spec = qb.build()
        assert len(spec.havings) == 1
        assert spec.havings[0].calculate_op == CalcOp.AVG
        assert spec.havings[0].column == "duration_ms"
        assert spec.havings[0].op == FilterOp.GREATER_THAN
        assert spec.havings[0].value == 500.0

    def test_complex_query_with_orders_and_havings(self):
        """Complex query with orders and havings."""
        from honeycomb.models.query_builder import QueryBuilder

        qb = (
            QueryBuilder()
            .last_1_hour()
            .count()
            .avg("duration_ms")
            .p99("duration_ms")
            .breakdown("service")
            .order_by(CalcOp.AVG, OrderDirection.DESCENDING, column="duration_ms")
            .having(CalcOp.COUNT, FilterOp.GREATER_THAN, 100.0)
            .having(CalcOp.P99, FilterOp.LESS_THAN, 1000.0, column="duration_ms")
            .limit(20)
        )

        spec = qb.build()
        assert len(spec.orders) == 1
        assert spec.orders[0].op == CalcOp.AVG
        assert spec.orders[0].column == "duration_ms"

        assert len(spec.havings) == 2
        assert spec.havings[0].calculate_op == CalcOp.COUNT
        assert spec.havings[0].column is None
        assert spec.havings[1].calculate_op == CalcOp.P99
        assert spec.havings[1].column == "duration_ms"
