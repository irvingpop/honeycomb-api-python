"""Queries resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.queries import Query, QuerySpec
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient
    from ..models.query_builder import QueryBuilder


class QueriesResource(BaseResource):
    """Resource for managing Honeycomb queries.

    Queries define how to analyze your data. They can be used with
    triggers, SLOs, or run directly to get results.

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     query = await client.queries.create_async(
        ...         dataset="my-dataset",
        ...         spec=QuerySpec(time_range=3600, calculations=[...])
        ...     )
        ...     query_obj = await client.queries.get_async(
        ...         dataset="my-dataset",
        ...         query_id=query.id
        ...     )

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     query = client.queries.create(dataset="my-dataset", spec=...)
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, query_id: str | None = None) -> str:
        """Build API path for queries."""
        base = f"/1/queries/{dataset}"
        if query_id:
            return f"{base}/{query_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def create_async(self, dataset: str, spec: QuerySpec) -> Query:
        """Create a new query (async).

        Args:
            dataset: The dataset slug.
            spec: Query specification.

        Returns:
            Created Query object.

        Raises:
            HoneycombValidationError: If the query spec is invalid.
            HoneycombNotFoundError: If the dataset doesn't exist.
        """
        data = await self._post_async(self._build_path(dataset), json=spec.model_dump_for_api())
        return self._parse_model(Query, data)

    async def get_async(self, dataset: str, query_id: str) -> Query:
        """Get a specific query (async).

        Args:
            dataset: The dataset slug.
            query_id: Query ID.

        Returns:
            Query object.

        Raises:
            HoneycombNotFoundError: If the query doesn't exist.
        """
        data = await self._get_async(self._build_path(dataset, query_id))
        return self._parse_model(Query, data)

    async def create_with_annotation_async(
        self,
        dataset: str,
        builder: QueryBuilder,
    ) -> tuple[Query, str]:
        """Create a query and annotation together from QueryBuilder (async).

        This is a convenience method for QueryBuilder instances that have
        query names (.name() was called). It creates both the query and
        its annotation in one call.

        Args:
            dataset: The dataset slug.
            builder: QueryBuilder with .name() called

        Returns:
            Tuple of (Query object, annotation_id)

        Raises:
            ValueError: If the QueryBuilder doesn't have a name

        Example:
            >>> query_builder = (
            ...     QueryBuilder()
            ...     .last_1_hour()
            ...     .count()
            ...     .name("Error Count")
            ...     .description("Tracks errors over time")
            ... )
            >>> query, annotation_id = await client.queries.create_with_annotation_async(
            ...     "my-dataset", query_builder
            ... )
            >>> # Use query.id and annotation_id in BoardBuilder
        """
        from ..models.query_annotations import QueryAnnotationCreate

        # Check if this has a name
        if not hasattr(builder, "has_name") or not builder.has_name():
            raise ValueError(
                "create_with_annotation requires a QueryBuilder with .name() called. "
                "Use create_async() for plain QuerySpec objects."
            )

        # Create the query first
        query = await self.create_async(dataset, builder.build())

        # Create the annotation
        annotation = QueryAnnotationCreate(
            name=builder.get_name() or "",
            query_id=query.id,
            description=builder.get_description(),
        )
        created_annotation = await self._client.query_annotations.create_async(dataset, annotation)

        return (query, created_annotation.id)

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def create(self, dataset: str, spec: QuerySpec) -> Query:
        """Create a new query.

        Args:
            dataset: The dataset slug.
            spec: Query specification.

        Returns:
            Created Query object.

        Raises:
            HoneycombValidationError: If the query spec is invalid.
            HoneycombNotFoundError: If the dataset doesn't exist.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")
        data = self._post_sync(self._build_path(dataset), json=spec.model_dump_for_api())
        return self._parse_model(Query, data)

    def get(self, dataset: str, query_id: str) -> Query:
        """Get a specific query.

        Args:
            dataset: The dataset slug.
            query_id: Query ID.

        Returns:
            Query object.

        Raises:
            HoneycombNotFoundError: If the query doesn't exist.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, query_id))
        return self._parse_model(Query, data)
