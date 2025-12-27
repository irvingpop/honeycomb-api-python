"""Query Annotations resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.query_annotations import QueryAnnotation, QueryAnnotationCreate
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class QueryAnnotationsResource(BaseResource):
    """Resource for managing query annotations.

    Query Annotations add name and description metadata to queries for
    collaboration and documentation. They are required for adding query
    panels to boards.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     # Create annotation for a saved query
        ...     annotation = await client.query_annotations.create_async(
        ...         dataset="my-dataset",
        ...         annotation=QueryAnnotationCreate(
        ...             name="Error Rate Analysis",
        ...             query_id="abc123",
        ...             description="Tracks HTTP 5xx errors by service"
        ...         )
        ...     )
        ...     # Use annotation.id for board panels
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, annotation_id: str | None = None) -> str:
        """Build API path for query annotations."""
        base = f"/1/query_annotations/{dataset}"
        if annotation_id:
            return f"{base}/{annotation_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def list_async(
        self, dataset: str, *, include_board_annotations: bool = False
    ) -> list[QueryAnnotation]:
        """List all query annotations for a dataset (async).

        Args:
            dataset: Dataset slug.
            include_board_annotations: Include auto-created annotations from boards.

        Returns:
            List of QueryAnnotation objects.
        """
        params = {"include_board_annotations": str(include_board_annotations).lower()}
        data = await self._get_async(self._build_path(dataset), params=params)
        return self._parse_model_list(QueryAnnotation, data)

    async def get_async(self, dataset: str, annotation_id: str) -> QueryAnnotation:
        """Get a specific query annotation (async).

        Args:
            dataset: Dataset slug.
            annotation_id: Query annotation ID.

        Returns:
            QueryAnnotation object.
        """
        data = await self._get_async(self._build_path(dataset, annotation_id))
        return self._parse_model(QueryAnnotation, data)

    async def create_async(
        self, dataset: str, annotation: QueryAnnotationCreate
    ) -> QueryAnnotation:
        """Create a new query annotation (async).

        Args:
            dataset: Dataset slug.
            annotation: Query annotation configuration.

        Returns:
            Created QueryAnnotation object.
        """
        data = await self._post_async(
            self._build_path(dataset), json=annotation.model_dump_for_api()
        )
        return self._parse_model(QueryAnnotation, data)

    async def update_async(
        self, dataset: str, annotation_id: str, annotation: QueryAnnotationCreate
    ) -> QueryAnnotation:
        """Update an existing query annotation (async).

        Note: The query_id field cannot be changed after creation.

        Args:
            dataset: Dataset slug.
            annotation_id: Query annotation ID.
            annotation: Updated query annotation configuration.

        Returns:
            Updated QueryAnnotation object.
        """
        data = await self._put_async(
            self._build_path(dataset, annotation_id), json=annotation.model_dump_for_api()
        )
        return self._parse_model(QueryAnnotation, data)

    async def delete_async(self, dataset: str, annotation_id: str) -> None:
        """Delete a query annotation (async).

        Args:
            dataset: Dataset slug.
            annotation_id: Query annotation ID.
        """
        await self._delete_async(self._build_path(dataset, annotation_id))

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def list(
        self, dataset: str, *, include_board_annotations: bool = False
    ) -> list[QueryAnnotation]:
        """List all query annotations for a dataset.

        Args:
            dataset: Dataset slug.
            include_board_annotations: Include auto-created annotations from boards.

        Returns:
            List of QueryAnnotation objects.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use list_async() for async mode, or pass sync=True to client")
        params = {"include_board_annotations": str(include_board_annotations).lower()}
        data = self._get_sync(self._build_path(dataset), params=params)
        return self._parse_model_list(QueryAnnotation, data)

    def get(self, dataset: str, annotation_id: str) -> QueryAnnotation:
        """Get a specific query annotation.

        Args:
            dataset: Dataset slug.
            annotation_id: Query annotation ID.

        Returns:
            QueryAnnotation object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, annotation_id))
        return self._parse_model(QueryAnnotation, data)

    def create(self, dataset: str, annotation: QueryAnnotationCreate) -> QueryAnnotation:
        """Create a new query annotation.

        Args:
            dataset: Dataset slug.
            annotation: Query annotation configuration.

        Returns:
            Created QueryAnnotation object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(dataset), json=annotation.model_dump_for_api())
        return self._parse_model(QueryAnnotation, data)

    def update(
        self, dataset: str, annotation_id: str, annotation: QueryAnnotationCreate
    ) -> QueryAnnotation:
        """Update an existing query annotation.

        Note: The query_id field cannot be changed after creation.

        Args:
            dataset: Dataset slug.
            annotation_id: Query annotation ID.
            annotation: Updated query annotation configuration.

        Returns:
            Updated QueryAnnotation object.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use update_async() for async mode, or pass sync=True to client")
        data = self._put_sync(
            self._build_path(dataset, annotation_id), json=annotation.model_dump_for_api()
        )
        return self._parse_model(QueryAnnotation, data)

    def delete(self, dataset: str, annotation_id: str) -> None:
        """Delete a query annotation.

        Args:
            dataset: Dataset slug.
            annotation_id: Query annotation ID.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use delete_async() for async mode, or pass sync=True to client")
        self._delete_sync(self._build_path(dataset, annotation_id))
