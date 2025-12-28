"""Test cases for Datasets resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 2 test cases (skeleton - expand to 8)
"""

TEST_CASES = [
    {
        "id": "dataset_create",
        "description": "Create new dataset",
        "prompt": "Create a dataset named 'api-logs' with description 'Production API logs'",
        "expected_tool": "honeycomb_create_dataset",
        "expected_params": {
            "name": "api-logs",
            "description": "Production API logs",
        },
        "assertion_checks": [],
    },
    {
        "id": "dataset_list",
        "description": "List all datasets",
        "prompt": "List all datasets",
        "expected_tool": "honeycomb_list_datasets",
        "expected_params": {},
        "assertion_checks": [],
    },
]
