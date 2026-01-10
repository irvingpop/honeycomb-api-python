"""Shared validation logic for SLO constraints.

These functions are used by both SLOToolInput and SLOBuilder
to ensure consistent validation across SDK and Claude tool usage.
"""


def validate_slo_time_period(time_period_days: int) -> None:
    """Validate SLO time period is within Honeycomb limits.

    SLOs can have time periods from 1 to 90 days.

    Args:
        time_period_days: Time period in days

    Raises:
        ValueError: If time_period_days is outside 1-90 range
    """
    if not 1 <= time_period_days <= 90:
        raise ValueError(
            f"SLO time period must be 1-90 days, got {time_period_days} days. "
            "Common values: 7 (1 week), 14 (2 weeks), 30 (1 month), 90 (1 quarter)."
        )


def validate_slo_target_percentage(target_percentage: float) -> None:
    """Validate SLO target percentage is within reasonable bounds.

    Target percentages should be between 0 and 100.

    Args:
        target_percentage: Target as percentage (e.g., 99.9)

    Raises:
        ValueError: If target_percentage is outside 0-100 range
    """
    if not 0 <= target_percentage <= 100:
        raise ValueError(
            f"SLO target percentage must be 0-100, got {target_percentage}. "
            "Common values: 95.0, 99.0, 99.9, 99.95, 99.99."
        )
