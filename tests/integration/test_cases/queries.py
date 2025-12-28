"""Test cases for Queries resource.

Coverage:
- 3 tools (create, get, run)
- 1 test case (skeleton - expand to 8)
"""

TEST_CASES = [
    {
        "id": "query_create_basic",
        "description": "Create basic query",
        "prompt": "Create a query in dataset 'api-logs' that counts requests over the last hour",
        "expected_tool": "honeycomb_create_query",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [
            "params['query']['calculations'][0]['op'] == 'COUNT'",
        ],
    },
]
