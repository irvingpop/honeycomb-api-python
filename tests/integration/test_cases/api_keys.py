"""Test cases for API Keys resource (v2).

Coverage:
- 5 tools (list, get, create, update, delete)
- 7 test cases covering key management operations
"""

TEST_CASES = [
    {
        "id": "api_key_list",
        "description": "List all API keys",
        "prompt": "List all my API keys",
        "expected_tool": "honeycomb_list_api_keys",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "api_key_list_filtered",
        "description": "List ingest keys only",
        "prompt": "List all my ingest keys",
        "expected_tool": "honeycomb_list_api_keys",
        "expected_params": {
            "key_type": "ingest",
        },
        "assertion_checks": [
            "'key_type' in params",
        ],
    },
    {
        "id": "api_key_get",
        "description": "Get specific API key",
        "prompt": "Get API key 'hcaik_123'",
        "expected_tool": "honeycomb_get_api_key",
        "expected_params": {
            "key_id": "hcaik_123",
        },
        "assertion_checks": [
            "'key_id' in params",
        ],
    },
    {
        "id": "api_key_create",
        "description": "Create a new ingest API key",
        "prompt": "Create an ingest API key named 'Production Ingest' in environment 'hcaen_456'",
        "expected_tool": "honeycomb_create_api_key",
        "expected_params": {
            "name": "Production Ingest",
            "key_type": "ingest",
            "environment_id": "hcaen_456",
        },
        "assertion_checks": [
            "'name' in params",
            "'key_type' in params",
            "'environment_id' in params",
        ],
    },
    {
        "id": "api_key_update_name",
        "description": "Rename an API key",
        "prompt": "Rename API key 'hcaik_123' to 'Updated Name'",
        "expected_tool": "honeycomb_update_api_key",
        "expected_params": {
            "key_id": "hcaik_123",
            "name": "Updated Name",
        },
        "assertion_checks": [
            "'key_id' in params",
            "'name' in params",
        ],
    },
    {
        "id": "api_key_disable",
        "description": "Disable an API key",
        "prompt": "Disable API key 'hcaik_789'",
        "expected_tool": "honeycomb_update_api_key",
        "expected_params": {
            "key_id": "hcaik_789",
            "disabled": True,
        },
        "assertion_checks": [
            "'key_id' in params",
            "'disabled' in params",
            "params['disabled'] == True",
        ],
    },
    {
        "id": "api_key_delete",
        "description": "Delete an API key",
        "prompt": "Delete API key 'hcaik_999'",
        "expected_tool": "honeycomb_delete_api_key",
        "expected_params": {
            "key_id": "hcaik_999",
        },
        "assertion_checks": [
            "'key_id' in params",
        ],
    },
]
