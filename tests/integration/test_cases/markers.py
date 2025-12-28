"""Test cases for Markers resource.

Coverage:
- 9 tools (markers: list, create, update, delete + settings: list, get, create, update, delete)
- 1 test case (skeleton - expand to 12)
"""

TEST_CASES = [
    {
        "id": "marker_create_deployment",
        "description": "Create deployment marker",
        "prompt": (
            "Create a deployment marker in dataset 'api-logs' for version v1.2.3 deployed now"
        ),
        "expected_tool": "honeycomb_create_marker",
        "expected_params": {
            "dataset": "api-logs",
        },
        "assertion_checks": [],
    },
]
