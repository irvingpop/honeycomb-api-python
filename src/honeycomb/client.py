"""Honeycomb API client with async-first design and sync wrapper."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Any

import httpx

from .auth import create_auth
from .exceptions import (
    HoneycombAPIError,
    HoneycombAuthError,
    HoneycombConnectionError,
    HoneycombForbiddenError,
    HoneycombNotFoundError,
    HoneycombRateLimitError,
    HoneycombServerError,
    HoneycombTimeoutError,
    HoneycombValidationError,
)

if TYPE_CHECKING:
    from .resources.api_keys import ApiKeysResource
    from .resources.boards import BoardsResource
    from .resources.burn_alerts import BurnAlertsResource
    from .resources.columns import ColumnsResource
    from .resources.datasets import DatasetsResource
    from .resources.derived_columns import DerivedColumnsResource
    from .resources.environments import EnvironmentsResource
    from .resources.events import EventsResource
    from .resources.markers import MarkersResource
    from .resources.queries import QueriesResource
    from .resources.query_annotations import QueryAnnotationsResource
    from .resources.query_results import QueryResultsResource
    from .resources.recipients import RecipientsResource
    from .resources.service_map_dependencies import ServiceMapDependenciesResource
    from .resources.slos import SLOsResource
    from .resources.triggers import TriggersResource


DEFAULT_BASE_URL = "https://api.honeycomb.io"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts.
        base_delay: Base delay in seconds for exponential backoff.
        max_delay: Maximum delay in seconds between retries.
        exponential_base: Base for exponential backoff calculation.
        retry_statuses: HTTP status codes that should trigger a retry.
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    retry_statuses: set[int] = field(default_factory=lambda: {429, 500, 502, 503, 504})


@dataclass
class RateLimitInfo:
    """Rate limit information from response headers.

    Attributes:
        limit: Total requests allowed in the time window.
        remaining: Remaining requests in the current time window.
        reset: Seconds until the rate limit resets.
    """

    limit: int | None = None
    remaining: int | None = None
    reset: int | None = None


class HoneycombClient:
    """Async-first client for the Honeycomb API.

    Supports both async and sync usage patterns.

    Example (async - recommended):
        >>> async with HoneycombClient(api_key="your-key") as client:
        ...     datasets = await client.datasets.list()
        ...     triggers = await client.triggers.list(dataset="my-dataset")

    Example (sync):
        >>> with HoneycombClient(api_key="your-key", sync=True) as client:
        ...     datasets = client.datasets.list()

    Args:
        api_key: Honeycomb API key for single-environment access.
        management_key: Management API key ID for multi-environment access.
        management_secret: Management API key secret.
        base_url: API base URL (default: https://api.honeycomb.io).
        timeout: Request timeout in seconds (default: 30).
        max_retries: Maximum retry attempts for failed requests (default: 3).
        retry_config: Custom retry configuration (optional, overrides max_retries).
        sync: If True, use synchronous HTTP client (default: False).
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        management_key: str | None = None,
        management_secret: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_config: RetryConfig | None = None,
        sync: bool = False,
    ) -> None:
        self._auth = create_auth(
            api_key=api_key,
            management_key=management_key,
            management_secret=management_secret,
        )
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_config = retry_config or RetryConfig(max_retries=max_retries)
        self._sync_mode = sync

        # HTTP clients (lazily initialized)
        self._async_client: httpx.AsyncClient | None = None
        self._sync_client: httpx.Client | None = None

        # Resource instances (lazily initialized)
        self._triggers: TriggersResource | None = None
        self._slos: SLOsResource | None = None
        self._datasets: DatasetsResource | None = None
        self._boards: BoardsResource | None = None
        self._queries: QueriesResource | None = None
        self._query_annotations: QueryAnnotationsResource | None = None
        self._query_results: QueryResultsResource | None = None
        self._columns: ColumnsResource | None = None
        self._derived_columns: DerivedColumnsResource | None = None
        self._markers: MarkersResource | None = None
        self._recipients: RecipientsResource | None = None
        self._burn_alerts: BurnAlertsResource | None = None
        self._events: EventsResource | None = None
        self._api_keys: ApiKeysResource | None = None
        self._environments: EnvironmentsResource | None = None
        self._service_map_dependencies: ServiceMapDependenciesResource | None = None

    # -------------------------------------------------------------------------
    # Resource accessors
    # -------------------------------------------------------------------------

    @property
    def triggers(self) -> TriggersResource:
        """Access the Triggers API."""
        if self._triggers is None:
            from .resources.triggers import TriggersResource

            self._triggers = TriggersResource(self)
        return self._triggers

    @property
    def slos(self) -> SLOsResource:
        """Access the SLOs API."""
        if self._slos is None:
            from .resources.slos import SLOsResource

            self._slos = SLOsResource(self)
        return self._slos

    @property
    def datasets(self) -> DatasetsResource:
        """Access the Datasets API."""
        if self._datasets is None:
            from .resources.datasets import DatasetsResource

            self._datasets = DatasetsResource(self)
        return self._datasets

    @property
    def boards(self) -> BoardsResource:
        """Access the Boards API."""
        if self._boards is None:
            from .resources.boards import BoardsResource

            self._boards = BoardsResource(self)
        return self._boards

    @property
    def queries(self) -> QueriesResource:
        """Access the Queries API."""
        if self._queries is None:
            from .resources.queries import QueriesResource

            self._queries = QueriesResource(self)
        return self._queries

    @property
    def query_annotations(self) -> QueryAnnotationsResource:
        """Access the Query Annotations API."""
        if self._query_annotations is None:
            from .resources.query_annotations import QueryAnnotationsResource

            self._query_annotations = QueryAnnotationsResource(self)
        return self._query_annotations

    @property
    def query_results(self) -> QueryResultsResource:
        """Access the Query Results API."""
        if self._query_results is None:
            from .resources.query_results import QueryResultsResource

            self._query_results = QueryResultsResource(self)
        return self._query_results

    @property
    def columns(self) -> ColumnsResource:
        """Access the Columns API."""
        if self._columns is None:
            from .resources.columns import ColumnsResource

            self._columns = ColumnsResource(self)
        return self._columns

    @property
    def derived_columns(self) -> DerivedColumnsResource:
        """Access the Derived Columns (Calculated Fields) API."""
        if self._derived_columns is None:
            from .resources.derived_columns import DerivedColumnsResource

            self._derived_columns = DerivedColumnsResource(self)
        return self._derived_columns

    @property
    def markers(self) -> MarkersResource:
        """Access the Markers API."""
        if self._markers is None:
            from .resources.markers import MarkersResource

            self._markers = MarkersResource(self)
        return self._markers

    @property
    def recipients(self) -> RecipientsResource:
        """Access the Recipients API."""
        if self._recipients is None:
            from .resources.recipients import RecipientsResource

            self._recipients = RecipientsResource(self)
        return self._recipients

    @property
    def burn_alerts(self) -> BurnAlertsResource:
        """Access the Burn Alerts API."""
        if self._burn_alerts is None:
            from .resources.burn_alerts import BurnAlertsResource

            self._burn_alerts = BurnAlertsResource(self)
        return self._burn_alerts

    @property
    def events(self) -> EventsResource:
        """Access the Events API (data ingestion)."""
        if self._events is None:
            from .resources.events import EventsResource

            self._events = EventsResource(self)
        return self._events

    @property
    def api_keys(self) -> ApiKeysResource:
        """Access the API Keys API (v2 team-scoped)."""
        if self._api_keys is None:
            from .resources.api_keys import ApiKeysResource

            self._api_keys = ApiKeysResource(self)
        return self._api_keys

    @property
    def environments(self) -> EnvironmentsResource:
        """Access the Environments API (v2 team-scoped)."""
        if self._environments is None:
            from .resources.environments import EnvironmentsResource

            self._environments = EnvironmentsResource(self)
        return self._environments

    @property
    def service_map_dependencies(self) -> ServiceMapDependenciesResource:
        """Access the Service Map Dependencies API."""
        if self._service_map_dependencies is None:
            from .resources.service_map_dependencies import ServiceMapDependenciesResource

            self._service_map_dependencies = ServiceMapDependenciesResource(self)
        return self._service_map_dependencies

    # -------------------------------------------------------------------------
    # HTTP client management
    # -------------------------------------------------------------------------

    def _get_sync_client(self) -> httpx.Client:
        """Get or create the sync HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self._base_url,
                headers=self._auth.get_headers(),
                timeout=self._timeout,
            )
        return self._sync_client

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._auth.get_headers(),
                timeout=self._timeout,
            )
        return self._async_client

    # -------------------------------------------------------------------------
    # Context managers
    # -------------------------------------------------------------------------

    async def __aenter__(self) -> HoneycombClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.aclose()

    def __enter__(self) -> HoneycombClient:
        """Sync context manager entry."""
        if not self._sync_mode:
            raise RuntimeError("Use 'async with' for async mode, or pass sync=True to constructor")
        return self

    def __exit__(self, *args: Any) -> None:
        """Sync context manager exit."""
        self.close()

    async def aclose(self) -> None:
        """Close async HTTP client."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    def close(self) -> None:
        """Close sync HTTP client."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None

    # -------------------------------------------------------------------------
    # Request methods (internal)
    # -------------------------------------------------------------------------

    def _parse_rate_limit_headers(self, response: httpx.Response) -> RateLimitInfo:
        """Parse rate limit information from response headers.

        Supports multiple header formats:
        - RateLimit: limit=100, remaining=50, reset=60
        - X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
        """
        info = RateLimitInfo()

        # Try structured RateLimit header (RFC draft)
        if "RateLimit" in response.headers:
            rate_limit = response.headers["RateLimit"]
            for part in rate_limit.split(","):
                part = part.strip()
                if "=" in part:
                    key, value = part.split("=", 1)
                    key = key.strip()
                    try:
                        if key == "limit":
                            info.limit = int(value)
                        elif key == "remaining":
                            info.remaining = int(value)
                        elif key == "reset":
                            info.reset = int(value)
                    except ValueError:
                        pass

        # Try X-RateLimit-* headers (common format)
        if "X-RateLimit-Limit" in response.headers:
            with suppress(ValueError):
                info.limit = int(response.headers["X-RateLimit-Limit"])

        if "X-RateLimit-Remaining" in response.headers:
            with suppress(ValueError):
                info.remaining = int(response.headers["X-RateLimit-Remaining"])

        if "X-RateLimit-Reset" in response.headers:
            with suppress(ValueError):
                info.reset = int(response.headers["X-RateLimit-Reset"])

        return info

    def _parse_retry_after(self, response: httpx.Response) -> int | None:
        """Parse Retry-After header.

        Supports both formats:
        - Delay-seconds: "60"
        - HTTP-date: "Wed, 21 Oct 2015 07:28:00 GMT"

        Returns:
            Number of seconds to wait, or None if header not present.
        """
        retry_after = response.headers.get("Retry-After")
        if not retry_after:
            return None

        # Try parsing as integer (seconds)
        try:
            return int(retry_after)
        except ValueError:
            pass

        # Try parsing as HTTP date (RFC 7231)
        try:
            retry_date = parsedate_to_datetime(retry_after)
            now = datetime.now(retry_date.tzinfo)
            delta = (retry_date - now).total_seconds()
            return max(int(delta), 0)
        except (ValueError, TypeError):
            pass

        return None

    def _parse_error_response(self, response: httpx.Response) -> tuple[str, list[dict] | None]:
        """Parse error message from response body.

        Handles multiple error formats:
        - Simple: {"error": "message"}
        - RFC 7807: {"title": "...", "detail": "..."}
        - JSON:API: {"errors": [{"detail": "..."}]}
        """
        try:
            body = response.json()
        except Exception:
            return response.text or "Unknown error", None

        errors: list[dict] | None = None

        # Simple format (most common for Honeycomb)
        if "error" in body:
            return body["error"], None

        # RFC 7807 Problem Details
        if "title" in body:
            msg = body["title"]
            if "detail" in body:
                msg = f"{msg}: {body['detail']}"
            errors = body.get("type_detail")
            return msg, errors

        # JSON:API format
        if "errors" in body and isinstance(body["errors"], list):
            first = body["errors"][0] if body["errors"] else {}
            msg = first.get("detail") or first.get("title") or "Unknown error"
            return msg, body["errors"]

        return str(body), None

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Raise appropriate exception for error responses."""
        if response.is_success:
            return

        status = response.status_code
        message, errors = self._parse_error_response(response)
        request_id = response.headers.get("X-Request-Id")

        if status == 401:
            raise HoneycombAuthError(message, status, request_id)
        elif status == 403:
            raise HoneycombForbiddenError(message, status, request_id)
        elif status == 404:
            raise HoneycombNotFoundError(message, status, request_id)
        elif status == 422:
            raise HoneycombValidationError(message, status, request_id, errors=errors)
        elif status == 429:
            retry_after = self._parse_retry_after(response)
            raise HoneycombRateLimitError(message, status, request_id, retry_after=retry_after)
        elif 500 <= status < 600:
            raise HoneycombServerError(message, status, request_id)
        else:
            raise HoneycombAPIError(message, status, request_id)

    def _should_retry(self, response: httpx.Response, attempt: int) -> bool:
        """Determine if request should be retried."""
        if attempt >= self._retry_config.max_retries:
            return False
        return response.status_code in self._retry_config.retry_statuses

    def _calculate_backoff(self, attempt: int, retry_after: int | None = None) -> float:
        """Calculate backoff delay for retry.

        Args:
            attempt: The current retry attempt number (0-indexed).
            retry_after: Explicit retry delay in seconds from server (optional).

        Returns:
            Number of seconds to wait before retrying.
        """
        if retry_after:
            return float(retry_after)

        # Exponential backoff: base_delay * (exponential_base ^ attempt)
        delay = self._retry_config.base_delay * (self._retry_config.exponential_base**attempt)
        return min(delay, self._retry_config.max_delay)

    # -------------------------------------------------------------------------
    # Async request methods
    # -------------------------------------------------------------------------

    async def _request_async(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make an async HTTP request with retry logic."""
        client = self._get_async_client()
        last_response: httpx.Response | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                    headers=headers,
                )
                last_response = response

                if response.is_success:
                    return response

                if self._should_retry(response, attempt):
                    retry_after = self._parse_retry_after(response)
                    delay = self._calculate_backoff(attempt, retry_after)
                    await asyncio.sleep(delay)
                    continue

                # Non-retryable error
                self._raise_for_status(response)

            except httpx.TimeoutException as e:
                if attempt < self._max_retries:
                    await asyncio.sleep(self._calculate_backoff(attempt))
                    continue
                raise HoneycombTimeoutError(timeout=self._timeout) from e

            except httpx.ConnectError as e:
                if attempt < self._max_retries:
                    await asyncio.sleep(self._calculate_backoff(attempt))
                    continue
                raise HoneycombConnectionError(original_error=e) from e

        # Should not reach here, but just in case
        if last_response is not None:
            self._raise_for_status(last_response)
        raise HoneycombAPIError("Max retries exceeded", 0)

    async def get_async(self, path: str, *, params: dict | None = None) -> httpx.Response:
        """Make an async GET request."""
        return await self._request_async("GET", path, params=params)

    async def post_async(
        self,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make an async POST request."""
        return await self._request_async("POST", path, json=json, params=params, headers=headers)

    async def put_async(
        self,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make an async PUT request."""
        return await self._request_async("PUT", path, json=json, params=params, headers=headers)

    async def patch_async(
        self,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make an async PATCH request."""
        return await self._request_async("PATCH", path, json=json, params=params, headers=headers)

    async def delete_async(self, path: str, *, params: dict | None = None) -> httpx.Response:
        """Make an async DELETE request."""
        return await self._request_async("DELETE", path, params=params)

    # -------------------------------------------------------------------------
    # Sync request methods
    # -------------------------------------------------------------------------

    def _request_sync(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make a sync HTTP request with retry logic."""
        import time

        client = self._get_sync_client()
        last_response: httpx.Response | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                    headers=headers,
                )
                last_response = response

                if response.is_success:
                    return response

                if self._should_retry(response, attempt):
                    retry_after = self._parse_retry_after(response)
                    delay = self._calculate_backoff(attempt, retry_after)
                    time.sleep(delay)
                    continue

                # Non-retryable error
                self._raise_for_status(response)

            except httpx.TimeoutException as e:
                if attempt < self._max_retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                raise HoneycombTimeoutError(timeout=self._timeout) from e

            except httpx.ConnectError as e:
                if attempt < self._max_retries:
                    time.sleep(self._calculate_backoff(attempt))
                    continue
                raise HoneycombConnectionError(original_error=e) from e

        # Should not reach here, but just in case
        if last_response is not None:
            self._raise_for_status(last_response)
        raise HoneycombAPIError("Max retries exceeded", 0)

    def get_sync(self, path: str, *, params: dict | None = None) -> httpx.Response:
        """Make a sync GET request."""
        return self._request_sync("GET", path, params=params)

    def post_sync(
        self,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make a sync POST request."""
        return self._request_sync("POST", path, json=json, params=params, headers=headers)

    def put_sync(
        self,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make a sync PUT request."""
        return self._request_sync("PUT", path, json=json, params=params, headers=headers)

    def patch_sync(
        self,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make a sync PATCH request."""
        return self._request_sync("PATCH", path, json=json, params=params, headers=headers)

    def delete_sync(self, path: str, *, params: dict | None = None) -> httpx.Response:
        """Make a sync DELETE request."""
        return self._request_sync("DELETE", path, params=params)

    # -------------------------------------------------------------------------
    # Convenience properties
    # -------------------------------------------------------------------------

    @property
    def is_sync(self) -> bool:
        """Return True if client is in sync mode."""
        return self._sync_mode

    @property
    def base_url(self) -> str:
        """Return the API base URL."""
        return self._base_url
