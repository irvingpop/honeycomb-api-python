"""Query Results resource for Honeycomb API."""

from __future__ import annotations

import asyncio
import time as time_module
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ..models.queries import Query, QueryResult, QuerySpec
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient

# Default max results for run_all_async
DEFAULT_MAX_RESULTS = 100_000

# Duplication threshold for smart stopping
DUPLICATION_THRESHOLD = 0.5  # 50%


class QueryResultsResource(BaseResource):
    """Resource for running queries and getting results.

    Query results represent the execution of a query against a dataset.
    You must first create a saved query, then run it to get results.

    Note:
        Query Results API requires Enterprise plan.

    Example (async - run saved query):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     # First create a saved query
        ...     query = await client.queries.create_async(
        ...         dataset="my-dataset",
        ...         spec=QuerySpec(time_range=3600, calculations=[...])
        ...     )
        ...     # Then run it and poll for results
        ...     result = await client.query_results.run_async(
        ...         dataset="my-dataset",
        ...         query_id=query.id,
        ...         poll_interval=1.0,
        ...         timeout=60.0,
        ...     )
        ...     print(f"Found {len(result.data.rows)} rows")

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
        query_id: str,
        disable_series: bool = True,
        limit: int | None = None,
    ) -> str:
        """Create a query result (start query execution) (async).

        Args:
            dataset: The dataset slug.
            query_id: Saved query ID (from queries.create_async).
            disable_series: If True, disable timeseries data and allow up to 10K results
                           (default: True for better performance).
            limit: Override result limit (max 10,000 when disable_series=True, 1,000 otherwise).
                   Defaults to 10,000 when disable_series=True, 1,000 when False.

        Returns:
            Query result ID for polling.

        Raises:
            HoneycombNotFoundError: If the query doesn't exist.
            HoneycombValidationError: If the query spec is invalid.

        Note:
            Query Results API requires Enterprise plan.
        """
        json_data = {
            "query_id": query_id,
            "disable_series": disable_series,
        }

        # Set limit - default to 10K when disable_series=True, 1K otherwise
        if limit is not None:
            json_data["limit"] = limit
        elif disable_series:
            json_data["limit"] = 10000
        else:
            json_data["limit"] = 1000

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
        query_id: str,
        disable_series: bool = True,
        limit: int | None = None,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> QueryResult:
        """Run a saved query and poll for results (async).

        Convenience method that creates a query result and polls until complete.

        Args:
            dataset: The dataset slug.
            query_id: Saved query ID (from queries.create_async).
            disable_series: If True, disable timeseries data and allow up to 10K results
                           (default: True for better performance).
            limit: Override result limit (max 10,000 when disable_series=True, 1,000 otherwise).
                   Defaults to 10,000 when disable_series=True, 1,000 when False.
            poll_interval: Seconds between poll attempts (default: 1.0).
            timeout: Maximum seconds to wait for results (default: 60.0).

        Returns:
            QueryResult with completed data (up to 10K rows if disable_series=True).

        Raises:
            HoneycombTimeoutError: If query doesn't complete within timeout.
            HoneycombNotFoundError: If the query doesn't exist.

        Note:
            For > 10K results, use run_all_async() with sort-based pagination.
            Query Results API requires Enterprise plan.
        """
        from ..exceptions import HoneycombTimeoutError

        # Create the query result
        result_id = await self.create_async(
            dataset, query_id=query_id, disable_series=disable_series, limit=limit
        )

        # Poll for completion
        start_time = asyncio.get_event_loop().time()
        while True:
            result = await self.get_async(dataset, result_id)

            # Check if query is complete (has results)
            if result.data is not None and result.data.results is not None:
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
        disable_series: bool = True,
        limit: int | None = None,
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
            spec: Query specification (don't set spec.limit > 1000).
            disable_series: If True, disable timeseries data and allow up to 10K results
                           (default: True for better performance).
            limit: Override result limit (max 10,000 when disable_series=True, 1,000 otherwise).
                   Defaults to 10,000 when disable_series=True, 1,000 when False.
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
            >>> print(f"Saved as query {query.id} with {len(result.data.rows)} rows")
        """
        # Create the saved query
        query = await self._client.queries.create_async(dataset, spec)

        # Run it and poll for results
        result = await self.run_async(
            dataset,
            query_id=query.id,
            disable_series=disable_series,
            limit=limit,
            poll_interval=poll_interval,
            timeout=timeout,
        )

        return query, result

    async def run_all_async(
        self,
        dataset: str,
        spec: QuerySpec,
        sort_field: str | None = None,
        sort_order: str = "descending",
        max_results: int = DEFAULT_MAX_RESULTS,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
        on_page: Callable[[int, int], None] | None = None,
    ) -> list[dict]:
        """Paginate through > 10K results using sort-based cursor pagination.

        WARNING: This makes multiple API calls (rate limit: 10/min).
        Each page returns up to 10,000 rows. For 100K rows, expect ~10 queries taking ~60 seconds.

        How it works:
        1. Converts relative time_range to absolute start/end timestamps
        2. Creates saved queries with sort order (no limit in spec)
        3. Executes each with disable_series=True and limit=10000
        4. Captures last value in sort field
        5. Re-runs with HAVING (for calculations) or filter (for breakdowns): sort_field <= last_value
        6. Deduplicates results by composite key (breakdowns + calculation values)
        7. Repeats until: no more results, max_results reached, or >50% duplicates detected
        8. Returns deduplicated list of all rows

        Args:
            dataset: Dataset slug.
            spec: Query specification (time range, calculations, filters, breakdowns).
            sort_field: Field to sort/paginate by. Defaults to first calculation's alias.
                       Must be a calculation alias or breakdown field.
            sort_order: "ascending" or "descending" (default: "descending" for most important first).
            max_results: Maximum total results to return (default: 100,000).
            poll_interval: Seconds between polls for each query.
            timeout: Timeout for each individual query execution.
            on_page: Optional callback(page_num, total_rows) called after each page.

        Note:
            Each page returns up to 10,000 rows (limit=10000 passed at execution time).
            Saved queries have max spec.limit of 1,000, so we don't set it in QuerySpec.

        Returns:
            List of all result rows (deduplicated).

        Raises:
            ValueError: If spec has conflicting orders or invalid configuration.
            HoneycombTimeoutError: If any query times out.

        Example:
            >>> # Get all high-latency requests in last 24h
            >>> rows = await client.query_results.run_all_async(
            ...     dataset="my-dataset",
            ...     spec=QuerySpec(
            ...         time_range=86400,
            ...         calculations=[
            ...             {"op": "AVG", "column": "duration_ms"}
            ...         ],
            ...         filters=[{"column": "duration_ms", "op": ">", "value": 1000}],
            ...         breakdowns=["trace.trace_id", "name"],
            ...     ),
            ...     on_page=lambda page, total: print(f"Page {page}: {total} rows so far"),
            ... )
            >>> print(f"Total: {len(rows)} slow requests")

        Note:
            Rate limit is 10 requests/minute. Large result sets will take time.
            The method uses smart stopping: if >50% duplicates detected between
            pages, pagination stops (indicates long tail of identical values).
        """
        # Validate spec
        if not spec.calculations:
            raise ValueError("spec.calculations is required for run_all_async")

        # Determine sort field (default to first calculation)
        if sort_field is None:
            # Auto-default from first calculation
            first_calc = spec.calculations[0]
            if first_calc.get("alias"):
                # Alias provided - use it for both orders and access
                sort_field_for_access = first_calc["alias"]
                sort_field_for_orders = first_calc["alias"]
            else:
                # No alias - use uppercase op for both (results use uppercase like "COUNT")
                sort_field_for_orders = first_calc.get("op", "COUNT")
                sort_field_for_access = first_calc.get("op", "COUNT")
        else:
            # User provided sort_field - check if it matches a calculation op
            matched_calc = None
            for calc in spec.calculations:
                # Check if sort_field matches this calculation's op (case-insensitive)
                if calc.get("op", "").lower() == sort_field.lower():
                    matched_calc = calc
                    break
                # Or matches the alias exactly
                if calc.get("alias") == sort_field:
                    matched_calc = calc
                    break

            if matched_calc:
                # Matched a calculation - use uppercase op or alias
                if matched_calc.get("alias"):
                    sort_field_for_access = matched_calc["alias"]
                    sort_field_for_orders = matched_calc["alias"]
                else:
                    # No alias - use uppercase op for both
                    sort_field_for_orders = matched_calc.get("op", "COUNT")
                    sort_field_for_access = matched_calc.get("op", "COUNT")
            else:
                # Assume it's a breakdown field - use as-is
                sort_field_for_access = sort_field
                sort_field_for_orders = sort_field

        # Check for conflicting orders
        if spec.orders:
            raise ValueError(
                "spec.orders must be None for run_all_async (sorting is managed automatically). "
                "Remove orders or use run_async() instead."
            )

        # Normalize time range to absolute timestamps
        start_time, end_time = self._normalize_time_range(spec)

        # Track all rows and seen keys for deduplication
        all_rows: list[dict] = []
        seen_keys: set[tuple] = set()
        cursor_value: Any | None = None
        page_num = 0

        while len(all_rows) < max_results:
            page_num += 1

            # Build page spec
            page_spec = spec.model_copy(deep=True)
            page_spec.start_time = start_time
            page_spec.end_time = end_time
            page_spec.time_range = None  # Use absolute times instead

            # Don't set page_spec.limit - saved queries have max 1000
            # Instead pass limit=10000 when creating query result
            page_spec.limit = None

            # Set sort order
            page_spec.orders = [{"op": sort_field_for_orders, "order": sort_order}]

            # Add cursor condition for pagination (skip first page)
            if cursor_value is not None:
                # descending: get values <= cursor (lower values)
                # ascending: get values >= cursor (higher values)
                cursor_op = "<=" if sort_order == "descending" else ">="

                # Check if we're paginating on a calculation or breakdown
                is_calculation = any(
                    calc.get("alias") == sort_field_for_access
                    or calc.get("op") == sort_field_for_access
                    for calc in spec.calculations
                )

                if is_calculation:
                    # Use HAVING for calculation results
                    # HAVING uses "calculate_op" field, not "column"
                    cursor_having = {
                        "calculate_op": sort_field_for_access,  # e.g., "COUNT" or alias
                        "op": cursor_op,
                        "value": cursor_value,
                    }
                    page_spec.havings = (page_spec.havings or []) + [cursor_having]
                else:
                    # Use filter for breakdown fields
                    cursor_filter = {
                        "column": sort_field_for_access,
                        "op": cursor_op,
                        "value": cursor_value,
                    }
                    page_spec.filters = (page_spec.filters or []) + [cursor_filter]

            # Debug logging for troubleshooting
            import logging

            logger = logging.getLogger(__name__)
            if page_num > 1 and cursor_value is not None:
                filter_type = "HAVING" if is_calculation else "filter"
                logger.debug(
                    f"Page {page_num}: Using {filter_type} on '{sort_field_for_access}' "
                    f"{cursor_op} {cursor_value}"
                )

            # Run the page query (create and run in one call)
            try:
                _, result = await self.create_and_run_async(
                    dataset,
                    spec=page_spec,
                    disable_series=True,
                    limit=10000,  # Override to get max results per page
                    poll_interval=poll_interval,
                    timeout=timeout,
                )
            except Exception:
                # Log the spec that failed for debugging
                logger.error(f"Failed to create/run query on page {page_num}")
                logger.error(f"Spec: {page_spec.model_dump_for_api()}")
                raise

            if not result.data or not result.data.results or len(result.data.results) == 0:
                break  # No more results

            # Deduplicate and collect new rows (use unwrapped rows)
            new_rows_count = 0
            for row in result.data.rows:
                # Build composite unique key from breakdowns + calculations
                key = self._build_row_key(row, spec)

                if key not in seen_keys:
                    seen_keys.add(key)
                    all_rows.append(row)
                    new_rows_count += 1

            # Progress callback
            if on_page:
                on_page(page_num, len(all_rows))

            # Smart stopping: if >50% duplicates, we've hit a long tail
            duplication_rate = 1.0 - (new_rows_count / len(result.data.rows))
            if duplication_rate > DUPLICATION_THRESHOLD:
                break  # Stop pagination (long tail of identical values)

            # Check if this was the last page (less than 10K means no more results)
            if len(result.data.rows) < 10000:
                break

            # Update cursor to last row's sort value
            try:
                cursor_value = result.data.rows[-1][sort_field_for_access]
            except (KeyError, IndexError) as e:
                raise ValueError(
                    f"Sort field '{sort_field_for_access}' not found in query results. "
                    "Ensure it's a calculation alias or breakdown field."
                ) from e

        return all_rows

    def _normalize_time_range(self, spec: QuerySpec) -> tuple[int, int]:
        """Convert relative time_range to absolute start/end timestamps.

        Args:
            spec: Query specification with time_range or start/end times.

        Returns:
            Tuple of (start_time, end_time) as Unix timestamps.
        """
        now = int(time_module.time())

        # If absolute times provided, use them
        if spec.start_time is not None and spec.end_time is not None:
            return spec.start_time, spec.end_time

        # If only start_time, add time_range
        if spec.start_time is not None:
            time_range = spec.time_range or 3600  # Default 1 hour
            return spec.start_time, spec.start_time + time_range

        # If only end_time, subtract time_range
        if spec.end_time is not None:
            time_range = spec.time_range or 3600
            return spec.end_time - time_range, spec.end_time

        # Relative from now
        time_range = spec.time_range or 3600
        return now - time_range, now

    def _build_row_key(self, row: dict, spec: QuerySpec) -> tuple:
        """Build composite unique key from breakdowns and calculation values.

        The key consists of:
        - All breakdown field values
        - All calculation result values (in order)

        This ensures uniqueness based on the group-by dimensions and aggregated values.

        Args:
            row: Query result row.
            spec: Query specification (for breakdowns and calculations).

        Returns:
            Tuple of values representing the unique key.
        """
        key_parts = []

        # Add breakdown values
        if spec.breakdowns:
            for breakdown in spec.breakdowns:
                key_parts.append(row.get(breakdown))

        # Add calculation values
        if spec.calculations:
            for calc in spec.calculations:
                # Use alias if present, otherwise uppercase op (results use "COUNT" not "count")
                field = calc.get("alias") or calc.get("op", "COUNT")
                key_parts.append(row.get(field))

        return tuple(key_parts)

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def create(
        self,
        dataset: str,
        query_id: str,
        disable_series: bool = True,
        limit: int | None = None,
    ) -> str:
        """Create a query result (start query execution).

        Args:
            dataset: The dataset slug.
            query_id: Saved query ID (from queries.create).
            disable_series: If True, disable timeseries data and allow up to 10K results
                           (default: True for better performance).
            limit: Override result limit (max 10,000 when disable_series=True, 1,000 otherwise).
                   Defaults to 10,000 when disable_series=True, 1,000 when False.

        Returns:
            Query result ID for polling.

        Raises:
            HoneycombNotFoundError: If the query doesn't exist.
            HoneycombValidationError: If the query spec is invalid.

        Note:
            Query Results API requires Enterprise plan.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")

        json_data = {
            "query_id": query_id,
            "disable_series": disable_series,
        }

        # Set limit - default to 10K when disable_series=True, 1K otherwise
        if limit is not None:
            json_data["limit"] = limit
        elif disable_series:
            json_data["limit"] = 10000
        else:
            json_data["limit"] = 1000

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
        query_id: str,
        disable_series: bool = True,
        limit: int | None = None,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> QueryResult:
        """Run a saved query and poll for results.

        Convenience method that creates a query result and polls until complete.

        Args:
            dataset: The dataset slug.
            query_id: Saved query ID (from queries.create).
            disable_series: If True, disable timeseries data and allow up to 10K results
                           (default: True for better performance).
            limit: Override result limit (max 10,000 when disable_series=True, 1,000 otherwise).
                   Defaults to 10,000 when disable_series=True, 1,000 when False.
            poll_interval: Seconds between poll attempts (default: 1.0).
            timeout: Maximum seconds to wait for results (default: 60.0).

        Returns:
            QueryResult with completed data (up to 10K rows if disable_series=True).

        Raises:
            HoneycombTimeoutError: If query doesn't complete within timeout.
            HoneycombNotFoundError: If the query doesn't exist.

        Note:
            Query Results API requires Enterprise plan.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use run_async() for async mode, or pass sync=True to client")

        import time

        from ..exceptions import HoneycombTimeoutError

        # Create the query result
        result_id = self.create(
            dataset, query_id=query_id, disable_series=disable_series, limit=limit
        )

        # Poll for completion
        start_time = time.time()
        while True:
            result = self.get(dataset, result_id)

            # Check if query is complete (has results)
            if result.data is not None and result.data.results is not None:
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
        disable_series: bool = True,
        limit: int | None = None,
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
            spec: Query specification (don't set spec.limit > 1000).
            disable_series: If True, disable timeseries data and allow up to 10K results
                           (default: True for better performance).
            limit: Override result limit (max 10,000 when disable_series=True, 1,000 otherwise).
                   Defaults to 10,000 when disable_series=True, 1,000 when False.
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
            >>> print(f"Saved as query {query.id} with {len(result.data.rows)} rows")
        """
        if not self._client.is_sync:
            raise RuntimeError(
                "Use create_and_run_async() for async mode, or pass sync=True to client"
            )

        # Create the saved query
        query = self._client.queries.create(dataset, spec)

        # Run it and poll for results
        result = self.run(
            dataset,
            query_id=query.id,
            disable_series=disable_series,
            limit=limit,
            poll_interval=poll_interval,
            timeout=timeout,
        )

        return query, result
