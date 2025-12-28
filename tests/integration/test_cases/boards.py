"""Test cases for Boards resource.

Coverage:
- 5 tools (list, get, create, update, delete)
- 1 test case (skeleton - expand to 12)
"""

TEST_CASES = [
    {
        "id": "board_create_simple",
        "description": "Create board with existing query IDs",
        "prompt": (
            "Create a board named 'API Dashboard' with query panels for "
            "query IDs q-123 and q-456"
        ),
        "expected_tool": "honeycomb_create_board",
        "expected_params": {
            "name": "API Dashboard",
        },
        "assertion_checks": [
            "len(params['panels']) >= 2",
        ],
    },
]
