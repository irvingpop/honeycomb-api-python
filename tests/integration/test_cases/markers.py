"""Test cases for Markers resource.

Coverage:
- Markers: 4 tools (list, create, update, delete)
- Marker Settings: 5 tools (list, get, create, update, delete)
- 9 test cases (1 per operation)
"""

TEST_CASES = [
    # Markers
    {
        "id": "marker_list",
        "description": "List markers in dataset",
        "prompt": "List all markers in dataset api-logs",
        "expected_tool": "honeycomb_list_markers",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [],
    },
    {
        "id": "marker_create",
        "description": "Create deployment marker",
        "prompt": "Create a deployment marker in api-logs with message 'deploy v1.2.3' and type 'deploy'",
        "expected_tool": "honeycomb_create_marker",
        "expected_params": {
            "dataset": "api-logs",
            "message": "deploy v1.2.3",
            "type": "deploy",
        },
        "assertion_checks": [
            "'message' in params",
            "'type' in params",
        ],
    },
    {
        "id": "marker_update",
        "description": "Update marker message",
        "prompt": "Update marker abc123 in api-logs to have message 'updated deploy v1.2.4' and type 'deploy'",
        "expected_tool": "honeycomb_update_marker",
        "expected_params": {
            "dataset": "api-logs",
            "marker_id": "abc123",
        },
        "assertion_checks": [
            "'marker_id' in params",
            "'message' in params",
        ],
    },
    {
        "id": "marker_delete",
        "description": "Delete marker by ID",
        "prompt": "Delete marker xyz789 from dataset production",
        "expected_tool": "honeycomb_delete_marker",
        "expected_params": {
            "dataset": "production",
            "marker_id": "xyz789",
        },
        "assertion_checks": [],
    },
    # Marker Settings
    {
        "id": "marker_setting_list",
        "description": "List marker settings (primary use case)",
        "prompt": "List all marker settings in dataset api-logs",
        "expected_tool": "honeycomb_list_marker_settings",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [],
    },
    {
        "id": "marker_setting_get",
        "description": "Get specific marker setting by ID",
        "prompt": "Get marker setting set-123 from dataset api-logs",
        "expected_tool": "honeycomb_get_marker_setting",
        "expected_params": {
            "dataset": "api-logs",
            "setting_id": "set-123",
        },
        "assertion_checks": [],
    },
    {
        "id": "marker_setting_create",
        "description": "Create marker type-to-color mapping",
        "prompt": "Create a marker setting in api-logs for type 'deploy' with color green (#00FF00)",
        "expected_tool": "honeycomb_create_marker_setting",
        "expected_params": {
            "dataset": "api-logs",
            "type": "deploy",
            "color": "#00FF00",
        },
        "assertion_checks": [
            "'type' in params",
            "'color' in params",
        ],
    },
    {
        "id": "marker_setting_update",
        "description": "Update marker setting color",
        "prompt": "Update marker setting set-456 in production to have type 'incident' and color red (#FF0000)",
        "expected_tool": "honeycomb_update_marker_setting",
        "expected_params": {
            "dataset": "production",
            "setting_id": "set-456",
        },
        "assertion_checks": [
            "'setting_id' in params",
            "'type' in params",
            "'color' in params",
        ],
    },
    {
        "id": "marker_setting_delete",
        "description": "Delete marker setting by ID",
        "prompt": "Delete marker setting set-789 from dataset api-logs",
        "expected_tool": "honeycomb_delete_marker_setting",
        "expected_params": {
            "dataset": "api-logs",
            "setting_id": "set-789",
        },
        "assertion_checks": [],
    },
]
