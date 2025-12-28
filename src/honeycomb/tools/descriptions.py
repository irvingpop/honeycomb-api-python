"""Hand-crafted tool descriptions for Claude tool definitions.

Each description follows the quality requirements:
1. What it does (1 sentence)
2. When to use it (1 sentence)
3. Key parameters explained (1-2 sentences)
4. Important caveats/limitations (if any)
"""

# ==============================================================================
# Triggers (Alerts)
# ==============================================================================

TRIGGER_DESCRIPTIONS = {
    "honeycomb_list_triggers": (
        "Lists all triggers (alerts) configured in a Honeycomb dataset. "
        "Use this to discover existing alerting rules before creating new ones or when migrating from another observability platform. "
        "Requires the dataset slug parameter to specify which dataset's triggers to retrieve. "
        "Returns a list of trigger objects with their IDs, names, thresholds, and recipient configurations."
    ),
    "honeycomb_get_trigger": (
        "Retrieves detailed configuration for a specific trigger by ID. "
        "Use this to inspect an existing trigger's query specification, threshold settings, frequency, and recipients before modifying or replicating it. "
        "Requires both the dataset slug and trigger ID parameters. "
        "Returns the complete trigger configuration including the query spec, threshold operator and value, evaluation frequency, and notification recipients."
    ),
    "honeycomb_create_trigger": (
        "Creates a new trigger (alert) that fires when query results cross a threshold. "
        "Use this when setting up alerting rules for service health monitoring, error rates, latency thresholds, or when migrating Datadog monitors to Honeycomb. "
        "Requires a dataset, query specification with calculations and filters, threshold operator and value, and evaluation frequency in seconds. "
        "The query can be provided inline with calculations, filters, and time range. "
        "Recipients must already exist in Honeycomb (create them first with honeycomb_create_recipient if needed). "
        "Note: Trigger queries have a maximum time_range of 3600 seconds (1 hour) and support only a single calculation."
    ),
    "honeycomb_update_trigger": (
        "Updates an existing trigger's configuration including its query, threshold, frequency, or recipients. "
        "Use this to adjust alerting thresholds, change notification targets, or update query filters as service behavior evolves. "
        "Requires the dataset slug, trigger ID, and the complete updated trigger configuration. "
        "Note: This replaces the entire trigger configuration, so include all fields you want to preserve."
    ),
    "honeycomb_delete_trigger": (
        "Permanently deletes a trigger from Honeycomb. "
        "Use this when decommissioning services, consolidating redundant alerts, or cleaning up test triggers. "
        "Requires both the dataset slug and trigger ID. "
        "Warning: This action cannot be undone. The trigger will stop firing immediately and historical alert data will be lost."
    ),
}

# ==============================================================================
# SLOs (Service Level Objectives)
# ==============================================================================

SLO_DESCRIPTIONS = {
    "honeycomb_list_slos": (
        "Lists all Service Level Objectives (SLOs) defined in a Honeycomb dataset. "
        "Use this to discover existing SLOs, review service reliability targets, or before creating related burn alerts. "
        "Requires the dataset slug parameter. "
        "Returns a list of SLO objects with their IDs, names, target percentages, time periods, and SLI (Service Level Indicator) definitions."
    ),
    "honeycomb_get_slo": (
        "Retrieves detailed configuration for a specific SLO by ID. "
        "Use this to inspect an SLO's target percentage, time period, SLI expression, and associated burn alerts. "
        "Requires both the dataset slug and SLO ID. "
        "Returns the complete SLO configuration including the derived column used for the SLI calculation."
    ),
    "honeycomb_create_slo": (
        "Creates a new Service Level Objective (SLO) with optional derived column and burn alerts. "
        "Use this when defining reliability targets for services, such as 99.9% availability or p99 latency under 200ms. "
        "Requires a dataset, SLO name, target percentage (or per-million), time period in days, and an SLI definition with an alias. "
        "If the SLI expression is provided, a new derived column will be created automatically. "
        "You can also configure burn alerts to notify when error budget is depleting too quickly. "
        "Supports both single-dataset and environment-wide SLOs (when multiple datasets are specified)."
    ),
    "honeycomb_update_slo": (
        "Updates an existing SLO's target percentage, time period, or SLI configuration. "
        "Use this to adjust reliability targets as service requirements change or to associate different derived columns. "
        "Requires the dataset slug, SLO ID, and the complete updated SLO configuration. "
        "Note: This replaces the entire SLO configuration. To update burn alerts separately, use burn alert tools instead."
    ),
    "honeycomb_delete_slo": (
        "Permanently deletes an SLO from Honeycomb. "
        "Use this when decommissioning services, consolidating reliability metrics, or removing test SLOs. "
        "Requires both the dataset slug and SLO ID. "
        "Warning: This action cannot be undone. Associated burn alerts will also be deleted."
    ),
}

# ==============================================================================
# Burn Alerts (SLO Budget Alerts)
# ==============================================================================

BURN_ALERT_DESCRIPTIONS = {
    "honeycomb_list_burn_alerts": (
        "Lists all burn alerts configured for a specific SLO. "
        "Use this to discover existing error budget alerts before creating new ones or when reviewing SLO alerting configuration. "
        "Requires both the dataset slug and SLO ID parameters. "
        "Returns a list of burn alert objects with their IDs, alert types (exhaustion_time or budget_rate), thresholds, and recipients."
    ),
    "honeycomb_get_burn_alert": (
        "Retrieves detailed configuration for a specific burn alert by ID. "
        "Use this to inspect an existing burn alert's threshold, alert type, and recipient configuration. "
        "Requires both the dataset slug and burn alert ID. "
        "Returns the complete burn alert configuration including the SLO it's attached to."
    ),
    "honeycomb_create_burn_alert": (
        "Creates a new burn alert that fires when an SLO's error budget is depleting too quickly. "
        "Use this to get early warning when service reliability is degrading, before completely exhausting your error budget. "
        "Requires a dataset, the SLO ID to attach to, alert type (exhaustion_time or budget_rate), and threshold value. "
        "For exhaustion_time alerts, specify the threshold in minutes (fires when budget will be exhausted in X minutes). "
        "For budget_rate alerts, specify threshold as percentage drop within a time window. "
        "Recipients must already exist in Honeycomb (create them first with honeycomb_create_recipient if needed)."
    ),
    "honeycomb_update_burn_alert": (
        "Updates an existing burn alert's threshold, recipients, or alert type. "
        "Use this to adjust alerting sensitivity as you learn about your service's error budget consumption patterns. "
        "Requires the dataset slug, burn alert ID, and the complete updated burn alert configuration. "
        "Note: This replaces the entire burn alert configuration, so include all fields you want to preserve."
    ),
    "honeycomb_delete_burn_alert": (
        "Permanently deletes a burn alert from an SLO. "
        "Use this when adjusting SLO alerting strategy or removing redundant burn alerts. "
        "Requires both the dataset slug and burn alert ID. "
        "Warning: This action cannot be undone. The alert will stop firing immediately."
    ),
}

# Combined mapping of all descriptions
ALL_DESCRIPTIONS = {
    **TRIGGER_DESCRIPTIONS,
    **SLO_DESCRIPTIONS,
    **BURN_ALERT_DESCRIPTIONS,
}


def get_description(tool_name: str) -> str:
    """Get the hand-crafted description for a tool.

    Args:
        tool_name: The tool name (e.g., "honeycomb_create_trigger")

    Returns:
        The description string

    Raises:
        KeyError: If tool name not found
    """
    if tool_name not in ALL_DESCRIPTIONS:
        raise KeyError(
            f"No description found for tool '{tool_name}'. "
            f"Available tools: {', '.join(sorted(ALL_DESCRIPTIONS.keys()))}"
        )
    return ALL_DESCRIPTIONS[tool_name]


def validate_description(description: str, min_length: int = 50) -> None:
    """Validate a description meets quality requirements.

    Args:
        description: The description to validate
        min_length: Minimum character count (default 50)

    Raises:
        ValueError: If description is invalid
    """
    if not description:
        raise ValueError("Description cannot be empty")

    if len(description) < min_length:
        raise ValueError(
            f"Description must be at least {min_length} characters (got {len(description)})"
        )

    # Check for placeholder text
    placeholders = ["TODO", "TBD", "FIXME", "XXX"]
    for placeholder in placeholders:
        if placeholder in description.upper():
            raise ValueError(f"Description contains placeholder text: {placeholder}")
