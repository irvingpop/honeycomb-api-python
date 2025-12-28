"""Test cases for Recipients resource.

Coverage:
- 6 tools (list, get, create, update, delete, get_triggers)
- 2 test cases (skeleton - expand to 10, one per recipient type)
"""

TEST_CASES = [
    {
        "id": "recipient_email_create",
        "description": "Create email recipient",
        "prompt": "Create an email recipient for alerts to user@example.com",
        "expected_tool": "honeycomb_create_recipient",
        "expected_params": {
            "type": "email",
            "target": "user@example.com",
        },
        "assertion_checks": [],
    },
    {
        "id": "recipient_slack_create",
        "description": "Create Slack recipient",
        "prompt": "Create a Slack recipient that sends alerts to #ops-alerts channel",
        "expected_tool": "honeycomb_create_recipient",
        "expected_params": {
            "type": "slack",
            "target": "#ops-alerts",
        },
        "assertion_checks": [],
    },
]
