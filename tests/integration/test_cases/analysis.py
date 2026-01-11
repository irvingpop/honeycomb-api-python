"""Eval test cases for analysis tools.

These test cases verify that Claude correctly selects and parameterizes
the honeycomb_search_columns and honeycomb_get_environment_summary tools.
"""

TEST_CASES = [
    # ==============================================================================
    # honeycomb_search_columns test cases
    # ==============================================================================
    {
        "id": "search_columns_basic",
        "description": "Basic column search for error-related columns",
        "prompt": "Search for columns related to 'error' across all datasets in Honeycomb",
        "expected_tool": "honeycomb_search_columns",
        "expected_params": {"query": "error"},
        "assertion_checks": [
            "'query' in params",
            "params['query'].lower() == 'error' or 'error' in params['query'].lower()",
        ],
    },
    {
        "id": "search_columns_specific_dataset",
        "description": "Search columns in a specific dataset",
        "prompt": "Find all columns containing 'latency' in the api-logs dataset",
        "expected_tool": "honeycomb_search_columns",
        "expected_params": {"query": "latency", "dataset": "api-logs"},
        "assertion_checks": [
            "'query' in params",
            "'latency' in params['query'].lower()",
            "params.get('dataset') == 'api-logs'",
        ],
    },
    {
        "id": "search_columns_with_pagination",
        "description": "Search columns with pagination parameters",
        "prompt": "Search for 'http' columns in Honeycomb, show me the first 20 results",
        "expected_tool": "honeycomb_search_columns",
        "expected_params": {"query": "http"},
        "assertion_checks": [
            "'http' in params['query'].lower()",
            "params.get('limit', 50) <= 50",
        ],
    },
    {
        "id": "search_columns_status_code",
        "description": "Search for status code columns",
        "prompt": "Find columns that might contain HTTP status codes in my Honeycomb environment",
        "expected_tool": "honeycomb_search_columns",
        "expected_params": {},
        "assertion_checks": [
            "'query' in params",
            "any(term in params['query'].lower() for term in ['status', 'code', 'http'])",
        ],
    },
    {
        "id": "search_columns_duration",
        "description": "Search for duration/timing columns",
        "prompt": "I need to find columns related to request duration or latency in Honeycomb",
        "expected_tool": "honeycomb_search_columns",
        "expected_params": {},
        "assertion_checks": [
            "'query' in params",
            "any(term in params['query'].lower() for term in ['duration', 'latency', 'time', 'ms'])",
        ],
    },
    {
        "id": "search_columns_service",
        "description": "Search for service-related columns",
        "prompt": "What columns are available for service identification in Honeycomb?",
        "expected_tool": "honeycomb_search_columns",
        "expected_params": {},
        "assertion_checks": [
            "'query' in params",
            "any(term in params['query'].lower() for term in ['service', 'name'])",
        ],
    },
    # ==============================================================================
    # honeycomb_get_environment_summary test cases
    # ==============================================================================
    {
        "id": "environment_summary_basic",
        "description": "Get basic environment summary",
        "prompt": "Give me an overview of all datasets in my Honeycomb environment",
        "expected_tool": "honeycomb_get_environment_summary",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "environment_summary_with_columns",
        "description": "Get environment summary including sample columns",
        "prompt": "Show me a summary of my Honeycomb environment with sample column names for each dataset",
        "expected_tool": "honeycomb_get_environment_summary",
        "expected_params": {"include_sample_columns": True},
        "assertion_checks": [
            "params.get('include_sample_columns', True) == True",
        ],
    },
    {
        "id": "environment_summary_compact",
        "description": "Get compact environment summary without columns",
        "prompt": "List all Honeycomb datasets with just their column counts, no need to show sample columns",
        "expected_tool": "honeycomb_get_environment_summary",
        "expected_params": {"include_sample_columns": False},
        "assertion_checks": [
            "params.get('include_sample_columns') == False",
        ],
    },
    {
        "id": "environment_summary_discovery",
        "description": "Discover environment structure for migration",
        "prompt": "I'm migrating dashboards from Datadog. What datasets and data do I have available in Honeycomb?",
        "expected_tool": "honeycomb_get_environment_summary",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "environment_summary_data_inventory",
        "description": "Get data inventory for audit",
        "prompt": "I need an inventory of what telemetry data we're collecting in Honeycomb",
        "expected_tool": "honeycomb_get_environment_summary",
        "expected_params": {},
        "assertion_checks": [],
    },
    {
        "id": "environment_summary_understand_schema",
        "description": "Understand the overall schema",
        "prompt": "Help me understand what kind of data is in each Honeycomb dataset",
        "expected_tool": "honeycomb_get_environment_summary",
        "expected_params": {},
        "assertion_checks": [],
    },
]
