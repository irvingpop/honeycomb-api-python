"""Boards resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.boards import Board, BoardCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class BoardsResource(BaseResource):
    """Resource for managing Honeycomb boards.

    Boards are dashboards that display visualizations of your data.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     boards = await client.boards.list()
        ...     board = await client.boards.get(board_id="abc123")

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     boards = client.boards.list()
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, board_id: str | None = None) -> str:
        """Build API path for boards."""
        base = "/1/boards"
        if board_id:
            return f"{base}/{board_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(self) -> list[Board]:
        """List all boards (async).

        Returns:
            List of Board objects.
        """
        data = await self._get_async(self._build_path())
        return self._parse_model_list(Board, data)

    async def get_async(self, board_id: str) -> Board:
        """Get a specific board (async).

        Args:
            board_id: Board ID.

        Returns:
            Board object.
        """
        data = await self._get_async(self._build_path(board_id))
        return self._parse_model(Board, data)

    async def create_async(self, board: BoardCreate) -> Board:
        """Create a new board (async).

        Args:
            board: Board configuration.

        Returns:
            Created Board object.
        """
        data = await self._post_async(self._build_path(), json=board.model_dump_for_api())
        return self._parse_model(Board, data)

    async def update_async(self, board_id: str, board: BoardCreate) -> Board:
        """Update an existing board (async).

        Args:
            board_id: Board ID.
            board: Updated board configuration.

        Returns:
            Updated Board object.
        """
        data = await self._put_async(self._build_path(board_id), json=board.model_dump_for_api())
        return self._parse_model(Board, data)

    async def delete_async(self, board_id: str) -> None:
        """Delete a board (async).

        Args:
            board_id: Board ID.
        """
        await self._delete_async(self._build_path(board_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(self) -> list[Board]:
        """List all boards.

        Returns:
            List of Board objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path())
        return self._parse_model_list(Board, data)

    def get(self, board_id: str) -> Board:
        """Get a specific board.

        Args:
            board_id: Board ID.

        Returns:
            Board object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(board_id))
        return self._parse_model(Board, data)

    def create(self, board: BoardCreate) -> Board:
        """Create a new board.

        Args:
            board: Board configuration.

        Returns:
            Created Board object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(), json=board.model_dump_for_api())
        return self._parse_model(Board, data)

    def update(self, board_id: str, board: BoardCreate) -> Board:
        """Update an existing board.

        Args:
            board_id: Board ID.
            board: Updated board configuration.

        Returns:
            Updated Board object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(self._build_path(board_id), json=board.model_dump_for_api())
        return self._parse_model(Board, data)

    def delete(self, board_id: str) -> None:
        """Delete a board.

        Args:
            board_id: Board ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(board_id))
