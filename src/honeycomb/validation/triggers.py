"""Shared validation logic for trigger constraints.

These functions are used by both TriggerBuilder and TriggerToolInput
to ensure consistent validation across SDK and Claude tool usage.
"""


def validate_trigger_time_range(time_range: int) -> None:
    """Validate trigger time range is within Honeycomb API limits.

    Triggers have a maximum time range of 3600 seconds (1 hour).

    Args:
        time_range: Time range in seconds

    Raises:
        ValueError: If time_range exceeds 3600 seconds
    """
    if time_range > 3600:
        raise ValueError(
            f"Trigger time range must be ≤ 3600 seconds (1 hour), got {time_range}s. "
            "Use a shorter time range like 600s (10 min), 1800s (30 min), or 3600s (1 hour)."
        )


def validate_trigger_frequency(frequency: int) -> None:
    """Validate trigger evaluation frequency is within bounds.

    Triggers can run every 60 seconds (1 minute) to 86400 seconds (1 day).

    Args:
        frequency: Evaluation frequency in seconds

    Raises:
        ValueError: If frequency is outside 60-86400 second range
    """
    if not 60 <= frequency <= 86400:
        raise ValueError(
            f"Trigger frequency must be 60-86400 seconds (1 min to 1 day), got {frequency}s. "
            "Common values: 60s (1 min), 300s (5 min), 900s (15 min), 3600s (1 hour)."
        )


def validate_time_range_frequency_ratio(time_range: int, frequency: int) -> None:
    """Validate time range vs frequency constraint.

    Honeycomb API rule: time_range must be ≤ frequency * 4
    This ensures the query window doesn't extend too far beyond the evaluation period.

    Args:
        time_range: Query time range in seconds
        frequency: Evaluation frequency in seconds

    Raises:
        ValueError: If time_range > frequency * 4

    Examples:
        - frequency=60s → max time_range=240s ✓
        - frequency=300s → max time_range=1200s ✓
        - frequency=900s → max time_range=3600s ✓
    """
    max_time_range = frequency * 4
    if time_range > max_time_range:
        raise ValueError(
            f"Time range ({time_range}s) cannot be more than 4x frequency ({frequency}s). "
            f"Maximum time range for this frequency: {max_time_range}s. "
            f"Either increase frequency or decrease time range."
        )


def validate_exceeded_limit(exceeded_limit: int) -> None:
    """Validate exceeded_limit is within bounds.

    The exceeded_limit controls how many consecutive evaluations must
    exceed the threshold before the trigger fires.

    Args:
        exceeded_limit: Number of consecutive violations (1-5)

    Raises:
        ValueError: If exceeded_limit is not 1-5
    """
    if not 1 <= exceeded_limit <= 5:
        raise ValueError(
            f"exceeded_limit must be 1-5, got {exceeded_limit}. "
            "This controls how many consecutive evaluations must exceed the threshold."
        )


def validate_trigger_calculation_not_heatmap(calculation_op: str) -> None:
    """Validate that trigger calculation is not HEATMAP.

    Triggers do not support HEATMAP calculations per Honeycomb API constraints.

    Args:
        calculation_op: Calculation operator (e.g., "COUNT", "AVG", "HEATMAP")

    Raises:
        ValueError: If calculation is HEATMAP
    """
    if calculation_op.upper() == "HEATMAP":
        raise ValueError(
            "Trigger queries may not use HEATMAP calculation. "
            "Use COUNT, AVG, SUM, MIN, MAX, P50, P90, P95, P99, or COUNT_DISTINCT instead."
        )


def validate_trigger_no_orders() -> None:
    """Validate that trigger query does not have orders field set.

    Trigger queries do not support the orders field per Honeycomb API constraints.

    Raises:
        ValueError: Always (should only be called if orders are present)
    """
    raise ValueError(
        "Trigger queries do not support 'orders'. "
        "Remove the orders field from your trigger query. "
        "Triggers evaluate against a single calculated value, not ordered results."
    )


def validate_trigger_no_limit() -> None:
    """Validate that trigger query does not have limit field set.

    Trigger queries do not support the limit field per Honeycomb API constraints.

    Raises:
        ValueError: Always (should only be called if limit is present)
    """
    raise ValueError(
        "Trigger queries do not support 'limit'. "
        "Remove the limit field from your trigger query. "
        "Triggers evaluate against a single calculated value, not limited result sets."
    )
