"""Queries resource for Honeycomb API."""

from __future__ import annotations

from typing import TYPE_CHECKING, overload

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
        ...         QueryBuilder()
        ...             .dataset("my-dataset")
        ...             .last_1_hour()
        ...             .count()
        ...     )
        ...     query_obj = await client.queries.get_async(
        ...         dataset="my-dataset",
        ...         query_id=query.id
        ...     )

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     query = client.queries.create(
        ...         QueryBuilder().dataset("my-dataset").count()
        ...     )
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

    @overload
    async def create_async(self, spec: QueryBuilder) -> Query: ...

    @overload
    async def create_async(self, spec: QuerySpec, *, dataset: str) -> Query: ...

    async def create_async(
        self, spec: QuerySpec | QueryBuilder, *, dataset: str | None = None
    ) -> Query:
        """Create a new query (async).

        Args:
            spec: Query specification (QueryBuilder or QuerySpec).
            dataset: Dataset slug. Required for QuerySpec, extracted from QueryBuilder.

        Returns:
            Created Query object.

        Raises:
            HoneycombValidationError: If the query spec is invalid.
            HoneycombNotFoundError: If the dataset doesn't exist.
            ValueError: If dataset parameter is misused.

        Example (QueryBuilder - recommended):
            >>> query = await client.queries.create_async(
            ...     QueryBuilder()
            ...         .dataset("my-dataset")
            ...         .last_1_hour()
            ...         .count()
            ... )

        Example (QuerySpec - advanced):
            >>> query = await client.queries.create_async(
            ...     QuerySpec(time_range=3600, calculations=[{"op": "COUNT"}]),
            ...     dataset="my-dataset"
            ... )
        """
        from ..models.query_builder import QueryBuilder

        # Extract dataset based on spec type
        if isinstance(spec, QueryBuilder):
            if dataset is not None:
                raise ValueError(
                    "dataset parameter not allowed with QueryBuilder. "
                    "Use .dataset() on the builder instead."
                )
            dataset = spec.get_dataset()
            query_spec = spec.build()
        else:
            if dataset is None:
                raise ValueError(
                    "dataset parameter required when using QuerySpec. "
                    "Pass dataset='your-dataset' or use QueryBuilder instead."
                )
            query_spec = spec

        data = await self._post_async(
            self._build_path(dataset), json=query_spec.model_dump_for_api()
        )
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
        builder: QueryBuilder,
    ) -> tuple[Query, str]:
        """Create a query and annotation together from QueryBuilder (async).

        This is a convenience method for QueryBuilder instances that have
        query names (.name() was called). It creates both the query and
        its annotation in one call. Dataset is extracted from the builder.

        Args:
            builder: QueryBuilder with .name() and .dataset() called

        Returns:
            Tuple of (Query object, annotation_id)

        Raises:
            ValueError: If the QueryBuilder doesn't have a name

        Example:
            >>> query_builder = (
            ...     QueryBuilder()
            ...     .dataset("my-dataset")
            ...     .last_1_hour()
            ...     .count()
            ...     .name("Error Count")
            ...     .description("Tracks errors over time")
            ... )
            >>> query, annotation_id = await client.queries.create_with_annotation_async(
            ...     query_builder
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

        # Extract dataset from builder
        dataset = builder.get_dataset()

        # Create the query first
        query = await self.create_async(builder)

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

    @overload
    def create(self, spec: QueryBuilder) -> Query: ...

    @overload
    def create(self, spec: QuerySpec, *, dataset: str) -> Query: ...

    def create(self, spec: QuerySpec | QueryBuilder, *, dataset: str | None = None) -> Query:
        """Create a new query.

        Args:
            spec: Query specification (QueryBuilder or QuerySpec).
            dataset: Dataset slug. Required for QuerySpec, extracted from QueryBuilder.

        Returns:
            Created Query object.

        Raises:
            HoneycombValidationError: If the query spec is invalid.
            HoneycombNotFoundError: If the dataset doesn't exist.
            ValueError: If dataset parameter is misused.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")

        from ..models.query_builder import QueryBuilder

        # Extract dataset based on spec type
        if isinstance(spec, QueryBuilder):
            if dataset is not None:
                raise ValueError(
                    "dataset parameter not allowed with QueryBuilder. "
                    "Use .dataset() on the builder instead."
                )
            dataset = spec.get_dataset()
            query_spec = spec.build()
        else:
            if dataset is None:
                raise ValueError(
                    "dataset parameter required when using QuerySpec. "
                    "Pass dataset='your-dataset' or use QueryBuilder instead."
                )
            query_spec = spec

        data = self._post_sync(self._build_path(dataset), json=query_spec.model_dump_for_api())
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
