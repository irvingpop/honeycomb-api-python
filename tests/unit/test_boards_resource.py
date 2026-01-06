"""Tests for boards resource (board views CRUD operations)."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from honeycomb.models.boards import BoardViewCreate, BoardViewFilter
from honeycomb.models.query_builder import FilterOp


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
            return_value=Response(200, json={"id": "view-new", "name": "New View", "filters": []})
        )

        async with client:
            view_create = BoardViewCreate(
                name="New View",
                filters=[
                    BoardViewFilter(column="status", operation=FilterOp.EQUALS, value="active")
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
            return_value=Response(200, json={"id": "view-1", "name": "Updated View", "filters": []})
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
            return_value=Response(200, json={"id": "view-new", "name": "New View", "filters": []})
        )

        with client:
            view_create = BoardViewCreate(name="New View", filters=[])
            view = client.boards.create_view(board_id="board-1", view=view_create)
            assert view.id == "view-new"
