"""Unit tests for column search fuzzy matching algorithm."""

from honeycomb.tools.analysis.column_search import (
    calculate_similarity,
    expression_references_column,
)


class TestCalculateSimilarity:
    """Tests for the calculate_similarity function."""

    def test_exact_match(self):
        """Exact match should return 1.0."""
        assert calculate_similarity("status_code", "status_code") == 1.0

    def test_exact_match_case_insensitive(self):
        """Exact match should be case insensitive."""
        assert calculate_similarity("STATUS_CODE", "status_code") == 1.0
        assert calculate_similarity("status_code", "STATUS_CODE") == 1.0
        assert calculate_similarity("Status_Code", "status_code") == 1.0

    def test_prefix_match(self):
        """Prefix match should return 0.9."""
        assert calculate_similarity("status", "status_code") == 0.9
        assert calculate_similarity("http", "http.method") == 0.9
        assert calculate_similarity("duration", "duration_ms") == 0.9

    def test_prefix_match_case_insensitive(self):
        """Prefix match should be case insensitive."""
        assert calculate_similarity("STATUS", "status_code") == 0.9
        assert calculate_similarity("HTTP", "http.method") == 0.9

    def test_substring_match(self):
        """Substring match should return 0.8."""
        assert calculate_similarity("code", "status_code") == 0.8
        assert calculate_similarity("method", "http.method") == 0.8
        assert calculate_similarity("error", "has_error_flag") == 0.8

    def test_substring_match_case_insensitive(self):
        """Substring match should be case insensitive."""
        assert calculate_similarity("CODE", "status_code") == 0.8
        assert calculate_similarity("METHOD", "http.method") == 0.8

    def test_fuzzy_match(self):
        """Fuzzy match should return ratio * 0.7."""
        # Typo in query - should still get some similarity
        score = calculate_similarity("statis", "status")
        assert 0.3 < score < 0.8

        # Similar word
        score = calculate_similarity("latency", "duration")
        assert 0.0 < score < 0.5

    def test_no_match(self):
        """Completely different strings should have low similarity."""
        score = calculate_similarity("xyz", "status_code")
        assert score < 0.3

        score = calculate_similarity("foo", "bar")
        assert score < 0.3

    def test_empty_strings(self):
        """Empty strings should be handled gracefully."""
        # Empty query is a prefix of any string (since "".startswith("") is True)
        score = calculate_similarity("", "status_code")
        assert score == 0.9  # Prefix match

        # Empty column name - fuzzy match gives low score
        score = calculate_similarity("status", "")
        assert score < 0.3

    def test_score_ordering(self):
        """Verify score ordering: exact > prefix > substring > fuzzy."""
        exact = calculate_similarity("status", "status")
        prefix = calculate_similarity("status", "status_code")
        substring = calculate_similarity("status", "http_status_code")
        fuzzy = calculate_similarity("statis", "status_code")

        assert exact > prefix > substring > fuzzy


class TestExpressionReferencesColumn:
    """Tests for the expression_references_column function."""

    def test_simple_reference(self):
        """Simple column reference should be detected."""
        assert expression_references_column("$status_code", "status_code")
        assert expression_references_column("$duration_ms", "duration_ms")

    def test_reference_in_function(self):
        """Column reference inside a function should be detected."""
        assert expression_references_column("IF(LT($status_code, 400), 1, 0)", "status_code")
        assert expression_references_column("GT($duration_ms, 1000)", "duration_ms")
        assert expression_references_column("CONCAT($service, '-', $environment)", "service")
        assert expression_references_column("CONCAT($service, '-', $environment)", "environment")

    def test_no_reference(self):
        """Non-matching columns should not be detected."""
        assert not expression_references_column("$status_code", "duration_ms")
        assert not expression_references_column("IF(LT($status_code, 400), 1, 0)", "error")

    def test_partial_name_no_match(self):
        """Partial column name should not match."""
        # "status" should not match "$status_code"
        assert not expression_references_column("$status_code", "status")
        # "code" should not match "$status_code"
        assert not expression_references_column("$status_code", "code")

    def test_column_name_as_substring_no_match(self):
        """Column name that is a substring of another column should not match."""
        # "error" should not match "$error_count"
        assert not expression_references_column("$error_count", "error")
        # "http" should not match "$http_status"
        assert not expression_references_column("$http_status", "http")

    def test_multiple_references(self):
        """Multiple column references should all be detectable."""
        expr = "IF(AND(GT($latency, 100), EQ($status, 'error')), 1, 0)"
        assert expression_references_column(expr, "latency")
        assert expression_references_column(expr, "status")
        assert not expression_references_column(expr, "error")  # "error" is a string literal

    def test_special_characters_in_column_name(self):
        """Column names with special characters should be escaped properly."""
        # Column names with dots
        assert expression_references_column("$http.status_code", "http.status_code")
        assert not expression_references_column("$http.status_code", "http")

    def test_case_sensitive(self):
        """Column references should be case sensitive."""
        # Honeycomb column references are case sensitive
        assert expression_references_column("$Status_Code", "Status_Code")
        # Note: Whether this should match depends on Honeycomb's behavior
        # Our current implementation is case sensitive which matches typical behavior
