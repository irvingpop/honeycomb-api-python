"""Exception hierarchy for Honeycomb API errors."""

from __future__ import annotations

from typing import Any


class HoneycombAPIError(Exception):
    """Base exception for all Honeycomb API errors.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code from the response.
        request_id: Honeycomb request ID for support debugging (if available).
        response_body: Raw response body (if available).
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        request_id: str | None = None,
        response_body: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.response_body = response_body

    def __str__(self) -> str:
        parts = [f"[{self.status_code}] {self.message}"]
        if self.request_id:
            parts.append(f"(request_id: {self.request_id})")
        return " ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"request_id={self.request_id!r})"
        )


class HoneycombAuthError(HoneycombAPIError):
    """401 Unauthorized - Invalid or missing API key.

    Raised when the API key is missing, invalid, or expired.
    """

    pass


class HoneycombForbiddenError(HoneycombAPIError):
    """403 Forbidden - Insufficient permissions.

    Raised when the API key doesn't have permission for the requested operation.
    """

    pass


class HoneycombNotFoundError(HoneycombAPIError):
    """404 Not Found - Resource doesn't exist.

    Raised when the requested resource (dataset, trigger, SLO, etc.) is not found.
    """

    pass


class HoneycombValidationError(HoneycombAPIError):
    """422 Validation Error - Invalid request data.

    Raised when the request body fails validation.

    Attributes:
        errors: List of field-level validation errors (if available).
                Can be dicts, strings, or other types depending on API response format.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 422,
        request_id: str | None = None,
        response_body: dict | None = None,
        errors: list[Any] | None = None,
    ) -> None:
        super().__init__(message, status_code, request_id, response_body)
        self.errors = errors or []

    def __str__(self) -> str:
        base = super().__str__()
        if self.errors:
            # Handle various error formats from Honeycomb API
            error_parts = []
            for e in self.errors:
                if isinstance(e, dict):
                    # Format 1: {"field": "...", "message": "..."}
                    if "field" in e and "message" in e:
                        error_parts.append(f"{e['field']}: {e['message']}")
                    # Format 2: {"detail": "...", "title": "..."}
                    elif "detail" in e or "title" in e:
                        detail = e.get("detail", e.get("title", ""))
                        error_parts.append(str(detail))
                    # Format 3: Any other dict - just stringify it
                    else:
                        error_parts.append(str(e))
                elif isinstance(e, str):
                    # Format 4: Plain string
                    error_parts.append(e)
                else:
                    # Format 5: Other types - stringify
                    error_parts.append(str(e))

            if error_parts:
                error_details = "; ".join(error_parts)
                return f"{base} - {error_details}"
        return base


class HoneycombRateLimitError(HoneycombAPIError):
    """429 Rate Limited - Too many requests.

    Raised when the API rate limit has been exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying (if provided by API).
    """

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        request_id: str | None = None,
        response_body: dict | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, status_code, request_id, response_body)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base = super().__str__()
        if self.retry_after:
            return f"{base} (retry after {self.retry_after}s)"
        return base


class HoneycombServerError(HoneycombAPIError):
    """5xx Server Error - Honeycomb service issue.

    Raised when Honeycomb's servers encounter an error.
    These errors are typically transient and can be retried.
    """

    pass


class HoneycombTimeoutError(HoneycombAPIError):
    """Request timed out.

    Raised when a request to the Honeycomb API times out.
    """

    def __init__(
        self,
        message: str = "Request timed out",
        timeout: float | None = None,
    ) -> None:
        super().__init__(message, status_code=0)
        self.timeout = timeout

    def __str__(self) -> str:
        if self.timeout:
            return f"{self.message} (timeout: {self.timeout}s)"
        return self.message


class HoneycombConnectionError(HoneycombAPIError):
    """Connection error.

    Raised when unable to connect to the Honeycomb API.
    """

    def __init__(
        self,
        message: str = "Failed to connect to Honeycomb API",
        original_error: Exception | None = None,
    ) -> None:
        super().__init__(message, status_code=0)
        self.original_error = original_error


def raise_for_status(
    status_code: int,
    response_body: dict | None = None,
    request_id: str | None = None,
) -> None:
    """Raise an appropriate exception based on HTTP status code.

    Args:
        status_code: HTTP status code from the response.
        response_body: Parsed response body (if available).
        request_id: Request ID from response headers (if available).

    Raises:
        HoneycombAuthError: For 401 responses.
        HoneycombForbiddenError: For 403 responses.
        HoneycombNotFoundError: For 404 responses.
        HoneycombValidationError: For 422 responses.
        HoneycombRateLimitError: For 429 responses.
        HoneycombServerError: For 5xx responses.
        HoneycombAPIError: For other error responses.
    """
    if 200 <= status_code < 300:
        return

    # Extract error message from response body
    message = "Unknown error"
    errors: list[Any] | None = None
    retry_after: int | None = None

    if response_body:
        # Try different error formats
        if "error" in response_body:
            message = response_body["error"]
        elif "message" in response_body:
            message = response_body["message"]
        elif "title" in response_body:
            message = response_body["title"]
            if "detail" in response_body:
                message = f"{message}: {response_body['detail']}"
        elif "errors" in response_body and isinstance(response_body["errors"], list):
            # JSON:API format
            first_error = response_body["errors"][0] if response_body["errors"] else {}
            message = first_error.get("detail") or first_error.get("title") or message
            errors = response_body["errors"]

        # Extract validation errors
        if "type_detail" in response_body:
            errors = response_body.get("type_detail", [])

    # Map status codes to exceptions
    if status_code == 401:
        raise HoneycombAuthError(message, status_code, request_id, response_body)
    elif status_code == 403:
        raise HoneycombForbiddenError(message, status_code, request_id, response_body)
    elif status_code == 404:
        raise HoneycombNotFoundError(message, status_code, request_id, response_body)
    elif status_code == 422:
        raise HoneycombValidationError(message, status_code, request_id, response_body, errors)
    elif status_code == 429:
        raise HoneycombRateLimitError(message, status_code, request_id, response_body, retry_after)
    elif 500 <= status_code < 600:
        raise HoneycombServerError(message, status_code, request_id, response_body)
    else:
        raise HoneycombAPIError(message, status_code, request_id, response_body)
