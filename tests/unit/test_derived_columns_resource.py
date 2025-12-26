"""Tests for DerivedColumnsResource (Calculated Fields API)."""

import pytest
import respx
from httpx import Response

from honeycomb import DerivedColumnCreate, HoneycombClient

# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_derived_columns_async():
    """Test listing derived columns (async)."""
    respx.get("https://api.honeycomb.io/1/derived_columns/test-dataset").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "dc-1",
                    "alias": "success_flag",
                    "expression": "IF(LT($status, 400), 1, 0)",
                    "description": "1 for success",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
                {
                    "id": "dc-2",
                    "alias": "error_flag",
                    "expression": "IF(GTE($status, 500), 1, 0)",
                    "description": "1 for error",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
            ],
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        columns = await client.derived_columns.list_async("test-dataset")
        assert len(columns) == 2
        assert columns[0].alias == "success_flag"
        assert columns[1].alias == "error_flag"


@pytest.mark.asyncio
@respx.mock
async def test_list_derived_columns_by_alias_async():
    """Test listing derived columns filtered by alias (async)."""
    respx.get("https://api.honeycomb.io/1/derived_columns/test-dataset?alias=success_flag").mock(
        return_value=Response(
            200,
            json={
                "id": "dc-1",
                "alias": "success_flag",
                "expression": "IF(LT($status, 400), 1, 0)",
                "description": "1 for success",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        columns = await client.derived_columns.list_async("test-dataset", alias="success_flag")
        assert len(columns) == 1
        assert columns[0].alias == "success_flag"


@pytest.mark.asyncio
@respx.mock
async def test_list_environment_wide_derived_columns_async():
    """Test listing environment-wide derived columns (async)."""
    respx.get("https://api.honeycomb.io/1/derived_columns/__all__").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "dc-1",
                    "alias": "global_flag",
                    "expression": "INT(1)",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            ],
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        columns = await client.derived_columns.list_async("__all__")
        assert len(columns) == 1
        assert columns[0].alias == "global_flag"


@pytest.mark.asyncio
@respx.mock
async def test_get_derived_column_async():
    """Test getting a specific derived column (async)."""
    respx.get("https://api.honeycomb.io/1/derived_columns/test-dataset/dc-123").mock(
        return_value=Response(
            200,
            json={
                "id": "dc-123",
                "alias": "success_flag",
                "expression": "IF(LT($status, 400), 1, 0)",
                "description": "1 for success",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        column = await client.derived_columns.get_async("test-dataset", "dc-123")
        assert column.id == "dc-123"
        assert column.alias == "success_flag"
        assert column.expression == "IF(LT($status, 400), 1, 0)"


@pytest.mark.asyncio
@respx.mock
async def test_create_derived_column_async():
    """Test creating a derived column (async)."""
    respx.post("https://api.honeycomb.io/1/derived_columns/test-dataset").mock(
        return_value=Response(
            201,
            json={
                "id": "dc-new",
                "alias": "new_column",
                "expression": "INT(1)",
                "description": "Test column",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        column = await client.derived_columns.create_async(
            "test-dataset",
            DerivedColumnCreate(alias="new_column", expression="INT(1)", description="Test column"),
        )
        assert column.id == "dc-new"
        assert column.alias == "new_column"


@pytest.mark.asyncio
@respx.mock
async def test_create_environment_wide_derived_column_async():
    """Test creating an environment-wide derived column (async)."""
    respx.post("https://api.honeycomb.io/1/derived_columns/__all__").mock(
        return_value=Response(
            201,
            json={
                "id": "dc-global",
                "alias": "global_column",
                "expression": "INT(1)",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        column = await client.derived_columns.create_async(
            "__all__", DerivedColumnCreate(alias="global_column", expression="INT(1)")
        )
        assert column.id == "dc-global"
        assert column.alias == "global_column"


@pytest.mark.asyncio
@respx.mock
async def test_update_derived_column_async():
    """Test updating a derived column (async)."""
    respx.put("https://api.honeycomb.io/1/derived_columns/test-dataset/dc-123").mock(
        return_value=Response(
            200,
            json={
                "id": "dc-123",
                "alias": "updated_column",
                "expression": "INT(2)",
                "description": "Updated",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        column = await client.derived_columns.update_async(
            "test-dataset",
            "dc-123",
            DerivedColumnCreate(alias="updated_column", expression="INT(2)", description="Updated"),
        )
        assert column.id == "dc-123"
        assert column.alias == "updated_column"
        assert column.expression == "INT(2)"


@pytest.mark.asyncio
@respx.mock
async def test_delete_derived_column_async():
    """Test deleting a derived column (async)."""
    respx.delete("https://api.honeycomb.io/1/derived_columns/test-dataset/dc-123").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.derived_columns.delete_async("test-dataset", "dc-123")


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_list_derived_columns_sync():
    """Test listing derived columns (sync)."""
    respx.get("https://api.honeycomb.io/1/derived_columns/test-dataset").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": "dc-1",
                    "alias": "success_flag",
                    "expression": "IF(LT($status, 400), 1, 0)",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            ],
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        columns = client.derived_columns.list("test-dataset")
        assert len(columns) == 1
        assert columns[0].alias == "success_flag"


@respx.mock
def test_list_derived_columns_by_alias_sync():
    """Test listing derived columns filtered by alias (sync)."""
    respx.get("https://api.honeycomb.io/1/derived_columns/test-dataset?alias=success_flag").mock(
        return_value=Response(
            200,
            json={
                "id": "dc-1",
                "alias": "success_flag",
                "expression": "IF(LT($status, 400), 1, 0)",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        columns = client.derived_columns.list("test-dataset", alias="success_flag")
        assert len(columns) == 1
        assert columns[0].alias == "success_flag"


@respx.mock
def test_get_derived_column_sync():
    """Test getting a specific derived column (sync)."""
    respx.get("https://api.honeycomb.io/1/derived_columns/test-dataset/dc-123").mock(
        return_value=Response(
            200,
            json={
                "id": "dc-123",
                "alias": "success_flag",
                "expression": "IF(LT($status, 400), 1, 0)",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        column = client.derived_columns.get("test-dataset", "dc-123")
        assert column.id == "dc-123"
        assert column.alias == "success_flag"


@respx.mock
def test_create_derived_column_sync():
    """Test creating a derived column (sync)."""
    respx.post("https://api.honeycomb.io/1/derived_columns/test-dataset").mock(
        return_value=Response(
            201,
            json={
                "id": "dc-new",
                "alias": "new_column",
                "expression": "INT(1)",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        column = client.derived_columns.create(
            "test-dataset", DerivedColumnCreate(alias="new_column", expression="INT(1)")
        )
        assert column.id == "dc-new"
        assert column.alias == "new_column"


@respx.mock
def test_update_derived_column_sync():
    """Test updating a derived column (sync)."""
    respx.put("https://api.honeycomb.io/1/derived_columns/test-dataset/dc-123").mock(
        return_value=Response(
            200,
            json={
                "id": "dc-123",
                "alias": "updated_column",
                "expression": "INT(2)",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        column = client.derived_columns.update(
            "test-dataset",
            "dc-123",
            DerivedColumnCreate(alias="updated_column", expression="INT(2)"),
        )
        assert column.id == "dc-123"
        assert column.alias == "updated_column"


@respx.mock
def test_delete_derived_column_sync():
    """Test deleting a derived column (sync)."""
    respx.delete("https://api.honeycomb.io/1/derived_columns/test-dataset/dc-123").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.derived_columns.delete("test-dataset", "dc-123")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.derived_columns.list("test-dataset")

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.derived_columns.get("test-dataset", "dc-123")

    with pytest.raises(RuntimeError, match="Use create_async"):
        client.derived_columns.create(
            "test-dataset", DerivedColumnCreate(alias="test", expression="INT(1)")
        )

    with pytest.raises(RuntimeError, match="Use update_async"):
        client.derived_columns.update(
            "test-dataset", "dc-123", DerivedColumnCreate(alias="test", expression="INT(1)")
        )

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.derived_columns.delete("test-dataset", "dc-123")


# -------------------------------------------------------------------------
# Builder integration tests
# -------------------------------------------------------------------------


@respx.mock
def test_create_with_builder_sync():
    """Test creating derived column using builder pattern (sync)."""
    from honeycomb import DerivedColumnBuilder

    respx.post("https://api.honeycomb.io/1/derived_columns/test-dataset").mock(
        return_value=Response(
            201,
            json={
                "id": "dc-built",
                "alias": "request_success",
                "expression": "IF(LT($status_code, 400), 1, 0)",
                "description": "1 if request succeeded, 0 otherwise",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        dc = (
            DerivedColumnBuilder("request_success")
            .expression("IF(LT($status_code, 400), 1, 0)")
            .description("1 if request succeeded, 0 otherwise")
            .build()
        )
        column = client.derived_columns.create("test-dataset", dc)
        assert column.id == "dc-built"
        assert column.alias == "request_success"


@pytest.mark.asyncio
@respx.mock
async def test_create_with_builder_async():
    """Test creating derived column using builder pattern (async)."""
    from honeycomb import DerivedColumnBuilder

    respx.post("https://api.honeycomb.io/1/derived_columns/test-dataset").mock(
        return_value=Response(
            201,
            json={
                "id": "dc-built",
                "alias": "error_flag",
                "expression": "IF(GTE($status, 500), 1, 0)",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        dc = DerivedColumnBuilder("error_flag").expression("IF(GTE($status, 500), 1, 0)").build()
        column = await client.derived_columns.create_async("test-dataset", dc)
        assert column.id == "dc-built"
        assert column.alias == "error_flag"
