"""Tests for the QueryBuilder and typed query models."""

import pytest

from honeycomb import (
    CalcOp,
    Calculation,
    Filter,
    FilterCombination,
    FilterOp,
    Having,
    Order,
    OrderDirection,
    QueryBuilder,
    QuerySpec,
    TriggerQuery,
)


class TestCalculation:
    """Tests for the Calculation model."""

    def test_create_with_enum(self):
        """Test creating Calculation with CalcOp enum."""
        calc = Calculation(op=CalcOp.COUNT)
        assert calc.op == CalcOp.COUNT
        assert calc.column is None
        assert calc.alias is None

    def test_create_with_string(self):
        """Test creating Calculation with string op."""
        calc = Calculation(op="P99", column="duration_ms")
        assert calc.op == "P99"
        assert calc.column == "duration_ms"

    def test_create_with_alias(self):
        """Test creating Calculation with alias."""
        calc = Calculation(op=CalcOp.AVG, column="duration_ms", alias="avg_duration")
        assert calc.alias == "avg_duration"

    def test_to_dict_basic(self):
        """Test converting Calculation to dict."""
        calc = Calculation(op=CalcOp.COUNT)
        d = calc.to_dict()
        assert d == {"op": "COUNT"}

    def test_to_dict_with_column(self):
        """Test converting Calculation with column to dict."""
        calc = Calculation(op=CalcOp.P99, column="duration_ms")
        d = calc.to_dict()
        assert d == {"op": "P99", "column": "duration_ms"}

    def test_to_dict_with_alias(self):
        """Test converting Calculation with alias to dict."""
        calc = Calculation(op=CalcOp.AVG, column="duration_ms", alias="avg")
        d = calc.to_dict()
        assert d == {"op": "AVG", "column": "duration_ms", "alias": "avg"}


class TestFilter:
    """Tests for the Filter model."""

    def test_create_with_enum(self):
        """Test creating Filter with FilterOp enum."""
        filt = Filter(column="status", op=FilterOp.EQUALS, value=200)
        assert filt.column == "status"
        assert filt.op == FilterOp.EQUALS
        assert filt.value == 200

    def test_create_with_string(self):
        """Test creating Filter with string op."""
        filt = Filter(column="error", op="exists", value=True)
        assert filt.op == "exists"

    def test_to_dict(self):
        """Test converting Filter to dict."""
        filt = Filter(column="status", op=FilterOp.GREATER_THAN_OR_EQUAL, value=500)
        d = filt.to_dict()
        assert d == {"column": "status", "op": ">=", "value": 500}


class TestOrder:
    """Tests for the Order model."""

    def test_create_with_defaults(self):
        """Test creating Order with defaults."""
        order = Order(op=CalcOp.COUNT)
        assert order.op == CalcOp.COUNT
        assert order.order == OrderDirection.DESCENDING

    def test_create_ascending(self):
        """Test creating ascending Order."""
        order = Order(op=CalcOp.AVG, column="duration_ms", order=OrderDirection.ASCENDING)
        assert order.order == OrderDirection.ASCENDING

    def test_to_dict(self):
        """Test converting Order to dict."""
        order = Order(op=CalcOp.COUNT, order=OrderDirection.DESCENDING)
        d = order.to_dict()
        assert d == {"op": "COUNT", "order": "descending"}


class TestHaving:
    """Tests for the Having model."""

    def test_create(self):
        """Test creating Having clause."""
        having = Having(calculate_op=CalcOp.COUNT, op=FilterOp.GREATER_THAN, value=100)
        assert having.calculate_op == CalcOp.COUNT
        assert having.op == FilterOp.GREATER_THAN
        assert having.value == 100

    def test_to_dict(self):
        """Test converting Having to dict."""
        having = Having(
            calculate_op=CalcOp.AVG, column="duration_ms", op=FilterOp.GREATER_THAN, value=500.0
        )
        d = having.to_dict()
        assert d == {"calculate_op": "AVG", "column": "duration_ms", "op": ">", "value": 500.0}


class TestQueryBuilder:
    """Tests for the QueryBuilder fluent API."""

    def test_time_range(self):
        """Test setting time range."""
        spec = QueryBuilder().time_range(3600).count().build()
        assert spec.time_range == 3600

    def test_time_presets(self):
        """Test time range presets."""
        assert QueryBuilder().last_10_minutes().build().time_range == 600
        assert QueryBuilder().last_30_minutes().build().time_range == 1800
        assert QueryBuilder().last_1_hour().build().time_range == 3600
        assert QueryBuilder().last_2_hours().build().time_range == 7200
        assert QueryBuilder().last_8_hours().build().time_range == 28800
        assert QueryBuilder().last_24_hours().build().time_range == 86400
        assert QueryBuilder().last_1_day().build().time_range == 86400
        assert QueryBuilder().last_7_days().build().time_range == 604800
        assert QueryBuilder().last_14_days().build().time_range == 1209600
        assert QueryBuilder().last_28_days().build().time_range == 2419200

    def test_absolute_time(self):
        """Test setting absolute time range."""
        spec = QueryBuilder().absolute_time(1000000, 1003600).count().build()
        assert spec.start_time == 1000000
        assert spec.end_time == 1003600
        assert spec.time_range is None

    def test_start_time_and_end_time(self):
        """Test setting start_time and end_time separately."""
        spec = QueryBuilder().start_time(1000000).end_time(1003600).count().build()
        assert spec.start_time == 1000000
        assert spec.end_time == 1003600
        assert spec.time_range is None

    def test_time_range_clears_absolute_time(self):
        """Test that time_range() clears any absolute time settings."""
        spec = (
            QueryBuilder()
            .start_time(1000000)
            .end_time(1003600)
            .time_range(3600)  # This should clear start/end
            .count()
            .build()
        )
        assert spec.time_range == 3600
        assert spec.start_time is None
        assert spec.end_time is None

    def test_absolute_time_clears_time_range(self):
        """Test that absolute time methods clear time_range."""
        spec = (
            QueryBuilder()
            .time_range(3600)
            .start_time(1000000)  # This clears time_range
            .end_time(1003600)
            .count()
            .build()
        )
        assert spec.start_time == 1000000
        assert spec.end_time == 1003600
        assert spec.time_range is None

    def test_incomplete_absolute_time_raises_error(self):
        """Test that setting only start_time or end_time raises an error."""
        with pytest.raises(ValueError, match="Both start_time and end_time must be set"):
            QueryBuilder().start_time(1000000).count().build()

        with pytest.raises(ValueError, match="Both start_time and end_time must be set"):
            QueryBuilder().end_time(1003600).count().build()

    def test_granularity(self):
        """Test setting granularity."""
        spec = QueryBuilder().time_range(3600).granularity(60).count().build()
        assert spec.granularity == 60

    def test_count(self):
        """Test adding COUNT calculation."""
        spec = QueryBuilder().count().build()
        assert len(spec.calculations) == 1
        assert spec.calculations[0].op == CalcOp.COUNT

    def test_count_with_alias(self):
        """Test adding COUNT with alias."""
        spec = QueryBuilder().count(alias="total").build()
        assert spec.calculations[0].alias == "total"

    def test_multiple_calculations(self):
        """Test adding multiple calculations."""
        spec = QueryBuilder().count().p99("duration_ms").avg("duration_ms").build()
        assert len(spec.calculations) == 3
        assert spec.calculations[0].op == CalcOp.COUNT
        assert spec.calculations[1].op == CalcOp.P99
        assert spec.calculations[1].column == "duration_ms"
        assert spec.calculations[2].op == CalcOp.AVG

    def test_all_calculation_shortcuts(self):
        """Test all calculation shortcut methods."""
        builder = QueryBuilder()
        builder.count()
        builder.sum("col")
        builder.avg("col")
        builder.min("col")
        builder.max("col")
        builder.count_distinct("col")
        builder.p50("col")
        builder.p90("col")
        builder.p95("col")
        builder.p99("col")
        builder.heatmap("col")
        builder.concurrency()
        spec = builder.build()
        assert len(spec.calculations) == 12

    def test_filter(self):
        """Test adding filter."""
        spec = QueryBuilder().filter("status", FilterOp.EQUALS, 200).build()
        assert len(spec.filters) == 1
        assert spec.filters[0].column == "status"
        assert spec.filters[0].op == FilterOp.EQUALS
        assert spec.filters[0].value == 200

    def test_where_alias(self):
        """Test where() as alias for filter()."""
        spec = QueryBuilder().where("status", ">=", 500).build()
        assert len(spec.filters) == 1

    def test_where_equals(self):
        """Test where_equals shortcut."""
        spec = QueryBuilder().where_equals("service", "api").build()
        assert spec.filters[0].op == FilterOp.EQUALS
        assert spec.filters[0].value == "api"

    def test_where_exists(self):
        """Test where_exists shortcut."""
        spec = QueryBuilder().where_exists("error").build()
        assert spec.filters[0].op == FilterOp.EXISTS

    def test_filter_combination(self):
        """Test setting filter combination."""
        spec = (
            QueryBuilder()
            .filter("status", FilterOp.EQUALS, 200)
            .filter("service", FilterOp.EQUALS, "api")
            .filter_with(FilterCombination.OR)
            .build()
        )
        assert spec.filter_combination == FilterCombination.OR

    def test_breakdown(self):
        """Test adding breakdowns."""
        spec = QueryBuilder().breakdown("service", "endpoint").build()
        assert spec.breakdowns == ["service", "endpoint"]

    def test_group_by_alias(self):
        """Test group_by() as alias for breakdown()."""
        spec = QueryBuilder().group_by("service").build()
        assert spec.breakdowns == ["service"]

    def test_order_by(self):
        """Test adding order."""
        spec = QueryBuilder().order_by(CalcOp.COUNT, OrderDirection.DESCENDING).build()
        assert len(spec.orders) == 1
        assert spec.orders[0].op == CalcOp.COUNT
        assert spec.orders[0].order == OrderDirection.DESCENDING

    def test_order_by_count(self):
        """Test order_by_count shortcut."""
        spec = QueryBuilder().order_by_count().build()
        assert spec.orders[0].op == CalcOp.COUNT

    def test_limit(self):
        """Test setting limit."""
        spec = QueryBuilder().limit(100).build()
        assert spec.limit == 100

    def test_having(self):
        """Test adding having clause."""
        spec = QueryBuilder().having(CalcOp.COUNT, FilterOp.GREATER_THAN, 100).build()
        assert len(spec.havings) == 1
        assert spec.havings[0].calculate_op == CalcOp.COUNT
        assert spec.havings[0].op == FilterOp.GREATER_THAN
        assert spec.havings[0].value == 100

    def test_complex_query(self):
        """Test building a complex query."""
        spec = (
            QueryBuilder()
            .last_24_hours()
            .granularity(300)
            .count()
            .p99("duration_ms")
            .avg("duration_ms", alias="avg_duration")
            .where("status", FilterOp.GREATER_THAN_OR_EQUAL, 500)
            .where_exists("error")
            .filter_with(FilterCombination.AND)
            .breakdown("service", "endpoint")
            .order_by_count(OrderDirection.DESCENDING)
            .limit(100)
            .having(CalcOp.COUNT, FilterOp.GREATER_THAN, 10)
            .build()
        )
        assert spec.time_range == 86400
        assert spec.granularity == 300
        assert len(spec.calculations) == 3
        assert len(spec.filters) == 2
        assert spec.filter_combination == FilterCombination.AND
        assert spec.breakdowns == ["service", "endpoint"]
        assert len(spec.orders) == 1
        assert spec.limit == 100
        assert len(spec.havings) == 1

    def test_build_for_trigger(self):
        """Test building TriggerQuery."""
        trigger_query = QueryBuilder().last_30_minutes().p99("duration_ms").build_for_trigger()
        assert isinstance(trigger_query, TriggerQuery)
        assert trigger_query.time_range == 1800

    def test_build_for_trigger_validates_time_range(self):
        """Test that build_for_trigger validates time range <= 3600."""
        with pytest.raises(ValueError, match="must be <= 3600"):
            QueryBuilder().last_2_hours().count().build_for_trigger()

    def test_build_for_trigger_rejects_absolute_time(self):
        """Test that build_for_trigger rejects absolute time ranges."""
        with pytest.raises(ValueError, match="does not support absolute time"):
            QueryBuilder().absolute_time(1000, 2000).count().build_for_trigger()

    # -------------------------------------------------------------------------
    # Filter Shortcut Tests
    # -------------------------------------------------------------------------

    def test_eq_shortcut(self):
        """Test .eq() filter shortcut."""
        spec = QueryBuilder().eq("status", 200).build()
        assert spec.filters[0].column == "status"
        assert spec.filters[0].op == FilterOp.EQUALS
        assert spec.filters[0].value == 200

    def test_ne_shortcut(self):
        """Test .ne() filter shortcut."""
        spec = QueryBuilder().ne("status", 500).build()
        assert spec.filters[0].op == FilterOp.NOT_EQUALS

    def test_gt_shortcut(self):
        """Test .gt() filter shortcut."""
        spec = QueryBuilder().gt("duration_ms", 100).build()
        assert spec.filters[0].op == FilterOp.GREATER_THAN

    def test_gte_shortcut(self):
        """Test .gte() filter shortcut."""
        spec = QueryBuilder().gte("status", 500).build()
        assert spec.filters[0].op == FilterOp.GREATER_THAN_OR_EQUAL

    def test_lt_shortcut(self):
        """Test .lt() filter shortcut."""
        spec = QueryBuilder().lt("duration_ms", 1000).build()
        assert spec.filters[0].op == FilterOp.LESS_THAN

    def test_lte_shortcut(self):
        """Test .lte() filter shortcut."""
        spec = QueryBuilder().lte("status", 299).build()
        assert spec.filters[0].op == FilterOp.LESS_THAN_OR_EQUAL

    def test_starts_with_shortcut(self):
        """Test .starts_with() filter shortcut."""
        spec = QueryBuilder().starts_with("endpoint", "/api").build()
        assert spec.filters[0].op == FilterOp.STARTS_WITH

    def test_does_not_start_with_shortcut(self):
        """Test .does_not_start_with() filter shortcut."""
        spec = QueryBuilder().does_not_start_with("endpoint", "/internal").build()
        assert spec.filters[0].op == FilterOp.DOES_NOT_START_WITH

    def test_contains_shortcut(self):
        """Test .contains() filter shortcut."""
        spec = QueryBuilder().contains("message", "error").build()
        assert spec.filters[0].op == FilterOp.CONTAINS

    def test_does_not_contain_shortcut(self):
        """Test .does_not_contain() filter shortcut."""
        spec = QueryBuilder().does_not_contain("message", "debug").build()
        assert spec.filters[0].op == FilterOp.DOES_NOT_CONTAIN

    def test_exists_shortcut(self):
        """Test .exists() filter shortcut."""
        spec = QueryBuilder().exists("error").build()
        assert spec.filters[0].op == FilterOp.EXISTS

    def test_does_not_exist_shortcut(self):
        """Test .does_not_exist() filter shortcut."""
        spec = QueryBuilder().does_not_exist("cached").build()
        assert spec.filters[0].op == FilterOp.DOES_NOT_EXIST

    def test_is_in_shortcut(self):
        """Test .is_in() filter shortcut."""
        spec = QueryBuilder().is_in("service", ["api", "web"]).build()
        assert spec.filters[0].op == FilterOp.IN
        assert spec.filters[0].value == ["api", "web"]

    def test_not_in_shortcut(self):
        """Test .not_in() filter shortcut."""
        spec = QueryBuilder().not_in("service", ["internal"]).build()
        assert spec.filters[0].op == FilterOp.NOT_IN


class TestQuerySpecBuilder:
    """Tests for QuerySpec.builder() class method."""

    def test_builder_class_method(self):
        """Test that QuerySpec.builder() returns a QueryBuilder."""
        builder = QuerySpec.builder()
        assert isinstance(builder, QueryBuilder)

    def test_build_from_class_method(self):
        """Test building QuerySpec from class method."""
        spec = QuerySpec.builder().count().last_1_hour().build()
        assert isinstance(spec, QuerySpec)
        assert spec.time_range == 3600


class TestQuerySpecWithTypedModels:
    """Tests for QuerySpec accepting typed models."""

    def test_accept_calculation_objects(self):
        """Test that QuerySpec accepts Calculation objects."""
        spec = QuerySpec(
            time_range=3600,
            calculations=[Calculation(op=CalcOp.COUNT)],
        )
        assert spec.calculations[0].op == CalcOp.COUNT

    def test_accept_filter_objects(self):
        """Test that QuerySpec accepts Filter objects."""
        spec = QuerySpec(
            time_range=3600,
            filters=[Filter(column="status", op=FilterOp.EQUALS, value=200)],
        )
        assert spec.filters[0].column == "status"

    def test_accept_mixed_calculations(self):
        """Test that QuerySpec accepts mixed Calculation objects and dicts."""
        spec = QuerySpec(
            time_range=3600,
            calculations=[
                Calculation(op=CalcOp.COUNT),
                {"op": "P99", "column": "duration_ms"},
            ],
        )
        assert len(spec.calculations) == 2

    def test_model_dump_for_api_normalizes_typed_models(self):
        """Test that model_dump_for_api normalizes typed models to dicts."""
        spec = QuerySpec(
            time_range=3600,
            calculations=[Calculation(op=CalcOp.P99, column="duration_ms")],
            filters=[Filter(column="status", op=FilterOp.GREATER_THAN_OR_EQUAL, value=500)],
        )
        data = spec.model_dump_for_api()
        assert data["calculations"] == [{"op": "P99", "column": "duration_ms"}]
        assert data["filters"] == [{"column": "status", "op": ">=", "value": 500}]

    def test_model_dump_for_api_handles_dicts(self):
        """Test that model_dump_for_api handles dicts (backward compat)."""
        spec = QuerySpec(
            time_range=3600,
            calculations=[{"op": "COUNT"}],
        )
        data = spec.model_dump_for_api()
        assert data["calculations"] == [{"op": "COUNT"}]


class TestTriggerQueryWithTypedModels:
    """Tests for TriggerQuery accepting typed models."""

    def test_accept_calculation_objects(self):
        """Test that TriggerQuery accepts Calculation objects."""
        query = TriggerQuery(
            time_range=900,
            calculations=[Calculation(op=CalcOp.P99, column="duration_ms")],
        )
        assert query.calculations[0].op == CalcOp.P99

    def test_accept_filter_objects(self):
        """Test that TriggerQuery accepts Filter objects."""
        query = TriggerQuery(
            time_range=900,
            filters=[Filter(column="error", op=FilterOp.EXISTS, value=True)],
        )
        assert query.filters[0].op == FilterOp.EXISTS

    def test_default_calculations(self):
        """Test that TriggerQuery has default calculations."""
        query = TriggerQuery()
        assert len(query.calculations) == 1
        assert query.calculations[0].op == CalcOp.COUNT
