"""Tests for exception hierarchy."""

import pytest

from honeycomb.exceptions import (
    HoneycombAPIError,
    HoneycombAuthError,
    HoneycombConnectionError,
    HoneycombForbiddenError,
    HoneycombNotFoundError,
    HoneycombRateLimitError,
    HoneycombServerError,
    HoneycombTimeoutError,
    HoneycombValidationError,
    raise_for_status,
)


class TestHoneycombAPIError:
    """Tests for base HoneycombAPIError."""

    def test_init(self):
        """Test basic initialization."""
        error = HoneycombAPIError("Something went wrong", 500)

        assert error.message == "Something went wrong"
        assert error.status_code == 500
        assert error.request_id is None
        assert error.response_body is None

    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        body = {"error": "test"}
        error = HoneycombAPIError(
            "Error message",
            400,
            request_id="req-123",
            response_body=body,
        )

        assert error.message == "Error message"
        assert error.status_code == 400
        assert error.request_id == "req-123"
        assert error.response_body == body

    def test_str_without_request_id(self):
        """Test string representation without request ID."""
        error = HoneycombAPIError("Error", 500)
        assert str(error) == "[500] Error"

    def test_str_with_request_id(self):
        """Test string representation with request ID."""
        error = HoneycombAPIError("Error", 500, request_id="req-abc")
        assert str(error) == "[500] Error (request_id: req-abc)"

    def test_repr(self):
        """Test repr representation."""
        error = HoneycombAPIError("Error", 500, request_id="req-123")
        assert "HoneycombAPIError" in repr(error)
        assert "message='Error'" in repr(error)
        assert "status_code=500" in repr(error)

    def test_exception_inheritance(self):
        """Test that HoneycombAPIError is an Exception."""
        error = HoneycombAPIError("Error", 500)
        assert isinstance(error, Exception)


class TestSpecificExceptions:
    """Tests for specific exception types."""

    def test_auth_error(self):
        """Test HoneycombAuthError."""
        error = HoneycombAuthError("Invalid API key", 401)
        assert isinstance(error, HoneycombAPIError)
        assert error.status_code == 401

    def test_forbidden_error(self):
        """Test HoneycombForbiddenError."""
        error = HoneycombForbiddenError("Permission denied", 403)
        assert isinstance(error, HoneycombAPIError)
        assert error.status_code == 403

    def test_not_found_error(self):
        """Test HoneycombNotFoundError."""
        error = HoneycombNotFoundError("Dataset not found", 404)
        assert isinstance(error, HoneycombAPIError)
        assert error.status_code == 404

    def test_server_error(self):
        """Test HoneycombServerError."""
        error = HoneycombServerError("Internal error", 500)
        assert isinstance(error, HoneycombAPIError)
        assert error.status_code == 500


class TestValidationError:
    """Tests for HoneycombValidationError."""

    def test_init_without_errors(self):
        """Test initialization without field errors."""
        error = HoneycombValidationError("Invalid input", 422)

        assert error.message == "Invalid input"
        assert error.status_code == 422
        assert error.errors == []

    def test_init_with_errors(self):
        """Test initialization with field errors."""
        field_errors = [
            {"field": "name", "message": "required"},
            {"field": "email", "message": "invalid format"},
        ]
        error = HoneycombValidationError("Validation failed", 422, errors=field_errors)

        assert error.errors == field_errors

    def test_str_with_errors(self):
        """Test string representation includes field errors."""
        field_errors = [{"field": "name", "message": "required"}]
        error = HoneycombValidationError("Validation failed", 422, errors=field_errors)

        assert "name: required" in str(error)


class TestRateLimitError:
    """Tests for HoneycombRateLimitError."""

    def test_init_without_retry_after(self):
        """Test initialization without retry_after."""
        error = HoneycombRateLimitError("Rate limited", 429)

        assert error.message == "Rate limited"
        assert error.retry_after is None

    def test_init_with_retry_after(self):
        """Test initialization with retry_after."""
        error = HoneycombRateLimitError("Rate limited", 429, retry_after=60)

        assert error.retry_after == 60

    def test_str_with_retry_after(self):
        """Test string representation includes retry_after."""
        error = HoneycombRateLimitError("Rate limited", 429, retry_after=30)
        assert "retry after 30s" in str(error)


class TestTimeoutError:
    """Tests for HoneycombTimeoutError."""

    def test_default_message(self):
        """Test default timeout message."""
        error = HoneycombTimeoutError()

        assert error.message == "Request timed out"
        assert error.status_code == 0

    def test_with_timeout_value(self):
        """Test with timeout value."""
        error = HoneycombTimeoutError(timeout=30.0)

        assert error.timeout == 30.0
        assert "30.0s" in str(error)


class TestConnectionError:
    """Tests for HoneycombConnectionError."""

    def test_default_message(self):
        """Test default connection error message."""
        error = HoneycombConnectionError()

        assert "Failed to connect" in error.message
        assert error.status_code == 0

    def test_with_original_error(self):
        """Test with original exception."""
        original = OSError("Connection refused")
        error = HoneycombConnectionError(original_error=original)

        assert error.original_error is original


class TestRaiseForStatus:
    """Tests for raise_for_status function."""

    def test_success_status_does_not_raise(self):
        """Test that 2xx status codes don't raise."""
        raise_for_status(200)
        raise_for_status(201)
        raise_for_status(204)

    def test_401_raises_auth_error(self):
        """Test that 401 raises HoneycombAuthError."""
        with pytest.raises(HoneycombAuthError) as exc_info:
            raise_for_status(401, {"error": "Invalid API key"})

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in exc_info.value.message

    def test_403_raises_forbidden_error(self):
        """Test that 403 raises HoneycombForbiddenError."""
        with pytest.raises(HoneycombForbiddenError) as exc_info:
            raise_for_status(403)

        assert exc_info.value.status_code == 403

    def test_404_raises_not_found_error(self):
        """Test that 404 raises HoneycombNotFoundError."""
        with pytest.raises(HoneycombNotFoundError) as exc_info:
            raise_for_status(404, {"error": "Dataset not found"})

        assert exc_info.value.status_code == 404

    def test_422_raises_validation_error(self):
        """Test that 422 raises HoneycombValidationError."""
        with pytest.raises(HoneycombValidationError) as exc_info:
            raise_for_status(422, {"error": "Validation failed"})

        assert exc_info.value.status_code == 422

    def test_429_raises_rate_limit_error(self):
        """Test that 429 raises HoneycombRateLimitError."""
        with pytest.raises(HoneycombRateLimitError) as exc_info:
            raise_for_status(429, {"error": "Rate limited"})

        assert exc_info.value.status_code == 429

    def test_500_raises_server_error(self):
        """Test that 500 raises HoneycombServerError."""
        with pytest.raises(HoneycombServerError) as exc_info:
            raise_for_status(500)

        assert exc_info.value.status_code == 500

    def test_502_raises_server_error(self):
        """Test that 502 raises HoneycombServerError."""
        with pytest.raises(HoneycombServerError):
            raise_for_status(502)

    def test_other_error_raises_base_error(self):
        """Test that other errors raise HoneycombAPIError."""
        with pytest.raises(HoneycombAPIError) as exc_info:
            raise_for_status(418)  # I'm a teapot

        assert exc_info.value.status_code == 418

    def test_request_id_passed_to_exception(self):
        """Test that request_id is passed to exception."""
        with pytest.raises(HoneycombAPIError) as exc_info:
            raise_for_status(500, request_id="req-xyz")

        assert exc_info.value.request_id == "req-xyz"

    def test_jsonapi_error_format(self):
        """Test parsing JSON:API error format."""
        body = {
            "errors": [
                {"title": "Not Found", "detail": "Resource does not exist"}
            ]
        }
        with pytest.raises(HoneycombNotFoundError) as exc_info:
            raise_for_status(404, body)

        assert "Resource does not exist" in exc_info.value.message

    def test_rfc7807_error_format(self):
        """Test parsing RFC 7807 Problem Details format."""
        body = {
            "title": "Bad Request",
            "detail": "The name field is required",
        }
        with pytest.raises(HoneycombAPIError) as exc_info:
            raise_for_status(400, body)

        assert "Bad Request" in exc_info.value.message
        assert "name field is required" in exc_info.value.message
