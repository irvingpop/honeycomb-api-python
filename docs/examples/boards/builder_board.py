"""Board Builder examples - using BoardBuilder for dashboard creation."""

from __future__ import annotations

from honeycomb import (
    Board,
    BoardBuilder,
    BoardPanelPosition,
    HoneycombClient,
)


# start_example:create_with_builder
async def create_board_with_builder(
    client: HoneycombClient,
    dataset: str,
) -> str:
    """Create a service dashboard with query panels using BoardBuilder.

    This example demonstrates:
    - Creating queries with annotations using QueryBuilder.annotate()
    - Multiple query panels with different visualization styles
    - Auto-layout for automatic panel arrangement
    - Tags for board organization
    """
    from honeycomb import QueryBuilder

    # Create queries with annotations (name + description)
    # Query 1: Request count (graph style)
    count_builder = (
        QueryBuilder()
        .last_24_hours()
        .count()
        .group_by("service")
        .annotate("Request Count", "Total requests by service over 24 hours")
    )
    q1, q1_annotation = await client.queries.create_with_annotation_async(dataset, count_builder)

    # Query 2: Average latency (table style)
    latency_builder = (
        QueryBuilder()
        .last_1_hour()
        .avg("duration_ms")
        .group_by("endpoint")
        .limit(10)
        .annotate("Avg Latency", "Top 10 endpoints by average latency")
    )
    q2, q2_annotation = await client.queries.create_with_annotation_async(dataset, latency_builder)

    # Build board with query panels
    board = (
        BoardBuilder("Service Health Dashboard")
        .description("Request metrics and latency tracking")
        .auto_layout()
        .tag("team", "platform")
        .tag("service", "api")
        # Add query panels with different styles
        .query(q1.id, q1_annotation, style="graph")
        .query(q2.id, q2_annotation, style="table")
        .build()
    )

    created = await client.boards.create_async(board)
    return created.id
# end_example:create_with_builder


# start_example:create_complex
async def create_complex_board(
    client: HoneycombClient,
    dataset: str,
    slo_id: str,
) -> str:
    """Create a comprehensive dashboard with all panel types and advanced features.

    This example demonstrates:
    - Multiple query panels with different styles (graph, table, combo)
    - SLO panel for availability tracking
    - Text panel for notes
    - Advanced visualization settings (hiding markers, UTC time)
    - Preset filters for dynamic filtering
    - Manual layout with precise positioning
    """
    from honeycomb import QueryBuilder

    # Create multiple queries with annotations
    # Query 1: Request count over time (graph with visualization settings)
    count_builder = (
        QueryBuilder()
        .last_24_hours()
        .count()
        .group_by("service")
        .annotate("Request Count", "Total requests by service over 24 hours")
    )
    q1, q1_annotation = await client.queries.create_with_annotation_async(dataset, count_builder)

    # Query 2: Average duration (table)
    latency_builder = (
        QueryBuilder()
        .last_1_hour()
        .avg("duration_ms")
        .group_by("endpoint")
        .limit(10)
        .annotate("Avg Latency", "Top 10 endpoints by average latency")
    )
    q2, q2_annotation = await client.queries.create_with_annotation_async(dataset, latency_builder)

    # Query 3: Error rate (combo - graph + table)
    error_builder = (
        QueryBuilder()
        .last_2_hours()
        .count()
        .gte("status_code", 400)
        .group_by("status_code")
        .annotate("Error Rate", "HTTP errors by status code")
    )
    q3, q3_annotation = await client.queries.create_with_annotation_async(dataset, error_builder)

    # Build comprehensive board with manual layout
    board = (
        BoardBuilder("Production Monitoring Dashboard")
        .description("Complete service health monitoring with queries, SLOs, and notes")
        .manual_layout()
        .tag("team", "platform")
        .tag("environment", "production")
        # Preset filters for dynamic filtering
        .preset_filter("service", "Service")
        .preset_filter("environment", "Environment")
        # Top row: Request count (large graph with advanced settings)
        .query(
            q1.id,
            q1_annotation,
            position=BoardPanelPosition(x_coordinate=0, y_coordinate=0, width=9, height=6),
            style="graph",
            visualization_settings={"hide_markers": True, "utc_xaxis": True},
        )
        # Top right: SLO status
        .slo(
            slo_id,
            position=BoardPanelPosition(x_coordinate=9, y_coordinate=0, width=3, height=6),
        )
        # Middle left: Latency table
        .query(
            q2.id,
            q2_annotation,
            position=BoardPanelPosition(x_coordinate=0, y_coordinate=6, width=6, height=5),
            style="table",
        )
        # Middle right: Error rate combo view
        .query(
            q3.id,
            q3_annotation,
            position=BoardPanelPosition(x_coordinate=6, y_coordinate=6, width=6, height=5),
            style="combo",
        )
        # Bottom: Notes panel (full width)
        .text(
            "## Monitoring Guidelines\n\n- Watch for latency > 500ms\n- Error rate should stay < 1%\n- Check SLO during peak hours",
            position=BoardPanelPosition(x_coordinate=0, y_coordinate=11, width=12, height=3),
        )
        .build()
    )

    created = await client.boards.create_async(board)
    return created.id
# end_example:create_complex


# start_example:list
async def list_boards(client: HoneycombClient) -> list[Board]:
    """List all boards in the environment."""
    return await client.boards.list_async()
# end_example:list


# start_example:get
async def get_board(client: HoneycombClient, board_id: str) -> Board:
    """Get a specific board by ID."""
    return await client.boards.get_async(board_id)
# end_example:get


# start_example:update
async def update_board(client: HoneycombClient, board_id: str) -> Board:
    """Update a board's name and description."""
    existing = await client.boards.get_async(board_id)

    # Use BoardBuilder to recreate with updates
    board = (
        BoardBuilder("Updated Service Health Dashboard")
        .description("Updated: Comprehensive monitoring for API service")
        .auto_layout()
        .build()
    )

    return await client.boards.update_async(board_id, board)
# end_example:update


# start_example:delete
async def delete_board(client: HoneycombClient, board_id: str) -> None:
    """Delete a board."""
    await client.boards.delete_async(board_id)
# end_example:delete


# TEST_ASSERTIONS
async def test_lifecycle(
    client: HoneycombClient, board_id: str, expected_name: str
) -> None:
    """Verify the full lifecycle worked."""
    board = await client.boards.get_async(board_id)
    assert board.id == board_id
    assert board.name == expected_name
    assert board.type == "flexible"


# CLEANUP
async def cleanup(client: HoneycombClient, board_id: str) -> None:
    """Clean up resources (called even on test failure)."""
    try:
        await client.boards.delete_async(board_id)
    except Exception:
        pass  # Already deleted or doesn't exist
