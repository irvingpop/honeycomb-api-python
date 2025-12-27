"""Boards resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.boards import Board, BoardCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient
    from ..models.board_builder import BoardBundle


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

    async def create_from_bundle_async(self, bundle: BoardBundle) -> Board:
        """Create board from BoardBundle with automatic query creation.

        Orchestrates:
        1. Create queries + annotations from QueryBuilder instances
        2. Assemble all panel configurations
        3. Create board with all panels

        Panels are added to the board in the order they appear in the bundle:
        - Auto-layout: Honeycomb arranges panels in this order
        - Manual-layout: Respects explicit positions

        Args:
            bundle: BoardBundle from BoardBuilder.build()

        Returns:
            Created Board object

        Example:
            >>> board = await client.boards.create_from_bundle_async(
            ...     BoardBuilder("Dashboard")
            ...         .auto_layout()
            ...         .query(
            ...             QueryBuilder()
            ...                 .dataset("api-logs")
            ...                 .last_1_hour()
            ...                 .count()
            ...                 .name("Request Count")
            ...         )
            ...         .build()
            ... )
        """

        panels = []

        # Create query panels from QueryBuilder instances
        for qb_panel in bundle.query_builder_panels:
            dataset = qb_panel.dataset_override or qb_panel.builder.get_dataset()
            query, annotation_id = await self._client.queries.create_with_annotation_async(
                dataset, qb_panel.builder
            )
            panels.append(
                self._build_query_panel_dict(
                    query.id,
                    annotation_id,
                    qb_panel.position,
                    qb_panel.style,
                    qb_panel.visualization,
                    dataset,
                )
            )

        # Add existing query panels
        for existing in bundle.existing_query_panels:
            panels.append(
                self._build_query_panel_dict(
                    existing.query_id,
                    existing.annotation_id,
                    existing.position,
                    existing.style,
                    existing.visualization,
                    existing.dataset,
                )
            )

        # Add SLO panels
        for slo in bundle.slo_panels:
            panels.append(self._build_slo_panel_dict(slo.slo_id, slo.position))

        # Add text panels
        for text in bundle.text_panels:
            panels.append(self._build_text_panel_dict(text.content, text.position))

        # Create board
        board_create = BoardCreate(
            name=bundle.board_name,
            description=bundle.board_description,
            type="flexible",
            panels=panels if panels else None,
            layout_generation=bundle.layout_generation,
            tags=bundle.tags,
            preset_filters=bundle.preset_filters,
        )

        return await self.create_async(board_create)

    def _build_query_panel_dict(
        self,
        query_id: str,
        annotation_id: str,
        position: tuple[int, int, int, int] | None,
        style: str,
        visualization: dict[str, Any] | None,
        dataset: str | None,
    ) -> dict[str, Any]:
        """Build query panel dictionary for API."""
        query_panel: dict[str, Any] = {
            "query_id": query_id,
            "query_annotation_id": annotation_id,
            "query_style": style,
        }
        # Only include dataset for environment-wide queries or explicit overrides
        # Dataset-scoped queries don't need dataset in panel (query itself knows)
        if dataset and dataset == "__all__":
            query_panel["dataset"] = dataset
        if visualization:
            query_panel["visualization_settings"] = visualization

        panel: dict[str, Any] = {
            "type": "query",
            "query_panel": query_panel,
        }
        if position:
            panel["position"] = {
                "x_coordinate": position[0],
                "y_coordinate": position[1],
                "width": position[2],
                "height": position[3],
            }
        return panel

    def _build_slo_panel_dict(
        self,
        slo_id: str,
        position: tuple[int, int, int, int] | None,
    ) -> dict[str, Any]:
        """Build SLO panel dictionary for API."""
        panel = {"type": "slo", "slo_panel": {"slo_id": slo_id}}
        if position:
            panel["position"] = {
                "x_coordinate": position[0],
                "y_coordinate": position[1],
                "width": position[2],
                "height": position[3],
            }
        return panel

    def _build_text_panel_dict(
        self,
        content: str,
        position: tuple[int, int, int, int] | None,
    ) -> dict[str, Any]:
        """Build text panel dictionary for API."""
        panel = {"type": "text", "text_panel": {"content": content}}
        if position:
            panel["position"] = {
                "x_coordinate": position[0],
                "y_coordinate": position[1],
                "width": position[2],
                "height": position[3],
            }
        return panel

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

    def create_from_bundle(self, bundle: BoardBundle) -> Board:
        """Create board from BoardBundle with automatic query creation (sync).

        Orchestrates:
        1. Create queries + annotations from QueryBuilder instances
        2. Assemble all panel configurations
        3. Create board with all panels

        Args:
            bundle: BoardBundle from BoardBuilder.build()

        Returns:
            Created Board object
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use create_from_bundle_async() for async mode, or pass sync=True to client"
            )
        import asyncio

        return asyncio.run(self.create_from_bundle_async(bundle))
