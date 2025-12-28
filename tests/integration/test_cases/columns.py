"""Test cases for Columns resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 5 test cases (1 per operation)
"""

TEST_CASES = [
    {
        "id": "column_create",
        "description": "Create column with description",
        "prompt": "Create a column named 'duration_ms' of type float with description 'Request duration in milliseconds' in dataset 'api-logs'",
        "expected_tool": "honeycomb_create_column",
        "expected_params": {
            "dataset": "api-logs",
            "key_name": "duration_ms",
            "type": "float",
            "description": "Request duration in milliseconds",
        },
        "assertion_checks": [
            "'dataset' in params",
            "'key_name' in params",
        ],
    },
    {
        "id": "column_list",
        "description": "List all columns in dataset",
        "prompt": "List all columns in dataset 'api-logs'",
        "expected_tool": "honeycomb_list_columns",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [],
    },
    {
        "id": "column_get",
        "description": "Get specific column by ID",
        "prompt": "Get column col-123 from dataset api-logs",
        "expected_tool": "honeycomb_get_column",
        "expected_params": {
            "dataset": "api-logs",
            "column_id": "col-123",
        },
        "assertion_checks": [],
    },
    {
        "id": "column_update",
        "description": "Update column metadata",
        "prompt": "Update column col-123 in dataset 'api-logs': set key_name to 'endpoint', type to string, and description to 'API endpoint path'",
        "expected_tool": "honeycomb_update_column",
        "expected_params": {
            "dataset": "api-logs",
            "column_id": "col-123",
            "key_name": "endpoint",
            "type": "string",
            "description": "API endpoint path",
        },
        "assertion_checks": [
            "'column_id' in params",
            "'key_name' in params",
        ],
    },
    {
        "id": "column_delete",
        "description": "Delete column by ID",
        "prompt": "Delete column col-789 from dataset my-dataset",
        "expected_tool": "honeycomb_delete_column",
        "expected_params": {
            "dataset": "my-dataset",
            "column_id": "col-789",
        },
        "assertion_checks": [],
    },
]
