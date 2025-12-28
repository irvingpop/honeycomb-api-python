"""Builder conversion helpers for Claude tool input.

This module converts tool input dictionaries (from Claude) to Builder instances,
enabling single-call resource creation with nested structures.
"""

from typing import Any

from honeycomb.models import (
    BurnAlertBuilder,
    BurnAlertType,
    SLOBuilder,
    TriggerBuilder,
)


def _build_trigger(data: dict[str, Any]) -> TriggerBuilder:
    """Convert tool input to TriggerBuilder.

    Args:
        data: Tool input dict from Claude (includes dataset, name, query, threshold, etc.)

    Returns:
        Configured TriggerBuilder instance ready to build()

    Example:
        >>> data = {
        ...     "dataset": "api-logs",
        ...     "name": "High Error Rate",
        ...     "query": {
        ...         "time_range": 900,
        ...         "calculations": [{"op": "COUNT"}],
        ...         "filters": [{"column": "status", "op": ">=", "value": 500}]
        ...     },
        ...     "threshold": {"op": ">", "value": 100},
        ...     "frequency": 900
        ... }
        >>> builder = _build_trigger(data)
        >>> trigger = builder.build()
    """
    builder = TriggerBuilder(data["name"])

    # Set description if provided
    if "description" in data:
        builder.description(data["description"])

    # Set dataset if provided
    if "dataset" in data:
        builder.dataset(data["dataset"])

    # Parse query
    query = data.get("query", {})

    # Time range
    if "time_range" in query:
        time_range = query["time_range"]
        # Use preset if matches common values
        if time_range == 600:
            builder.last_10_minutes()
        elif time_range == 1800:
            builder.last_30_minutes()
        elif time_range == 3600:
            builder.last_1_hour()
        else:
            # Use generic time_range for non-standard values (including 900)
            builder.time_range(time_range)

    # Calculations (trigger supports only ONE)
    calculations = query.get("calculations", [])
    if calculations:
        calc = calculations[0]  # Only use first calculation
        op = calc.get("op", "COUNT").upper()
        column = calc.get("column")

        if op == "COUNT":
            builder.count()
        elif op == "AVG" and column:
            builder.avg(column)
        elif op == "SUM" and column:
            builder.sum(column)
        elif op == "MAX" and column:
            builder.max(column)
        elif op == "MIN" and column:
            builder.min(column)
        elif op == "COUNT_DISTINCT" and column:
            builder.count_distinct(column)
        elif op == "HEATMAP" and column:
            builder.heatmap(column)
        elif op == "CONCURRENCY":
            builder.concurrency()
        elif op.startswith("P") and column:
            # Percentile (e.g., P99, P95, P90, P50)
            # Only P50, P90, P95, P99 are supported via direct methods
            percentile = int(op[1:])
            if percentile == 50:
                builder.p50(column)
            elif percentile == 90:
                builder.p90(column)
            elif percentile == 95:
                builder.p95(column)
            elif percentile == 99:
                builder.p99(column)
            # For other percentiles, would need to use generic calculation
            # but trigger builder doesn't support that, so skip

    # Filters
    filters = query.get("filters", [])
    for filt in filters:
        column = filt["column"]
        op_str = filt["op"]
        value = filt.get("value")

        # Use shorthand methods when possible for all filter types
        if op_str == "=":
            builder.eq(column, value)
        elif op_str == "!=":
            builder.ne(column, value)
        elif op_str == ">":
            builder.gt(column, value)
        elif op_str == ">=":
            builder.gte(column, value)
        elif op_str == "<":
            builder.lt(column, value)
        elif op_str == "<=":
            builder.lte(column, value)
        elif op_str == "starts-with":
            builder.starts_with(column, value)
        elif op_str == "does-not-start-with":
            # Use generic where() - no direct method for does-not-start-with
            builder.where(column, op_str, value)
        elif op_str == "contains":
            builder.contains(column, value)
        elif op_str == "does-not-contain":
            # Use generic where() - no direct method for does-not-contain
            builder.where(column, op_str, value)
        elif op_str == "exists":
            builder.exists(column)
        elif op_str == "does-not-exist":
            builder.does_not_exist(column)
        elif op_str == "in":
            builder.is_in(column, value)
        elif op_str == "not-in":
            # Use generic where() - no direct method for not-in
            builder.where(column, op_str, value)
        else:
            # Use generic filter method for any other operators
            builder.where(column, op_str, value)

    # Filter combination
    if "filter_combination" in query:
        builder.filter_with(query["filter_combination"])

    # Breakdowns (grouping)
    if "breakdowns" in query:
        for breakdown in query["breakdowns"]:
            builder.breakdown(breakdown)

    # Threshold
    threshold = data["threshold"]
    op = threshold["op"]
    value = threshold["value"]

    if op == ">":
        builder.threshold_gt(value)
    elif op == ">=":
        builder.threshold_gte(value)
    elif op == "<":
        builder.threshold_lt(value)
    elif op == "<=":
        builder.threshold_lte(value)

    # Exceeded limit
    if "exceeded_limit" in threshold:
        builder.exceeded_limit(threshold["exceeded_limit"])

    # Frequency
    if "frequency" in data:
        freq = data["frequency"]
        # Use presets when possible
        if freq == 60:
            builder.every_minute()
        elif freq == 300:
            builder.every_5_minutes()
        elif freq == 900:
            builder.every_15_minutes()
        elif freq == 1800:
            builder.every_30_minutes()
        elif freq == 3600:
            builder.every_hour()
        else:
            builder.frequency(freq)

    # Alert type
    if "alert_type" in data:
        if data["alert_type"] == "on_change":
            builder.alert_on_change()
        elif data["alert_type"] == "on_true":
            builder.alert_on_true()

    # Recipients
    recipients = data.get("recipients", [])
    for recip in recipients:
        if "id" in recip:
            # ID-based recipient (recommended)
            builder.recipient_id(recip["id"])
        elif recip.get("type") == "email":
            builder.email(recip["target"])
        elif recip.get("type") == "slack":
            builder.slack(recip["target"])
        elif recip.get("type") == "pagerduty":
            severity = recip.get("details", {}).get("severity", "critical")
            builder.pagerduty(recip["target"], severity=severity)

    # Tags
    tags = data.get("tags", [])
    for tag in tags:
        builder.tag(tag["key"], tag["value"])

    # Disabled flag
    if data.get("disabled", False):
        builder.disabled()

    return builder


def _build_slo(data: dict[str, Any]) -> SLOBuilder:
    """Convert tool input to SLOBuilder.

    Args:
        data: Tool input dict from Claude (includes dataset, name, sli, target, etc.)

    Returns:
        Configured SLOBuilder instance ready to build()

    Example:
        >>> data = {
        ...     "dataset": "api-logs",
        ...     "name": "API Availability",
        ...     "sli": {"alias": "success_rate"},
        ...     "target_per_million": 999000,
        ...     "time_period_days": 30
        ... }
        >>> builder = _build_slo(data)
        >>> bundle = builder.build()
    """
    builder = SLOBuilder(data["name"])

    # Description
    if "description" in data:
        builder.description(data["description"])

    # Dataset(s)
    if "dataset" in data:
        builder.dataset(data["dataset"])
    elif "datasets" in data:
        builder.datasets(data["datasets"])

    # SLI
    sli = data["sli"]
    alias = sli["alias"]

    if "expression" in sli:
        # New derived column
        expression = sli["expression"]
        description = sli.get("description")
        builder.sli(alias, expression, description)
    else:
        # Existing derived column
        builder.sli(alias)

    # Target
    if "target_per_million" in data:
        builder.target_per_million(data["target_per_million"])
    elif "target_percentage" in data:
        builder.target_percentage(data["target_percentage"])
    elif "target_nines" in data:
        builder.target_nines(data["target_nines"])

    # Time period
    if "time_period_days" in data:
        builder.time_period_days(data["time_period_days"])
    elif "time_period_weeks" in data:
        builder.time_period_weeks(data["time_period_weeks"])

    # Burn alerts
    burn_alerts = data.get("burn_alerts", [])
    for alert_data in burn_alerts:
        alert_type_str = alert_data["alert_type"]
        alert_type = BurnAlertType(alert_type_str)

        burn_builder = BurnAlertBuilder(alert_type)

        if "description" in alert_data:
            burn_builder.description(alert_data["description"])

        if alert_type == BurnAlertType.EXHAUSTION_TIME:
            burn_builder.exhaustion_minutes(alert_data["exhaustion_minutes"])
        elif alert_type == BurnAlertType.BUDGET_RATE:
            burn_builder.window_minutes(alert_data["budget_rate_window_minutes"])
            # Convert from per_million to percent
            threshold_per_million = alert_data["budget_rate_decrease_threshold_per_million"]
            threshold_percent = threshold_per_million / 10000  # e.g., 10000 → 1%
            burn_builder.threshold_percent(threshold_percent)

        # Recipients for burn alert
        recipients = alert_data.get("recipients", [])
        for recip in recipients:
            if "id" in recip:
                burn_builder.recipient_id(recip["id"])
            elif recip.get("type") == "email":
                burn_builder.email(recip["target"])
            elif recip.get("type") == "slack":
                burn_builder.slack(recip["target"])
            elif recip.get("type") == "pagerduty":
                severity = recip.get("details", {}).get("severity", "critical")
                burn_builder.pagerduty(recip["target"], severity=severity)

        # Add burn alert using the appropriate method based on type
        if alert_type == BurnAlertType.EXHAUSTION_TIME:
            builder.exhaustion_alert(burn_builder)
        elif alert_type == BurnAlertType.BUDGET_RATE:
            builder.budget_rate_alert(burn_builder)

    return builder


__all__ = [
    "_build_trigger",
    "_build_slo",
]
