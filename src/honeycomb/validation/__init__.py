"""Shared validation logic for Honeycomb resources.

This module provides validation functions that are used by both:
1. Tool input models (fail-fast validation for Claude tools)
2. Builder classes (validation during SDK usage)

By sharing validation logic, we ensure consistent error messages
and behavior across all usage patterns.
"""

from honeycomb.validation.boards import (
    format_query_spec,
    generate_query_signature,
    validate_no_duplicate_query_panels,
)
from honeycomb.validation.slos import (
    validate_slo_target_percentage,
    validate_slo_time_period,
)
from honeycomb.validation.triggers import (
    validate_exceeded_limit,
    validate_time_range_frequency_ratio,
    validate_trigger_frequency,
    validate_trigger_time_range,
)

__all__ = [
    # Trigger validation
    "validate_trigger_time_range",
    "validate_trigger_frequency",
    "validate_time_range_frequency_ratio",
    "validate_exceeded_limit",
    # SLO validation
    "validate_slo_time_period",
    "validate_slo_target_percentage",
    # Board validation
    "generate_query_signature",
    "format_query_spec",
    "validate_no_duplicate_query_panels",
]
