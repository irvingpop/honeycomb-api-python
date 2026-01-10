"""Tool input models for Claude Code integration.

These models are specifically designed for tool validation with strict schema constraints:
- All models use extra="forbid" to reject unknown fields
- All enum fields use strict enum types (no | str unions)
- All models generate JSON schemas with additionalProperties: false

These models are used by:
1. Tool schema generation (generator.py)
2. Tool input validation (builders.py)
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self

from honeycomb.models.query_builder import (
    Calculation,
    Filter,
    FilterCombination,
    FilterOp,
    Having,
    Order,
)

# =============================================================================
# Position & Layout
# =============================================================================


class PositionInput(BaseModel):
    """Panel position on the board grid (API-native structure).

    Note: This uses the API's named field structure instead of tuples.
    Board grid is 24 units wide, panels can be 1-24 units in width/height.
    """

    model_config = ConfigDict(extra="forbid")

    x_coordinate: int = Field(ge=0, description="X position on grid (0-based)")
    y_coordinate: int = Field(ge=0, description="Y position on grid (0-based)")
    width: int = Field(ge=1, le=24, description="Panel width in grid units (1-24)")
    height: int = Field(ge=1, le=24, description="Panel height in grid units (1-24)")


# =============================================================================
# Visualization Settings
# =============================================================================


class ChartSettingsInput(BaseModel):
    """Individual chart visualization settings within a query panel.

    Each calculation in a query can have its own chart settings.
    Use chart_index to target specific calculations (0-based).
    """

    model_config = ConfigDict(extra="forbid")

    chart_index: int = Field(
        default=0,
        ge=0,
        description="Chart index (0-based, for queries with multiple calculations)",
    )
    chart_type: Literal["default", "line", "stacked", "stat", "tsbar", "cbar", "cpie"] = Field(
        default="default",
        description="Chart type: default (auto), line (time series), stacked (stacked area), "
        "stat (single value), tsbar (time series bar), cbar (categorical bar), cpie (pie)",
    )
    log_scale: bool = Field(default=False, description="Use logarithmic Y-axis scale")
    omit_missing_values: bool = Field(
        default=False, description="Skip gaps in data instead of interpolating"
    )


class VisualizationSettingsInput(BaseModel):
    """Visualization settings for board query panels.

    Controls how the query results are displayed on the board.
    """

    model_config = ConfigDict(extra="forbid")

    hide_compare: bool = Field(default=False, description="Hide comparison time range overlay")
    hide_hovers: bool = Field(default=False, description="Disable hover tooltips on data points")
    hide_markers: bool = Field(default=False, description="Hide markers on data points")
    utc_xaxis: bool = Field(default=False, description="Show X-axis timestamps in UTC timezone")
    overlaid_charts: bool = Field(
        default=False, description="Overlay multiple calculations on same chart"
    )
    charts: list[ChartSettingsInput] | None = Field(
        default=None,
        description="Per-chart settings (one entry per calculation). If omitted, defaults apply.",
    )


# =============================================================================
# Calculated Fields
# =============================================================================


class CalculatedFieldInput(BaseModel):
    """Inline calculated field (derived column) for queries.

    Creates a computed column available only within this query.
    For reusable derived columns, use the Derived Columns API instead.

    Example expressions:
        - "MULTIPLY($duration_ms, 1000)" - convert ms to microseconds
        - "IF(LT($status_code, 400), 1, 0)" - success indicator
        - "CONCAT($service, '/', $endpoint)" - combine strings
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Field name/alias to reference in calculations and breakdowns")
    expression: str = Field(
        description="Formula expression using $column_name syntax. "
        "See https://docs.honeycomb.io/reference/derived-column-formula/"
    )


# =============================================================================
# Query Panel
# =============================================================================


class QueryPanelInput(BaseModel):
    """Query panel specification for board tool input.

    This model represents a complete query panel with FLAT structure.
    Query fields are at the top level, not nested under a 'query' object.

    Example (simple with chart_type shorthand):
        {
            "name": "CPU Usage",
            "dataset": "metrics",
            "time_range": 3600,
            "calculations": [{"op": "AVG", "column": "cpu_percent"}],
            "chart_type": "line"
        }

    Example (with full visualization settings):
        {
            "name": "Error Rate",
            "dataset": "api-logs",
            "time_range": 3600,
            "calculations": [{"op": "COUNT"}],
            "visualization": {
                "utc_xaxis": true,
                "charts": [{"chart_type": "stacked", "log_scale": true}]
            }
        }
    """

    model_config = ConfigDict(extra="forbid")

    # Panel metadata
    name: str = Field(description="Panel/query name")
    description: str | None = Field(default=None, description="Panel description")
    style: Literal["graph", "table", "combo"] = Field(
        default="graph", description="Panel display style"
    )
    visualization: VisualizationSettingsInput | None = Field(
        default=None,
        description="Full visualization settings. For simple cases, use chart_type instead.",
    )
    chart_type: Literal["default", "line", "stacked", "stat", "tsbar", "cbar", "cpie"] | None = (
        Field(
            default=None,
            description="Shorthand for visualization.charts[0].chart_type. "
            "Use for simple single-calculation panels. "
            "Values: line (time series), stacked (stacked area), stat (single number), "
            "tsbar (time series bar), cbar (categorical bar), cpie (pie chart)",
        )
    )
    position: PositionInput | None = Field(
        default=None,
        description="Panel position for manual layout (required if layout_generation=manual)",
    )

    # Query specification (FLAT, not nested)
    dataset: str | None = Field(
        default=None, description="Dataset slug (None = environment-wide query)"
    )
    time_range: int | None = Field(
        default=None, description="Time range in seconds (relative time)"
    )
    start_time: int | None = Field(
        default=None, description="Absolute start time (Unix timestamp, use with end_time)"
    )
    end_time: int | None = Field(
        default=None, description="Absolute end time (Unix timestamp, use with start_time)"
    )
    granularity: int | None = Field(default=None, description="Time granularity in seconds")
    calculations: list[Calculation] | None = Field(
        default=None, description="Calculations to perform (e.g., COUNT, AVG, P99)"
    )
    filters: list[Filter] | None = Field(default=None, description="Query filters")
    breakdowns: list[str] | None = Field(default=None, description="Columns to group by")
    filter_combination: FilterCombination | None = Field(
        default=None, description="How to combine filters (AND or OR)"
    )
    orders: list[Order] | None = Field(default=None, description="Result ordering")
    limit: int | None = Field(default=None, ge=1, le=1000, description="Result limit (max 1000)")
    havings: list[Having] | None = Field(
        default=None, description="Having clauses for post-aggregation filtering"
    )
    calculated_fields: list[CalculatedFieldInput] | None = Field(
        default=None,
        description="Inline calculated fields (derived columns) for this query only",
    )
    compare_time_offset_seconds: (
        Literal[1800, 3600, 7200, 28800, 86400, 604800, 2419200, 15724800] | None
    ) = Field(
        default=None,
        description="Compare against historical data offset by N seconds. "
        "Values: 1800 (30min), 3600 (1hr), 7200 (2hr), 28800 (8hr), "
        "86400 (24hr), 604800 (7d), 2419200 (28d), 15724800 (6mo)",
    )


# =============================================================================
# SLO Components
# =============================================================================


class SLIInput(BaseModel):
    """SLI (Service Level Indicator) specification for tool input.

    An SLI can either reference an existing column by alias, or create
    a new derived column inline by providing an expression.
    """

    model_config = ConfigDict(extra="forbid")

    alias: str = Field(description="Column alias for the SLI (e.g., 'success_rate')")
    expression: str | None = Field(
        default=None,
        description="Derived column expression (creates column if provided, e.g., 'LTE($duration_ms, 500)')",
    )
    description: str | None = Field(default=None, description="SLI description")


class RecipientInput(BaseModel):
    """Recipient specification (shared across triggers, SLOs, burn alerts).

    Either reference an existing recipient by ID, OR create a new one inline
    by providing type and target.

    Note: Only 'email' and 'webhook' types are testable without external integrations.
    Other types ('slack', 'pagerduty', 'msteams') require service configuration.
    """

    model_config = ConfigDict(extra="forbid")

    # Either reference existing recipient by ID...
    id: str | None = Field(default=None, description="Existing recipient ID")

    # ...OR create inline with type + target
    type: Literal["email", "webhook", "slack", "pagerduty", "msteams"] | None = Field(
        default=None, description="Recipient type (for inline creation)"
    )
    target: str | None = Field(
        default=None, description="Recipient target (email address, webhook URL, or integration ID)"
    )


class BurnAlertInput(BaseModel):
    """Burn alert specification for inline creation with SLOs.

    Two alert types:
    - exhaustion_time: Alert when budget will be exhausted in N minutes
    - budget_rate: Alert when budget is decreasing faster than threshold
    """

    model_config = ConfigDict(extra="forbid")

    alert_type: Literal["exhaustion_time", "budget_rate"] = Field(description="Alert type")
    description: str | None = Field(default=None, description="Alert description")

    # For exhaustion_time alerts
    exhaustion_minutes: int | None = Field(
        default=None, description="Minutes until budget exhaustion (required for exhaustion_time)"
    )

    # For budget_rate alerts
    budget_rate_window_minutes: int | None = Field(
        default=None, description="Window size in minutes (required for budget_rate)"
    )
    budget_rate_decrease_threshold_per_million: int | None = Field(
        default=None, description="Threshold in per-million units (required for budget_rate)"
    )

    # Recipients (optional)
    recipients: list[RecipientInput] | None = Field(default=None, description="Alert recipients")


class SLOToolInput(BaseModel):
    """Complete SLO tool input for creating SLOs."""

    model_config = ConfigDict(extra="forbid")

    # Required
    name: str = Field(description="SLO name")
    sli: SLIInput = Field(description="SLI specification")

    # Optional metadata
    description: str | None = Field(default=None, description="SLO description")

    # Dataset(s) - always a list, even for single dataset
    datasets: list[str] = Field(
        min_length=1,
        description="Dataset slug(s). Use single-element list for one dataset, multiple for environment-wide SLO",
    )

    # Target - only target_percentage exposed
    target_percentage: float = Field(
        description="Target as percentage (e.g., 99.9 for 99.9% success rate)"
    )

    # Time period
    time_period_days: int = Field(
        default=30,
        ge=1,
        le=90,
        description="SLO time period in days (1-90, typically 7, 14, or 30)",
    )

    # Inline burn alerts
    burn_alerts: list[BurnAlertInput] | None = Field(
        default=None, description="Burn alerts to create with the SLO"
    )

    # Tags
    tags: list[TagInput] | None = Field(default=None, description="SLO tags")

    @model_validator(mode="after")
    def validate_slo_constraints(self) -> Self:
        """Validate SLO-specific constraints using shared validation logic.

        Raises:
            ValueError: If constraints are violated:
                - time_period_days outside 1-90 range
                - target_percentage outside 0-100 range
        """
        from honeycomb.validation.slos import (
            validate_slo_target_percentage,
            validate_slo_time_period,
        )

        # Validate time period
        validate_slo_time_period(self.time_period_days)

        # Validate target percentage
        validate_slo_target_percentage(self.target_percentage)

        return self

    @model_validator(mode="after")
    def validate_tags_limit(self) -> Self:
        """Validate that tags don't exceed the maximum limit of 10."""
        if self.tags and len(self.tags) > 10:
            raise ValueError(
                f"Too many tags: {len(self.tags)} provided, but maximum is 10.\n"
                "Honeycomb limits resources to 10 tags each.\n"
                "Remove some tags to proceed."
            )
        return self


# =============================================================================
# Trigger Tool Input
# =============================================================================


class TriggerQueryInput(BaseModel):
    """Query specification for trigger tool input.

    Triggers support a subset of query features:
    - Single calculation only (min/max enforced by field validator)
    - No HEATMAP calculations
    - No orders or limit fields (not present in this model)
    - Relative time ranges only (no absolute start/end times)
    - Maximum time range of 3600 seconds (1 hour)
    """

    model_config = ConfigDict(extra="forbid")

    time_range: int = Field(description="Query time range in seconds (max 3600 for triggers)")
    calculations: list[Calculation] = Field(
        min_length=1,
        max_length=1,
        description="Calculation (triggers support exactly one calculation)",
    )
    filters: list[Filter] | None = Field(default=None, description="Query filters")
    breakdowns: list[str] | None = Field(default=None, description="Columns to group by")
    filter_combination: FilterCombination | None = Field(
        default=None, description="How to combine filters (AND or OR)"
    )
    granularity: int | None = Field(default=None, description="Time granularity in seconds")

    @model_validator(mode="after")
    def validate_trigger_query_constraints(self) -> Self:
        """Validate trigger-specific query constraints.

        Raises:
            ValueError: If HEATMAP calculation is used
        """
        from honeycomb.validation.triggers import validate_trigger_calculation_not_heatmap

        # Check that calculation is not HEATMAP
        if self.calculations:
            calc_op = self.calculations[0].op.value
            validate_trigger_calculation_not_heatmap(calc_op)

        return self


class TriggerThresholdInput(BaseModel):
    """Threshold specification for trigger tool input."""

    model_config = ConfigDict(extra="forbid")

    op: Literal[">", ">=", "<", "<="] = Field(description="Threshold comparison operator")
    value: float = Field(description="Threshold value")
    exceeded_limit: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Consecutive evaluations that must exceed threshold (1-5)",
    )


class TriggerToolInput(BaseModel):
    """Complete trigger tool input with cross-field validation.

    This model validates trigger constraints before builder execution,
    using shared validation functions that are also used by TriggerBuilder.
    """

    model_config = ConfigDict(extra="forbid")

    # Required fields
    name: str = Field(description="Trigger name")
    dataset: str = Field(description="Dataset slug")
    query: TriggerQueryInput = Field(description="Query specification")
    threshold: TriggerThresholdInput = Field(description="Threshold configuration")
    frequency: int = Field(
        default=900,
        ge=60,
        le=86400,
        description="Evaluation frequency in seconds (60-86400, typically 60, 300, 900, 1800, or 3600)",
    )

    # Optional fields
    description: str | None = Field(default=None, description="Trigger description")
    disabled: bool = Field(default=False, description="Whether trigger is disabled")
    alert_type: Literal["on_change", "on_true"] = Field(
        default="on_change", description="When to send alerts"
    )
    recipients: list[RecipientInput] | None = Field(
        default=None, description="Notification recipients (inline or by ID)"
    )
    tags: list[TagInput] | None = Field(default=None, description="Trigger tags")

    @model_validator(mode="after")
    def validate_trigger_constraints(self) -> Self:
        """Validate trigger-specific constraints using shared validation logic.

        Raises:
            ValueError: If constraints are violated:
                - time_range > 3600 seconds
                - frequency outside 60-86400 range
                - time_range > frequency * 4
        """
        from honeycomb.validation.triggers import (
            validate_time_range_frequency_ratio,
            validate_trigger_frequency,
            validate_trigger_time_range,
        )

        # Validate time range
        validate_trigger_time_range(self.query.time_range)

        # Validate frequency
        validate_trigger_frequency(self.frequency)

        # Validate time range vs frequency ratio
        validate_time_range_frequency_ratio(self.query.time_range, self.frequency)

        return self

    @model_validator(mode="after")
    def validate_tags_limit(self) -> Self:
        """Validate that tags don't exceed the maximum limit of 10."""
        if self.tags and len(self.tags) > 10:
            raise ValueError(
                f"Too many tags: {len(self.tags)} provided, but maximum is 10.\n"
                "Honeycomb limits resources to 10 tags each.\n"
                "Remove some tags to proceed."
            )
        return self


# =============================================================================
# Recipient Detail Models (for Recipients API)
# =============================================================================


class EmailRecipientDetailsInput(BaseModel):
    """Email recipient details for tool input."""

    model_config = ConfigDict(extra="forbid")

    email_address: str = Field(description="Email address to notify")


class SlackRecipientDetailsInput(BaseModel):
    """Slack recipient details for tool input."""

    model_config = ConfigDict(extra="forbid")

    slack_channel: str = Field(description="Slack channel (e.g., '#alerts')")


class PagerDutyRecipientDetailsInput(BaseModel):
    """PagerDuty recipient details for tool input."""

    model_config = ConfigDict(extra="forbid")

    pagerduty_integration_key: str = Field(
        min_length=32,
        max_length=32,
        description="PagerDuty integration key (exactly 32 characters)",
    )
    pagerduty_integration_name: str = Field(description="Name for this PagerDuty integration")


class WebhookHeaderInput(BaseModel):
    """HTTP header for webhook recipient."""

    model_config = ConfigDict(extra="forbid")

    header: str = Field(max_length=64, description="Header name (e.g., 'Authorization')")
    value: str | None = Field(
        default=None, max_length=750, description="Header value (e.g., 'Bearer token')"
    )


class WebhookTemplateVariableInput(BaseModel):
    """Template variable for webhook payload customization."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        max_length=64,
        pattern=r"^[a-z](?:[a-zA-Z0-9]+$)?$",
        description="Variable name (must start with lowercase, alphanumeric only)",
    )
    default_value: str | None = Field(
        default=None, max_length=256, description="Default value for this variable"
    )


class WebhookPayloadTemplateInput(BaseModel):
    """Payload template for specific alert type."""

    model_config = ConfigDict(extra="forbid")

    body: str | None = Field(
        default=None, description="JSON template string with {{variable}} placeholders"
    )


class WebhookPayloadTemplatesInput(BaseModel):
    """Payload templates for different alert types.

    Each alert type (trigger, budget_rate, exhaustion_time) can have a custom
    JSON payload template with variable substitution.
    """

    model_config = ConfigDict(extra="forbid")

    trigger: WebhookPayloadTemplateInput | None = Field(
        default=None, description="Payload template for trigger alerts"
    )
    budget_rate: WebhookPayloadTemplateInput | None = Field(
        default=None, description="Payload template for budget rate burn alerts"
    )
    exhaustion_time: WebhookPayloadTemplateInput | None = Field(
        default=None, description="Payload template for exhaustion time burn alerts"
    )


class WebhookPayloadsInput(BaseModel):
    """Webhook payload customization with templates and variables."""

    model_config = ConfigDict(extra="forbid")

    template_variables: list[WebhookTemplateVariableInput] | None = Field(
        default=None, description="Template variables for payload substitution (max 10)"
    )
    payload_templates: WebhookPayloadTemplatesInput | None = Field(
        default=None,
        description="Custom payload templates for different alert types (trigger, budget_rate, exhaustion_time)",
    )


class WebhookRecipientDetailsInput(BaseModel):
    """Webhook recipient details for tool input."""

    model_config = ConfigDict(extra="forbid")

    webhook_url: str = Field(max_length=2048, description="Webhook URL to POST to")
    webhook_name: str = Field(max_length=255, description="Name for this webhook")
    webhook_secret: str | None = Field(
        default=None, max_length=255, description="Optional secret for webhook signing"
    )
    webhook_headers: list[WebhookHeaderInput] | None = Field(
        default=None, description="Optional HTTP headers for authentication (max 5)"
    )
    webhook_payloads: WebhookPayloadsInput | None = Field(
        default=None,
        description="Optional custom payload templates with template variables",
    )


class MSTeamsRecipientDetailsInput(BaseModel):
    """MS Teams workflow recipient details for tool input."""

    model_config = ConfigDict(extra="forbid")

    webhook_url: str = Field(
        max_length=2048, description="Azure Logic Apps workflow URL for MS Teams"
    )
    webhook_name: str = Field(max_length=255, description="Name for this MS Teams recipient")


class RecipientCreateToolInput(BaseModel):
    """Recipient creation specification for Recipients API tools.

    This model is used for tool schema generation to provide proper validation
    of recipient details. The details schema varies by type - use the appropriate
    typed model for each recipient type.
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal["email", "slack", "pagerduty", "webhook", "msteams_workflow"] = Field(
        description="Type of recipient notification"
    )
    details: (
        EmailRecipientDetailsInput
        | SlackRecipientDetailsInput
        | PagerDutyRecipientDetailsInput
        | WebhookRecipientDetailsInput
        | MSTeamsRecipientDetailsInput
    ) = Field(description="Recipient-specific configuration (schema varies by type)")


# =============================================================================
# Board Panels
# =============================================================================


class TextPanelInput(BaseModel):
    """Text/markdown panel for boards."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(description="Markdown content for the panel")
    position: PositionInput | None = Field(
        default=None, description="Panel position (required for manual layout)"
    )


class SLOPanelInput(BaseModel):
    """Inline SLO panel for boards.

    Creates an SLO and adds it to the board in one operation.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="SLO name")
    description: str | None = Field(default=None, description="SLO description")
    dataset: str = Field(description="Dataset slug")
    sli: SLIInput = Field(description="SLI specification")
    target_percentage: float = Field(description="Target as percentage (e.g., 99.9)")
    time_period_days: int = Field(default=30, description="Time period in days")
    position: PositionInput | None = Field(
        default=None, description="Panel position (required for manual layout)"
    )


# =============================================================================
# Board Features
# =============================================================================


class TagInput(BaseModel):
    """Tag for boards, triggers, and SLOs.

    Tags are key-value pairs used to identify and organize resources in Honeycomb.

    Constraints:
    - Keys: 1-32 chars, lowercase letters and underscores only (e.g., "team", "service_type")
    - Values: 1-128 chars, must start with lowercase letter, can contain lowercase letters,
      numbers, forward slash (/), and dash (-) (e.g., "platform", "api/backend", "staging-east-1")
    - Maximum 10 tags per resource

    Common examples:
    - {"key": "team", "value": "platform"}
    - {"key": "environment", "value": "production"}
    - {"key": "service_type", "value": "api/backend"}
    - {"key": "region", "value": "us-east-1"}
    """

    model_config = ConfigDict(extra="forbid")

    key: str = Field(
        min_length=1,
        max_length=32,
        pattern=r"^[a-z_]+$",
        description="Tag key: lowercase letters and underscores only, 1-32 chars",
    )
    value: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[a-z][a-z0-9/-]*$",
        description="Tag value: must start with lowercase letter, can contain lowercase letters, "
        "numbers, / and -, 1-128 chars",
    )


class PresetFilterInput(BaseModel):
    """Preset filter column for boards.

    Preset filters allow users to filter board results by specific columns
    using the board UI controls.
    """

    model_config = ConfigDict(extra="forbid")

    column: str = Field(description="Column name to filter on")
    alias: str = Field(description="Display alias for the filter control")


class BoardViewFilter(BaseModel):
    """Filter for board views.

    Board views allow saved filter configurations that users can switch between.
    """

    model_config = ConfigDict(extra="forbid")

    column: str = Field(description="Column name to filter on")
    operation: FilterOp = Field(description="Filter operation")
    value: Any | None = Field(
        default=None, description="Filter value (optional for exists/does-not-exist operations)"
    )


class BoardViewInput(BaseModel):
    """Named view with filters for boards."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="View name")
    filters: list[BoardViewFilter] | None = Field(default=None, description="View filters")


# =============================================================================
# Board Tool Input
# =============================================================================


class BoardToolInput(BaseModel):
    """Complete board tool input for creating boards.

    Supports three layout modes:
    - auto: Automatically arranges panels (position not required)
    - manual: User-specified positions (position required for all panels)

    Panel types:
    - inline_query_panels: Query panels (creates queries inline)
    - inline_slo_panels: SLO panels (creates SLOs inline)
    - text_panels: Markdown/text panels
    - slo_panels: Reference existing SLOs by ID
    """

    model_config = ConfigDict(extra="forbid")

    # Board metadata
    name: str = Field(description="Board name")
    description: str | None = Field(default=None, description="Board description")
    layout_generation: Literal["auto", "manual"] = Field(
        default="auto", description="Layout mode (auto or manual)"
    )

    # Panels
    inline_query_panels: list[QueryPanelInput] | None = Field(
        default=None, description="Query panels to create inline"
    )
    inline_slo_panels: list[SLOPanelInput] | None = Field(
        default=None, description="SLO panels to create inline"
    )
    text_panels: list[TextPanelInput] | None = Field(
        default=None, description="Text/markdown panels"
    )
    slo_panels: list[str] | None = Field(
        default=None, description="Existing SLO IDs to add as panels"
    )

    # Board features
    tags: list[TagInput] | None = Field(default=None, description="Board tags (key-value pairs)")
    preset_filters: list[PresetFilterInput] | None = Field(
        default=None, description="Preset filter columns for board UI"
    )
    views: list[BoardViewInput] | None = Field(
        default=None, description="Named views with saved filter configurations"
    )

    @model_validator(mode="after")
    def validate_no_duplicate_queries(self) -> Self:
        """Validate that no duplicate query specifications exist in inline_query_panels.

        Uses shared validation logic from honeycomb.validation.boards.

        Raises:
            ValueError: If duplicate query specifications are detected, with details
                       about which panels are duplicates and how to fix them.
        """
        if self.inline_query_panels:
            from honeycomb.validation.boards import validate_no_duplicate_query_panels

            validate_no_duplicate_query_panels(self.inline_query_panels)

        return self

    @model_validator(mode="after")
    def validate_tags_limit(self) -> Self:
        """Validate that tags don't exceed the maximum limit of 10.

        Raises:
            ValueError: If more than 10 tags are provided.
        """
        if self.tags and len(self.tags) > 10:
            raise ValueError(
                f"Too many tags: {len(self.tags)} provided, but maximum is 10.\n"
                "Honeycomb limits resources to 10 tags each.\n"
                "Remove some tags to proceed."
            )

        return self
