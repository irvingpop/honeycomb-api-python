"""Tests for DerivedColumnBuilder and DerivedColumn models."""

import pytest

from honeycomb import DerivedColumn, DerivedColumnBuilder, DerivedColumnCreate


class TestDerivedColumnCreate:
    """Tests for the DerivedColumnCreate model."""

    def test_create_minimal(self):
        """Test creating DerivedColumnCreate with minimal fields."""
        dc = DerivedColumnCreate(alias="test_col", expression="IF(EQUALS($status, 200), 1, 0)")
        assert dc.alias == "test_col"
        assert dc.expression == "IF(EQUALS($status, 200), 1, 0)"
        assert dc.description is None

    def test_create_with_description(self):
        """Test creating DerivedColumnCreate with description."""
        dc = DerivedColumnCreate(
            alias="test_col",
            expression="IF(EQUALS($status, 200), 1, 0)",
            description="1 if successful, 0 otherwise",
        )
        assert dc.description == "1 if successful, 0 otherwise"

    def test_model_dump_for_api_minimal(self):
        """Test serializing DerivedColumnCreate without description."""
        dc = DerivedColumnCreate(alias="test_col", expression="INT(1)")
        data = dc.model_dump_for_api()
        assert data == {"alias": "test_col", "expression": "INT(1)"}
        assert "description" not in data

    def test_model_dump_for_api_with_description(self):
        """Test serializing DerivedColumnCreate with description."""
        dc = DerivedColumnCreate(
            alias="test_col", expression="INT(1)", description="Always returns 1"
        )
        data = dc.model_dump_for_api()
        assert data == {
            "alias": "test_col",
            "expression": "INT(1)",
            "description": "Always returns 1",
        }


class TestDerivedColumn:
    """Tests for the DerivedColumn response model."""

    def test_create(self):
        """Test creating DerivedColumn from response data."""
        dc = DerivedColumn(
            id="dc-123",
            alias="test_col",
            expression="INT(1)",
            description="Test column",
            created_at=None,
            updated_at=None,
        )
        assert dc.id == "dc-123"
        assert dc.alias == "test_col"
        assert dc.expression == "INT(1)"
        assert dc.description == "Test column"

    def test_create_minimal(self):
        """Test creating DerivedColumn with minimal required fields."""
        dc = DerivedColumn(id="dc-123", alias="test_col", expression="INT(1)")
        assert dc.id == "dc-123"
        assert dc.description is None
        assert dc.created_at is None
        assert dc.updated_at is None


class TestDerivedColumnBuilder:
    """Tests for the DerivedColumnBuilder fluent API."""

    def test_minimal_build(self):
        """Test building with minimal required fields."""
        dc = DerivedColumnBuilder("test_col").expression("INT(1)").build()
        assert isinstance(dc, DerivedColumnCreate)
        assert dc.alias == "test_col"
        assert dc.expression == "INT(1)"
        assert dc.description is None

    def test_with_description(self):
        """Test building with description."""
        dc = (
            DerivedColumnBuilder("test_col")
            .expression("INT(1)")
            .description("Always returns 1")
            .build()
        )
        assert dc.description == "Always returns 1"

    def test_method_chaining(self):
        """Test that methods support chaining."""
        builder = DerivedColumnBuilder("test_col")
        result1 = builder.expression("INT(1)")
        result2 = result1.description("Test")
        assert result1 is builder
        assert result2 is builder

    def test_build_without_expression_raises_error(self):
        """Test that building without expression raises error."""
        builder = DerivedColumnBuilder("test_col")
        with pytest.raises(ValueError, match="Expression is required"):
            builder.build()

    def test_complex_expression(self):
        """Test building with complex expression."""
        dc = (
            DerivedColumnBuilder("success_flag")
            .expression("IF(LT($status_code, 400), 1, 0)")
            .description("1 if request succeeded, 0 otherwise")
            .build()
        )
        assert dc.alias == "success_flag"
        assert dc.expression == "IF(LT($status_code, 400), 1, 0)"
        assert dc.description == "1 if request succeeded, 0 otherwise"

    def test_sli_expression(self):
        """Test building SLI-style expression."""
        dc = (
            DerivedColumnBuilder("api_success_rate")
            .expression("IF(AND(EXISTS($status), LT($status, 500)), 1, 0)")
            .description("SLI for API availability - 1 for success, 0 for failure")
            .build()
        )
        assert dc.alias == "api_success_rate"
        assert "IF(AND(EXISTS($status), LT($status, 500)), 1, 0)" in dc.expression

    def test_mathematical_expression(self):
        """Test building mathematical expression."""
        dc = (
            DerivedColumnBuilder("error_rate_percent")
            .expression("MULT(DIV($errors, $total_requests), 100)")
            .description("Error rate as percentage")
            .build()
        )
        assert dc.alias == "error_rate_percent"
        assert "MULT(DIV(" in dc.expression

    def test_overwrite_expression(self):
        """Test that setting expression twice overwrites the first."""
        dc = (
            DerivedColumnBuilder("test_col")
            .expression("INT(1)")
            .expression("INT(2)")  # Overwrite
            .build()
        )
        assert dc.expression == "INT(2)"

    def test_overwrite_description(self):
        """Test that setting description twice overwrites the first."""
        dc = (
            DerivedColumnBuilder("test_col")
            .expression("INT(1)")
            .description("First description")
            .description("Second description")  # Overwrite
            .build()
        )
        assert dc.description == "Second description"

    def test_empty_alias(self):
        """Test creating builder with empty alias."""
        builder = DerivedColumnBuilder("")
        dc = builder.expression("INT(1)").build()
        assert dc.alias == ""

    def test_special_characters_in_alias(self):
        """Test alias with special characters."""
        dc = DerivedColumnBuilder("my_derived_column_2024").expression("INT(1)").build()
        assert dc.alias == "my_derived_column_2024"

    def test_docstring_example(self):
        """Test the example from the class docstring."""
        dc = (
            DerivedColumnBuilder("request_success")
            .expression("IF(LT($status_code, 400), 1, 0)")
            .description("1 if request succeeded, 0 otherwise")
            .build()
        )
        assert dc.alias == "request_success"
        assert dc.expression == "IF(LT($status_code, 400), 1, 0)"
        assert dc.description == "1 if request succeeded, 0 otherwise"


class TestDerivedColumnBuilderPatterns:
    """Tests for common derived column patterns."""

    def test_boolean_flag_pattern(self):
        """Test creating a boolean flag derived column."""
        dc = (
            DerivedColumnBuilder("is_error")
            .expression("IF(GTE($status, 500), 1, 0)")
            .description("1 if request is an error, 0 otherwise")
            .build()
        )
        assert dc.expression == "IF(GTE($status, 500), 1, 0)"

    def test_categorization_pattern(self):
        """Test creating a categorization derived column."""
        dc = (
            DerivedColumnBuilder("status_category")
            .expression(
                "IF(LT($status, 300), 'success', IF(LT($status, 400), 'redirect', IF(LT($status, 500), 'client_error', 'server_error')))"
            )
            .description("Categorize HTTP status codes")
            .build()
        )
        assert dc.alias == "status_category"

    def test_normalization_pattern(self):
        """Test creating a normalization derived column."""
        dc = (
            DerivedColumnBuilder("normalized_endpoint")
            .expression("REGEX_REPLACE($endpoint, '[0-9]+', ':id')")
            .description("Replace IDs in endpoints with :id placeholder")
            .build()
        )
        assert "REGEX_REPLACE" in dc.expression

    def test_aggregation_prep_pattern(self):
        """Test creating derived column for aggregation."""
        dc = (
            DerivedColumnBuilder("latency_bucket")
            .expression("IF(LT($duration, 100), 'fast', IF(LT($duration, 500), 'medium', 'slow'))")
            .description("Bucket requests by latency")
            .build()
        )
        assert dc.alias == "latency_bucket"
