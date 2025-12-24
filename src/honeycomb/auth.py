"""Authentication strategies for Honeycomb API."""

from abc import ABC, abstractmethod

import httpx


class AuthStrategy(ABC):
    """Base class for authentication strategies."""

    @abstractmethod
    def apply_to_request(self, request: httpx.Request) -> httpx.Request:
        """Apply authentication to an HTTP request.

        Args:
            request: The httpx Request to authenticate.

        Returns:
            The authenticated request.
        """
        ...

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns:
            Dictionary of headers to add to requests.
        """
        ...


class APIKeyAuth(AuthStrategy):
    """Authentication using a Honeycomb API key.

    This is the standard authentication method for single-environment access.
    Uses the X-Honeycomb-Team header.

    Example:
        >>> auth = APIKeyAuth("hcaik_01234567890123456789")
        >>> headers = auth.get_headers()
        >>> # {"X-Honeycomb-Team": "hcaik_01234567890123456789"}
    """

    HEADER_NAME = "X-Honeycomb-Team"

    def __init__(self, api_key: str) -> None:
        """Initialize API key authentication.

        Args:
            api_key: The Honeycomb API key (typically starts with 'hcaik_').
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        self.api_key = api_key

    def apply_to_request(self, request: httpx.Request) -> httpx.Request:
        """Apply API key authentication to request."""
        request.headers[self.HEADER_NAME] = self.api_key
        return request

    def get_headers(self) -> dict[str, str]:
        """Get API key authentication headers."""
        return {self.HEADER_NAME: self.api_key}


class ManagementKeyAuth(AuthStrategy):
    """Authentication using a Honeycomb Management API key.

    This authentication method is for multi-environment management operations.
    Uses the Authorization header with Bearer token format: "Bearer {key_id}:{key_secret}".

    Example:
        >>> auth = ManagementKeyAuth(
        ...     key_id="hcamk_01234567890123456789",
        ...     key_secret="abcdef123456"
        ... )
        >>> headers = auth.get_headers()
        >>> # {"Authorization": "Bearer hcamk_01234567890123456789:abcdef123456"}
    """

    HEADER_NAME = "Authorization"

    def __init__(self, key_id: str, key_secret: str) -> None:
        """Initialize Management API key authentication.

        Args:
            key_id: The Management API key ID (typically starts with 'hcamk_').
            key_secret: The Management API key secret.
        """
        if not key_id:
            raise ValueError("Management key ID cannot be empty")
        if not key_secret:
            raise ValueError("Management key secret cannot be empty")
        self.key_id = key_id
        self.key_secret = key_secret

    @property
    def token(self) -> str:
        """Get the combined token for the Authorization header."""
        return f"{self.key_id}:{self.key_secret}"

    def apply_to_request(self, request: httpx.Request) -> httpx.Request:
        """Apply Management key authentication to request."""
        request.headers[self.HEADER_NAME] = f"Bearer {self.token}"
        return request

    def get_headers(self) -> dict[str, str]:
        """Get Management key authentication headers."""
        return {self.HEADER_NAME: f"Bearer {self.token}"}


def create_auth(
    *,
    api_key: str | None = None,
    management_key: str | None = None,
    management_secret: str | None = None,
) -> AuthStrategy:
    """Create an appropriate authentication strategy based on provided credentials.

    Args:
        api_key: Honeycomb API key for single-environment access.
        management_key: Management API key ID for multi-environment access.
        management_secret: Management API key secret.

    Returns:
        An AuthStrategy instance.

    Raises:
        ValueError: If no credentials provided or invalid combination.

    Example:
        >>> # API key auth
        >>> auth = create_auth(api_key="hcaik_xxx")

        >>> # Management key auth
        >>> auth = create_auth(management_key="hcamk_xxx", management_secret="secret")
    """
    if api_key and (management_key or management_secret):
        raise ValueError("Cannot use both api_key and management_key authentication")

    if api_key:
        return APIKeyAuth(api_key)

    if management_key or management_secret:
        if not management_key:
            raise ValueError("management_key is required when using management_secret")
        if not management_secret:
            raise ValueError("management_secret is required when using management_key")
        return ManagementKeyAuth(management_key, management_secret)

    raise ValueError("Must provide either api_key or both management_key and management_secret")
