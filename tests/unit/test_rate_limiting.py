"""Tests for rate limiting and retry functionality."""

from datetime import datetime, timezone
from email.utils import format_datetime

import httpx
import pytest
import respx

from honeycomb import HoneycombClient, RateLimitInfo, RetryConfig
from honeycomb.exceptions import HoneycombNotFoundError, HoneycombRateLimitError


class TestRateLimitInfo:
    """Tests for RateLimitInfo dataclass."""

    def test_default_values(self):
        """Test RateLimitInfo with default values."""
        info = RateLimitInfo()
        assert info.limit is None
        assert info.remaining is None
        assert info.reset is None

    def test_with_values(self):
        """Test RateLimitInfo with explicit values."""
        info = RateLimitInfo(limit=100, remaining=50, reset=60)
        assert info.limit == 100
        assert info.remaining == 50
        assert info.reset == 60


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_default_values(self):
        """Test RetryConfig with default values."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 30.0
        assert config.exponential_base == 2.0
        assert config.retry_statuses == {429, 500, 502, 503, 504}

    def test_custom_values(self):
        """Test RetryConfig with custom values."""
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=60.0,
            exponential_base=3.0,
            retry_statuses={429, 503},
        )
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 3.0
        assert config.retry_statuses == {429, 503}


class TestParseRateLimitHeaders:
    """Tests for rate limit header parsing."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return HoneycombClient(api_key="test-key")

    def test_parse_structured_ratelimit_header(self, client):
        """Test parsing structured RateLimit header."""
        response = httpx.Response(
            200,
            headers={"RateLimit": "limit=100, remaining=50, reset=60"},
        )
        info = client._parse_rate_limit_headers(response)

        assert info.limit == 100
        assert info.remaining == 50
        assert info.reset == 60

    def test_parse_x_ratelimit_headers(self, client):
        """Test parsing X-RateLimit-* headers."""
        response = httpx.Response(
            200,
            headers={
                "X-RateLimit-Limit": "200",
                "X-RateLimit-Remaining": "150",
                "X-RateLimit-Reset": "120",
            },
        )
        info = client._parse_rate_limit_headers(response)

        assert info.limit == 200
        assert info.remaining == 150
        assert info.reset == 120

    def test_parse_no_rate_limit_headers(self, client):
        """Test parsing when no rate limit headers present."""
        response = httpx.Response(200, headers={})
        info = client._parse_rate_limit_headers(response)

        assert info.limit is None
        assert info.remaining is None
        assert info.reset is None

    def test_parse_invalid_rate_limit_values(self, client):
        """Test handling invalid rate limit values."""
        response = httpx.Response(
            200,
            headers={
                "X-RateLimit-Limit": "invalid",
                "X-RateLimit-Remaining": "50",
            },
        )
        info = client._parse_rate_limit_headers(response)

        # Invalid values should be ignored
        assert info.limit is None
        assert info.remaining == 50


class TestParseRetryAfter:
    """Tests for Retry-After header parsing."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return HoneycombClient(api_key="test-key")

    def test_parse_retry_after_seconds(self, client):
        """Test parsing Retry-After as seconds."""
        response = httpx.Response(429, headers={"Retry-After": "60"})
        retry_after = client._parse_retry_after(response)

        assert retry_after == 60

    def test_parse_retry_after_http_date(self, client):
        """Test parsing Retry-After as HTTP date."""
        # Create a date 60 seconds in the future
        future_date = datetime.now(timezone.utc)
        # Add 60 seconds worth of microseconds
        future_date = future_date.replace(microsecond=0)
        future_date = datetime.fromtimestamp(
            future_date.timestamp() + 60,
            tz=timezone.utc,
        )

        date_str = format_datetime(future_date, usegmt=True)
        response = httpx.Response(429, headers={"Retry-After": date_str})
        retry_after = client._parse_retry_after(response)

        # Should be approximately 60 seconds (allow 5 second margin for test execution)
        assert retry_after is not None
        assert 55 <= retry_after <= 65

    def test_parse_retry_after_missing(self, client):
        """Test parsing when Retry-After header is missing."""
        response = httpx.Response(429, headers={})
        retry_after = client._parse_retry_after(response)

        assert retry_after is None

    def test_parse_retry_after_invalid(self, client):
        """Test parsing invalid Retry-After value."""
        response = httpx.Response(429, headers={"Retry-After": "invalid"})
        retry_after = client._parse_retry_after(response)

        assert retry_after is None


class TestCalculateBackoff:
    """Tests for exponential backoff calculation."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return HoneycombClient(api_key="test-key")

    def test_backoff_uses_retry_after_when_provided(self, client):
        """Test backoff uses explicit retry_after value."""
        delay = client._calculate_backoff(attempt=0, retry_after=45)
        assert delay == 45.0

    def test_backoff_exponential_growth(self, client):
        """Test exponential backoff growth."""
        # Default: base_delay=1.0, exponential_base=2.0
        assert client._calculate_backoff(0) == 1.0  # 1 * 2^0
        assert client._calculate_backoff(1) == 2.0  # 1 * 2^1
        assert client._calculate_backoff(2) == 4.0  # 1 * 2^2
        assert client._calculate_backoff(3) == 8.0  # 1 * 2^3

    def test_backoff_respects_max_delay(self, client):
        """Test backoff respects max_delay."""
        # Attempt 10 would be 1024 seconds, but should cap at 30
        delay = client._calculate_backoff(10)
        assert delay == 30.0

    def test_backoff_with_custom_config(self):
        """Test backoff with custom RetryConfig."""
        config = RetryConfig(base_delay=2.0, exponential_base=3.0, max_delay=100.0)
        client = HoneycombClient(api_key="test-key", retry_config=config)

        assert client._calculate_backoff(0) == 2.0  # 2 * 3^0
        assert client._calculate_backoff(1) == 6.0  # 2 * 3^1
        assert client._calculate_backoff(2) == 18.0  # 2 * 3^2
        assert client._calculate_backoff(5) == 100.0  # Capped at max_delay


class TestShouldRetry:
    """Tests for retry decision logic."""

    @pytest.fixture
    def client(self):
        """Create a test client with max_retries=3."""
        return HoneycombClient(api_key="test-key", max_retries=3)

    def test_should_retry_429(self, client):
        """Test should retry on 429 rate limit."""
        response = httpx.Response(429)
        assert client._should_retry(response, attempt=0) is True

    def test_should_retry_500(self, client):
        """Test should retry on 500 server error."""
        response = httpx.Response(500)
        assert client._should_retry(response, attempt=0) is True

    def test_should_retry_502(self, client):
        """Test should retry on 502 bad gateway."""
        response = httpx.Response(502)
        assert client._should_retry(response, attempt=0) is True

    def test_should_retry_503(self, client):
        """Test should retry on 503 service unavailable."""
        response = httpx.Response(503)
        assert client._should_retry(response, attempt=0) is True

    def test_should_not_retry_404(self, client):
        """Test should not retry on 404 not found."""
        response = httpx.Response(404)
        assert client._should_retry(response, attempt=0) is False

    def test_should_not_retry_when_max_retries_exceeded(self, client):
        """Test should not retry when max attempts reached."""
        response = httpx.Response(500)
        assert client._should_retry(response, attempt=3) is False

    def test_custom_retry_statuses(self):
        """Test custom retry status codes."""
        config = RetryConfig(retry_statuses={429, 503})
        client = HoneycombClient(api_key="test-key", retry_config=config)

        assert client._should_retry(httpx.Response(429), 0) is True
        assert client._should_retry(httpx.Response(503), 0) is True
        assert client._should_retry(httpx.Response(500), 0) is False  # Not in custom set


@pytest.mark.asyncio
class TestRetryBehavior:
    """Integration tests for retry behavior."""

    @respx.mock
    async def test_retries_on_429_with_retry_after(self, respx_mock):
        """Test retry on 429 with Retry-After header."""
        client = HoneycombClient(api_key="test-key", max_retries=2)

        # First request returns 429 with Retry-After
        route = respx_mock.get("https://api.honeycomb.io/test").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "0"}),
                httpx.Response(200, json={"result": "success"}),
            ]
        )

        async with client:
            response = await client.get_async("/test")
            assert response.status_code == 200
            assert route.call_count == 2

    @respx.mock
    async def test_retries_on_500(self, respx_mock):
        """Test retry on 500 server error."""
        client = HoneycombClient(api_key="test-key", max_retries=2)

        route = respx_mock.get("https://api.honeycomb.io/test").mock(
            side_effect=[
                httpx.Response(500),
                httpx.Response(200, json={"result": "success"}),
            ]
        )

        async with client:
            response = await client.get_async("/test")
            assert response.status_code == 200
            assert route.call_count == 2

    @respx.mock
    async def test_raises_after_max_retries(self, respx_mock):
        """Test raises exception after exhausting retries."""
        client = HoneycombClient(api_key="test-key", max_retries=2)

        respx_mock.get("https://api.honeycomb.io/test").mock(
            return_value=httpx.Response(429, json={"error": "Rate limited"})
        )

        async with client:
            with pytest.raises(HoneycombRateLimitError) as exc_info:
                await client.get_async("/test")

            assert exc_info.value.status_code == 429

    @respx.mock
    async def test_no_retry_on_404(self, respx_mock):
        """Test does not retry on 404."""
        client = HoneycombClient(api_key="test-key", max_retries=3)

        route = respx_mock.get("https://api.honeycomb.io/test").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )

        async with client:
            with pytest.raises(HoneycombNotFoundError):  # Should raise without retrying
                await client.get_async("/test")

            # Should only be called once (no retries)
            assert route.call_count == 1


def test_sync_retry_behavior():
    """Test retry behavior in sync mode."""
    with respx.mock:
        client = HoneycombClient(api_key="test-key", max_retries=2, sync=True)

        route = respx.get("https://api.honeycomb.io/test").mock(
            side_effect=[
                httpx.Response(500),
                httpx.Response(200, json={"result": "success"}),
            ]
        )

        with client:
            response = client.get_sync("/test")
            assert response.status_code == 200
            assert route.call_count == 2
