# Honeycomb API Tools Specification

**Status**: Proposal
**Author**: Migration Tooling Team
**Date**: 2026-01-10

## Overview

This document specifies two new MCP tools for the honeycomb-api package to support LLM-driven exploration of Honeycomb environments. These tools enable Claude to intelligently navigate large environments with many datasets and thousands of columns.

## Motivation

When translating observability dashboards from other platforms (Datadog, Grafana, New Relic) to Honeycomb, Claude needs to map source metrics to Honeycomb columns. In production environments:

- Datasets can have **thousands of columns**
- Environments can have **dozens of datasets**
- Including all columns in the prompt is impractical (token limits, cost, latency)

These tools enable an **agentic exploration pattern** where Claude searches for relevant columns on-demand rather than receiving everything upfront.

## Tool 1: `honeycomb_search_columns`

### Purpose

Search for columns across one or all datasets in an environment using fuzzy matching. Includes both regular columns and derived columns.

### Tool Definition

```python
SEARCH_COLUMNS_TOOL = {
    "name": "honeycomb_search_columns",
    "description": """Search for columns in Honeycomb datasets by name pattern.

Use this tool to find columns that match metrics from source dashboards.
Returns column names, types, and which dataset they belong to.
Includes both regular columns and derived columns.

Examples:
- Search for "latency" to find duration/latency columns
- Search for "error" to find error-related columns
- Search for "http.status" to find HTTP status code columns
- Search in a specific dataset or across all datasets""",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (partial column name, supports fuzzy matching)"
            },
            "dataset": {
                "type": "string",
                "description": "Optional: specific dataset to search. If omitted, searches all datasets."
            },
            "limit": {
                "type": "integer",
                "description": "Maximum results to return (default: 50, max: 1000)",
                "default": 50
            },
            "offset": {
                "type": "integer",
                "description": "Offset for pagination (default: 0)",
                "default": 0
            }
        },
        "required": ["query"]
    }
}
```

### Response Schema

```python
@dataclass
class ColumnSearchResult:
    column: str                    # Column name (or derived column alias)
    dataset: str                   # Dataset the column belongs to (or "__environment__" for env-wide DCs)
    type: str                      # Column type (string, integer, float, boolean)
    description: str               # Column description (if available)
    similarity: float              # Match score (0.0 - 1.0)
    last_written: str | None       # Relative timestamp, e.g. "7 days ago", ">60 days ago"
    is_derived: bool               # True if this is a derived column
    derived_expression: str | None # For derived columns: the expression (e.g., "LT($status_code, 500)")

@dataclass
class SearchColumnsResponse:
    results: list[ColumnSearchResult]
    related_derived_columns: list[ColumnSearchResult]  # DCs that reference matched columns
    total_matches: int             # Total matches before limit/offset applied
    datasets_searched: int         # Number of datasets searched
    has_more: bool                 # True if more results available (pagination)
```

### Example Response

```json
{
    "results": [
        {
            "column": "http.response.latency_ms",
            "dataset": "frontend-service",
            "type": "float",
            "description": "HTTP response latency in milliseconds",
            "similarity": 0.92,
            "last_written": "10 seconds ago",
            "is_derived": false,
            "derived_expression": null
        },
        {
            "column": "duration_ms",
            "dataset": "frontend-service",
            "type": "float",
            "description": "Span duration",
            "similarity": 0.65,
            "last_written": "10 seconds ago",
            "is_derived": false,
            "derived_expression": null
        },
        {
            "column": "latency_bucket",
            "dataset": "__environment__",
            "type": "string",
            "description": "Latency SLI bucket",
            "similarity": 0.70,
            "last_written": null,
            "is_derived": true,
            "derived_expression": "IF(LTE($duration_ms, 100), \"fast\", IF(LTE($duration_ms, 500), \"medium\", \"slow\"))"
        }
    ],
    "related_derived_columns": [
        {
            "column": "is_slow_request",
            "dataset": "frontend-service",
            "type": "boolean",
            "description": "Request took >1s",
            "similarity": 0.0,
            "last_written": null,
            "is_derived": true,
            "derived_expression": "GT($http.response.latency_ms, 1000)"
        }
    ],
    "total_matches": 45,
    "datasets_searched": 8,
    "has_more": true
}
```

### Implementation Notes

1. **Fuzzy Matching**: Use `difflib.SequenceMatcher` or similar for substring and fuzzy matching
2. **Case Insensitive**: Searches should be case-insensitive
3. **Cross-Dataset**: When `dataset` is omitted, search all datasets
4. **Caching**: Consider caching column lists per dataset (columns don't change frequently)
5. **Derived Columns**:
   - Include both environment-wide derived columns and dataset-specific derived columns
   - When searching all datasets: fetch environment DCs from `GET /1/derived_columns` AND iterate through each dataset to get dataset-specific DCs
   - This complexity should be transparent to the caller
6. **Related Derived Columns**: Also return derived columns whose expressions reference any of the matched columns (helps LLM discover useful computed fields)
7. **Pagination**: Support `offset` parameter for paginated results; return `has_more` flag

### Search Algorithm

```python
def search_columns(query: str, columns: list[str]) -> list[tuple[str, float]]:
    """
    Score columns against query using multiple strategies:
    1. Exact match (score: 1.0)
    2. Prefix match (score: 0.9)
    3. Substring match (score: 0.8)
    4. Fuzzy match using SequenceMatcher (score: ratio * 0.7)
    """
    results = []
    query_lower = query.lower()

    for column in columns:
        col_lower = column.lower()

        if col_lower == query_lower:
            score = 1.0
        elif col_lower.startswith(query_lower):
            score = 0.9
        elif query_lower in col_lower:
            score = 0.8
        else:
            # Fuzzy match
            ratio = SequenceMatcher(None, query_lower, col_lower).ratio()
            score = ratio * 0.7

        if score > 0.3:  # Minimum threshold
            results.append((column, score))

    return sorted(results, key=lambda x: x[1], reverse=True)
```

---

## Tool 2: `honeycomb_get_environment_summary`

### Purpose

Provide a high-level overview of all datasets in an environment, enabling Claude to understand the environment structure and make informed dataset selection decisions.

### Tool Definition

```python
ENVIRONMENT_SUMMARY_TOOL = {
    "name": "honeycomb_get_environment_summary",
    "description": """Get a summary of all datasets in the Honeycomb environment.

Use this tool to understand what datasets exist and their characteristics
before deciding which dataset(s) to use for a translation.

Returns dataset names, descriptions, column counts, and sample column names
to help identify the right dataset for specific metrics.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "include_sample_columns": {
                "type": "boolean",
                "description": "Include sample column names for each dataset (default: true)",
                "default": True
            },
            "sample_column_count": {
                "type": "integer",
                "description": "Number of sample columns per dataset (default: 10, max: 50)",
                "default": 10
            }
        },
        "required": []
    }
}
```

### Response Schema

```python
@dataclass
class SemanticGroups:
    """Flags indicating presence of OpenTelemetry semantic convention groups."""
    has_otel_traces: bool        # trace.*, span.*, service.name, duration_ms
    has_http: bool               # http.* fields
    has_db: bool                 # db.* fields (database operations)
    has_k8s: bool                # k8s.* fields (Kubernetes)
    has_cloud: bool              # cloud.* fields (AWS, GCP, Azure)
    has_system_metrics: bool     # system.* fields (CPU, memory, disk, network)
    has_histograms: bool         # Fields with .max, .count, .avg, .sum, .p50, etc.
    has_logs: bool               # body, severity, severity_text

@dataclass
class DatasetSummary:
    name: str                    # Dataset slug
    description: str             # Dataset description
    column_count: int            # Total number of columns
    derived_column_count: int    # Number of derived columns
    last_written: str | None     # Relative timestamp, e.g. "10 seconds ago", "7 days ago"
    semantic_groups: SemanticGroups  # Which OTel semantic groups are present
    custom_columns: list[str]    # Non-OTel columns (unique to this dataset)

@dataclass
class EnvironmentSummaryResponse:
    environment: str             # Environment name/slug
    dataset_count: int           # Total number of datasets
    datasets: list[DatasetSummary]
    environment_derived_columns: list[DerivedColumnSummary] | None

@dataclass
class DerivedColumnSummary:
    alias: str
    expression: str
    description: str | None
```

### Example Response

```json
{
    "environment": "production",
    "dataset_count": 5,
    "datasets": [
        {
            "name": "frontend-service",
            "description": "Web frontend traces and metrics",
            "column_count": 245,
            "derived_column_count": 12,
            "last_written": "10 seconds ago",
            "semantic_groups": {
                "has_otel_traces": true,
                "has_http": true,
                "has_db": false,
                "has_k8s": true,
                "has_cloud": true,
                "has_system_metrics": false,
                "has_histograms": false,
                "has_logs": false
            },
            "custom_columns": [
                "user.id",
                "user.plan_tier",
                "feature_flag.enabled",
                "checkout.cart_value",
                "ab_test.variant"
            ]
        },
        {
            "name": "api-gateway",
            "description": "API gateway request/response data",
            "column_count": 189,
            "derived_column_count": 5,
            "last_written": "10 seconds ago",
            "semantic_groups": {
                "has_otel_traces": true,
                "has_http": true,
                "has_db": false,
                "has_k8s": true,
                "has_cloud": false,
                "has_system_metrics": false,
                "has_histograms": false,
                "has_logs": false
            },
            "custom_columns": [
                "upstream.service",
                "rate_limit.exceeded",
                "auth.method",
                "request.size_bytes",
                "response.size_bytes"
            ]
        },
        {
            "name": "host-metrics",
            "description": "Infrastructure metrics from hosts",
            "column_count": 412,
            "derived_column_count": 2,
            "last_written": "30 seconds ago",
            "semantic_groups": {
                "has_otel_traces": false,
                "has_http": false,
                "has_db": false,
                "has_k8s": true,
                "has_cloud": true,
                "has_system_metrics": true,
                "has_histograms": true,
                "has_logs": false
            },
            "custom_columns": [
                "host.name",
                "host.id",
                "process.name"
            ]
        }
    ],
    "environment_derived_columns": [
        {
            "alias": "sli.availability",
            "expression": "LT($http.response.status_code, 500)",
            "description": "Request succeeded (non-5xx)"
        },
        {
            "alias": "sli.latency_bucket",
            "expression": "IF(LTE($duration_ms, 100), \"fast\", \"slow\")",
            "description": "Latency SLI bucket"
        }
    ]
}
```

### Semantic Group Detection

Detect OpenTelemetry semantic convention groups by checking for column prefixes:

```python
SEMANTIC_GROUP_PATTERNS = {
    "has_otel_traces": [
        "trace.trace_id", "trace.span_id", "trace.parent_id",
        "span.kind", "span.name", "span.status",
        "service.name", "service.version",
        "duration_ms", "name"  # common Honeycomb trace fields
    ],
    "has_http": ["http."],
    "has_db": ["db."],
    "has_k8s": ["k8s."],
    "has_cloud": ["cloud."],
    "has_system_metrics": ["system."],
    "has_histograms": [".max", ".min", ".count", ".sum", ".avg", ".p50", ".p90", ".p95", ".p99"],
    "has_logs": ["body", "severity", "severity_text", "log."],
}

def detect_semantic_groups(columns: list[str]) -> SemanticGroups:
    """Detect which OTel semantic groups are present in columns."""
    col_set = set(col.lower() for col in columns)

    def has_group(patterns: list[str]) -> bool:
        for pattern in patterns:
            if pattern.endswith("."):
                # Prefix match
                if any(c.startswith(pattern) for c in col_set):
                    return True
            elif pattern.startswith("."):
                # Suffix match (for histograms)
                if any(c.endswith(pattern) for c in col_set):
                    return True
            else:
                # Exact match
                if pattern in col_set:
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
```

### Custom Column Extraction

Only return columns that don't match known OTel semantic conventions:

```python
KNOWN_PREFIXES = [
    "trace.", "span.", "service.", "http.", "db.", "k8s.", "cloud.",
    "system.", "log.", "net.", "rpc.", "messaging.", "faas.", "process.",
    "exception.", "thread.", "code.", "enduser.",
]
KNOWN_EXACT = [
    "duration_ms", "name", "body", "severity", "severity_text",
]

def extract_custom_columns(columns: list[str], max_count: int = 20) -> list[str]:
    """Extract columns that don't match known OTel conventions."""
    custom = []
    for col in columns:
        col_lower = col.lower()
        # Skip known prefixes
        if any(col_lower.startswith(p) for p in KNOWN_PREFIXES):
            continue
        # Skip known exact matches
        if col_lower in KNOWN_EXACT:
            continue
        # Skip histogram suffixes on otherwise-known columns
        if any(col_lower.endswith(s) for s in [".max", ".min", ".count", ".sum", ".avg", ".p50", ".p90", ".p95", ".p99"]):
            base = col_lower.rsplit(".", 1)[0]
            if any(base.startswith(p) for p in KNOWN_PREFIXES):
                continue
        custom.append(col)

    return custom[:max_count]
```

### Implementation Notes

1. **Semantic Group Summarization**: Instead of listing standard OTel columns, use boolean flags to indicate which groups are present. This dramatically reduces response size for datasets with hundreds of standard columns.

2. **Custom Columns Only**: The `custom_columns` field contains only non-OTel columns that are unique to this dataset - these are what differentiate datasets and help with matching.

3. **Performance**: This may require multiple API calls; consider:
   - Parallel fetching of dataset metadata
   - Caching with reasonable TTL (5-10 minutes)

4. **Derived Columns**: Include both dataset-level and environment-level derived columns with their expressions.

---

## Usage Patterns

### Pattern 1: Direct Dataset Translation

When user specifies a target dataset:

```
1. User provides source dashboard + target dataset
2. Claude uses honeycomb_search_columns(query="<metric>", dataset="<target>")
3. Claude maps source metrics to found columns
4. Translation proceeds with validated columns
```

### Pattern 2: Auto-Select Dataset Mode

When user wants automatic dataset selection:

```
1. User provides source dashboard, no target dataset
2. Claude calls honeycomb_get_environment_summary()
3. Claude analyzes source metrics and dataset summaries
4. Claude selects best-matching dataset(s)
5. Claude uses honeycomb_search_columns() to find specific columns
6. Translation proceeds with validated columns
```

### Pattern 3: Multi-Dataset Board

For dashboards that span multiple data sources:

```
1. Claude calls honeycomb_get_environment_summary()
2. For each panel/query in source:
   a. Extract source metrics
   b. honeycomb_search_columns(query="<metric>") across all datasets
   c. Select best dataset for that panel
3. Generate board with panels targeting appropriate datasets
```

---

## API Requirements

These tools require the following Honeycomb API capabilities:

| Capability | API Endpoint | Notes |
|------------|--------------|-------|
| List datasets | `GET /1/datasets` | Already supported |
| Get dataset columns | `GET /1/columns/{dataset}` | Already supported |
| List derived columns | `GET /1/derived_columns/{dataset}` | Already supported |
| List environment DCs | `GET /1/derived_columns` | May need environment scope |

---

## Testing Requirements

### Unit Tests

1. Column search fuzzy matching accuracy (exact, prefix, substring, fuzzy)
2. Semantic group detection accuracy
3. Custom column extraction (correctly filters OTel columns)
4. Derived column expression parsing (extract referenced columns)
5. Related derived column discovery
6. Response schema validation
7. Pagination behavior

### Integration Tests

1. Search across multiple datasets
2. Handle datasets with 1000+ columns
3. Handle environments with 50+ datasets
4. Derived column retrieval (environment-wide + dataset-specific)
5. Cross-dataset derived column deduplication

### Performance Tests

1. Search latency with large column counts
2. Environment summary generation time
3. Cache effectiveness
4. Parallel dataset fetching

---

## Design Decisions

### Relative Timestamps for `last_written`

The `last_written` field uses **relative timestamps** (e.g., "10 seconds ago", "7 days ago", ">60 days ago") rather than ISO timestamps. Rationale:

1. **LLM Reasoning**: Relative timestamps are easier for Claude to reason about without date/time calculations
2. **Immediate Context**: "7 days ago" immediately conveys staleness, while "2026-01-03T15:30:00Z" requires mental math
3. **Staleness Buckets**: Natural buckets for decision-making:
   - Recent: "10 seconds ago", "5 minutes ago"
   - Active: "2 hours ago", "1 day ago"
   - Stale: "30 days ago"
   - Very stale: ">60 days ago"

### Semantic Group Summarization

Instead of listing all OTel columns, we use boolean flags (e.g., `has_http: true`). Rationale:

1. **Token Efficiency**: A dataset with 200 http.* columns becomes a single boolean
2. **Assumed Knowledge**: Claude knows what http.* columns typically exist
3. **Focus on Unique**: Custom columns are what differentiate datasets

---

## Open Questions

1. **Search Syntax**: Should we support advanced search syntax?
   - `type:float` - filter by column type
   - `dataset:frontend-*` - wildcard dataset matching
   - `"exact phrase"` - exact matching

2. **Caching Strategy**: What TTL is appropriate for column lists? Options:
   - Short (1 minute) - more accurate, more API calls
   - Medium (5 minutes) - balanced
   - Long (15 minutes) - better performance, may miss new columns

3. **Additional Semantic Groups**: Should we detect more OTel semantic convention groups?
   - `rpc.*` - gRPC/RPC operations
   - `messaging.*` - message queue operations
   - `faas.*` - serverless/FaaS operations
   - `net.*` - network attributes

4. **Dataset Activity Threshold**: Should stale datasets (no data in >60 days) be excluded or flagged differently in the environment summary?

---

## Timeline Estimate

| Phase | Work |
|-------|------|
| Phase 1 | `honeycomb_search_columns` basic implementation |
| Phase 2 | `honeycomb_get_environment_summary` implementation |
| Phase 3 | Caching layer |
| Phase 4 | Testing and refinement |

---

## References

- [Honeycomb API Documentation](https://docs.honeycomb.io/api/)
- [MCP Tool Specification](https://modelcontextprotocol.io/)
- [Migration Tooling PLAN.md - Phase 10.3](../PLAN.md)
