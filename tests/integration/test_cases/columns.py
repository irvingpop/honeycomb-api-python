"""Test cases for Columns resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 1 test case (skeleton - expand to 8)
"""

TEST_CASES = [
    {
        "id": "column_create",
        "description": "Create column with type",
        "prompt": "Create a column named 'user_id' of type string in dataset 'api-logs'",
        "expected_tool": "honeycomb_create_column",
        "expected_params": {
            "dataset": "api-logs",
            "key_name": "user_id",
            "type": "string",
        },
        "assertion_checks": [],
    },
]
