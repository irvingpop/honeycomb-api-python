"""Test cases for Queries resource.

Coverage:
- 3 tools (create, get, run)
- 16 test cases focusing on query_run complexity, calculated fields, and compare time offset
"""

TEST_CASES = [
    # Basic operations
    {
        "id": "query_create",
        "description": "Create saved query",
        "prompt": "Create a query in dataset 'api-logs' that counts requests in the last hour",
        "expected_tool": "honeycomb_create_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 3600,
        },
        "assertion_checks": [
            "'calculations' in params",
            "'time_range' in params",
        ],
    },
    {
        "id": "query_get",
        "description": "Get saved query by ID",
        "prompt": "Get query q-123 from dataset api-logs",
        "expected_tool": "honeycomb_get_query",
        "expected_params": {
            "dataset": "api-logs",
            "query_id": "q-123",
        },
        "assertion_checks": [],
    },
    # Complex query_run test cases
    {
        "id": "query_run_multiple_calculations",
        "description": "Multiple calculation types (COUNT, AVG, P99)",
        "prompt": (
            "Show me request count, average duration_ms, and P99 duration_ms "
            "from api-logs for the past 2 hours"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 7200,
        },
        "assertion_checks": [
            "len(params['calculations']) >= 3",
            "any(c.get('op') == 'COUNT' for c in params['calculations'])",
            "any(c.get('op') == 'AVG' and c.get('column') == 'duration_ms' for c in params['calculations'])",
            "any(c.get('op') == 'P99' and c.get('column') == 'duration_ms' for c in params['calculations'])",
        ],
    },
    {
        "id": "query_run_complex_filters",
        "description": "Multiple AND filters with different operators",
        "prompt": (
            "Query api-logs counting slow server errors: "
            "status_code >= 500 AND duration_ms > 1000 AND method = POST in the last hour"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 3600,
        },
        "assertion_checks": [
            "'filters' in params",
            "len(params['filters']) >= 3",
            "any(f.get('column') == 'status_code' and f.get('op') == '>=' and f.get('value') == 500 for f in params['filters'])",
            "any(f.get('column') == 'duration_ms' and f.get('op') == '>' and f.get('value') == 1000 for f in params['filters'])",
            "any(f.get('column') == 'method' and f.get('value') == 'POST' for f in params['filters'])",
        ],
    },
    {
        "id": "query_run_breakdowns_with_ordering",
        "description": "Breakdowns with ORDER BY",
        "prompt": (
            "Analyze api-logs grouped by endpoint: show request count and P95 latency, "
            "sorted by request volume descending, last 30 minutes"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 1800,
        },
        "assertion_checks": [
            "'breakdowns' in params",
            "'endpoint' in params.get('breakdowns', [])",
            "any(c.get('op') == 'COUNT' for c in params.get('calculations', []))",
            "any(c.get('op') == 'P95' and c.get('column') == 'duration_ms' for c in params.get('calculations', []))",
            "'orders' in params or 'order' in params",
        ],
    },
    {
        "id": "query_run_heatmap",
        "description": "HEATMAP calculation type",
        "prompt": "Generate a heatmap distribution of request durations in api-logs over the past hour",
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 3600,
        },
        "assertion_checks": [
            "any(c.get('op') == 'HEATMAP' and c.get('column') in ['duration_ms', 'duration'] for c in params.get('calculations', []))",
        ],
    },
    {
        "id": "query_run_having_with_limit",
        "description": "HAVING clause with LIMIT",
        "prompt": (
            "Find the top 20 busiest endpoints in api-logs (endpoints with more than 100 requests) "
            "over the last 2 hours"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 7200,
        },
        "assertion_checks": [
            "'breakdowns' in params and 'endpoint' in params['breakdowns']",
            "'limit' in params and params['limit'] <= 20",
            "'havings' in params or 'having' in params or 'orders' in params",
        ],
    },
    {
        "id": "query_run_string_operators",
        "description": "String filter operators (contains, starts-with)",
        "prompt": (
            "How many API v2 requests from Mozilla browsers hit api-logs in the past hour? "
            "Filter for endpoint containing '/api/v2' and user_agent starting with 'Mozilla'"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 3600,
        },
        "assertion_checks": [
            "'filters' in params",
            "len(params['filters']) >= 2",
            "any(f.get('column') == 'endpoint' and f.get('op') == 'contains' and '/api/v2' in str(f.get('value', '')) for f in params['filters'])",
            "any(f.get('column') == 'user_agent' and f.get('op') == 'starts-with' and 'Mozilla' in str(f.get('value', '')) for f in params['filters'])",
        ],
    },
    {
        "id": "query_run_exists_operator",
        "description": "EXISTS filter operator",
        "prompt": "Count authenticated requests in api-logs (where user_id field is present) from the last 30 minutes",
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 1800,
        },
        "assertion_checks": [
            "'filters' in params",
            "any(f.get('column') == 'user_id' and f.get('op') in ['exists', '!=', 'does-not-equal'] for f in params['filters'])",
        ],
    },
    {
        "id": "query_run_multi_breakdown_multi_calc",
        "description": "Multiple breakdowns with multiple calculations",
        "prompt": (
            "Break down api-logs by endpoint and status_code: "
            "I need request count, average latency, and max latency for the past 4 hours"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 14400,
        },
        "assertion_checks": [
            "'breakdowns' in params",
            "len(params.get('breakdowns', [])) >= 2",
            "'endpoint' in params.get('breakdowns', [])",
            "'status_code' in params.get('breakdowns', [])",
            "len(params.get('calculations', [])) >= 3",
            "any(c.get('op') == 'COUNT' for c in params['calculations'])",
            "any(c.get('op') == 'AVG' and c.get('column') in ['duration_ms', 'duration', 'latency'] for c in params['calculations'])",
            "any(c.get('op') == 'MAX' and c.get('column') in ['duration_ms', 'duration', 'latency'] for c in params['calculations'])",
        ],
    },
    {
        "id": "query_run_or_filter_combination",
        "description": "OR filter combination",
        "prompt": (
            "Check api-logs for problematic requests of either type: server errors (status >= 500) OR slow responses (duration > 5000ms) in the last hour"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 3600,
        },
        "assertion_checks": [
            "'filters' in params",
            "len(params['filters']) >= 2",
            "any(f.get('column') in ['status_code', 'status'] and f.get('value') == 500 for f in params['filters'])",
            "any(f.get('column') in ['duration_ms', 'duration'] and f.get('value') == 5000 for f in params['filters'])",
            "params.get('filter_combination') == 'OR'",
        ],
    },
    {
        "id": "query_run_sum_calculation",
        "description": "SUM calculation with breakdown",
        "prompt": (
            "Calculate total bytes transferred per endpoint in production dataset over the last 6 hours"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "production",
            "time_range": 21600,
        },
        "assertion_checks": [
            "'breakdowns' in params and 'endpoint' in params['breakdowns']",
            "any(c.get('op') == 'SUM' and c.get('column') in ['bytes', 'bytes_transferred', 'size'] for c in params.get('calculations', []))",
        ],
    },
    {
        "id": "query_run_environment_wide",
        "description": "Environment-wide query across all datasets",
        "prompt": (
            "Run an environment-wide query showing total error count (status_code >= 500) "
            "across all my datasets in the past hour"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "__all__",
            "time_range": 3600,
        },
        "assertion_checks": [
            "params.get('dataset') == '__all__'",
            "'filters' in params",
            "any(f.get('column') == 'status_code' and f.get('op') == '>=' and f.get('value') == 500 for f in params['filters'])",
            "any(c.get('op') == 'COUNT' for c in params.get('calculations', []))",
        ],
    },
    # Calculated fields (inline derived columns)
    {
        "id": "query_run_calculated_field",
        "description": "Query with inline calculated field",
        "prompt": (
            "Run a query on api-logs for the past hour: "
            "create a calculated field named 'latency_bucket' with expression IF(LTE($duration_ms, 100), 'fast', 'slow'), "
            "then count requests grouped by this latency_bucket"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 3600,
        },
        "assertion_checks": [
            "'calculated_fields' in params",
            "len(params.get('calculated_fields', [])) >= 1",
            "any(cf.get('name') == 'latency_bucket' for cf in params.get('calculated_fields', []))",
            "any('IF(' in cf.get('expression', '') or 'LTE(' in cf.get('expression', '') for cf in params.get('calculated_fields', []))",
            "'breakdowns' in params and 'latency_bucket' in params['breakdowns']",
        ],
    },
    {
        "id": "query_run_calculated_field_success_indicator",
        "description": "Query with calculated field for success rate",
        "prompt": (
            "Analyze api-logs over the past 2 hours: "
            "create a calculated field named 'is_success' using expression IF(LT($status_code, 400), 1, 0), "
            "then calculate the average of is_success to get the success rate"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 7200,
        },
        "assertion_checks": [
            "'calculated_fields' in params",
            "any(cf.get('name') == 'is_success' for cf in params.get('calculated_fields', []))",
            "any('IF(' in cf.get('expression', '') and 'status_code' in cf.get('expression', '') for cf in params.get('calculated_fields', []))",
            "any(c.get('op') == 'AVG' and c.get('column') == 'is_success' for c in params.get('calculations', []))",
        ],
    },
    # Compare time offset (historical comparison)
    {
        "id": "query_run_compare_24h",
        "description": "Query with 24-hour historical comparison",
        "prompt": (
            "Run a query on api-logs showing request count over the past hour "
            "and compare to the same time yesterday (24 hours ago)"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 3600,
        },
        "assertion_checks": [
            "'compare_time_offset_seconds' in params",
            "params.get('compare_time_offset_seconds') == 86400",
            "any(c.get('op') == 'COUNT' for c in params.get('calculations', []))",
        ],
    },
    {
        "id": "query_run_compare_7d",
        "description": "Query with 7-day historical comparison",
        "prompt": (
            "Analyze api-logs P99 latency over the past 4 hours "
            "and compare it to the same time period one week ago"
        ),
        "expected_tool": "honeycomb_run_query",
        "expected_params": {
            "dataset": "api-logs",
            "time_range": 14400,
        },
        "assertion_checks": [
            "'compare_time_offset_seconds' in params",
            "params.get('compare_time_offset_seconds') == 604800",
            "any(c.get('op') == 'P99' and c.get('column') in ['duration_ms', 'duration', 'latency'] for c in params.get('calculations', []))",
        ],
    },
]
