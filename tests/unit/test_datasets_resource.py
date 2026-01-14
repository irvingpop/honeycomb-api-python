"""Tests for DatasetsResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from tests.factories import (
    DatasetCreateFactory,
    DatasetFactory,
    DatasetUpdateFactory,
    mock_list_response,
    mock_response,
)

# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_datasets_async():
    """Test listing datasets (async)."""
    respx.get("https://api.honeycomb.io/1/datasets").mock(
        return_value=Response(200, json=mock_list_response(DatasetFactory, count=3))
    )

    async with HoneycombClient(api_key="test-key") as client:
        datasets = await client.datasets.list_async()
        assert len(datasets) == 3


@pytest.mark.asyncio
@respx.mock
async def test_list_datasets_empty_async():
    """Test listing datasets returns empty list (async)."""
    respx.get("https://api.honeycomb.io/1/datasets").mock(return_value=Response(200, json=[]))

    async with HoneycombClient(api_key="test-key") as client:
        datasets = await client.datasets.list_async()
        assert len(datasets) == 0


@pytest.mark.asyncio
@respx.mock
async def test_get_dataset_async():
    """Test getting a specific dataset (async)."""
    respx.get("https://api.honeycomb.io/1/datasets/test-dataset").mock(
        return_value=Response(
            200, json=mock_response(DatasetFactory, slug="test-dataset", name="Test Dataset")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        dataset = await client.datasets.get_async(slug="test-dataset")
        assert dataset.slug == "test-dataset"
        assert dataset.name == "Test Dataset"


@pytest.mark.asyncio
@respx.mock
async def test_create_dataset_async():
    """Test creating a dataset (async)."""
    respx.post("https://api.honeycomb.io/1/datasets").mock(
        return_value=Response(
            201, json=mock_response(DatasetFactory, slug="new-dataset", name="New Dataset")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = DatasetCreateFactory.build(name="New Dataset")
        dataset = await client.datasets.create_async(dataset=request)
        assert dataset.slug == "new-dataset"
        assert dataset.name == "New Dataset"


@pytest.mark.asyncio
@respx.mock
async def test_update_dataset_async():
    """Test updating a dataset (async)."""
    respx.put("https://api.honeycomb.io/1/datasets/test-dataset").mock(
        return_value=Response(
            200,
            json=mock_response(
                DatasetFactory, slug="test-dataset", description="Updated description"
            ),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = DatasetUpdateFactory.build(description="Updated description")
        dataset = await client.datasets.update_async(slug="test-dataset", dataset=request)
        assert dataset.slug == "test-dataset"
        assert dataset.description == "Updated description"


@pytest.mark.asyncio
@respx.mock
async def test_delete_dataset_async():
    """Test deleting a dataset (async)."""
    respx.delete("https://api.honeycomb.io/1/datasets/test-dataset").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.datasets.delete_async(slug="test-dataset")


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_list_datasets_sync():
    """Test listing datasets (sync)."""
    respx.get("https://api.honeycomb.io/1/datasets").mock(
        return_value=Response(200, json=mock_list_response(DatasetFactory, count=2))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        datasets = client.datasets.list()
        assert len(datasets) == 2


@respx.mock
def test_list_datasets_empty_sync():
    """Test listing datasets returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/1/datasets").mock(return_value=Response(200, json=[]))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        datasets = client.datasets.list()
        assert len(datasets) == 0


@respx.mock
def test_get_dataset_sync():
    """Test getting a specific dataset (sync)."""
    respx.get("https://api.honeycomb.io/1/datasets/test-dataset").mock(
        return_value=Response(200, json=mock_response(DatasetFactory, slug="test-dataset"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        dataset = client.datasets.get(slug="test-dataset")
        assert dataset.slug == "test-dataset"


@respx.mock
def test_create_dataset_sync():
    """Test creating a dataset (sync)."""
    respx.post("https://api.honeycomb.io/1/datasets").mock(
        return_value=Response(201, json=mock_response(DatasetFactory, slug="new-dataset"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = DatasetCreateFactory.build(name="New Dataset")
        dataset = client.datasets.create(dataset=request)
        assert dataset.slug == "new-dataset"


@respx.mock
def test_update_dataset_sync():
    """Test updating a dataset (sync)."""
    respx.put("https://api.honeycomb.io/1/datasets/test-dataset").mock(
        return_value=Response(200, json=mock_response(DatasetFactory, slug="test-dataset"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = DatasetUpdateFactory.build(description="Updated")
        dataset = client.datasets.update(slug="test-dataset", dataset=request)
        assert dataset.slug == "test-dataset"


@respx.mock
def test_delete_dataset_sync():
    """Test deleting a dataset (sync)."""
    respx.delete("https://api.honeycomb.io/1/datasets/test-dataset").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.datasets.delete(slug="test-dataset")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.datasets.list()

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.datasets.get(slug="test-dataset")

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = DatasetCreateFactory.build()
        client.datasets.create(dataset=request)

    with pytest.raises(RuntimeError, match="Use update_async"):
        request = DatasetUpdateFactory.build()
        client.datasets.update(slug="test-dataset", dataset=request)

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.datasets.delete(slug="test-dataset")


# -------------------------------------------------------------------------
# Convenience method tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_set_delete_protected_async():
    """Test convenience method for setting delete protection (async)."""
    respx.put("https://api.honeycomb.io/1/datasets/test-dataset").mock(
        return_value=Response(200, json=mock_response(DatasetFactory, slug="test-dataset"))
    )

    async with HoneycombClient(api_key="test-key") as client:
        dataset = await client.datasets.set_delete_protected_async(
            slug="test-dataset", protected=True
        )
        assert dataset.slug == "test-dataset"


@respx.mock
def test_set_delete_protected_sync():
    """Test convenience method for setting delete protection (sync)."""
    respx.put("https://api.honeycomb.io/1/datasets/test-dataset").mock(
        return_value=Response(200, json=mock_response(DatasetFactory, slug="test-dataset"))
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        dataset = client.datasets.set_delete_protected(slug="test-dataset", protected=False)
        assert dataset.slug == "test-dataset"
