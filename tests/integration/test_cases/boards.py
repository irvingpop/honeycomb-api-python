"""Test cases for Boards resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 10 test cases with inline SLO creation, environment-wide queries, and comprehensive assertions
"""

TEST_CASES = [
    # Basic CRUD
    {
        "id": "board_list",
        "description": "List all boards",
        "prompt": "List all my dashboards",
        "expected_tool": "honeycomb_list_boards",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "board_get",
        "description": "Get board by ID",
        "prompt": "Get board board-123",
        "expected_tool": "honeycomb_get_board",
        "expected_params": {
            "board_id": "board-123",
        },
        "assertion_checks": [],
    },
    {
        "id": "board_delete",
        "description": "Delete board by ID",
        "prompt": "Delete board board-456",
        "expected_tool": "honeycomb_delete_board",
        "expected_params": {
            "board_id": "board-456",
        },
        "assertion_checks": [],
    },
    # Complex inline panel creation
    {
        "id": "board_create_inline_queries",
        "description": "Board with multiple inline query panels",
        "prompt": (
            "Create a board named 'API Health Dashboard' with auto-layout and two query panels: "
            "first panel named 'Error Count' from api-logs showing COUNT of errors (status_code >= 500) over 1 hour, "
            "second panel named 'P99 Latency' from api-logs showing P99 of duration_ms over 1 hour"
        ),
        "expected_tool": "honeycomb_create_board",
        "expected_params": {
            "name": "API Health Dashboard",
            "layout_generation": "auto",
        },
        "assertion_checks": [
            "'inline_query_panels' in params",
            "len(params['inline_query_panels']) >= 2",
            # Verify first panel structure
            "any(p.get('name') == 'Error Count' and p.get('dataset') == 'api-logs' and p.get('time_range') == 3600 for p in params['inline_query_panels'])",
            # Verify second panel has P99 calculation
            "any(p.get('name') == 'P99 Latency' and any(c.get('op') == 'P99' and c.get('column') in ['duration_ms', 'duration'] for c in p.get('calculations', [])) for p in params['inline_query_panels'])",
        ],
    },
    {
        "id": "board_create_with_text_panel",
        "description": "Board with inline queries and text panel",
        "prompt": (
            "Build a dashboard called 'Service Overview' with description 'Main service health' using auto-layout. "
            "Add a query panel named 'Request Rate' from production dataset showing COUNT broken down by endpoint over 2 hours. "
            "Also add a text panel with markdown: ## Service Status - Monitor during peak hours"
        ),
        "expected_tool": "honeycomb_create_board",
        "expected_params": {
            "name": "Service Overview",
            "description": "Main service health",
            "layout_generation": "auto",
        },
        "assertion_checks": [
            "'inline_query_panels' in params and len(params['inline_query_panels']) >= 1",
            "params['inline_query_panels'][0].get('name') == 'Request Rate'",
            "params['inline_query_panels'][0].get('dataset') == 'production'",
            "'breakdowns' in params['inline_query_panels'][0] and 'endpoint' in params['inline_query_panels'][0]['breakdowns']",
            "'text_panels' in params and len(params['text_panels']) >= 1",
            "any('Service Status' in str(tp.get('content', '')) for tp in params.get('text_panels', []))",
        ],
    },
    {
        "id": "board_create_complex_query",
        "description": "Board with complex query panel (filters, breakdowns, orders, limit)",
        "prompt": (
            "Create an 'SRE Dashboard' with auto-layout containing one query panel named 'Top Errors by Service': "
            "use api-logs dataset, count requests where status_code >= 500, "
            "group by service field, order by COUNT descending, limit to top 20, time range 1 hour"
        ),
        "expected_tool": "honeycomb_create_board",
        "expected_params": {
            "name": "SRE Dashboard",
            "layout_generation": "auto",
        },
        "assertion_checks": [
            "'inline_query_panels' in params",
            "len(params['inline_query_panels']) >= 1",
            "params['inline_query_panels'][0].get('dataset') == 'api-logs'",
            "params['inline_query_panels'][0].get('time_range') == 3600",
            "'filters' in params['inline_query_panels'][0]",
            "any(f.get('column') in ['status_code', 'status'] and f.get('value') == 500 for f in params['inline_query_panels'][0]['filters'])",
            "'breakdowns' in params['inline_query_panels'][0]",
            "'service' in params['inline_query_panels'][0].get('breakdowns', [])",
            "params['inline_query_panels'][0].get('limit', 0) <= 20",
        ],
    },
    {
        "id": "board_create_environment_wide_query",
        "description": "Board with environment-wide query (no dataset)",
        "prompt": (
            "Create a 'Cross-Service Dashboard' with auto-layout and one query panel named 'Total Errors' "
            "showing environment-wide COUNT of all errors (status_code >= 500) across all datasets in the past hour"
        ),
        "expected_tool": "honeycomb_create_board",
        "expected_params": {
            "name": "Cross-Service Dashboard",
        },
        "assertion_checks": [
            "'inline_query_panels' in params",
            "len(params['inline_query_panels']) >= 1",
            # Environment-wide is represented as dataset: "__all__"
            "params['inline_query_panels'][0].get('dataset') == '__all__'",
            "any(c.get('op') == 'COUNT' for c in params['inline_query_panels'][0].get('calculations', []))",
            "any(f.get('column') in ['status_code', 'status'] and f.get('value') == 500 for f in params['inline_query_panels'][0].get('filters', []))",
        ],
    },
    {
        "id": "board_create_inline_slo",
        "description": "Board with inline SLO creation (SLI with expression)",
        "prompt": (
            "Create a 'Production Monitoring' board with auto-layout containing: "
            "query panel 'Request Count' from production with COUNT over 1 day, "
            "and inline SLO panel named 'API Availability' for api-logs with 99.9% target (3 nines) over 30 days "
            "using SLI alias 'success_rate' with expression IF(LT($status_code, 400), 1, 0)"
        ),
        "expected_tool": "honeycomb_create_board",
        "expected_params": {
            "name": "Production Monitoring",
        },
        "assertion_checks": [
            "'inline_query_panels' in params and len(params['inline_query_panels']) >= 1",
            "'inline_slo_panels' in params and len(params['inline_slo_panels']) >= 1",
            "params['inline_slo_panels'][0].get('name') == 'API Availability'",
            "params['inline_slo_panels'][0].get('dataset') == 'api-logs'",
            "params['inline_slo_panels'][0]['sli'].get('alias') == 'success_rate'",
            "'expression' in params['inline_slo_panels'][0]['sli']",
            "params['inline_slo_panels'][0].get('target_nines') == 3",
            "params['inline_slo_panels'][0].get('time_period_days') == 30",
        ],
    },
    {
        "id": "board_create_with_slo_panel",
        "description": "Board with inline query and existing SLO ID",
        "prompt": (
            "Make a board called 'Platform Health' with auto-layout containing: "
            "a query panel named 'Request Count' from production showing COUNT over 4 hours, "
            "and an existing SLO panel for SLO ID slo-abc123"
        ),
        "expected_tool": "honeycomb_create_board",
        "expected_params": {
            "name": "Platform Health",
        },
        "assertion_checks": [
            "'inline_query_panels' in params and len(params['inline_query_panels']) >= 1",
            "params['inline_query_panels'][0].get('name') == 'Request Count'",
            "params['inline_query_panels'][0].get('time_range') == 14400",
            "'slo_panels' in params and len(params['slo_panels']) >= 1",
            "'slo-abc123' in params.get('slo_panels', [])",
        ],
    },
    {
        "id": "board_create_multi_panel_types",
        "description": "Board with all panel types (query, SLO, text) and tags",
        "prompt": (
            "Create an 'Operations Dashboard' with auto-layout and tag team=platform. "
            "Include query panel 'Error Rate' from api-logs counting errors over 1 hour, "
            "existing SLO panel slo-789, "
            "and text panel: ## Alerts - Check PagerDuty for incidents"
        ),
        "expected_tool": "honeycomb_create_board",
        "expected_params": {
            "name": "Operations Dashboard",
        },
        "assertion_checks": [
            "'inline_query_panels' in params and len(params['inline_query_panels']) >= 1",
            "params['inline_query_panels'][0].get('dataset') == 'api-logs'",
            "params['inline_query_panels'][0].get('time_range') == 3600",
            "'slo_panels' in params and 'slo-789' in params['slo_panels']",
            "'text_panels' in params",
            "any('Alerts' in str(tp.get('content', '')) for tp in params.get('text_panels', []))",
            "'tags' in params and any(t.get('key') == 'team' and t.get('value') == 'platform' for t in params['tags'])",
        ],
    },
]
