"""Semantic group detection for OpenTelemetry conventions.

Detects which OTel semantic convention groups are present in a list of columns
and extracts custom (non-OTel) columns.
"""

from honeycomb.tools.analysis.models import SemanticGroups

# OTel semantic convention patterns for detection
SEMANTIC_GROUP_PATTERNS: dict[str, list[str]] = {
    "has_otel_traces": [
        "trace.trace_id",
        "trace.span_id",
        "trace.parent_id",
        "span.kind",
        "span.name",
        "span.status",
        "service.name",
        "service.version",
        "duration_ms",
        "name",
    ],
    "has_http": ["http."],
    "has_db": ["db."],
    "has_k8s": ["k8s."],
    "has_cloud": ["cloud."],
    "has_system_metrics": ["system."],
    "has_histograms": [".max", ".min", ".count", ".sum", ".avg", ".p50", ".p90", ".p95", ".p99"],
    "has_logs": ["body", "severity", "severity_text", "log."],
}

# Known OTel prefixes for filtering custom columns
KNOWN_OTEL_PREFIXES = [
    "trace.",
    "span.",
    "service.",
    "http.",
    "db.",
    "k8s.",
    "cloud.",
    "system.",
    "log.",
    "net.",
    "rpc.",
    "messaging.",
    "faas.",
    "process.",
    "exception.",
    "thread.",
    "code.",
    "enduser.",
    "container.",
    "host.",
    "os.",
    "telemetry.",
    "aws.",
    "gcp.",
    "azure.",
]

# Known exact OTel column names
KNOWN_OTEL_EXACT = [
    "duration_ms",
    "name",
    "body",
    "severity",
    "severity_text",
]


def detect_semantic_groups(columns: list[str]) -> SemanticGroups:
    """Detect which OTel semantic groups are present in columns.

    Args:
        columns: List of column names to analyze

    Returns:
        SemanticGroups with boolean flags for each detected group
    """
    col_set = {col.lower() for col in columns}

    def has_group(patterns: list[str]) -> bool:
        for pattern in patterns:
            if pattern.endswith("."):
                # Prefix match (e.g., "http.")
                if any(c.startswith(pattern) for c in col_set):
                    return True
            elif pattern.startswith("."):
                # Suffix match (e.g., ".max" for histograms)
                if any(c.endswith(pattern) for c in col_set):
                    return True
            else:
                # Exact match
                if pattern.lower() in col_set:
                    return True
        return False

    return SemanticGroups(
        has_otel_traces=has_group(SEMANTIC_GROUP_PATTERNS["has_otel_traces"]),
        has_http=has_group(SEMANTIC_GROUP_PATTERNS["has_http"]),
        has_db=has_group(SEMANTIC_GROUP_PATTERNS["has_db"]),
        has_k8s=has_group(SEMANTIC_GROUP_PATTERNS["has_k8s"]),
        has_cloud=has_group(SEMANTIC_GROUP_PATTERNS["has_cloud"]),
        has_system_metrics=has_group(SEMANTIC_GROUP_PATTERNS["has_system_metrics"]),
        has_histograms=has_group(SEMANTIC_GROUP_PATTERNS["has_histograms"]),
        has_logs=has_group(SEMANTIC_GROUP_PATTERNS["has_logs"]),
    )


def extract_custom_columns(columns: list[str], max_count: int = 20) -> list[str]:
    """Extract columns that don't match known OTel conventions.

    Args:
        columns: List of column names to filter
        max_count: Maximum number of custom columns to return

    Returns:
        List of non-OTel column names, up to max_count
    """
    custom: list[str] = []

    for col in columns:
        col_lower = col.lower()

        # Skip known prefixes
        if any(col_lower.startswith(p) for p in KNOWN_OTEL_PREFIXES):
            continue

        # Skip known exact matches
        if col_lower in KNOWN_OTEL_EXACT:
            continue

        # Skip histogram suffixes on otherwise-known columns
        histogram_suffixes = [
            ".max",
            ".min",
            ".count",
            ".sum",
            ".avg",
            ".p50",
            ".p90",
            ".p95",
            ".p99",
        ]
        if any(col_lower.endswith(s) for s in histogram_suffixes):
            base = col_lower.rsplit(".", 1)[0]
            if any(base.startswith(p) for p in KNOWN_OTEL_PREFIXES):
                continue

        custom.append(col)

    return custom[:max_count]
