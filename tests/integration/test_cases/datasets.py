"""Test cases for Datasets resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 5 test cases (1 per operation)
"""

TEST_CASES = [
    {
        "id": "dataset_create",
        "description": "Create dataset with description",
        "prompt": "Create a dataset named 'production-logs' with description 'Production API logs'",
        "expected_tool": "honeycomb_create_dataset",
        "expected_params": {
            "name": "production-logs",
            "description": "Production API logs",
        },
        "assertion_checks": [
            "'name' in params",
        ],
    },
    {
        "id": "dataset_list",
        "description": "List all datasets",
        "prompt": "List all datasets",
        "expected_tool": "honeycomb_list_datasets",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "dataset_get",
        "description": "Get specific dataset by slug",
        "prompt": "Get the dataset with slug 'api-logs'",
        "expected_tool": "honeycomb_get_dataset",
        "expected_params": {
            "slug": "api-logs",
        },
        "assertion_checks": [],
    },
    {
        "id": "dataset_update",
        "description": "Update dataset description",
        "prompt": "Update dataset 'api-logs' to have name 'API Logs' and description 'Updated logs'",
        "expected_tool": "honeycomb_update_dataset",
        "expected_params": {
            "slug": "api-logs",
            "name": "API Logs",
            "description": "Updated logs",
        },
        "assertion_checks": [
            "'slug' in params",
            "'name' in params",
        ],
    },
    {
        "id": "dataset_delete",
        "description": "Delete dataset by slug",
        "prompt": "Delete the dataset with slug 'test-dataset'",
        "expected_tool": "honeycomb_delete_dataset",
        "expected_params": {
            "slug": "test-dataset",
        },
        "assertion_checks": [],
    },
]
