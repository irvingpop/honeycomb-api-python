"""Test cases for Events resource.

Coverage:
- 2 tools (send_event, send_events_batch)
- 1 test case (skeleton - expand to 4)
"""

TEST_CASES = [
    {
        "id": "event_send_single",
        "description": "Send single event",
        "prompt": (
            "Send an event to dataset 'api-logs' with data: "
            "{endpoint: '/api/users', status_code: 200, duration: 150}"
        ),
        "expected_tool": "honeycomb_send_event",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [
            "'data' in params",
        ],
    },
]
