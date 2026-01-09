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

import json
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
    limit: int | None = Field(default=None, description="Result limit (max 1000)")
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
    """Complete SLO tool input for creating SLOs.

    Note: Only target_percentage is exposed to tools (most intuitive format).
    The target_nines format has been removed entirely.
    """

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
        default=30, description="SLO time period in days (typically 7, 14, or 30)"
    )

    # Inline burn alerts
    burn_alerts: list[BurnAlertInput] | None = Field(
        default=None, description="Burn alerts to create with the SLO"
    )


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


def _generate_query_signature(panel: QueryPanelInput) -> str:
    """Generate a signature for the core query specification.

    This signature represents the fields that Honeycomb uses to generate a QueryID.
    Two queries with the same signature will have the same QueryID and cannot both
    be added to the same board.

    Fields that affect QueryID:
    - dataset
    - calculations
    - filters
    - breakdowns
    - time_range / start_time / end_time
    - granularity
    - filter_combination
    - havings
    - calculated_fields

    Fields that do NOT affect QueryID (visualization only):
    - name, description
    - orders, limit
    - chart_type, visualization settings
    - position, style
    """
    # Sort filters and breakdowns for consistent comparison
    filters_sorted = None
    if panel.filters:
        filters_sorted = sorted(
            [f.model_dump() for f in panel.filters], key=lambda x: x.get("column", "")
        )

    breakdowns_sorted = None
    if panel.breakdowns:
        breakdowns_sorted = sorted(panel.breakdowns)

    calculated_fields_sorted = None
    if panel.calculated_fields:
        calculated_fields_sorted = sorted(
            [cf.model_dump() for cf in panel.calculated_fields], key=lambda x: x["name"]
        )

    havings_sorted = None
    if panel.havings:
        havings_sorted = sorted([h.model_dump() for h in panel.havings], key=str)

    # Build signature dict with only QueryID-affecting fields
    sig = {
        "dataset": panel.dataset,
        "calculations": [c.model_dump() for c in panel.calculations]
        if panel.calculations
        else None,
        "filters": filters_sorted,
        "breakdowns": breakdowns_sorted,
        "time_range": panel.time_range,
        "start_time": panel.start_time,
        "end_time": panel.end_time,
        "granularity": panel.granularity,
        "filter_combination": panel.filter_combination,
        "havings": havings_sorted,
        "calculated_fields": calculated_fields_sorted,
    }

    return json.dumps(sig, sort_keys=True)


def _format_query_spec(panel: QueryPanelInput) -> str:
    """Format a query spec summary for error messages."""
    parts = []

    # Dataset
    if panel.dataset:
        parts.append(f"dataset={panel.dataset}")

    # Calculations
    if panel.calculations:
        calc_str = ", ".join(
            f"{c.op}" + (f"({c.column})" if c.column else "") for c in panel.calculations
        )
        parts.append(f"calculations=[{calc_str}]")

    # Filters
    if panel.filters:
        filter_str = ", ".join(
            f"{f.column} {f.op} {f.value}"
            for f in panel.filters[:2]  # Show first 2
        )
        if len(panel.filters) > 2:
            filter_str += f", ... ({len(panel.filters)} total)"
        parts.append(f"filters=[{filter_str}]")

    # Breakdowns
    if panel.breakdowns:
        breakdown_str = ", ".join(panel.breakdowns[:2])  # Show first 2
        if len(panel.breakdowns) > 2:
            breakdown_str += f", ... ({len(panel.breakdowns)} total)"
        parts.append(f"breakdowns=[{breakdown_str}]")

    # Time range
    if panel.time_range:
        parts.append(f"time_range={panel.time_range}s")

    return ", ".join(parts)


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

        Honeycomb generates QueryIDs based on the core query specification (dataset,
        calculations, filters, breakdowns, time_range, etc.). A board cannot have
        multiple panels with the same QueryID, even if they have different names or
        visualization settings.

        Raises:
            ValueError: If duplicate query specifications are detected, with details
                       about which panels are duplicates and how to fix them.
        """
        if not self.inline_query_panels:
            return self

        # Track query signatures and the panels that use them
        signatures: dict[str, list[QueryPanelInput]] = {}
        for panel in self.inline_query_panels:
            sig = _generate_query_signature(panel)
            if sig not in signatures:
                signatures[sig] = []
            signatures[sig].append(panel)

        # Find duplicates
        duplicates = {sig: panels for sig, panels in signatures.items() if len(panels) > 1}

        if duplicates:
            # Build detailed error message
            error_lines = [
                "Duplicate query specifications detected.",
                "A board cannot have multiple panels with identical query specs "
                "(same dataset, calculations, filters, breakdowns, time_range).",
                "",
                "Duplicates found:",
            ]

            for _sig, panels in duplicates.items():
                # Show which panels are duplicates
                panel_names = [f'"{p.name}"' for p in panels]
                error_lines.append(f"  • Panels {' and '.join(panel_names)}")

                # Show the common query spec
                spec_summary = _format_query_spec(panels[0])
                error_lines.append(f"    → Both query: {spec_summary}")

            error_lines.extend(
                [
                    "",
                    "To fix: Make queries different by changing calculations, filters, breakdowns, or time_range.",
                    "Note: Different panel names, orders, limits, or chart_types do NOT make queries unique.",
                ]
            )

            raise ValueError("\n".join(error_lines))

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
