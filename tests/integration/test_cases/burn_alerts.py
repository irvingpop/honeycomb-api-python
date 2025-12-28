"""Test cases for Burn Alerts resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 3 test cases
- Variations: exhaustion_time, budget_rate
"""

TEST_CASES = [
    {
        "id": "burn_alert_exhaustion_time",
        "description": "Exhaustion time burn alert",
        "prompt": (
            "Create an exhaustion time burn alert for SLO slo-123 in dataset 'api-logs' "
            "that alerts when budget will be exhausted in 60 minutes"
        ),
        "expected_tool": "honeycomb_create_burn_alert",
        "expected_params": {
            "dataset": "api-logs",
            "slo_id": "slo-123",
            "alert_type": "exhaustion_time",
            "exhaustion_minutes": 60,
        },
        "assertion_checks": [],
    },
    {
        "id": "burn_alert_budget_rate",
        "description": "Budget rate burn alert",
        "prompt": (
            "Create a budget_rate burn alert for SLO slo-abc123 in dataset 'api-logs' "
            "that fires when the error budget decreases by more than 5% in a 60 minute window"
        ),
        "expected_tool": "honeycomb_create_burn_alert",
        "expected_params": {
            "dataset": "api-logs",
            "slo_id": "slo-abc123",
            "alert_type": "budget_rate",
            "budget_rate_decrease_threshold_per_million": 50000,
            "budget_rate_window_minutes": 60,
        },
        "assertion_checks": [],
    },
    {
        "id": "burn_alert_list",
        "description": "List burn alerts for SLO",
        "prompt": "List burn alerts for SLO slo-789 in dataset production",
        "expected_tool": "honeycomb_list_burn_alerts",
        "expected_params": {
            "dataset": "production",
            "slo_id": "slo-789",
        },
        "assertion_checks": [],
    },
]
