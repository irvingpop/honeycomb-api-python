"""Test cases for Derived Columns resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 1 test case (skeleton - expand to 8)
"""

TEST_CASES = [
    {
        "id": "derived_column_create",
        "description": "Create derived column with expression",
        "prompt": (
            "Create a derived column named 'error_rate' in dataset 'api-logs' "
            "with expression 'COUNT(status_code >= 500) / COUNT(*)'"
        ),
        "expected_tool": "honeycomb_create_derived_column",
        "expected_params": {
            "dataset": "api-logs",
            "alias": "error_rate",
        },
        "assertion_checks": [
            "'expression' in params",
        ],
    },
]
