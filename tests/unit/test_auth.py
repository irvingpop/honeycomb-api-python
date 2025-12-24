"""Tests for authentication strategies."""

import pytest

from honeycomb.auth import APIKeyAuth, ManagementKeyAuth, create_auth


class TestAPIKeyAuth:
    """Tests for APIKeyAuth strategy."""

    def test_init_with_valid_key(self):
        """Test initialization with a valid API key."""
        auth = APIKeyAuth("hcaik_01234567890123456789")
        assert auth.api_key == "hcaik_01234567890123456789"

    def test_init_with_empty_key_raises(self):
        """Test that empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            APIKeyAuth("")

    def test_get_headers(self):
        """Test that get_headers returns correct header."""
        auth = APIKeyAuth("test-key")
        headers = auth.get_headers()

        assert headers == {"X-Honeycomb-Team": "test-key"}

    def test_header_name_constant(self):
        """Test that header name is X-Honeycomb-Team."""
        assert APIKeyAuth.HEADER_NAME == "X-Honeycomb-Team"


class TestManagementKeyAuth:
    """Tests for ManagementKeyAuth strategy."""

    def test_init_with_valid_credentials(self):
        """Test initialization with valid credentials."""
        auth = ManagementKeyAuth("hcamk_key123", "secret456")
        assert auth.key_id == "hcamk_key123"
        assert auth.key_secret == "secret456"

    def test_init_with_empty_key_id_raises(self):
        """Test that empty key ID raises ValueError."""
        with pytest.raises(ValueError, match="Management key ID cannot be empty"):
            ManagementKeyAuth("", "secret")

    def test_init_with_empty_secret_raises(self):
        """Test that empty secret raises ValueError."""
        with pytest.raises(ValueError, match="Management key secret cannot be empty"):
            ManagementKeyAuth("key", "")

    def test_token_property(self):
        """Test that token property combines key_id and key_secret."""
        auth = ManagementKeyAuth("key123", "secret456")
        assert auth.token == "key123:secret456"

    def test_get_headers(self):
        """Test that get_headers returns correct Authorization header."""
        auth = ManagementKeyAuth("key123", "secret456")
        headers = auth.get_headers()

        assert headers == {"Authorization": "Bearer key123:secret456"}

    def test_header_name_constant(self):
        """Test that header name is Authorization."""
        assert ManagementKeyAuth.HEADER_NAME == "Authorization"


class TestCreateAuth:
    """Tests for create_auth factory function."""

    def test_create_with_api_key(self):
        """Test creating APIKeyAuth with api_key parameter."""
        auth = create_auth(api_key="test-api-key")

        assert isinstance(auth, APIKeyAuth)
        assert auth.api_key == "test-api-key"

    def test_create_with_management_key(self):
        """Test creating ManagementKeyAuth with management credentials."""
        auth = create_auth(management_key="key123", management_secret="secret456")

        assert isinstance(auth, ManagementKeyAuth)
        assert auth.key_id == "key123"
        assert auth.key_secret == "secret456"

    def test_create_with_no_credentials_raises(self):
        """Test that no credentials raises ValueError."""
        with pytest.raises(ValueError, match="Must provide either api_key"):
            create_auth()

    def test_create_with_both_auth_types_raises(self):
        """Test that providing both auth types raises ValueError."""
        with pytest.raises(ValueError, match="Cannot use both"):
            create_auth(api_key="key", management_key="mgmt")

    def test_create_with_api_key_and_management_secret_raises(self):
        """Test that api_key with management_secret raises ValueError."""
        with pytest.raises(ValueError, match="Cannot use both"):
            create_auth(api_key="key", management_secret="secret")

    def test_create_with_only_management_key_raises(self):
        """Test that only management_key without secret raises ValueError."""
        with pytest.raises(ValueError, match="management_secret is required"):
            create_auth(management_key="key123")

    def test_create_with_only_management_secret_raises(self):
        """Test that only management_secret without key raises ValueError."""
        with pytest.raises(ValueError, match="management_key is required"):
            create_auth(management_secret="secret456")
