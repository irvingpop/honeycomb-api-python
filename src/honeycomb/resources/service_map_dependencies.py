"""Service Map Dependencies resource for Honeycomb API."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

from ..models.service_map_dependencies import (
    ServiceMapDependency,
    ServiceMapDependencyRequest,
    ServiceMapDependencyRequestCreate,
    ServiceMapDependencyRequestStatus,
    ServiceMapDependencyResult,
)
from .base import BaseResource

if TYPE_CHECKING:
    from ..client import HoneycombClient

# Default page size for pagination (API max is 100)
DEFAULT_PAGE_SIZE = 100

# Default max pages to prevent runaway pagination (64000 items / 100 per page = 640)
DEFAULT_MAX_PAGES = 640


class ServiceMapDependenciesResource(BaseResource):
    """Resource for querying service map dependencies.

    Service Map Dependencies allow you to query the relationships between services
    in your distributed system based on trace data.

    Warning:
        Large time ranges or unfiltered queries can return up to 64,000 dependencies.
        With a page size of 100, this may result in up to 640 API requests.
        The default rate limit is 100 requests per minute per operation.
        If you need higher limits, contact Honeycomb support: https://www.honeycomb.io/support

    Example (async):
        >>> async with HoneycombClient(api_key="...") as client:
        ...     # Get dependencies for the last 2 hours
        ...     deps = await client.service_map_dependencies.get_async(
        ...         request=ServiceMapDependencyRequestCreate(time_range=7200)
        ...     )
        ...
        ...     # Filter to specific services
        ...     deps = await client.service_map_dependencies.get_async(
        ...         request=ServiceMapDependencyRequestCreate(
        ...             time_range=3600,
        ...             filters=[ServiceMapNode(name="user-service")]
        ...         )
        ...     )

    Example (sync):
        >>> with HoneycombClient(api_key="...", sync=True) as client:
        ...     deps = client.service_map_dependencies.get(
        ...         request=ServiceMapDependencyRequestCreate(time_range=7200)
        ...     )
    """

    def __init__(self, client: HoneycombClient) -> None:
        super().__init__(client)

    def _extract_cursor(self, next_link: str | None) -> str | None:
        """Extract cursor value from pagination next link."""
        if not next_link:
            return None
        parsed = urlparse(next_link)
        query_params = parse_qs(parsed.query)
        cursor_values = query_params.get("page[after]", [])
        return cursor_values[0] if cursor_values else None

    def _build_params(
        self,
        cursor: str | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> dict[str, Any]:
        """Build query parameters for get requests."""
        params: dict[str, Any] = {"page[size]": page_size}
        if cursor:
            params["page[after]"] = cursor
        return params

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def create_async(
        self,
        request: ServiceMapDependencyRequestCreate,
        limit: int = 10000,
    ) -> ServiceMapDependencyRequest:
        """Create a Service Map Dependencies request (async).

        This initiates an asynchronous query for service dependencies.
        Use get_async() with the returned request_id to retrieve results.

        Args:
            request: The dependency query parameters.
            limit: Maximum number of dependencies to return (default: 10000, max: 64000).

        Returns:
            ServiceMapDependencyRequest with request_id and status.
        """
        params = {"limit": min(limit, 64000)}
        data = await self._post_async(
            "/1/maps/dependencies/requests",
            json=request.model_dump_for_api(),
            params=params,
        )
        return ServiceMapDependencyRequest.model_validate(data)

    async def get_result_async(
        self,
        request_id: str,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> ServiceMapDependencyResult:
        """Get results for a Service Map Dependencies request (async).

        Automatically paginates through all results. For queries returning
        many dependencies, this may result in multiple API requests.

        Args:
            request_id: The request ID from create_async().
            max_pages: Maximum number of pages to fetch (default: 640).
                       Set to limit API requests for very large result sets.

        Returns:
            ServiceMapDependencyResult with all dependencies.

        Note:
            Large queries can return up to 64,000 dependencies (640 pages).
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        all_dependencies: list[ServiceMapDependency] = []
        cursor: str | None = None
        result_status: ServiceMapDependencyRequestStatus = ServiceMapDependencyRequestStatus.PENDING
        result_request_id: str = request_id
        pages_fetched = 0

        while pages_fetched < max_pages:
            params = self._build_params(cursor=cursor)
            data = await self._get_async(
                f"/1/maps/dependencies/requests/{request_id}",
                params=params,
            )

            result_status = ServiceMapDependencyRequestStatus(data.get("status", "pending"))
            result_request_id = data.get("request_id", request_id)

            # If not ready yet, return current state
            if result_status != ServiceMapDependencyRequestStatus.READY:
                return ServiceMapDependencyResult(
                    request_id=result_request_id,
                    status=result_status,
                    dependencies=None,
                )

            # Parse dependencies from this page
            deps = data.get("dependencies") or []
            all_dependencies.extend(ServiceMapDependency.model_validate(d) for d in deps)
            pages_fetched += 1

            # Check for next page
            next_link = data.get("links", {}).get("next")
            cursor = self._extract_cursor(next_link)
            if not cursor:
                break

        return ServiceMapDependencyResult(
            request_id=result_request_id,
            status=result_status,
            dependencies=all_dependencies,
        )

    async def get_async(
        self,
        request: ServiceMapDependencyRequestCreate,
        limit: int = 10000,
        max_pages: int = DEFAULT_MAX_PAGES,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> ServiceMapDependencyResult:
        """Create and retrieve Service Map Dependencies in one call (async).

        This is a convenience method that creates a request, polls until
        ready, and returns all dependencies with automatic pagination.

        Args:
            request: The dependency query parameters.
            limit: Maximum dependencies to return (default: 10000, max: 64000).
            max_pages: Maximum pages to fetch (default: 640).
            poll_interval: Seconds between status checks (default: 1.0).
            timeout: Maximum seconds to wait for results (default: 60.0).

        Returns:
            ServiceMapDependencyResult with all dependencies.

        Raises:
            TimeoutError: If results are not ready within timeout.

        Note:
            Large queries can return up to 64,000 dependencies (640 pages).
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        # Create the request
        req = await self.create_async(request, limit=limit)

        # Poll until ready
        start_time = asyncio.get_event_loop().time()
        while True:
            result = await self.get_result_async(req.request_id, max_pages=max_pages)

            if result.status == ServiceMapDependencyRequestStatus.READY:
                return result

            if result.status == ServiceMapDependencyRequestStatus.ERROR:
                return result

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Service map dependencies request {req.request_id} did not complete "
                    f"within {timeout} seconds"
                )

            await asyncio.sleep(poll_interval)

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def create(
        self,
        request: ServiceMapDependencyRequestCreate,
        limit: int = 10000,
    ) -> ServiceMapDependencyRequest:
        """Create a Service Map Dependencies request.

        This initiates an asynchronous query for service dependencies.
        Use get_result() with the returned request_id to retrieve results.

        Args:
            request: The dependency query parameters.
            limit: Maximum number of dependencies to return (default: 10000, max: 64000).

        Returns:
            ServiceMapDependencyRequest with request_id and status.
        """
        if not self._client.is_sync:
            raise RuntimeError("Use create_async() for async mode, or pass sync=True to client")

        params = {"limit": min(limit, 64000)}
        data = self._post_sync(
            "/1/maps/dependencies/requests",
            json=request.model_dump_for_api(),
            params=params,
        )
        return ServiceMapDependencyRequest.model_validate(data)

    def get_result(
        self,
        request_id: str,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> ServiceMapDependencyResult:
        """Get results for a Service Map Dependencies request.

        Automatically paginates through all results. For queries returning
        many dependencies, this may result in multiple API requests.

        Args:
            request_id: The request ID from create().
            max_pages: Maximum number of pages to fetch (default: 640).
                       Set to limit API requests for very large result sets.

        Returns:
            ServiceMapDependencyResult with all dependencies.

        Note:
            Large queries can return up to 64,000 dependencies (640 pages).
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_result_async() for async mode, or pass sync=True to client")

        all_dependencies: list[ServiceMapDependency] = []
        cursor: str | None = None
        result_status: ServiceMapDependencyRequestStatus = ServiceMapDependencyRequestStatus.PENDING
        result_request_id: str = request_id
        pages_fetched = 0

        while pages_fetched < max_pages:
            params = self._build_params(cursor=cursor)
            data = self._get_sync(
                f"/1/maps/dependencies/requests/{request_id}",
                params=params,
            )

            result_status = ServiceMapDependencyRequestStatus(data.get("status", "pending"))
            result_request_id = data.get("request_id", request_id)

            # If not ready yet, return current state
            if result_status != ServiceMapDependencyRequestStatus.READY:
                return ServiceMapDependencyResult(
                    request_id=result_request_id,
                    status=result_status,
                    dependencies=None,
                )

            # Parse dependencies from this page
            deps = data.get("dependencies") or []
            all_dependencies.extend(ServiceMapDependency.model_validate(d) for d in deps)
            pages_fetched += 1

            # Check for next page
            next_link = data.get("links", {}).get("next")
            cursor = self._extract_cursor(next_link)
            if not cursor:
                break

        return ServiceMapDependencyResult(
            request_id=result_request_id,
            status=result_status,
            dependencies=all_dependencies,
        )

    def get(
        self,
        request: ServiceMapDependencyRequestCreate,
        limit: int = 10000,
        max_pages: int = DEFAULT_MAX_PAGES,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> ServiceMapDependencyResult:
        """Create and retrieve Service Map Dependencies in one call.

        This is a convenience method that creates a request, polls until
        ready, and returns all dependencies with automatic pagination.

        Args:
            request: The dependency query parameters.
            limit: Maximum dependencies to return (default: 10000, max: 64000).
            max_pages: Maximum pages to fetch (default: 640).
            poll_interval: Seconds between status checks (default: 1.0).
            timeout: Maximum seconds to wait for results (default: 60.0).

        Returns:
            ServiceMapDependencyResult with all dependencies.

        Raises:
            TimeoutError: If results are not ready within timeout.

        Note:
            Large queries can return up to 64,000 dependencies (640 pages).
            The default rate limit is 100 requests per minute per operation.
            Contact Honeycomb support for higher limits: https://www.honeycomb.io/support
        """
        if not self._client.is_sync:
            raise RuntimeError("Use get_async() for async mode, or pass sync=True to client")

        # Create the request
        req = self.create(request, limit=limit)

        # Poll until ready
        start_time = time.time()
        while True:
            result = self.get_result(req.request_id, max_pages=max_pages)

            if result.status == ServiceMapDependencyRequestStatus.READY:
                return result

            if result.status == ServiceMapDependencyRequestStatus.ERROR:
                return result

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Service map dependencies request {req.request_id} did not complete "
                    f"within {timeout} seconds"
                )

            time.sleep(poll_interval)
