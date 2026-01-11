"""Response models for analysis tools.

These dataclasses define the response schemas for honeycomb_search_columns
and honeycomb_get_environment_summary tools.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ColumnSearchResult:
    """A column matching a search query."""

    column: str
    """Column name (or derived column alias)."""

    dataset: str
    """Dataset the column belongs to (or '__environment__' for env-wide DCs)."""

    type: str
    """Column type (string, integer, float, boolean)."""

    description: str | None
    """Column description (if available)."""

    similarity: float
    """Match score (0.0 - 1.0)."""

    last_written: str | None
    """Relative timestamp, e.g. '7 days ago', '>60 days ago'."""

    is_derived: bool
    """True if this is a derived column."""

    derived_expression: str | None
    """For derived columns: the expression (e.g., 'LT($status_code, 500)')."""


@dataclass
class SearchColumnsResponse:
    """Response for honeycomb_search_columns."""

    results: list[ColumnSearchResult]
    """Column matches sorted by similarity score."""

    related_derived_columns: list[ColumnSearchResult]
    """Derived columns that reference matched columns."""

    total_matches: int
    """Total matches before limit/offset applied."""

    datasets_searched: int
    """Number of datasets searched."""

    has_more: bool
    """True if more results available (pagination)."""


@dataclass
class SemanticGroups:
    """Flags indicating presence of OpenTelemetry semantic convention groups."""

    has_otel_traces: bool = False
    """trace.*, span.*, service.name, duration_ms."""

    has_http: bool = False
    """http.* fields."""

    has_db: bool = False
    """db.* fields (database operations)."""

    has_k8s: bool = False
    """k8s.* fields (Kubernetes)."""

    has_cloud: bool = False
    """cloud.* fields (AWS, GCP, Azure)."""

    has_system_metrics: bool = False
    """system.* fields (CPU, memory, disk, network)."""

    has_histograms: bool = False
    """Fields with .max, .count, .avg, .sum, .p50, etc."""

    has_logs: bool = False
    """body, severity, severity_text."""


@dataclass
class DatasetSummary:
    """Summary of a single dataset."""

    name: str
    """Dataset slug."""

    description: str | None
    """Dataset description."""

    column_count: int
    """Total number of columns."""

    derived_column_count: int
    """Number of derived columns."""

    last_written: str | None
    """Relative timestamp, e.g. '10 seconds ago', '7 days ago'."""

    semantic_groups: SemanticGroups
    """Which OTel semantic groups are present."""

    custom_columns: list[str] = field(default_factory=list)
    """Non-OTel columns (unique to this dataset)."""


@dataclass
class DerivedColumnSummary:
    """Summary of a derived column."""

    alias: str
    """Derived column alias."""

    expression: str
    """Derived column expression."""

    description: str | None
    """Derived column description."""


@dataclass
class EnvironmentSummaryResponse:
    """Response for honeycomb_get_environment_summary."""

    environment: str
    """Environment name/slug."""

    dataset_count: int
    """Total number of datasets."""

    datasets: list[DatasetSummary]
    """Dataset summaries."""

    environment_derived_columns: list[DerivedColumnSummary] | None
    """Environment-wide derived columns."""


def format_relative_time(dt: datetime | None) -> str | None:
    """Convert a datetime to a relative timestamp string.

    Args:
        dt: The datetime to convert (should be timezone-aware)

    Returns:
        Relative timestamp like '10 seconds ago', '7 days ago', '>60 days ago',
        or None if input is None
    """
    if dt is None:
        return None

    # Ensure we're comparing timezone-aware datetimes
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)

    delta = now - dt
    seconds = delta.total_seconds()

    if seconds < 0:
        return "just now"

    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 86400 * 60:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return ">60 days ago"
