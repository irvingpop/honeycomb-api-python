"""Test cases for Recipients resource.

Coverage:
- 6 tools (list, get, create, update, delete, get_triggers)
- 6 test cases (1 per operation)
"""

TEST_CASES = [
    {
        "id": "recipient_create",
        "description": "Create email recipient",
        "prompt": "Create an email recipient that sends alerts to oncall@example.com",
        "expected_tool": "honeycomb_create_recipient",
        "expected_params": {
            "type": "email",
            "details": {"email_address": "oncall@example.com"},
        },
        "assertion_checks": [
            "'type' in params",
            "'details' in params",
        ],
    },
    {
        "id": "recipient_list",
        "description": "List all recipients",
        "prompt": "List all notification recipients",
        "expected_tool": "honeycomb_list_recipients",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "recipient_get",
        "description": "Get specific recipient by ID",
        "prompt": "Get recipient rec-123",
        "expected_tool": "honeycomb_get_recipient",
        "expected_params": {
            "recipient_id": "rec-123",
        },
        "assertion_checks": [],
    },
    {
        "id": "recipient_update",
        "description": "Update recipient configuration",
        "prompt": "Update recipient rec-123 to send email alerts to new-oncall@example.com",
        "expected_tool": "honeycomb_update_recipient",
        "expected_params": {
            "recipient_id": "rec-123",
            "type": "email",
            "details": {"email_address": "new-oncall@example.com"},
        },
        "assertion_checks": [
            "'recipient_id' in params",
        ],
    },
    {
        "id": "recipient_delete",
        "description": "Delete recipient by ID",
        "prompt": "Delete recipient rec-456",
        "expected_tool": "honeycomb_delete_recipient",
        "expected_params": {
            "recipient_id": "rec-456",
        },
        "assertion_checks": [],
    },
    {
        "id": "recipient_get_triggers",
        "description": "Get triggers for recipient",
        "prompt": "Show me which triggers are using recipient rec-789",
        "expected_tool": "honeycomb_get_recipient_triggers",
        "expected_params": {
            "recipient_id": "rec-789",
        },
        "assertion_checks": [],
    },
]
