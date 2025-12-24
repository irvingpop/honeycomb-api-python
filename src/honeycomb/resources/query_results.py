"""Query Results resource for Honeycomb API."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from ..models.queries import Query, QueryResult, QuerySpec
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient


class QueryResultsResource(BaseResource):
    """Resource for running queries and getting results.

    Query results represent the execution of a query against a dataset.
    You can either run a saved query by ID or create and run a query inline.

    Example (async with polling):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     # Run a query and poll for results
        ...     result = await client.query_results.run_async(
        ...         dataset="my-dataset",
        ...         spec=QuerySpec(time_range=3600, calculations=[...]),
        ...         poll_interval=1.0,
        ...         timeout=60.0,
        ...     )
        ...     print(f"Found {len(result.data)} rows")

    Example (manual polling):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     # Create query result
        ...     query_result_id = await client.query_results.create_async(
        ...         dataset="my-dataset",
        ...         spec=QuerySpec(...)
        ...     )
        ...     # Poll for completion
        ...     result = await client.query_results.get_async(
        ...         dataset="my-dataset",
        ...         query_result_id=query_result_id
        ...     )
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _build_path(self, dataset: str, query_result_id: str | None = None) -> str:
        """Build API path for query results."""
        base = f"/1/query_results/{dataset}"
        if query_result_id:
            return f"{base}/{query_result_id}"
        return base

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def create_async(
        self,
        dataset: str,
        spec: QuerySpec | None = None,
        query_id: str | None = None,
    ) -> str:
        """Create a query result (start query execution) (async).

        Provide either spec (inline query) or query_id (saved query).

        Args:
            dataset: The dataset slug.
            spec: Inline query specification (optional).
            query_id: Saved query ID (optional).

        Returns:
            Query result ID for polling.

        Raises:
            ValueError: If neither spec nor query_id is provided.
            HoneycombValidationError: If the query spec is invalid.
        """
        if not spec and not query_id:
            raise ValueError("Must provide either spec or query_id")

        json_data = {}
        if spec:
            json_data = spec.model_dump_for_api()
        if query_id:
            json_data["query_id"] = query_id

        data = await self._post_async(self._build_path(dataset), json=json_data)
        # API returns {"id": "query-result-id"}
        return data["id"]

    async def get_async(self, dataset: str, query_result_id: str) -> QueryResult:
        """Get query result status/data (async).

        Args:
            dataset: The dataset slug.
            query_result_id: Query result ID.

        Returns:
            QueryResult with data if query is complete.

        Raises:
            HoneycombNotFoundError: If the query result doesn't exist.
        """
        data = await self._get_async(self._build_path(dataset, query_result_id))
        return self._parse_model(QueryResult, data)

    async def run_async(
        self,
        dataset: str,
        spec: QuerySpec | None = None,
        query_id: str | None = None,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> QueryResult:
        """Run a query and poll for results (async).

        Convenience method that creates a query result and polls until complete.

        Args:
            dataset: The dataset slug.
            spec: Inline query specification (optional).
            query_id: Saved query ID (optional).
            poll_interval: Seconds between poll attempts (default: 1.0).
            timeout: Maximum seconds to wait for results (default: 60.0).

        Returns:
            QueryResult with completed data.

        Raises:
            TimeoutError: If query doesn't complete within timeout.
            HoneycombValidationError: If the query spec is invalid.
        """
        from ..exceptions import HoneycombTimeoutError

        # Create the query result
        result_id = await self.create_async(dataset, spec=spec, query_id=query_id)

        # Poll for completion
        start_time = asyncio.get_event_loop().time()
        while True:
            result = await self.get_async(dataset, result_id)

            # Check if query is complete (has data)
            if result.data is not None:
                return result

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                raise HoneycombTimeoutError(
                    f"Query did not complete within {timeout}s", timeout=timeout
                )

            # Wait before next poll
            await asyncio.sleep(poll_interval)

    async def create_and_run_async(
        self,
        dataset: str,
        spec: QuerySpec,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> tuple[Query, QueryResult]:
        """Create a saved query and run it in one call (async).

        Convenience method that:
        1. Creates a permanent saved query
        2. Executes it and polls for results
        3. Returns both the saved query and results

        This is useful when you want to save a query for future use
        AND get immediate results.

        Args:
            dataset: The dataset slug.
            spec: Query specification.
            poll_interval: Seconds between poll attempts (default: 1.0).
            timeout: Maximum seconds to wait for results (default: 60.0).

        Returns:
            Tuple of (Query, QueryResult) - the saved query and execution results.

        Raises:
            HoneycombTimeoutError: If query doesn't complete within timeout.
            HoneycombValidationError: If the query spec is invalid.

        Example:
            >>> query, result = await client.query_results.create_and_run_async(
            ...     "my-dataset",
            ...     QuerySpec(time_range=3600, calculations=[{"op": "COUNT"}]),
            ... )
            >>> print(f"Saved as query {query.id} with {len(result.data)} rows")
        """
        # Create the saved query
        query = await self._client.queries.create_async(dataset, spec)

        # Run it and poll for results
        result = await self.run_async(
            dataset, query_id=query.id, poll_interval=poll_interval, timeout=timeout
        )

        return query, result

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def create(
        self,
        dataset: str,
        spec: QuerySpec | None = None,
        query_id: str | None = None,
    ) -> str:
        """Create a query result (start query execution).

        Args:
            dataset: The dataset slug.
            spec: Inline query specification (optional).
            query_id: Saved query ID (optional).

        Returns:
            Query result ID for polling.

        Raises:
            ValueError: If neither spec nor query_id is provided.
            HoneycombValidationError: If the query spec is invalid.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")

        if not spec and not query_id:
            raise ValueError("Must provide either spec or query_id")

        json_data = {}
        if spec:
            json_data = spec.model_dump_for_api()
        if query_id:
            json_data["query_id"] = query_id

        data = self._post_sync(self._build_path(dataset), json=json_data)
        return data["id"]

    def get(self, dataset: str, query_result_id: str) -> QueryResult:
        """Get query result status/data.

        Args:
            dataset: The dataset slug.
            query_result_id: Query result ID.

        Returns:
            QueryResult with data if query is complete.

        Raises:
            HoneycombNotFoundError: If the query result doesn't exist.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")
        data = self._get_sync(self._build_path(dataset, query_result_id))
        return self._parse_model(QueryResult, data)

    def run(
        self,
        dataset: str,
        spec: QuerySpec | None = None,
        query_id: str | None = None,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> QueryResult:
        """Run a query and poll for results.

        Convenience method that creates a query result and polls until complete.

        Args:
            dataset: The dataset slug.
            spec: Inline query specification (optional).
            query_id: Saved query ID (optional).
            poll_interval: Seconds between poll attempts (default: 1.0).
            timeout: Maximum seconds to wait for results (default: 60.0).

        Returns:
            QueryResult with completed data.

        Raises:
            TimeoutError: If query doesn't complete within timeout.
            HoneycombValidationError: If the query spec is invalid.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use run_async() for async mode, or pass sync=True to client")

        import time

        from ..exceptions import HoneycombTimeoutError

        # Create the query result
        result_id = self.create(dataset, spec=spec, query_id=query_id)

        # Poll for completion
        start_time = time.time()
        while True:
            result = self.get(dataset, result_id)

            # Check if query is complete (has data)
            if result.data is not None:
                return result

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise HoneycombTimeoutError(
                    f"Query did not complete within {timeout}s", timeout=timeout
                )

            # Wait before next poll
            time.sleep(poll_interval)

    def create_and_run(
        self,
        dataset: str,
        spec: QuerySpec,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> tuple[Query, QueryResult]:
        """Create a saved query and run it in one call.

        Convenience method that:
        1. Creates a permanent saved query
        2. Executes it and polls for results
        3. Returns both the saved query and results

        This is useful when you want to save a query for future use
        AND get immediate results.

        Args:
            dataset: The dataset slug.
            spec: Query specification.
            poll_interval: Seconds between poll attempts (default: 1.0).
            timeout: Maximum seconds to wait for results (default: 60.0).

        Returns:
            Tuple of (Query, QueryResult) - the saved query and execution results.

        Raises:
            HoneycombTimeoutError: If query doesn't complete within timeout.
            HoneycombValidationError: If the query spec is invalid.

        Example:
            >>> query, result = client.query_results.create_and_run(
            ...     "my-dataset",
            ...     QuerySpec(time_range=3600, calculations=[{"op": "COUNT"}]),
            ... )
            >>> print(f"Saved as query {query.id} with {len(result.data)} rows")
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use create_and_run_async() for async mode, or pass sync=True to client"
            )

        # Create the saved query
        query = self._client.queries.create(dataset, spec)

        # Run it and poll for results
        result = self.run(dataset, query_id=query.id, poll_interval=poll_interval, timeout=timeout)

        return query, result
