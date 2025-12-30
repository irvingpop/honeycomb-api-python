"""Test cases for Auth resource.

Coverage:
- 1 tool (get)
- 4 test cases covering v1/v2 auto-detection and explicit version selection
"""

TEST_CASES = [
    {
        "id": "auth_which_team",
        "description": "Get team information from API key",
        "prompt": "Which team am I authenticated to?",
        "expected_tool": "honeycomb_get_auth",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "auth_permissions",
        "description": "Get API key permissions",
        "prompt": "What permissions do I have?",
        "expected_tool": "honeycomb_get_auth",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "auth_environment",
        "description": "Get environment associated with credentials",
        "prompt": "Which environment are my credentials associated with?",
        "expected_tool": "honeycomb_get_auth",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "auth_management_key_info",
        "description": "Get management key info explicitly",
        "prompt": "Show me my management key information including scopes",
        "expected_tool": "honeycomb_get_auth",
        "expected_params": {
            "use_v2": True,
        },
        "assertion_checks": [
            "'use_v2' in params",
            "params['use_v2'] == True",
        ],
    },
]
