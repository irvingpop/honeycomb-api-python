"""Test cases for Triggers resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 13 test cases
- Variations: COUNT, P99, multiple filters, string operators, exists operator,
  email recipients, webhook recipients, webhook with auth headers, tags, exceeded_limit
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
    {
        "id": "trigger_with_email_recipient",
        "description": "Trigger with inline email recipient",
        "prompt": (
            "Create a trigger named 'Error Spike' in dataset 'api-logs' that alerts "
            "when error count (status_code >= 500) exceeds 50 in the last 15 minutes. "
            "Send email notifications to oncall@example.com"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
            "name": "Error Spike",
            "threshold": {"op": ">", "value": 50},
        },
        "assertion_checks": [
            "'recipients' in params",
            "len(params['recipients']) >= 1",
            "any(r.get('type') == 'email' and r.get('target') == 'oncall@example.com' for r in params['recipients'])",
        ],
    },
    {
        "id": "trigger_with_webhook_recipient",
        "description": "Trigger with inline webhook recipient",
        "prompt": (
            "Create a trigger named 'Latency Alert' in dataset 'api-logs' that alerts "
            "when P99 latency exceeds 2000ms in the last 30 minutes. "
            "Send webhook notification to https://hooks.example.com/alerts with name 'Latency Webhook'"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
            "name": "Latency Alert",
        },
        "assertion_checks": [
            "'recipients' in params",
            "any(r.get('type') == 'webhook' for r in params['recipients'])",
            "any(r.get('target') == 'https://hooks.example.com/alerts' or "
            "r.get('details', {}).get('webhook_url') == 'https://hooks.example.com/alerts' "
            "for r in params['recipients'])",
        ],
    },
    {
        "id": "trigger_with_webhook_auth_headers",
        "description": "Trigger with webhook recipient including auth headers",
        "prompt": (
            "Create a trigger named 'Critical API Errors' in dataset 'api-logs' that alerts "
            "when critical errors (status_code >= 500) exceed 10 in the last 10 minutes. "
            "Send webhook to https://api.example.com/notifications with Authorization header 'Bearer token123'"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [
            "'recipients' in params",
            "any(r.get('type') == 'webhook' for r in params['recipients'])",
        ],
    },
    {
        "id": "trigger_with_tags",
        "description": "Trigger with organizational tags",
        "prompt": (
            "Create a trigger named 'Service Health' in dataset 'api-logs' "
            "that alerts when request count < 100 in the last 15 minutes (low traffic alert). "
            "Tag it with team=platform and severity=medium"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
            "name": "Service Health",
            "threshold": {"op": "<", "value": 100},
        },
        "assertion_checks": [
            "'tags' in params",
            "any(t.get('key') == 'team' and t.get('value') == 'platform' for t in params.get('tags', []))",
        ],
    },
    {
        "id": "trigger_with_exceeded_limit",
        "description": "Trigger with exceeded_limit (must fail N times before alerting)",
        "prompt": (
            "Create a trigger in dataset 'api-logs' that alerts when error count > 50 "
            "in the last 15 minutes, but only after the threshold is exceeded 3 consecutive times "
            "to avoid false positives"
        ),
        "expected_tool": "honeycomb_create_trigger",
        "expected_params": {
            "dataset": "api-logs",
            "threshold": {"op": ">", "value": 50},
        },
        "assertion_checks": [
            "'threshold' in params",
            "params['threshold'].get('exceeded_limit') == 3 or params['threshold'].get('exceeded_limit') is None",
        ],
    },
]
