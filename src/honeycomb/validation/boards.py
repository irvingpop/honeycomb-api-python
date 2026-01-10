"""Shared validation logic for board constraints.

These functions are used by BoardToolInput to ensure boards are valid
before any queries or API calls are made.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from honeycomb.models.tool_inputs import QueryPanelInput


def generate_query_signature(panel: QueryPanelInput) -> str:
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

    Args:
        panel: QueryPanelInput to generate signature for

    Returns:
        JSON string representing the query signature
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


def format_query_spec(panel: QueryPanelInput) -> str:
    """Format a query spec summary for error messages.

    Args:
        panel: QueryPanelInput to format

    Returns:
        Human-readable summary of the query specification
    """
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


def validate_no_duplicate_query_panels(
    inline_query_panels: list[QueryPanelInput],
) -> None:
    """Validate that no duplicate query specifications exist in panel list.

    Honeycomb generates QueryIDs based on the core query specification. A board
    cannot have multiple panels with the same QueryID, even if they have different
    names or visualization settings.

    Args:
        inline_query_panels: List of QueryPanelInput to validate

    Raises:
        ValueError: If duplicate query specifications are detected, with details
                   about which panels are duplicates and how to fix them.
    """
    if not inline_query_panels:
        return

    # Track query signatures and the panels that use them
    signatures: dict[str, list[QueryPanelInput]] = {}
    for panel in inline_query_panels:
        sig = generate_query_signature(panel)
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
            spec_summary = format_query_spec(panels[0])
            error_lines.append(f"    → Both query: {spec_summary}")

        error_lines.extend(
            [
                "",
                "To fix: Make queries different by changing calculations, filters, breakdowns, or time_range.",
                "Note: Different panel names, orders, limits, or chart_types do NOT make queries unique.",
            ]
        )

        raise ValueError("\n".join(error_lines))
