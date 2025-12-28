"""Test cases for Derived Columns resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 5 test cases (1 per operation)
"""

TEST_CASES = [
    {
        "id": "derived_column_create",
        "description": "Create derived column with expression",
        "prompt": (
            "Create a derived column named 'is_error' in dataset 'api-logs' "
            "with expression IF(GTE($status_code, 500), 1, 0) and description '1 if error'"
        ),
        "expected_tool": "honeycomb_create_derived_column",
        "expected_params": {
            "dataset": "api-logs",
            "alias": "is_error",
        },
        "assertion_checks": [
            "'expression' in params",
            "'alias' in params",
        ],
    },
    {
        "id": "derived_column_list",
        "description": "List derived columns in dataset",
        "prompt": "List all derived columns in dataset 'api-logs'",
        "expected_tool": "honeycomb_list_derived_columns",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [],
    },
    {
        "id": "derived_column_get",
        "description": "Get specific derived column",
        "prompt": "Get derived column dc-123 from dataset api-logs",
        "expected_tool": "honeycomb_get_derived_column",
        "expected_params": {
            "dataset": "api-logs",
            "derived_column_id": "dc-123",
        },
        "assertion_checks": [],
    },
    {
        "id": "derived_column_update",
        "description": "Update derived column expression",
        "prompt": (
            "Update derived column dc-123 in dataset 'api-logs': "
            "set alias to 'is_success', expression to IF(LT($status_code, 400), 1, 0), "
            "and description to 'Success indicator'"
        ),
        "expected_tool": "honeycomb_update_derived_column",
        "expected_params": {
            "dataset": "api-logs",
            "derived_column_id": "dc-123",
            "alias": "is_success",
        },
        "assertion_checks": [
            "'derived_column_id' in params",
            "'expression' in params",
        ],
    },
    {
        "id": "derived_column_delete",
        "description": "Delete derived column by ID",
        "prompt": "Delete derived column dc-456 from dataset production",
        "expected_tool": "honeycomb_delete_derived_column",
        "expected_params": {
            "dataset": "production",
            "derived_column_id": "dc-456",
        },
        "assertion_checks": [],
    },
]
