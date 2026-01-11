"""Unit tests for semantic groups detection."""

from honeycomb.tools.analysis.semantic_groups import (
    KNOWN_OTEL_EXACT,
    KNOWN_OTEL_PREFIXES,
    detect_semantic_groups,
    extract_custom_columns,
)


class TestDetectSemanticGroups:
    """Tests for the detect_semantic_groups function."""

    def test_http_columns(self):
        """HTTP columns should be detected."""
        columns = ["http.method", "http.status_code", "http.url", "custom_field"]
        groups = detect_semantic_groups(columns)
        assert groups.has_http is True
        assert groups.has_otel_traces is False
        assert groups.has_db is False

    def test_otel_trace_columns(self):
        """OTel trace columns should be detected."""
        columns = ["trace.trace_id", "span.span_id", "service.name", "duration_ms"]
        groups = detect_semantic_groups(columns)
        assert groups.has_otel_traces is True
        assert groups.has_http is False

    def test_db_columns(self):
        """Database columns should be detected."""
        columns = ["db.system", "db.statement", "db.operation"]
        groups = detect_semantic_groups(columns)
        assert groups.has_db is True

    def test_k8s_columns(self):
        """Kubernetes columns should be detected."""
        columns = ["k8s.pod.name", "k8s.namespace.name", "k8s.deployment.name"]
        groups = detect_semantic_groups(columns)
        assert groups.has_k8s is True

    def test_cloud_columns(self):
        """Cloud columns should be detected."""
        columns = ["cloud.provider", "cloud.region", "cloud.account.id"]
        groups = detect_semantic_groups(columns)
        assert groups.has_cloud is True

    def test_system_metrics_columns(self):
        """System metrics columns should be detected."""
        columns = ["system.cpu.utilization", "system.memory.usage", "system.disk.io"]
        groups = detect_semantic_groups(columns)
        assert groups.has_system_metrics is True

    def test_histogram_columns(self):
        """Histogram suffix columns should be detected."""
        columns = ["latency.p50", "latency.p90", "latency.p99", "requests.count", "duration.avg"]
        groups = detect_semantic_groups(columns)
        assert groups.has_histograms is True

    def test_logs_columns(self):
        """Log columns should be detected."""
        columns = ["body", "severity", "severity_text", "log.level"]
        groups = detect_semantic_groups(columns)
        assert groups.has_logs is True

    def test_mixed_columns(self):
        """Multiple semantic groups should all be detected."""
        columns = [
            "http.method",
            "db.system",
            "k8s.pod.name",
            "duration_ms",
            "trace.trace_id",
        ]
        groups = detect_semantic_groups(columns)
        assert groups.has_http is True
        assert groups.has_db is True
        assert groups.has_k8s is True
        assert groups.has_otel_traces is True

    def test_case_insensitive(self):
        """Detection should be case insensitive."""
        columns = ["HTTP.METHOD", "Duration_Ms", "TRACE.TRACE_ID"]
        groups = detect_semantic_groups(columns)
        assert groups.has_http is True
        assert groups.has_otel_traces is True

    def test_empty_columns(self):
        """Empty column list should return all False."""
        groups = detect_semantic_groups([])
        assert groups.has_http is False
        assert groups.has_otel_traces is False
        assert groups.has_db is False
        assert groups.has_k8s is False
        assert groups.has_cloud is False
        assert groups.has_system_metrics is False
        assert groups.has_histograms is False
        assert groups.has_logs is False

    def test_no_semantic_groups(self):
        """Custom columns should not trigger any semantic groups."""
        columns = ["user_id", "cart_value", "custom_metric"]
        groups = detect_semantic_groups(columns)
        assert groups.has_http is False
        assert groups.has_otel_traces is False
        assert groups.has_db is False


class TestExtractCustomColumns:
    """Tests for the extract_custom_columns function."""

    def test_filters_otel_columns(self):
        """OTel columns should be filtered out."""
        columns = ["http.method", "custom_field", "my_metric", "db.statement"]
        custom = extract_custom_columns(columns)
        assert "custom_field" in custom
        assert "my_metric" in custom
        assert "http.method" not in custom
        assert "db.statement" not in custom

    def test_filters_known_exact_columns(self):
        """Known exact OTel columns should be filtered out."""
        columns = ["duration_ms", "name", "body", "severity", "custom_field"]
        custom = extract_custom_columns(columns)
        assert "custom_field" in custom
        assert "duration_ms" not in custom
        assert "name" not in custom
        assert "body" not in custom
        assert "severity" not in custom

    def test_filters_histogram_suffixes(self):
        """Histogram suffixes on OTel columns should be filtered out."""
        columns = [
            "http.duration.p99",
            "custom.p99",
            "system.cpu.avg",
            "my_metric.avg",
        ]
        custom = extract_custom_columns(columns)
        # http.duration.p99 is an OTel prefix + histogram suffix
        assert "http.duration.p99" not in custom
        # system.cpu.avg is an OTel prefix + histogram suffix
        assert "system.cpu.avg" not in custom
        # custom.p99 and my_metric.avg are custom with histogram suffixes
        # These should be kept because the base is not OTel
        assert "custom.p99" in custom
        assert "my_metric.avg" in custom

    def test_respects_max_count(self):
        """Should respect max_count limit."""
        columns = [f"custom_{i}" for i in range(50)]
        custom = extract_custom_columns(columns, max_count=10)
        assert len(custom) == 10

    def test_default_max_count(self):
        """Default max_count should be 20."""
        columns = [f"custom_{i}" for i in range(50)]
        custom = extract_custom_columns(columns)
        assert len(custom) == 20

    def test_preserves_order(self):
        """Should preserve the original order of columns."""
        columns = ["first_custom", "http.method", "second_custom", "db.system", "third_custom"]
        custom = extract_custom_columns(columns)
        assert custom == ["first_custom", "second_custom", "third_custom"]

    def test_empty_columns(self):
        """Empty column list should return empty list."""
        custom = extract_custom_columns([])
        assert custom == []

    def test_all_otel_columns(self):
        """All OTel columns should return empty list."""
        columns = ["http.method", "db.statement", "trace.trace_id", "duration_ms"]
        custom = extract_custom_columns(columns)
        assert custom == []

    def test_all_custom_columns(self):
        """All custom columns should be returned (up to max)."""
        columns = ["user_id", "cart_value", "session_id"]
        custom = extract_custom_columns(columns)
        assert custom == columns


class TestKnownPrefixes:
    """Tests for KNOWN_OTEL_PREFIXES constant."""

    def test_common_prefixes_included(self):
        """Common OTel prefixes should be included."""
        assert "http." in KNOWN_OTEL_PREFIXES
        assert "db." in KNOWN_OTEL_PREFIXES
        assert "trace." in KNOWN_OTEL_PREFIXES
        assert "span." in KNOWN_OTEL_PREFIXES
        assert "k8s." in KNOWN_OTEL_PREFIXES
        assert "cloud." in KNOWN_OTEL_PREFIXES
        assert "system." in KNOWN_OTEL_PREFIXES

    def test_all_prefixes_have_dot(self):
        """All prefixes should end with a dot."""
        for prefix in KNOWN_OTEL_PREFIXES:
            assert prefix.endswith("."), f"Prefix '{prefix}' should end with '.'"


class TestKnownExactColumns:
    """Tests for KNOWN_OTEL_EXACT constant."""

    def test_common_exact_columns_included(self):
        """Common exact OTel columns should be included."""
        assert "duration_ms" in KNOWN_OTEL_EXACT
        assert "name" in KNOWN_OTEL_EXACT
        assert "body" in KNOWN_OTEL_EXACT
        assert "severity" in KNOWN_OTEL_EXACT
