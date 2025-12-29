"""Test case registry for DeepEval Claude tool validation.

This package contains test case definitions organized by resource.
Each resource module exports a TEST_CASES list.

To add test cases for a resource:
1. Edit the corresponding file in this directory (e.g., triggers.py)
2. Append to TEST_CASES array
3. Tests automatically pick up the new cases
"""

from typing import Any

from . import (
    boards,
    burn_alerts,
    columns,
    datasets,
    derived_columns,
    events,
    markers,
    queries,
    recipients,
    service_map,
    slos,
    triggers,
)

# ==============================================================================
# Master Registry
# ==============================================================================

ALL_TEST_CASES_BY_RESOURCE = {
    # Priority 1 (Implemented - comprehensive coverage)
    "triggers": triggers.TEST_CASES,
    "slos": slos.TEST_CASES,
    "burn_alerts": burn_alerts.TEST_CASES,
    # Priority 2 & 3 (All implemented)
    "datasets": datasets.TEST_CASES,
    "columns": columns.TEST_CASES,
    "derived_columns": derived_columns.TEST_CASES,
    "recipients": recipients.TEST_CASES,
    "queries": queries.TEST_CASES,
    "boards": boards.TEST_CASES,
    "markers": markers.TEST_CASES,
    "events": events.TEST_CASES,
    "service_map": service_map.TEST_CASES,
}


def get_all_test_cases() -> list[dict[str, Any]]:
    """Get all test cases across all resources.

    Returns:
        List of test case dicts with resource metadata added
    """
    all_cases = []
    for resource, cases in ALL_TEST_CASES_BY_RESOURCE.items():
        for case in cases:
            case_with_resource = {**case, "resource": resource}
            all_cases.append(case_with_resource)
    return all_cases


def get_test_cases_for_resource(resource: str) -> list[dict[str, Any]]:
    """Get test cases for a specific resource.

    Args:
        resource: Resource name (e.g., "triggers", "slos")

    Returns:
        List of test case dicts
    """
    return ALL_TEST_CASES_BY_RESOURCE.get(resource, [])
