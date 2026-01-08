"""Board Builder examples - using BoardBuilder for dashboard creation."""

from __future__ import annotations

from honeycomb import Board, HoneycombClient


# start_example:create_with_builder
async def create_board_with_builder(client: HoneycombClient, dataset: str = "integration-test") -> str:
    """Create a service dashboard with inline QueryBuilder instances.

    This example demonstrates:
    - Inline QueryBuilder with name in constructor
    - Automatic query + annotation creation via create_from_bundle_async()
    - Multiple query panels with different visualization styles
    - Auto-layout for automatic panel arrangement
    - Dataset scoping variations (explicit vs environment-wide)
    """
    from honeycomb import BoardBuilder, QueryBuilder

    # Single fluent call with inline QueryBuilder instances
    created = await client.boards.create_from_bundle_async(
        BoardBuilder("Service Health Dashboard")
        .description("Request metrics and latency tracking")
        .auto_layout()
        .tag("team", "platform")
        .tag("service", "api")
        # Query 1: Dataset-scoped query
        .query(
            QueryBuilder("Request Count")
            .dataset(dataset)
            .last_24_hours()
            .count()
            .group_by("service")
            .description("Total requests by service over 24 hours"),
            style="graph",
        )
        # Query 2: Environment-wide query (all datasets)
        .query(
            QueryBuilder("Avg Latency")
            .environment_wide()
            .last_1_hour()
            .avg("duration_ms")
            .group_by("endpoint")
            .limit(10)
            .description("Top 10 endpoints by average latency"),
            style="table",
        )
        .build()
    )
    return created.id
# end_example:create_with_builder


# start_example:create_complex
async def create_complex_board(client: HoneycombClient, dataset: str = "my-dataset") -> str:
    """Create a comprehensive dashboard with all panel types and advanced features.

    This example demonstrates:
    - Inline QueryBuilder and SLOBuilder instances
    - Automatic creation of queries, SLOs, and board
    - Multiple query panels with different styles (graph, table, combo)
    - Inline SLO panel creation
    - Text panel for notes
    - Advanced visualization settings (hiding markers, UTC time)
    - Preset filters for dynamic filtering
    - Manual layout with precise positioning using PositionInput
    """
    from honeycomb import BoardBuilder, QueryBuilder, SLOBuilder
    from honeycomb.models.tool_inputs import PositionInput

    # Single fluent call with inline builders and manual positioning
    created = await client.boards.create_from_bundle_async(
        BoardBuilder("Production Monitoring Dashboard")
        .description("Complete service health monitoring with queries, SLOs, and notes")
        .manual_layout()
        .tag("team", "platform")
        .tag("environment", "production")
        # Preset filters for dynamic filtering
        .preset_filter("service", "Service")
        .preset_filter("environment", "Environment")
        # Top row: Request count (dataset-scoped, graph with advanced settings)
        .query(
            QueryBuilder("Request Count")
            .dataset(dataset)
            .last_24_hours()
            .count()
            .group_by("service")
            .description("Total requests by service over 24 hours"),
            position=PositionInput(x_coordinate=0, y_coordinate=0, width=9, height=6),
            style="graph",
            visualization={"hide_markers": True, "utc_xaxis": True},
        )
        # Top right: Inline SLO creation with new derived column
        .slo(
            SLOBuilder("API Availability")
            .dataset(dataset)
            .target_percentage(99.9)
            .sli(
                alias="board_sli_success",
                expression="IF(LT($status_code, 400), 1, 0)",
                description="Success rate: 1 if status < 400, 0 otherwise",
            )
            .description("API success rate SLO"),
            position=PositionInput(x_coordinate=9, y_coordinate=0, width=3, height=6),
        )
        # Middle left: Latency table (environment-wide)
        .query(
            QueryBuilder("Avg Latency")
            .environment_wide()
            .last_1_hour()
            .avg("duration_ms")
            .group_by("endpoint")
            .limit(10)
            .description("Top 10 endpoints by average latency"),
            position=PositionInput(x_coordinate=0, y_coordinate=6, width=6, height=5),
            style="table",
        )
        # Middle right: Error rate combo view (dataset-scoped)
        .query(
            QueryBuilder("Error Rate")
            .dataset(dataset)
            .last_2_hours()
            .count()
            .gte("status_code", 400)
            .group_by("status_code")
            .description("HTTP errors by status code"),
            position=PositionInput(x_coordinate=6, y_coordinate=6, width=6, height=5),
            style="combo",
        )
        # Bottom: Notes panel (full width)
        .text(
            "## Monitoring Guidelines\n\n- Watch for latency > 500ms\n- Error rate should stay < 1%\n- Check SLO during peak hours",
            position=PositionInput(x_coordinate=0, y_coordinate=11, width=12, height=3),
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
async def update_board(client: HoneycombClient, board_id: str) -> Board:
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


# start_example:create_with_views
async def create_board_with_views(client: HoneycombClient, dataset: str = "integration-test") -> str:
    """Create a board with multiple views for different perspectives."""
    from honeycomb import BoardBuilder, QueryBuilder

    created = await client.boards.create_from_bundle_async(
        BoardBuilder("Service Dashboard")
        .description("Multi-perspective service monitoring")
        .auto_layout()
        .query(
            QueryBuilder("Request Metrics")
            .dataset(dataset)
            .last_1_hour()
            .count()
            .group_by("service"),
            style="graph",
        )
        # View 1: Active services only
        .add_view("Active Services", [{"column": "status", "operation": "=", "value": "active"}])
        # View 2: Production environment
        .add_view("Production", [{"column": "environment", "operation": "=", "value": "production"}])
        # View 3: Errors (multi-filter)
        .add_view(
            "Errors",
            [
                {"column": "status_code", "operation": ">=", "value": 400},
                {"column": "environment", "operation": "=", "value": "production"},
            ],
        )
        .build()
    )
    return created.id
# end_example:create_with_views


# start_example:manage_views
async def manage_board_views(client: HoneycombClient, board_id: str) -> None:
    """List, create, get, update, and delete board views."""
    from honeycomb.models.boards import BoardViewCreate, BoardViewFilter
    from honeycomb.models.query_builder import FilterOp

    # List all views
    views = await client.boards.list_views_async(board_id)
    print(f"Found {len(views)} views")

    # Create a new view
    new_view = await client.boards.create_view_async(
        board_id,
        BoardViewCreate(
            name="Slow Requests",
            filters=[
                BoardViewFilter(column="duration_ms", operation=FilterOp.GREATER_THAN, value=1000)
            ],
        ),
    )

    # Get the view
    view = await client.boards.get_view_async(board_id, new_view.id)
    print(f"View: {view.name}")

    # Update the view
    await client.boards.update_view_async(
        board_id,
        new_view.id,
        BoardViewCreate(name="Very Slow Requests", filters=view.filters),
    )

    # Delete the view
    await client.boards.delete_view_async(board_id, new_view.id)
# end_example:manage_views


# start_example:export_with_views
async def export_and_import_board(client: HoneycombClient, board_id: str) -> str:
    """Export a board with views and import it."""
    import json

    # Export board with views
    data = await client.boards.export_with_views_async(board_id)

    # Data is portable (no IDs/timestamps)
    assert "id" not in data
    assert "created_at" not in data

    # Save to file
    json_str = json.dumps(data, indent=2)
    print(f"Exported: {json_str[:100]}...")

    return board_id  # Return for cleanup
# end_example:export_with_views


# TEST_ASSERTIONS
async def test_lifecycle(client: HoneycombClient, board_id: str, expected_name: str) -> None:
    """Verify the full lifecycle worked."""
    board = await client.boards.get_async(board_id)
    assert board.id == board_id
    assert board.name == expected_name
    assert board.type == "flexible"


# CLEANUP
async def cleanup(client: HoneycombClient, board_id: str, dataset: str = "my-dataset") -> None:
    """Clean up resources (called even on test failure)."""
    # Delete board
    try:
        if board_id:
            await client.boards.delete_async(board_id)
    except Exception:
        pass  # Already deleted or doesn't exist
