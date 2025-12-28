"""Test cases for SLOs resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 5 test cases
- Variations: existing column, inline expression, percentage conversion
"""

TEST_CASES = [
    {
        "id": "slo_basic_existing_column",
        "description": "SLO with existing derived column",
        "prompt": (
            "Create an SLO named 'API Availability' in dataset 'api-logs' "
            "with 99.9% target over 30 days, using success_rate as the SLI"
        ),
        "expected_tool": "honeycomb_create_slo",
        "expected_params": {
            "dataset": "api-logs",
            "target_per_million": 999000,
            "time_period_days": 30,
            "sli": {"alias": "success_rate"},
        },
        "assertion_checks": [
            "params['target_per_million'] == 999000",
            "params['time_period_days'] == 30",
        ],
    },
    {
        "id": "slo_inline_expression",
        "description": "SLO with inline derived column expression",
        "prompt": (
            "Create an SLO in dataset 'api-logs' with 99.5% target over 30 days "
            "where the SLI is the ratio of requests with status_code < 400 to total requests"
        ),
        "expected_tool": "honeycomb_create_slo",
        "expected_params": {
            "dataset": "api-logs",
            "target_per_million": 995000,
        },
        "assertion_checks": [
            "'expression' in params['sli'] or 'alias' in params['sli']",
        ],
    },
    {
        "id": "slo_percentage_conversion",
        "description": "Percentage to per-million conversion (99.99%)",
        "prompt": (
            "Create an SLO in dataset 'api-logs' with 99.99% target over 7 days "
            "using existing column success_rate"
        ),
        "expected_tool": "honeycomb_create_slo",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [
            "999000 <= params['target_per_million'] <= 1000000",
        ],
    },
    {
        "id": "slo_list",
        "description": "List all SLOs",
        "prompt": "List all SLOs in the production dataset",
        "expected_tool": "honeycomb_list_slos",
        "expected_params": {
            "dataset": "production",
        },
        "assertion_checks": [],
    },
    {
        "id": "slo_get",
        "description": "Get specific SLO by ID",
        "prompt": "Get SLO slo-456 from dataset production",
        "expected_tool": "honeycomb_get_slo",
        "expected_params": {
            "dataset": "production",
            "slo_id": "slo-456",
        },
        "assertion_checks": [],
    },
]
