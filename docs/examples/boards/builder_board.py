"""Board Builder examples - using BoardBuilder for dashboard creation."""

from __future__ import annotations

from honeycomb import Board, HoneycombClient


# start_example:create_with_builder
async def create_board_with_builder(
    client: HoneycombClient,
    dataset: str,
) -> str:
    """Create a service dashboard with inline QueryBuilder instances.

    This example demonstrates:
    - Inline QueryBuilder instances with .name() and .description()
    - Automatic query + annotation creation via create_from_bundle_async()
    - Multiple query panels with different visualization styles
    - Auto-layout for automatic panel arrangement
    - Tags for board organization
    """
    from honeycomb import BoardBuilder, QueryBuilder

    # Single fluent call with inline QueryBuilder instances
    created = await client.boards.create_from_bundle_async(
        BoardBuilder("Service Health Dashboard")
        .description("Request metrics and latency tracking")
        .auto_layout()
        .tag("team", "platform")
        .tag("service", "api")
        # Query panels with inline QueryBuilder
        .query(
            QueryBuilder()
            .dataset(dataset)
            .last_24_hours()
            .count()
            .group_by("service")
            .name("Request Count")
            .description("Total requests by service over 24 hours"),
            style="graph",
        )
        .query(
            QueryBuilder()
            .dataset(dataset)
            .last_1_hour()
            .avg("duration_ms")
            .group_by("endpoint")
            .limit(10)
            .name("Avg Latency")
            .description("Top 10 endpoints by average latency"),
            style="table",
        )
        .build()
    )
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
    - Inline QueryBuilder instances with automatic query creation
    - Multiple query panels with different styles (graph, table, combo)
    - SLO panel for availability tracking
    - Text panel for notes
    - Advanced visualization settings (hiding markers, UTC time)
    - Preset filters for dynamic filtering
    - Manual layout with precise positioning using tuples
    """
    from honeycomb import BoardBuilder, QueryBuilder

    # Single fluent call with inline QueryBuilder and manual positioning
    created = await client.boards.create_from_bundle_async(
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
            QueryBuilder()
            .dataset(dataset)
            .last_24_hours()
            .count()
            .group_by("service")
            .name("Request Count")
            .description("Total requests by service over 24 hours"),
            position=(0, 0, 9, 6),
            style="graph",
            visualization={"hide_markers": True, "utc_xaxis": True},
        )
        # Top right: SLO status
        .slo(slo_id, position=(9, 0, 3, 6))
        # Middle left: Latency table
        .query(
            QueryBuilder()
            .dataset(dataset)
            .last_1_hour()
            .avg("duration_ms")
            .group_by("endpoint")
            .limit(10)
            .name("Avg Latency")
            .description("Top 10 endpoints by average latency"),
            position=(0, 6, 6, 5),
            style="table",
        )
        # Middle right: Error rate combo view
        .query(
            QueryBuilder()
            .dataset(dataset)
            .last_2_hours()
            .count()
            .gte("status_code", 400)
            .group_by("status_code")
            .name("Error Rate")
            .description("HTTP errors by status code"),
            position=(6, 6, 6, 5),
            style="combo",
        )
        # Bottom: Notes panel (full width)
        .text(
            "## Monitoring Guidelines\n\n- Watch for latency > 500ms\n- Error rate should stay < 1%\n- Check SLO during peak hours",
            position=(0, 11, 12, 3),
        )
        .build()
    )
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
async def update_board(client: HoneycombClient, board_id: str, dataset: str) -> Board:
    """Update a board's name and description."""
    from honeycomb import BoardCreate

    # For updates, we need to use BoardCreate directly (not BoardBundle)
    # since we're not creating new queries
    board_create = BoardCreate(
        name="Updated Service Health Dashboard",
        description="Updated: Comprehensive monitoring for API service",
        type="flexible",
        layout_generation="auto",
    )

    return await client.boards.update_async(board_id, board_create)
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
