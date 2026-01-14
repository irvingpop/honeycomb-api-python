"""Tests for ColumnsResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from tests.factories import ColumnCreateFactory, ColumnFactory, mock_response

# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_columns_async():
    """Test listing columns for a dataset (async)."""
    mock_data = [
        mock_response(ColumnFactory, id="col-1", key_name="status_code"),
        mock_response(ColumnFactory, id="col-2", key_name="user_id"),
        mock_response(ColumnFactory, id="col-3", key_name="duration_ms"),
    ]
    respx.get("https://api.honeycomb.io/1/columns/test-dataset").mock(
        return_value=Response(200, json=mock_data)
    )

    async with HoneycombClient(api_key="test-key") as client:
        columns = await client.columns.list_async(dataset="test-dataset")
        assert len(columns) == 3
        assert columns[0].id == "col-1"
        assert columns[0].key_name == "status_code"
        assert columns[1].id == "col-2"
        assert columns[2].id == "col-3"


@pytest.mark.asyncio
@respx.mock
async def test_list_columns_empty_async():
    """Test listing columns returns empty list (async)."""
    respx.get("https://api.honeycomb.io/1/columns/test-dataset").mock(
        return_value=Response(200, json=[])
    )

    async with HoneycombClient(api_key="test-key") as client:
        columns = await client.columns.list_async(dataset="test-dataset")
        assert len(columns) == 0


@pytest.mark.asyncio
@respx.mock
async def test_get_column_async():
    """Test getting a specific column (async)."""
    respx.get("https://api.honeycomb.io/1/columns/test-dataset/col-123").mock(
        return_value=Response(
            200,
            json=mock_response(ColumnFactory, id="col-123", key_name="request_id", type="string"),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        column = await client.columns.get_async(dataset="test-dataset", column_id="col-123")
        assert column.id == "col-123"
        assert column.key_name == "request_id"
        assert column.type.value == "string"


@pytest.mark.asyncio
@respx.mock
async def test_create_column_async():
    """Test creating a column (async)."""
    respx.post("https://api.honeycomb.io/1/columns/test-dataset").mock(
        return_value=Response(
            201,
            json=mock_response(
                ColumnFactory, id="new-col", key_name="new_field", description="New field"
            ),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = ColumnCreateFactory.build(key_name="new_field", description="New field")
        column = await client.columns.create_async(dataset="test-dataset", column=request)
        assert column.id == "new-col"
        assert column.key_name == "new_field"
        assert column.description == "New field"


@pytest.mark.asyncio
@respx.mock
async def test_update_column_async():
    """Test updating a column (async)."""
    respx.put("https://api.honeycomb.io/1/columns/test-dataset/col-123").mock(
        return_value=Response(
            200,
            json=mock_response(
                ColumnFactory,
                id="col-123",
                key_name="updated_field",
                description="Updated description",
            ),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = ColumnCreateFactory.build(
            key_name="updated_field", description="Updated description"
        )
        column = await client.columns.update_async(
            dataset="test-dataset", column_id="col-123", column=request
        )
        assert column.id == "col-123"
        assert column.key_name == "updated_field"
        assert column.description == "Updated description"


@pytest.mark.asyncio
@respx.mock
async def test_delete_column_async():
    """Test deleting a column (async)."""
    respx.delete("https://api.honeycomb.io/1/columns/test-dataset/col-123").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.columns.delete_async(dataset="test-dataset", column_id="col-123")


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_list_columns_sync():
    """Test listing columns for a dataset (sync)."""
    mock_data = [
        mock_response(ColumnFactory, id="col-1", key_name="status_code"),
        mock_response(ColumnFactory, id="col-2", key_name="user_id"),
    ]
    respx.get("https://api.honeycomb.io/1/columns/test-dataset").mock(
        return_value=Response(200, json=mock_data)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        columns = client.columns.list(dataset="test-dataset")
        assert len(columns) == 2
        assert columns[0].key_name == "status_code"
        assert columns[1].key_name == "user_id"


@respx.mock
def test_list_columns_empty_sync():
    """Test listing columns returns empty list (sync)."""
    respx.get("https://api.honeycomb.io/1/columns/test-dataset").mock(
        return_value=Response(200, json=[])
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        columns = client.columns.list(dataset="test-dataset")
        assert len(columns) == 0


@respx.mock
def test_get_column_sync():
    """Test getting a specific column (sync)."""
    respx.get("https://api.honeycomb.io/1/columns/test-dataset/col-123").mock(
        return_value=Response(
            200, json=mock_response(ColumnFactory, id="col-123", key_name="request_id")
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        column = client.columns.get(dataset="test-dataset", column_id="col-123")
        assert column.id == "col-123"
        assert column.key_name == "request_id"


@respx.mock
def test_create_column_sync():
    """Test creating a column (sync)."""
    respx.post("https://api.honeycomb.io/1/columns/test-dataset").mock(
        return_value=Response(
            201, json=mock_response(ColumnFactory, id="new-col", key_name="new_field")
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = ColumnCreateFactory.build(key_name="new_field")
        column = client.columns.create(dataset="test-dataset", column=request)
        assert column.id == "new-col"
        assert column.key_name == "new_field"


@respx.mock
def test_update_column_sync():
    """Test updating a column (sync)."""
    respx.put("https://api.honeycomb.io/1/columns/test-dataset/col-123").mock(
        return_value=Response(
            200,
            json=mock_response(ColumnFactory, id="col-123", key_name="updated_field", hidden=True),
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = ColumnCreateFactory.build(key_name="updated_field", hidden=True)
        column = client.columns.update(dataset="test-dataset", column_id="col-123", column=request)
        assert column.id == "col-123"
        assert column.key_name == "updated_field"
        assert column.hidden is True


@respx.mock
def test_delete_column_sync():
    """Test deleting a column (sync)."""
    respx.delete("https://api.honeycomb.io/1/columns/test-dataset/col-123").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.columns.delete(dataset="test-dataset", column_id="col-123")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.columns.list(dataset="test-dataset")

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.columns.get(dataset="test-dataset", column_id="col-123")

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = ColumnCreateFactory.build()
        client.columns.create(dataset="test-dataset", column=request)

    with pytest.raises(RuntimeError, match="Use update_async"):
        request = ColumnCreateFactory.build()
        client.columns.update(dataset="test-dataset", column_id="col-123", column=request)

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.columns.delete(dataset="test-dataset", column_id="col-123")
