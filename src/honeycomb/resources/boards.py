"""Boards resource for Honeycomb API."""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

from ..models.boards import Board, BoardCreate, BoardView, BoardViewCreate
from ..models.tool_inputs import PositionInput
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

    def _build_view_path(self, board_id: str, view_id: str | None = None) -> str:
        """Build API path for board views."""
        base = f"/1/boards/{board_id}/views"
        if view_id:
            return f"{base}/{view_id}"
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
        """Create board from BoardBundle with automatic query and view creation.

        Orchestrates:
        1. Create queries + annotations from QueryBuilder instances
        2. Assemble all panel configurations
        3. Create board with all panels
        4. Create views for the board (if any)

        Panels are added to the board in the order they appear in the bundle:
        - Auto-layout: Honeycomb arranges panels in this order
        - Manual-layout: Respects explicit positions

        If view creation fails, a warning is issued but the board creation succeeds.
        Views can be created manually later using create_view_async().

        Args:
            bundle: BoardBundle from BoardBuilder.build()

        Returns:
            Created Board object

        Example:
            >>> board = await client.boards.create_from_bundle_async(
            ...     BoardBuilder("Dashboard")
            ...         .auto_layout()
            ...         .query(
            ...             QueryBuilder("Request Count")
            ...                 .dataset("api-logs")
            ...                 .last_1_hour()
            ...                 .count()
            ...         )
            ...         .add_view("Active Only", [{"column": "status", "operation": "=", "value": "active"}])
            ...         .build()
            ... )
        """

        panels = []

        # Create query panels from QueryBuilder instances
        for qb_panel in bundle.query_builder_panels:
            # Apply dataset override if specified
            if qb_panel.dataset_override:
                # Temporarily override the dataset on the builder
                original_dataset = qb_panel.builder.get_dataset()
                qb_panel.builder.dataset(qb_panel.dataset_override)
                query, annotation_id = await self._client.queries.create_with_annotation_async(
                    qb_panel.builder
                )
                # Restore original dataset
                qb_panel.builder.dataset(original_dataset)
            else:
                query, annotation_id = await self._client.queries.create_with_annotation_async(
                    qb_panel.builder
                )
            panels.append(
                self._build_query_panel_dict(
                    query.id,
                    annotation_id,
                    qb_panel.position,
                    qb_panel.style,
                    qb_panel.visualization,
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
                )
            )

        # Create SLOs from SLOBuilder instances
        for slo_panel in bundle.slo_builder_panels:
            # Create SLO using existing orchestration
            slo_dict = await self._client.slos.create_from_bundle_async(slo_panel.builder.build())
            # Get first SLO (should only be one dataset for board usage)
            slo = next(iter(slo_dict.values()))
            panels.append(self._build_slo_panel_dict(slo.id, slo_panel.position))

        # Add existing SLO panels
        for slo_existing in bundle.existing_slo_panels:
            panels.append(self._build_slo_panel_dict(slo_existing.slo_id, slo_existing.position))

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

        board = await self.create_async(board_create)

        # Create views after board creation
        if bundle.views:
            import warnings

            for view_create in bundle.views:
                try:
                    await self.create_view_async(board.id, view_create)
                except Exception as e:
                    # Log but don't fail - board was created successfully
                    # User can retry view creation manually
                    warnings.warn(
                        f"Failed to create view '{view_create.name}' for board '{board.id}': {e}",
                        UserWarning,
                        stacklevel=2,
                    )

        return board

    def _build_query_panel_dict(
        self,
        query_id: str,
        annotation_id: str,
        position: PositionInput | None,
        style: str,
        visualization: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Build query panel dictionary for API."""
        query_panel: dict[str, Any] = {
            "query_id": query_id,
            "query_annotation_id": annotation_id,
            "query_style": style,
        }
        # Dataset is not included - query already knows its scope
        if visualization:
            query_panel["visualization_settings"] = visualization

        panel: dict[str, Any] = {
            "type": "query",
            "query_panel": query_panel,
        }
        if position:
            panel["position"] = {
                "x_coordinate": position.x_coordinate,
                "y_coordinate": position.y_coordinate,
                "width": position.width,
                "height": position.height,
            }
        return panel

    def _build_slo_panel_dict(
        self,
        slo_id: str,
        position: PositionInput | None,
    ) -> dict[str, Any]:
        """Build SLO panel dictionary for API."""
        panel = {"type": "slo", "slo_panel": {"slo_id": slo_id}}
        if position:
            panel["position"] = {
                "x_coordinate": position.x_coordinate,
                "y_coordinate": position.y_coordinate,
                "width": position.width,
                "height": position.height,
            }
        return panel

    def _build_text_panel_dict(
        self,
        content: str,
        position: PositionInput | None,
    ) -> dict[str, Any]:
        """Build text panel dictionary for API."""
        panel = {"type": "text", "text_panel": {"content": content}}
        if position:
            panel["position"] = {
                "x_coordinate": position.x_coordinate,
                "y_coordinate": position.y_coordinate,
                "width": position.width,
                "height": position.height,
            }
        return panel

    # -------------------------------------------------------------------------
    # Board View Methods - Async
    # -------------------------------------------------------------------------

    async def list_views_async(self, board_id: str) -> list[BoardView]:
        """List all views for a board (async).

        Args:
            board_id: Board ID.

        Returns:
            List of BoardView objects (max 50 per board).
        """
        data = await self._get_async(self._build_view_path(board_id))
        return self._parse_model_list(BoardView, data)

    async def get_view_async(self, board_id: str, view_id: str) -> BoardView:
        """Get a specific board view (async).

        Args:
            board_id: Board ID.
            view_id: View ID.

        Returns:
            BoardView object.
        """
        data = await self._get_async(self._build_view_path(board_id, view_id))
        return self._parse_model(BoardView, data)

    async def create_view_async(self, board_id: str, view: BoardViewCreate) -> BoardView:
        """Create a new board view (async).

        Args:
            board_id: Board ID.
            view: View configuration.

        Returns:
            Created BoardView object.

        Note:
            Each board is limited to 50 views maximum.
        """
        data = await self._post_async(
            self._build_view_path(board_id),
            json=view.model_dump_for_api(),
        )
        return self._parse_model(BoardView, data)

    async def update_view_async(
        self,
        board_id: str,
        view_id: str,
        view: BoardViewCreate,
    ) -> BoardView:
        """Update an existing board view (async).

        Args:
            board_id: Board ID.
            view_id: View ID.
            view: Updated view configuration.

        Returns:
            Updated BoardView object.
        """
        data = await self._put_async(
            self._build_view_path(board_id, view_id),
            json=view.model_dump_for_api(),
        )
        return self._parse_model(BoardView, data)

    async def delete_view_async(self, board_id: str, view_id: str) -> None:
        """Delete a board view (async).

        Args:
            board_id: Board ID.
            view_id: View ID.
        """
        await self._delete_async(self._build_view_path(board_id, view_id))

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

    # -------------------------------------------------------------------------
    # Board View Methods - Sync
    # -------------------------------------------------------------------------

    def list_views(self, board_id: str) -> builtins.list[BoardView]:
        """List all views for a board.

        Args:
            board_id: Board ID.

        Returns:
            List of BoardView objects (max 50 per board).
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_views_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_view_path(board_id))
        return self._parse_model_list(BoardView, data)

    def get_view(self, board_id: str, view_id: str) -> BoardView:
        """Get a specific board view.

        Args:
            board_id: Board ID.
            view_id: View ID.

        Returns:
            BoardView object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_view_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_view_path(board_id, view_id))
        return self._parse_model(BoardView, data)

    def create_view(self, board_id: str, view: BoardViewCreate) -> BoardView:
        """Create a new board view.

        Args:
            board_id: Board ID.
            view: View configuration.

        Returns:
            Created BoardView object.

        Note:
            Each board is limited to 50 views maximum.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use create_view_async() for async mode, or pass sync=True to client"
            )
        data = self._post_sync(
            self._build_view_path(board_id),
            json=view.model_dump_for_api(),
        )
        return self._parse_model(BoardView, data)

    def update_view(self, board_id: str, view_id: str, view: BoardViewCreate) -> BoardView:
        """Update an existing board view.

        Args:
            board_id: Board ID.
            view_id: View ID.
            view: Updated view configuration.

        Returns:
            Updated BoardView object.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use update_view_async() for async mode, or pass sync=True to client"
            )
        data = self._put_sync(
            self._build_view_path(board_id, view_id),
            json=view.model_dump_for_api(),
        )
        return self._parse_model(BoardView, data)

    def delete_view(self, board_id: str, view_id: str) -> None:
        """Delete a board view.

        Args:
            board_id: Board ID.
            view_id: View ID.
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use delete_view_async() for async mode, or pass sync=True to client"
            )
        self._delete_sync(self._build_view_path(board_id, view_id))

    # -------------------------------------------------------------------------
    # Export/Import with Views
    # -------------------------------------------------------------------------

    async def export_with_views_async(self, board_id: str) -> dict[str, Any]:
        """Export board with views included (async).

        Returns a dictionary suitable for JSON serialization and import,
        including all board data and associated views.

        Args:
            board_id: Board ID

        Returns:
            Dict with board data and views (IDs stripped for portability)

        Example:
            >>> data = await client.boards.export_with_views_async("board-123")
            >>> with open("board.json", "w") as f:
            ...     json.dump(data, f, indent=2)
        """
        board = await self.get_async(board_id)
        views = await self.list_views_async(board_id)

        # Export board without IDs and timestamps for portability
        data = board.model_dump(exclude={"id", "created_at", "updated_at"}, mode="json")

        # Add views (without IDs)
        if views:
            data["views"] = [v.model_dump(exclude={"id"}, mode="json") for v in views]

        return data

    def export_with_views(self, board_id: str) -> dict[str, Any]:
        """Export board with views included (sync).

        Returns a dictionary suitable for JSON serialization and import,
        including all board data and associated views.

        Args:
            board_id: Board ID

        Returns:
            Dict with board data and views (IDs stripped for portability)
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use export_with_views_async() for async mode, or pass sync=True to client"
            )
        import asyncio

        return asyncio.run(self.export_with_views_async(board_id))
