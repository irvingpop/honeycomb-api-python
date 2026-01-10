"""Builder conversion helpers for Claude tool input.

This module converts tool input dictionaries (from Claude) to Builder instances,
enabling single-call resource creation with nested structures.
"""

from typing import Any

from honeycomb.models import (
    BoardBuilder,
    BurnAlertBuilder,
    BurnAlertType,
    SLOBuilder,
    TriggerBuilder,
)
from honeycomb.models.tool_inputs import (
    BoardToolInput,
    PositionInput,
    SLOToolInput,
    TriggerToolInput,
    VisualizationSettingsInput,
)


def _build_visualization_dict(
    visualization: VisualizationSettingsInput | None,
    chart_type: str | None,
) -> dict[str, Any] | None:
    """Build visualization settings dict from typed model and/or chart_type shorthand.

    Args:
        visualization: Typed VisualizationSettingsInput model or None
        chart_type: Shorthand chart_type (e.g., "line", "stacked") or None

    Returns:
        Dict for API or None if no settings provided

    Priority:
        - If visualization is set, use it (converted to dict)
        - If chart_type is set but visualization is None, create minimal dict
        - If both are set, chart_type is ignored (visualization takes precedence)
    """
    if visualization is not None:
        # Convert typed model to dict, excluding None values
        result: dict[str, Any] = {}
        if visualization.hide_compare:
            result["hide_compare"] = True
        if visualization.hide_hovers:
            result["hide_hovers"] = True
        if visualization.hide_markers:
            result["hide_markers"] = True
        if visualization.utc_xaxis:
            result["utc_xaxis"] = True
        if visualization.overlaid_charts:
            result["overlaid_charts"] = True
        if visualization.charts:
            result["charts"] = [
                {
                    k: v
                    for k, v in {
                        "chart_index": chart.chart_index,
                        "chart_type": chart.chart_type,
                        "log_scale": chart.log_scale if chart.log_scale else None,
                        "omit_missing_values": (
                            chart.omit_missing_values if chart.omit_missing_values else None
                        ),
                    }.items()
                    if v is not None
                }
                for chart in visualization.charts
            ]
        return result if result else None

    if chart_type is not None:
        # Shorthand: create minimal visualization with just chart_type
        return {"charts": [{"chart_type": chart_type}]}

    return None


def _to_position_input(position: dict[str, Any] | list | tuple | None) -> PositionInput | None:
    """Convert position dict/tuple/list to PositionInput.

    Args:
        position: Position as dict (x_coordinate, y_coordinate, width, height),
                  tuple/list (x, y, w, h), or None

    Returns:
        PositionInput or None
    """
    if position is None:
        return None
    if isinstance(position, dict):
        return PositionInput(
            x_coordinate=position["x_coordinate"],
            y_coordinate=position["y_coordinate"],
            width=position["width"],
            height=position["height"],
        )
    # tuple or list (x, y, w, h)
    return PositionInput(
        x_coordinate=position[0],
        y_coordinate=position[1],
        width=position[2],
        height=position[3],
    )


def _build_trigger(data: dict[str, Any]) -> TriggerBuilder:
    """Convert tool input to TriggerBuilder with validation.

    Validates input using TriggerToolInput before building, ensuring fail-fast
    validation with clear error messages for Claude.

    Args:
        data: Tool input dict from Claude (includes dataset, name, query, threshold, etc.)

    Returns:
        Configured TriggerBuilder instance ready to build()

    Raises:
        ValidationError: If input validation fails (duplicate queries, invalid tags, etc.)

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
    # Validate input using TriggerToolInput (fail-fast with shared validators)
    validated = TriggerToolInput.model_validate(data)

    # Build from validated input
    builder = TriggerBuilder(validated.name)

    # Set description if provided
    if validated.description:
        builder.description(validated.description)

    # Set dataset
    builder.dataset(validated.dataset)

    # Parse query from validated model
    query = validated.query

    # Time range - use preset if matches common values
    time_range = query.time_range
    if time_range == 600:
        builder.last_10_minutes()
    elif time_range == 1800:
        builder.last_30_minutes()
    elif time_range == 3600:
        builder.last_1_hour()
    else:
        # Use generic time_range for non-standard values (including 900)
        builder.time_range(time_range)

    # Calculations (trigger supports only ONE - already validated)
    if query.calculations:
        calc = query.calculations[0]  # Only one allowed
        op = calc.op
        column = calc.column

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

    # Filters from validated model
    if query.filters:
        for filt in query.filters:
            # Use shorthand methods when possible for all filter types
            if filt.op == "=":
                builder.eq(filt.column, filt.value)
            elif filt.op == "!=":
                builder.ne(filt.column, filt.value)
            elif filt.op == ">":
                builder.gt(filt.column, filt.value)
            elif filt.op == ">=":
                builder.gte(filt.column, filt.value)
            elif filt.op == "<":
                builder.lt(filt.column, filt.value)
            elif filt.op == "<=":
                builder.lte(filt.column, filt.value)
            elif filt.op == "starts-with":
                builder.starts_with(filt.column, filt.value)
            elif filt.op == "does-not-start-with":
                builder.where(filt.column, filt.op, filt.value)
            elif filt.op == "contains":
                builder.contains(filt.column, filt.value)
            elif filt.op == "does-not-contain":
                builder.where(filt.column, filt.op, filt.value)
            elif filt.op == "exists":
                builder.exists(filt.column)
            elif filt.op == "does-not-exist":
                builder.does_not_exist(filt.column)
            elif filt.op == "in":
                builder.is_in(filt.column, filt.value)
            elif filt.op == "not-in":
                builder.where(filt.column, filt.op, filt.value)
            else:
                builder.where(filt.column, filt.op, filt.value)

    # Filter combination
    if query.filter_combination:
        builder.filter_with(query.filter_combination)

    # Breakdowns (grouping)
    if query.breakdowns:
        for breakdown in query.breakdowns:
            builder.breakdown(breakdown)

    # Threshold from validated model
    threshold = validated.threshold
    if threshold.op == ">":
        builder.threshold_gt(threshold.value)
    elif threshold.op == ">=":
        builder.threshold_gte(threshold.value)
    elif threshold.op == "<":
        builder.threshold_lt(threshold.value)
    elif threshold.op == "<=":
        builder.threshold_lte(threshold.value)

    # Exceeded limit
    if threshold.exceeded_limit:
        builder.exceeded_limit(threshold.exceeded_limit)

    # Frequency from validated model - use presets when possible
    freq = validated.frequency
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
    if validated.alert_type == "on_change":
        builder.alert_on_change()
    elif validated.alert_type == "on_true":
        builder.alert_on_true()

    # Recipients from validated model
    if validated.recipients:
        for recip in validated.recipients:
            if recip.id:
                # ID-based recipient (recommended)
                builder.recipient_id(recip.id)
            elif recip.type == "email" and recip.target:
                builder.email(recip.target)
            elif recip.type == "slack" and recip.target:
                builder.slack(recip.target)
            elif recip.type == "pagerduty" and recip.target:
                builder.pagerduty(recip.target, severity="critical")
            elif recip.type == "webhook" and recip.target:
                builder.webhook(recip.target, name="Webhook", secret=None)
            elif recip.type in ("msteams", "msteams_workflow") and recip.target:
                builder.msteams(recip.target)

    # Tags from validated model
    if validated.tags:
        for tag in validated.tags:
            builder.tag(tag.key, tag.value)

    # Disabled flag
    if validated.disabled:
        builder.disabled()

    return builder


def _build_slo(data: dict[str, Any]) -> SLOBuilder:
    """Convert tool input to SLOBuilder with Pydantic validation.

    Args:
        data: Tool input dict from Claude (includes dataset, name, sli, target, etc.)

    Returns:
        Configured SLOBuilder instance ready to build()

    Raises:
        ValidationError: If input data doesn't match SLOToolInput schema

    Example:
        >>> data = {
        ...     "datasets": ["api-logs"],
        ...     "name": "API Availability",
        ...     "sli": {"alias": "success_rate"},
        ...     "target_percentage": 99.9,
        ...     "time_period_days": 30
        ... }
        >>> builder = _build_slo(data)
        >>> bundle = builder.build()
    """
    # Validate input with Pydantic (raises ValidationError on invalid input)
    validated = SLOToolInput.model_validate(data)

    builder = SLOBuilder(validated.name)

    # Description
    if validated.description:
        builder.description(validated.description)

    # Dataset(s) - always a list, use single element for one dataset
    if len(validated.datasets) == 1:
        builder.dataset(validated.datasets[0])
    else:
        builder.datasets(validated.datasets)

    # SLI
    alias = validated.sli.alias

    if validated.sli.expression:
        # New derived column
        builder.sli(alias, validated.sli.expression, validated.sli.description)
    else:
        # Existing derived column
        builder.sli(alias)

    # Target (target_percentage is required in SLOToolInput)
    builder.target_percentage(validated.target_percentage)

    # Time period
    builder.time_period_days(validated.time_period_days)

    # Burn alerts (validated as BurnAlertInput models)
    burn_alerts = validated.burn_alerts or []
    for alert_data in burn_alerts:
        alert_type = BurnAlertType(alert_data.alert_type)

        burn_builder = BurnAlertBuilder(alert_type)

        if alert_data.description:
            burn_builder.description(alert_data.description)

        if alert_type == BurnAlertType.EXHAUSTION_TIME:
            if alert_data.exhaustion_minutes:
                burn_builder.exhaustion_minutes(alert_data.exhaustion_minutes)
        elif alert_type == BurnAlertType.BUDGET_RATE:
            if alert_data.budget_rate_window_minutes:
                burn_builder.window_minutes(alert_data.budget_rate_window_minutes)
            if alert_data.budget_rate_decrease_threshold_per_million:
                # Convert from per_million to percent
                threshold_per_million = alert_data.budget_rate_decrease_threshold_per_million
                threshold_percent = threshold_per_million / 10000  # e.g., 10000 → 1%
                burn_builder.threshold_percent(threshold_percent)

        # Recipients for burn alert (validated as RecipientInput models)
        recipients = alert_data.recipients or []
        for recip in recipients:
            if recip.id:
                burn_builder.recipient_id(recip.id)
            elif recip.type == "email" and recip.target:
                burn_builder.email(recip.target)
            elif recip.type == "slack" and recip.target:
                burn_builder.slack(recip.target)
            elif recip.type == "pagerduty" and recip.target:
                # Note: RecipientInput doesn't have details field, default to critical
                burn_builder.pagerduty(recip.target, severity="critical")
            elif recip.type == "webhook" and recip.target:
                burn_builder.webhook(recip.target, name="Webhook", secret=None)
            elif recip.type in ("msteams", "msteams_workflow") and recip.target:
                burn_builder.msteams(recip.target)

        # Add burn alert using the appropriate method based on type
        if alert_type == BurnAlertType.EXHAUSTION_TIME:
            builder.exhaustion_alert(burn_builder)
        elif alert_type == BurnAlertType.BUDGET_RATE:
            builder.budget_rate_alert(burn_builder)

    return builder


def _build_board(data: dict[str, Any]) -> BoardBuilder:
    """Convert tool input to BoardBuilder with Pydantic validation and inline panel creation.

    Args:
        data: Tool input dict from Claude (includes name, inline_query_panels, etc.)

    Returns:
        Configured BoardBuilder instance ready to build()

    Raises:
        ValidationError: If input data doesn't match BoardToolInput schema

    Example:
        >>> data = {
        ...     "name": "API Dashboard",
        ...     "layout_generation": "auto",
        ...     "inline_query_panels": [
        ...         {
        ...             "name": "Error Count",
        ...             "dataset": "api-logs",
        ...             "time_range": 3600,
        ...             "calculations": [{"op": "COUNT"}]
        ...         }
        ...     ],
        ...     "text_panels": [{"content": "## Notes"}]
        ... }
        >>> builder = _build_board(data)
        >>> bundle = builder.build()
    """
    from honeycomb.models.query_builder import QueryBuilder

    # Validate input with Pydantic (raises ValidationError on invalid input)
    validated = BoardToolInput.model_validate(data)

    builder = BoardBuilder(validated.name)

    # Description
    if validated.description:
        builder.description(validated.description)

    # Layout generation
    if validated.layout_generation == "auto":
        builder.auto_layout()
    else:
        builder.manual_layout()

    # Inline query panels (create QueryBuilder instances from validated models)
    for query_panel in validated.inline_query_panels or []:
        # Build QueryBuilder from validated QueryPanelInput model
        qb = QueryBuilder(query_panel.name)

        if query_panel.description:
            qb.description(query_panel.description)

        # Dataset - optional for environment-wide queries
        if query_panel.dataset:
            qb.dataset(query_panel.dataset)
        else:
            qb.environment_wide()  # Default to environment-wide

        # Time range
        if query_panel.time_range:
            qb.time_range(query_panel.time_range)

        # Calculations - these are already validated Calculation models
        for calc in query_panel.calculations or []:
            qb._calculations.append(calc)

        # Filters - these are already validated Filter models
        for filt in query_panel.filters or []:
            qb.filter(filt.column, filt.op, filt.value)

        # Breakdowns
        for breakdown in query_panel.breakdowns or []:
            qb.group_by(breakdown)

        # Orders - these are already validated Order models
        for order in query_panel.orders or []:
            # Order model has 'op' (CalcOp) and 'order' (OrderDirection) fields
            qb.order_by(order.column or order.op, order.order)

        # Limit
        if query_panel.limit:
            qb.limit(query_panel.limit)

        # Calculated fields (inline derived columns)
        for calc_field in query_panel.calculated_fields or []:
            qb.calculated_field(calc_field.name, calc_field.expression)

        # Compare time offset for historical comparison
        if query_panel.compare_time_offset_seconds:
            qb.compare_time_offset(query_panel.compare_time_offset_seconds)

        # Build visualization dict from typed model or chart_type shorthand
        viz_dict = _build_visualization_dict(query_panel.visualization, query_panel.chart_type)

        # Add to board with position and style
        builder.query(
            qb,
            position=query_panel.position,  # Already a PositionInput or None
            style=query_panel.style,
            visualization=viz_dict,
        )

    # Text panels (validated TextPanelInput models)
    for text_panel in validated.text_panels or []:
        builder.text(text_panel.content, position=text_panel.position)

    # Inline SLO panels (create SLOBuilder instances from validated SLOPanelInput models)
    for slo_panel in validated.inline_slo_panels or []:
        # Build SLOBuilder from validated SLOPanelInput model
        from honeycomb.models import SLOBuilder

        slo_builder = SLOBuilder(slo_panel.name)

        if slo_panel.description:
            slo_builder.description(slo_panel.description)

        # Dataset (required in SLOPanelInput)
        slo_builder.dataset(slo_panel.dataset)

        # SLI (validated SLIInput model)
        alias = slo_panel.sli.alias
        if slo_panel.sli.expression:
            # Inline derived column
            slo_builder.sli(alias, slo_panel.sli.expression, slo_panel.sli.description)
        else:
            # Existing derived column
            slo_builder.sli(alias)

        # Target (target_percentage is required in SLOPanelInput)
        slo_builder.target_percentage(slo_panel.target_percentage)

        # Time period
        slo_builder.time_period_days(slo_panel.time_period_days)

        # Add to board
        builder.slo(slo_builder, position=slo_panel.position)

    # Existing SLO panels (by ID - list of strings)
    for slo_id in validated.slo_panels or []:
        builder.slo(slo_id)

    # Tags (validated TagInput models)
    for tag in validated.tags or []:
        builder.tag(tag.key, tag.value)

    # Preset filters (validated PresetFilterInput models)
    for preset in validated.preset_filters or []:
        builder.preset_filter(preset.column, preset.alias)

    # Board views (validated BoardViewInput models)
    for view in validated.views or []:
        # Convert BoardViewFilter models to dicts for builder compatibility
        filters: list[dict[str, Any]] = []
        for board_view_filter in view.filters or []:
            filters.append(
                {
                    "column": board_view_filter.column,
                    "operation": board_view_filter.operation,
                    "value": board_view_filter.value,
                }
            )
        builder.add_view(view.name, filters)

    return builder


__all__ = [
    "_build_trigger",
    "_build_slo",
    "_build_board",
]
