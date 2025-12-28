"""Test cases for Triggers resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 8 test cases
- Variations: COUNT, P99, multiple filters, string operators, exists operator
"""

TEST_CASES = [
    {
        "id": "trigger_basic_count",
        "description": "Basic COUNT trigger with simple threshold",
        "prompt": (
            "Create a trigger named 'High Errors' in dataset 'api-logs' "
            "that fires when error count > 100 in the last 15 minutes"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
            "threshold": {"op": ">", "value": 100},
        },
        "assertion_checks": [
            "params['query']['calculations'][0]['op'] == 'COUNT'",
            "params['threshold']['value'] >= 100",
        ],
    },
    {
        "id": "trigger_p99_percentile",
        "description": "P99 calculation (not COUNT)",
        "prompt": (
            "Create a trigger in dataset 'api-logs' that alerts when "
            "P99 of duration exceeds 2000ms over the last 30 minutes"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
            "query": {"calculations": [{"op": "P99", "column": "duration"}]},
        },
        "assertion_checks": [
            "params['query']['calculations'][0]['op'] == 'P99'",
            "params['query']['calculations'][0]['column'] == 'duration'",
        ],
    },
    {
        "id": "trigger_multiple_filters",
        "description": "Multiple AND filter conditions",
        "prompt": (
            "Create a trigger in dataset 'api-logs' that alerts when the count of requests "
            "where status_code >= 500 AND duration > 1000 exceeds 100 in the last 15 minutes"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [
            "'filters' in params['query'] or 'filter_combination' in params['query']",
        ],
    },
    {
        "id": "trigger_string_contains",
        "description": "String filter operators (contains, starts-with)",
        "prompt": (
            "Create a trigger in dataset 'api-logs' that alerts when count of requests "
            "where endpoint contains '/api/v2' and method starts with 'POST' exceeds 1000"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
            "threshold": {"value": 1000},
        },
        "assertion_checks": [
            "'filters' in params['query'] or 'filter_combination' in params['query']",
        ],
    },
    {
        "id": "trigger_exists_filter",
        "description": "EXISTS filter operator",
        "prompt": (
            "Create a trigger in dataset 'api-logs' that alerts when count of requests "
            "where user_id exists exceeds 500"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
            "threshold": {"value": 500},
        },
        "assertion_checks": [],
    },
    {
        "id": "trigger_list",
        "description": "List all triggers in dataset",
        "prompt": "List all triggers in dataset 'api-logs'",
        "expected_tool": "honeycomb_list_triggers",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [],
    },
    {
        "id": "trigger_get",
        "description": "Get specific trigger by ID",
        "prompt": "Get trigger abc123 from dataset api-logs",
        "expected_tool": "honeycomb_get_trigger",
        "expected_params": {
            "dataset": "api-logs",
            "trigger_id": "abc123",
        },
        "assertion_checks": [],
    },
    {
        "id": "trigger_delete",
        "description": "Delete trigger by ID",
        "prompt": "Delete trigger abc123 from dataset my-dataset",
        "expected_tool": "honeycomb_delete_trigger",
        "expected_params": {
            "dataset": "my-dataset",
            "trigger_id": "abc123",
        },
        "assertion_checks": [],
    },
]
