"""Smoke tests for the generated Honeycomb API client."""

from honeycomb._generated import AuthenticatedClient
from honeycomb._generated.models.dataset import Dataset
from honeycomb._generated.models.slo import SLO
from honeycomb._generated.models.slo_create import SLOCreate
from honeycomb._generated.models.trigger_response import TriggerResponse


class TestGeneratedClientImports:
    """Test that all expected modules can be imported."""

    def test_client_imports(self):
        """Test client classes can be imported."""
        from honeycomb._generated import AuthenticatedClient, Client

        assert Client is not None
        assert AuthenticatedClient is not None

    def test_trigger_api_imports(self):
        """Test trigger API functions can be imported."""
        from honeycomb._generated.api.triggers import (
            create_trigger,
            delete_trigger,
            get_trigger,
            list_triggers,
            update_trigger,
        )

        assert all([list_triggers, create_trigger, get_trigger, update_trigger, delete_trigger])

    def test_slo_api_imports(self):
        """Test SLO API functions can be imported."""
        from honeycomb._generated.api.sl_os import (
            create_slo,
            delete_slo,
            get_slo,
            list_slos,
            update_slo,
        )

        assert all([list_slos, create_slo, get_slo, update_slo, delete_slo])

    def test_query_api_imports(self):
        """Test Query API functions can be imported."""
        from honeycomb._generated.api.queries import create_query, get_query
        from honeycomb._generated.api.query_data import create_query_result, get_query_result

        assert all([create_query, get_query, create_query_result, get_query_result])

    def test_board_api_imports(self):
        """Test Board API functions can be imported."""
        from honeycomb._generated.api.boards import (
            create_board,
            delete_board,
            get_board,
            list_boards,
            update_board,
        )

        assert all([list_boards, create_board, get_board, update_board, delete_board])


class TestClientInstantiation:
    """Test client can be instantiated correctly."""

    def test_authenticated_client_creation(self):
        """Test AuthenticatedClient can be created with token."""
        client = AuthenticatedClient(
            base_url="https://api.honeycomb.io",
            token="test-token-123",
        )

        assert client._base_url == "https://api.honeycomb.io"
        assert client.token == "test-token-123"

    def test_authenticated_client_custom_header(self):
        """Test AuthenticatedClient can use custom auth header name."""
        client = AuthenticatedClient(
            base_url="https://api.honeycomb.io",
            token="test-token-123",
            auth_header_name="X-Honeycomb-Team",
            prefix="",  # No prefix for API key auth
        )

        assert client.auth_header_name == "X-Honeycomb-Team"
        assert client.prefix == ""

    def test_client_with_headers(self):
        """Test client can add custom headers."""
        client = AuthenticatedClient(
            base_url="https://api.honeycomb.io",
            token="test-token",
        )

        new_client = client.with_headers({"X-Custom-Header": "value"})

        assert "X-Custom-Header" in new_client._headers

    def test_client_with_timeout(self):
        """Test client can set timeout."""
        import httpx

        client = AuthenticatedClient(
            base_url="https://api.honeycomb.io",
            token="test-token",
        )

        new_client = client.with_timeout(httpx.Timeout(30.0))

        assert new_client._timeout is not None


class TestModelSerialization:
    """Test that models can be serialized and deserialized."""

    def test_slo_create_to_dict(self):
        """Test SLOCreate model can be converted to dict."""
        from honeycomb._generated.models.slo_create_sli import SLOCreateSli

        slo = SLOCreate(
            name="Test SLO",
            time_period_days=30,
            target_per_million=999000,
            sli=SLOCreateSli(alias="sli_good"),
        )

        data = slo.to_dict()

        assert data["name"] == "Test SLO"
        assert data["time_period_days"] == 30
        assert data["target_per_million"] == 999000
        assert data["sli"]["alias"] == "sli_good"

    def test_slo_from_dict(self):
        """Test SLO model can be created from dict."""
        data = {
            "id": "slo-123",
            "name": "Test SLO",
            "time_period_days": 30,
            "target_per_million": 999000,
            "sli": {"alias": "sli_good"},
        }

        slo = SLO.from_dict(data)

        assert slo.id == "slo-123"
        assert slo.name == "Test SLO"

    def test_trigger_response_from_dict(self):
        """Test TriggerResponse model can be created from dict."""
        data = {
            "id": "trigger-456",
            "name": "High Latency Alert",
            "dataset_slug": "production",
            "frequency": 300,
            "disabled": False,
        }

        trigger = TriggerResponse.from_dict(data)

        assert trigger.id == "trigger-456"
        assert trigger.name == "High Latency Alert"
        assert trigger.frequency == 300

    def test_dataset_from_dict(self):
        """Test Dataset model can be created from dict."""
        data = {
            "name": "Production Dataset",
            "slug": "production",
            "description": "Production telemetry data",
        }

        dataset = Dataset.from_dict(data)

        assert dataset.name == "Production Dataset"
        assert dataset.slug == "production"


class TestApiEndpointSignatures:
    """Test that API endpoint functions have expected signatures."""

    def test_list_triggers_signature(self):
        """Test list_triggers has expected parameters."""
        import inspect

        from honeycomb._generated.api.triggers import list_triggers

        sig = inspect.signature(list_triggers.sync)
        params = list(sig.parameters.keys())

        assert "dataset_slug" in params
        assert "client" in params

    def test_create_slo_signature(self):
        """Test create_slo has expected parameters."""
        import inspect

        from honeycomb._generated.api.sl_os import create_slo

        sig = inspect.signature(create_slo.sync)
        params = list(sig.parameters.keys())

        assert "dataset_slug" in params
        assert "client" in params
        assert "body" in params

    def test_async_variants_exist(self):
        """Test that async variants exist for key endpoints."""
        from honeycomb._generated.api.sl_os import create_slo, list_slos
        from honeycomb._generated.api.triggers import create_trigger, list_triggers

        # Each module should have sync and asyncio functions
        assert hasattr(list_triggers, "sync")
        assert hasattr(list_triggers, "asyncio")
        assert hasattr(create_trigger, "sync")
        assert hasattr(create_trigger, "asyncio")
        assert hasattr(list_slos, "sync")
        assert hasattr(list_slos, "asyncio")
        assert hasattr(create_slo, "sync")
        assert hasattr(create_slo, "asyncio")
