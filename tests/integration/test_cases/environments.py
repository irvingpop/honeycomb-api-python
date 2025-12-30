"""Test cases for Environments resource (v2).

Coverage:
- 5 tools (list, get, create, update, delete)
- 8 test cases covering environment management and dataset integration
"""

TEST_CASES = [
    {
        "id": "environment_list",
        "description": "List all environments",
        "prompt": "List all my environments",
        "expected_tool": "honeycomb_list_environments",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "environment_get",
        "description": "Get specific environment",
        "prompt": "Get environment 'hcaen_123'",
        "expected_tool": "honeycomb_get_environment",
        "expected_params": {
            "env_id": "hcaen_123",
        },
        "assertion_checks": [
            "'env_id' in params",
        ],
    },
    {
        "id": "environment_get_with_datasets",
        "description": "Get environment with its datasets",
        "prompt": "Get environment 'hcaen_456' and show me all datasets in it",
        "expected_tool": "honeycomb_get_environment",
        "expected_params": {
            "env_id": "hcaen_456",
            "with_datasets": True,
        },
        "assertion_checks": [
            "'env_id' in params",
            "'with_datasets' in params",
            "params['with_datasets'] == True",
        ],
    },
    {
        "id": "environment_create",
        "description": "Create a new environment",
        "prompt": "Create an environment named 'Production'",
        "expected_tool": "honeycomb_create_environment",
        "expected_params": {
            "name": "Production",
        },
        "assertion_checks": [
            "'name' in params",
        ],
    },
    {
        "id": "environment_create_with_details",
        "description": "Create environment with color and description",
        "prompt": "Create a blue environment named 'Staging' with description 'Staging environment'",
        "expected_tool": "honeycomb_create_environment",
        "expected_params": {
            "name": "Staging",
            "color": "blue",
            "description": "Staging environment",
        },
        "assertion_checks": [
            "'name' in params",
            "'color' in params",
            "'description' in params",
        ],
    },
    {
        "id": "environment_update_description",
        "description": "Update environment description",
        "prompt": "Update environment 'hcaen_789' with description 'Updated staging'",
        "expected_tool": "honeycomb_update_environment",
        "expected_params": {
            "env_id": "hcaen_789",
            "description": "Updated staging",
        },
        "assertion_checks": [
            "'env_id' in params",
            "'description' in params",
        ],
    },
    {
        "id": "environment_disable_delete_protection",
        "description": "Disable delete protection on environment",
        "prompt": "Disable delete protection for environment 'hcaen_999'",
        "expected_tool": "honeycomb_update_environment",
        "expected_params": {
            "env_id": "hcaen_999",
            "delete_protected": False,
        },
        "assertion_checks": [
            "'env_id' in params",
            "'delete_protected' in params",
            "params['delete_protected'] == False",
        ],
    },
    {
        "id": "environment_delete",
        "description": "Delete an environment",
        "prompt": "Delete environment 'hcaen_abc'",
        "expected_tool": "honeycomb_delete_environment",
        "expected_params": {
            "env_id": "hcaen_abc",
        },
        "assertion_checks": [
            "'env_id' in params",
        ],
    },
]
