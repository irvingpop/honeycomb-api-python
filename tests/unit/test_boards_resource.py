"""Tests for boards resource (board views CRUD operations and orchestration)."""

import pytest
import respx
from httpx import Response

from honeycomb import BoardBuilder, HoneycombClient
from honeycomb.models.boards import BoardViewCreate, BoardViewFilter, BoardViewFilterOperation
from tests.factories import (
    BoardCreateFactory,
    BoardFactory,
    BoardViewFactory,
    mock_list_response,
    mock_response,
)


@pytest.mark.asyncio
class TestBoardOrchestration:
    """Tests for create_from_bundle_async orchestration."""

    @respx.mock
    async def test_panel_ordering_preserved_in_execution(self, respx_mock):
        """Test that panel order is preserved through full execution path.

        Verifies: BoardBuilder → BoardBundle → create_from_bundle_async → API panels
        """
        client = HoneycombClient(api_key="test-key")

        # Capture the request to verify panel order
        board_request = None

        def capture_board_request(request):
            nonlocal board_request
            board_request = request
            # Return a valid board response
            return Response(
                200,
                json={
                    "id": "board-123",
                    "name": "Test Board",
                    "type": "flexible",
                    "panels": [],  # Don't care about response panels, we check request
                    "layout_generation": "auto",
                },
            )

        respx_mock.post("https://api.honeycomb.io/1/boards").mock(side_effect=capture_board_request)

        # Build board with mixed panel types in specific order
        bundle = (
            BoardBuilder("Test Board")
            .auto_layout()
            .query("query-1", "annot-1", style="graph")  # Query panel first
            .text("## Section 1")  # Text panel second
            .slo("slo-1")  # SLO panel third
            .query("query-2", "annot-2", style="table")  # Query panel fourth
            .text("## Section 2")  # Text panel fifth
            .build()
        )

        async with client:
            board = await client.boards.create_from_bundle_async(bundle)

            # Verify board was created
            assert board.id == "board-123"

            # Parse the request that was sent
            import json

            request_body = json.loads(board_request.content)
            panels = request_body["panels"]

            # Verify panels are in exact insertion order
            assert len(panels) == 5, f"Expected 5 panels, got {len(panels)}"
            assert panels[0]["type"] == "query", f"Panel 0 should be query, got {panels[0]['type']}"
            assert panels[1]["type"] == "text", f"Panel 1 should be text, got {panels[1]['type']}"
            assert panels[2]["type"] == "slo", f"Panel 2 should be slo, got {panels[2]['type']}"
            assert panels[3]["type"] == "query", f"Panel 3 should be query, got {panels[3]['type']}"
            assert panels[4]["type"] == "text", f"Panel 4 should be text, got {panels[4]['type']}"

            # Verify query panel IDs are correct (order matters!)
            assert panels[0]["query_panel"]["query_id"] == "query-1", (
                "First query panel should be query-1"
            )
            assert panels[3]["query_panel"]["query_id"] == "query-2", (
                "Fourth query panel should be query-2"
            )

            # Verify text content is in correct order
            assert "Section 1" in panels[1]["text_panel"]["content"], (
                "Second panel should be Section 1"
            )
            assert "Section 2" in panels[4]["text_panel"]["content"], (
                "Fifth panel should be Section 2"
            )

            # Verify SLO ID is correct
            assert panels[2]["slo_panel"]["slo_id"] == "slo-1", "Third panel should be slo-1"


@pytest.mark.asyncio
class TestBoardViewsResourceAsync:
    """Tests for board views async methods."""

    @respx.mock
    async def test_list_views_async(self, respx_mock):
        """Test listing board views."""
        client = HoneycombClient(api_key="test-key")

        respx_mock.get("https://api.honeycomb.io/1/boards/board-1/views").mock(
            return_value=Response(
                200,
                json=[
                    {"id": "view-1", "name": "View 1", "filters": []},
                    {"id": "view-2", "name": "View 2", "filters": []},
                ],
            )
        )

        async with client:
            views = await client.boards.list_views_async(board_id="board-1")
            assert len(views) == 2
            assert views[0].id == "view-1"
            assert views[0].name == "View 1"
            assert views[1].id == "view-2"
            assert views[1].name == "View 2"

    @respx.mock
    async def test_get_view_async(self, respx_mock):
        """Test getting a specific view."""
        client = HoneycombClient(api_key="test-key")

        respx_mock.get("https://api.honeycomb.io/1/boards/board-1/views/view-1").mock(
            return_value=Response(
                200,
                json={
                    "id": "view-1",
                    "name": "My View",
                    "filters": [{"column": "status", "operation": "=", "value": "active"}],
                },
            )
        )

        async with client:
            view = await client.boards.get_view_async(board_id="board-1", view_id="view-1")
            assert view.id == "view-1"
            assert view.name == "My View"
            assert len(view.filters) == 1
            assert view.filters[0].column == "status"

    @respx.mock
    async def test_create_view_async(self, respx_mock):
        """Test creating a view."""
        client = HoneycombClient(api_key="test-key")

        respx_mock.post("https://api.honeycomb.io/1/boards/board-1/views").mock(
            return_value=Response(
                200, json=mock_response(BoardViewFactory, id="view-new", name="New View")
            )
        )

        async with client:
            view_create = BoardViewCreate(
                name="New View",
                filters=[
                    BoardViewFilter(
                        column="status", operation=BoardViewFilterOperation.EQUALS, value="active"
                    )
                ],
            )
            view = await client.boards.create_view_async(board_id="board-1", view=view_create)
            assert view.id == "view-new"
            assert view.name == "New View"

    @respx.mock
    async def test_update_view_async(self, respx_mock):
        """Test updating a view."""
        client = HoneycombClient(api_key="test-key")

        respx_mock.put("https://api.honeycomb.io/1/boards/board-1/views/view-1").mock(
            return_value=Response(
                200, json=mock_response(BoardViewFactory, id="view-1", name="Updated View")
            )
        )

        async with client:
            view_update = BoardViewCreate(name="Updated View", filters=[])
            view = await client.boards.update_view_async(
                board_id="board-1", view_id="view-1", view=view_update
            )
            assert view.id == "view-1"
            assert view.name == "Updated View"

    @respx.mock
    async def test_delete_view_async(self, respx_mock):
        """Test deleting a view."""
        client = HoneycombClient(api_key="test-key")

        respx_mock.delete("https://api.honeycomb.io/1/boards/board-1/views/view-1").mock(
            return_value=Response(204)
        )

        async with client:
            await client.boards.delete_view_async(board_id="board-1", view_id="view-1")
            # No exception = success

    @respx.mock
    async def test_export_with_views_async(self, respx_mock):
        """Test exporting board with views."""
        client = HoneycombClient(api_key="test-key")

        # Mock board fetch
        respx_mock.get("https://api.honeycomb.io/1/boards/board-1").mock(
            return_value=Response(
                200,
                json={
                    "id": "board-1",
                    "name": "Test Board",
                    "type": "flexible",
                    "panels": [],
                    "layout_generation": "auto",
                },
            )
        )

        # Mock views fetch
        respx_mock.get("https://api.honeycomb.io/1/boards/board-1/views").mock(
            return_value=Response(
                200,
                json=[
                    {"id": "view-1", "name": "Active View", "filters": []},
                    {"id": "view-2", "name": "Error View", "filters": []},
                ],
            )
        )

        async with client:
            data = await client.boards.export_with_views_async(board_id="board-1")

            assert data["name"] == "Test Board"
            assert "id" not in data  # IDs should be stripped
            assert "views" in data
            assert len(data["views"]) == 2
            assert data["views"][0]["name"] == "Active View"
            assert "id" not in data["views"][0]  # View IDs should be stripped


class TestBoardViewsResourceSync:
    """Tests for board views sync methods."""

    @respx.mock
    def test_list_views_sync(self, respx_mock):
        """Test listing board views (sync)."""
        client = HoneycombClient(api_key="test-key", sync=True)

        respx_mock.get("https://api.honeycomb.io/1/boards/board-1/views").mock(
            return_value=Response(200, json=[{"id": "view-1", "name": "View 1", "filters": []}])
        )

        with client:
            views = client.boards.list_views(board_id="board-1")
            assert len(views) == 1
            assert views[0].id == "view-1"

    @respx.mock
    def test_create_view_sync(self, respx_mock):
        """Test creating a view (sync)."""
        client = HoneycombClient(api_key="test-key", sync=True)

        respx_mock.post("https://api.honeycomb.io/1/boards/board-1/views").mock(
            return_value=Response(
                200, json=mock_response(BoardViewFactory, id="view-new", name="New View")
            )
        )

        with client:
            view_create = BoardViewCreate(name="New View", filters=[])
            view = client.boards.create_view(board_id="board-1", view=view_create)
            assert view.id == "view-new"


# =============================================================================
# Core Board CRUD Tests (added for Phase 4)
# =============================================================================


@pytest.mark.asyncio
@respx.mock
async def test_list_boards_async():
    """Test listing boards (async)."""
    respx.get("https://api.honeycomb.io/1/boards").mock(
        return_value=Response(200, json=mock_list_response(BoardFactory, count=3))
    )

    async with HoneycombClient(api_key="test-key") as client:
        boards = await client.boards.list_async()
        assert len(boards) == 3


@pytest.mark.asyncio
@respx.mock
async def test_list_boards_empty_async():
    """Test listing boards returns empty list (async)."""
    respx.get("https://api.honeycomb.io/1/boards").mock(return_value=Response(200, json=[]))

    async with HoneycombClient(api_key="test-key") as client:
        boards = await client.boards.list_async()
        assert len(boards) == 0


@pytest.mark.asyncio
@respx.mock
async def test_get_board_async():
    """Test getting a specific board (async)."""
    respx.get("https://api.honeycomb.io/1/boards/board-123").mock(
        return_value=Response(
            200, json=mock_response(BoardFactory, id="board-123", name="Test Board")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        board = await client.boards.get_async(board_id="board-123")
        assert board.id == "board-123"
        assert board.name == "Test Board"


@pytest.mark.asyncio
@respx.mock
async def test_create_board_async():
    """Test creating a board (async)."""
    respx.post("https://api.honeycomb.io/1/boards").mock(
        return_value=Response(
            201, json=mock_response(BoardFactory, id="new-board", name="New Board")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = BoardCreateFactory.build(name="New Board")
        board = await client.boards.create_async(board=request)
        assert board.id == "new-board"
        assert board.name == "New Board"


@pytest.mark.asyncio
@respx.mock
async def test_update_board_async():
    """Test updating a board (async)."""
    respx.put("https://api.honeycomb.io/1/boards/board-123").mock(
        return_value=Response(
            200, json=mock_response(BoardFactory, id="board-123", name="Updated Board")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = BoardCreateFactory.build(name="Updated Board")
        board = await client.boards.update_async(board_id="board-123", board=request)
        assert board.id == "board-123"
        assert board.name == "Updated Board"


@pytest.mark.asyncio
@respx.mock
async def test_delete_board_async():
    """Test deleting a board (async)."""
    respx.delete("https://api.honeycomb.io/1/boards/board-123").mock(return_value=Response(204))

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.boards.delete_async(board_id="board-123")


# Sync versions


@respx.mock
def test_list_boards_sync():
    """Test listing boards (sync)."""
    respx.get("https://api.honeycomb.io/1/boards").mock(
        return_value=Response(200, json=mock_list_response(BoardFactory, count=2))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        boards = client.boards.list()
        assert len(boards) == 2


@respx.mock
def test_list_boards_empty_sync():
    """Test listing boards returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/1/boards").mock(return_value=Response(200, json=[]))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        boards = client.boards.list()
        assert len(boards) == 0


@respx.mock
def test_get_board_sync():
    """Test getting a specific board (sync)."""
    respx.get("https://api.honeycomb.io/1/boards/board-123").mock(
        return_value=Response(200, json=mock_response(BoardFactory, id="board-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        board = client.boards.get(board_id="board-123")
        assert board.id == "board-123"


@respx.mock
def test_create_board_sync():
    """Test creating a board (sync)."""
    respx.post("https://api.honeycomb.io/1/boards").mock(
        return_value=Response(201, json=mock_response(BoardFactory, id="new-board"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = BoardCreateFactory.build(name="New Board")
        board = client.boards.create(board=request)
        assert board.id == "new-board"


@respx.mock
def test_update_board_sync():
    """Test updating a board (sync)."""
    respx.put("https://api.honeycomb.io/1/boards/board-123").mock(
        return_value=Response(200, json=mock_response(BoardFactory, id="board-123"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = BoardCreateFactory.build(name="Updated")
        board = client.boards.update(board_id="board-123", board=request)
        assert board.id == "board-123"


@respx.mock
def test_delete_board_sync():
    """Test deleting a board (sync)."""
    respx.delete("https://api.honeycomb.io/1/boards/board-123").mock(return_value=Response(204))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.boards.delete(board_id="board-123")


def test_sync_board_methods_require_sync_mode():
    """Test that sync board methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.boards.list()

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.boards.get(board_id="board-123")

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = BoardCreateFactory.build()
        client.boards.create(board=request)

    with pytest.raises(RuntimeError, match="Use update_async"):
        request = BoardCreateFactory.build()
        client.boards.update(board_id="board-123", board=request)

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.boards.delete(board_id="board-123")
