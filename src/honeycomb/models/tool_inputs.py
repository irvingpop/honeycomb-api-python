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

from pydantic import BaseModel, ConfigDict, Field

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
# Query Panel
# =============================================================================


class QueryPanelInput(BaseModel):
    """Query panel specification for board tool input.

    This model represents a complete query panel with FLAT structure.
    Query fields are at the top level, not nested under a 'query' object.

    Example:
        {
            "name": "CPU Usage",
            "dataset": "metrics",
            "time_range": 3600,
            "calculations": [{"op": "AVG", "column": "cpu_percent"}],
            "style": "graph"
        }
    """

    model_config = ConfigDict(extra="forbid")

    # Panel metadata
    name: str = Field(description="Panel/query name")
    description: str | None = Field(default=None, description="Panel description")
    style: Literal["graph", "table", "combo"] = Field(
        default="graph", description="Panel display style"
    )
    visualization: dict[str, Any] | None = Field(
        default=None, description="Visualization settings (chart-specific config)"
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

    # Dataset(s) - use either dataset OR datasets, not both
    dataset: str | None = Field(
        default=None, description="Single dataset slug (for dataset-scoped SLOs)"
    )
    datasets: list[str] | None = Field(
        default=None, description="Multiple dataset slugs (for environment-wide SLOs)"
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
    """Tag for boards."""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(description="Tag key")
    value: str = Field(description="Tag value")


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
