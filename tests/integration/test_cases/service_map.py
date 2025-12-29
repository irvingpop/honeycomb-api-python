"""Test cases for Service Map Dependencies resource.

Coverage:
- 1 tool (query_service_map with automatic create + poll + paginate)
- 1 test case
"""

TEST_CASES = [
    {
        "id": "service_map_query",
        "description": "Query service dependencies",
        "prompt": "Show me service dependencies from the last 2 hours",
        "expected_tool": "honeycomb_query_service_map",
        "expected_params": {
            "time_range": 7200,
        },
        "assertion_checks": [
            "'time_range' in params",
        ],
    },
]
