"""Tests for the wrapper HoneycombClient and resource classes."""

import pytest
import respx
from httpx import Response

from honeycomb import (
    SLI,
    BoardCreate,
    DatasetCreate,
    HoneycombAuthError,
    HoneycombClient,
    HoneycombNotFoundError,
    HoneycombValidationError,
    SLOCreate,
    Trigger,
    TriggerCreate,
    TriggerQuery,
    TriggerThreshold,
    TriggerThresholdOp,
)


class TestHoneycombClientInit:
    """Tests for HoneycombClient initialization."""

    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = HoneycombClient(api_key="test-key")
        assert client.base_url == "https://api.honeycomb.io"
        assert not client.is_sync

    def test_init_with_custom_base_url(self):
        """Test client initialization with custom base URL."""
        client = HoneycombClient(api_key="test-key", base_url="https://custom.api.io")
        assert client.base_url == "https://custom.api.io"

    def test_init_with_sync_mode(self):
        """Test client initialization in sync mode."""
        client = HoneycombClient(api_key="test-key", sync=True)
        assert client.is_sync

    def test_init_with_management_key(self):
        """Test client initialization with management key."""
        client = HoneycombClient(management_key="key-id", management_secret="secret")
        assert client.base_url == "https://api.honeycomb.io"

    def test_sync_context_manager_requires_sync_mode(self):
        """Test that sync context manager requires sync=True."""
        client = HoneycombClient(api_key="test-key")
        with pytest.raises(RuntimeError, match="Use 'async with'"), client:
            pass

    def test_sync_context_manager_works_with_sync_mode(self):
        """Test sync context manager with sync=True."""
        with HoneycombClient(api_key="test-key", sync=True) as client:
            assert client.is_sync


class TestResourceAccessors:
    """Tests for resource property accessors."""

    def test_triggers_resource_access(self):
        """Test lazy initialization of triggers resource."""
        client = HoneycombClient(api_key="test-key", sync=True)
        triggers = client.triggers
        assert triggers is not None
        # Verify same instance is returned on subsequent access
        assert client.triggers is triggers

    def test_slos_resource_access(self):
        """Test lazy initialization of SLOs resource."""
        client = HoneycombClient(api_key="test-key", sync=True)
        slos = client.slos
        assert slos is not None
        assert client.slos is slos

    def test_datasets_resource_access(self):
        """Test lazy initialization of datasets resource."""
        client = HoneycombClient(api_key="test-key", sync=True)
        datasets = client.datasets
        assert datasets is not None
        assert client.datasets is datasets

    def test_boards_resource_access(self):
        """Test lazy initialization of boards resource."""
        client = HoneycombClient(api_key="test-key", sync=True)
        boards = client.boards
        assert boards is not None
        assert client.boards is boards


class TestPydanticModels:
    """Tests for Pydantic model serialization."""

    def test_trigger_create_model(self):
        """Test TriggerCreate model serialization."""
        trigger = TriggerCreate(
            name="Test Trigger",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.GREATER_THAN,
                value=100.0,
            ),
            frequency=300,
        )
        data = trigger.model_dump_for_api()
        assert data["name"] == "Test Trigger"
        assert data["threshold"]["op"] == ">"
        assert data["threshold"]["value"] == 100.0
        assert data["frequency"] == 300

    def test_trigger_create_with_query(self):
        """Test TriggerCreate with inline query."""
        trigger = TriggerCreate(
            name="Query Trigger",
            threshold=TriggerThreshold(
                op=TriggerThresholdOp.LESS_THAN,
                value=10.0,
            ),
            query=TriggerQuery(
                time_range=900,
            ),
        )
        data = trigger.model_dump_for_api()
        assert "query" in data
        assert data["query"]["time_range"] == 900

    def test_trigger_response_model(self):
        """Test Trigger response model parsing."""
        data = {
            "id": "abc123",
            "name": "Test",
            "dataset_slug": "test-dataset",
            "threshold": {"op": ">", "value": 100},
            "frequency": 300,
            "disabled": False,
            "triggered": False,
        }
        trigger = Trigger.model_validate(data)
        assert trigger.id == "abc123"
        assert trigger.name == "Test"
        assert trigger.threshold.op == TriggerThresholdOp.GREATER_THAN

    def test_slo_create_model(self):
        """Test SLOCreate model serialization."""
        slo = SLOCreate(
            name="Test SLO",
            sli=SLI(alias="test-sli"),
            time_period_days=30,
            target_per_million=999000,
        )
        data = slo.model_dump_for_api()
        assert data["name"] == "Test SLO"
        assert data["time_period_days"] == 30
        assert data["target_per_million"] == 999000

    def test_dataset_create_model(self):
        """Test DatasetCreate model serialization."""
        dataset = DatasetCreate(
            name="Test Dataset",
            description="A test dataset",
        )
        data = dataset.model_dump_for_api()
        assert data["name"] == "Test Dataset"
        assert data["description"] == "A test dataset"

    def test_board_create_model(self):
        """Test BoardCreate model serialization."""
        board = BoardCreate(
            name="Test Board",
            column_layout="multi",
            style="visual",
        )
        data = board.model_dump_for_api()
        assert data["name"] == "Test Board"
        assert data["column_layout"] == "multi"


# -------------------------------------------------------------------------
# Sync resource tests with respx mocking
# -------------------------------------------------------------------------


@respx.mock
def test_list_datasets_sync():
    """Test listing datasets."""
    respx.get("https://api.honeycomb.io/1/datasets").mock(
        return_value=Response(
            200,
            json=[
                {"name": "Dataset 1", "slug": "dataset-1"},
                {"name": "Dataset 2", "slug": "dataset-2"},
            ],
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        datasets = client.datasets.list()
        assert len(datasets) == 2
        assert datasets[0].name == "Dataset 1"
        assert datasets[1].slug == "dataset-2"


@respx.mock
def test_get_dataset_sync():
    """Test getting a specific dataset."""
    respx.get("https://api.honeycomb.io/1/datasets/my-dataset").mock(
        return_value=Response(
            200,
            json={"name": "My Dataset", "slug": "my-dataset"},
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        dataset = client.datasets.get("my-dataset")
        assert dataset.name == "My Dataset"
        assert dataset.slug == "my-dataset"


@respx.mock
def test_create_dataset_sync():
    """Test creating a dataset."""
    respx.post("https://api.honeycomb.io/1/datasets").mock(
        return_value=Response(
            201,
            json={"name": "New Dataset", "slug": "new-dataset"},
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        dataset = client.datasets.create(DatasetCreate(name="New Dataset"))
        assert dataset.name == "New Dataset"


@respx.mock
def test_list_triggers_sync():
    """Test listing triggers."""
    respx.get("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "trigger-1",
                    "name": "Trigger 1",
                    "dataset_slug": "test-dataset",
                    "threshold": {"op": ">", "value": 100},
                    "frequency": 300,
                }
            ],
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        triggers = client.triggers.list("test-dataset")
        assert len(triggers) == 1
        assert triggers[0].name == "Trigger 1"


@respx.mock
def test_create_trigger_sync():
    """Test creating a trigger."""
    respx.post("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(
            201,
            json={
                "id": "new-trigger",
                "name": "New Trigger",
                "dataset_slug": "test-dataset",
                "threshold": {"op": ">", "value": 50},
                "frequency": 300,
            },
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        trigger = client.triggers.create(
            "test-dataset",
            TriggerCreate(
                name="New Trigger",
                threshold=TriggerThreshold(
                    op=TriggerThresholdOp.GREATER_THAN,
                    value=50.0,
                ),
            ),
        )
        assert trigger.id == "new-trigger"
        assert trigger.name == "New Trigger"


@respx.mock
def test_delete_trigger_sync():
    """Test deleting a trigger."""
    respx.delete("https://api.honeycomb.io/1/triggers/test-dataset/trigger-1").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.triggers.delete("test-dataset", "trigger-1")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


@respx.mock
def test_401_raises_auth_error():
    """Test that 401 response raises HoneycombAuthError."""
    respx.get("https://api.honeycomb.io/1/datasets").mock(
        return_value=Response(
            401,
            json={"error": "Invalid API key"},
        )
    )

    with HoneycombClient(api_key="bad-key", sync=True) as client:
        with pytest.raises(HoneycombAuthError) as exc_info:
            client.datasets.list()
        assert "Invalid API key" in str(exc_info.value)


@respx.mock
def test_404_raises_not_found_error():
    """Test that 404 response raises HoneycombNotFoundError."""
    respx.get("https://api.honeycomb.io/1/datasets/nonexistent").mock(
        return_value=Response(
            404,
            json={"error": "Dataset not found"},
        )
    )

    with (
        HoneycombClient(api_key="test-key", sync=True) as client,
        pytest.raises(HoneycombNotFoundError),
    ):
        client.datasets.get("nonexistent")


@respx.mock
def test_422_raises_validation_error():
    """Test that 422 response raises HoneycombValidationError."""
    respx.post("https://api.honeycomb.io/1/triggers/test-dataset").mock(
        return_value=Response(
            422,
            json={"error": "Invalid trigger configuration"},
        )
    )

    with (
        HoneycombClient(api_key="test-key", sync=True) as client,
        pytest.raises(HoneycombValidationError),
    ):
        client.triggers.create(
            "test-dataset",
            TriggerCreate(
                name="Bad Trigger",
                threshold=TriggerThreshold(
                    op=TriggerThresholdOp.GREATER_THAN,
                    value=50.0,
                ),
            ),
        )


# -------------------------------------------------------------------------
# Async method tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_datasets_async():
    """Test listing datasets asynchronously."""
    respx.get("https://api.honeycomb.io/1/datasets").mock(
        return_value=Response(
            200,
            json=[
                {"name": "Dataset 1", "slug": "dataset-1"},
            ],
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        datasets = await client.datasets.list_async()
        assert len(datasets) == 1
        assert datasets[0].name == "Dataset 1"


@pytest.mark.asyncio
@respx.mock
async def test_get_trigger_async():
    """Test getting a trigger asynchronously."""
    respx.get("https://api.honeycomb.io/1/triggers/test-dataset/trigger-1").mock(
        return_value=Response(
            200,
            json={
                "id": "trigger-1",
                "name": "Test Trigger",
                "dataset_slug": "test-dataset",
                "threshold": {"op": ">", "value": 100},
                "frequency": 300,
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        trigger = await client.triggers.get_async("test-dataset", "trigger-1")
        assert trigger.id == "trigger-1"
        assert trigger.name == "Test Trigger"


@pytest.mark.asyncio
@respx.mock
async def test_create_slo_async():
    """Test creating an SLO asynchronously."""
    respx.post("https://api.honeycomb.io/1/slos/test-dataset").mock(
        return_value=Response(
            201,
            json={
                "id": "slo-1",
                "name": "Test SLO",
                "sli": {},
                "time_period_days": 30,
                "target_per_million": 999000,
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        slo = await client.slos.create_async(
            "test-dataset",
            SLOCreate(
                name="Test SLO",
                sli=SLI(),
                time_period_days=30,
                target_per_million=999000,
            ),
        )
        assert slo.id == "slo-1"
        assert slo.name == "Test SLO"


class TestSyncMethodGuards:
    """Tests for sync method guards when client is in async mode."""

    def test_sync_method_raises_in_async_mode(self):
        """Test that sync methods raise when client is in async mode."""
        client = HoneycombClient(api_key="test-key")  # async mode by default
        with pytest.raises(RuntimeError, match="Use list_async"):
            client.datasets.list()

    def test_sync_trigger_method_raises_in_async_mode(self):
        """Test that sync trigger methods raise when client is in async mode."""
        client = HoneycombClient(api_key="test-key")
        with pytest.raises(RuntimeError, match="Use get_async"):
            client.triggers.get("dataset", "trigger-id")
