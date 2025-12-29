"""Test cases for Events resource.

Coverage:
- 2 tools (send_event, send_batch_events)
- 2 test cases (1 per operation)
"""

TEST_CASES = [
    {
        "id": "event_send_single",
        "description": "Send single event",
        "prompt": (
            "Send an event to dataset 'api-logs' with data: "
            "endpoint='/api/users', status_code=200, duration_ms=42"
        ),
        "expected_tool": "honeycomb_send_event",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [
            "'data' in params",
            "isinstance(params['data'], dict)",
        ],
    },
    {
        "id": "event_send_batch",
        "description": "Send batch of events",
        "prompt": (
            "Send a batch of 2 events to dataset 'api-logs': "
            "first event with endpoint='/api/users' and duration_ms=42, "
            "second event with endpoint='/api/posts' and duration_ms=18"
        ),
        "expected_tool": "honeycomb_send_batch_events",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [
            "'events' in params",
            "isinstance(params['events'], list)",
            "len(params['events']) >= 2",
        ],
    },
]
