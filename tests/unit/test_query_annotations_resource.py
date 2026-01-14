"""Tests for QueryAnnotationsResource."""

import pytest
import respx
from httpx import Response

from honeycomb import HoneycombClient
from tests.factories import (
    QueryAnnotationCreateFactory,
    QueryAnnotationFactory,
    mock_list_response,
    mock_response,
)

# -------------------------------------------------------------------------
# Async resource tests
# -------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_list_query_annotations_async():
    """Test listing query annotations (async)."""
    respx.get(
        "https://api.honeycomb.io/1/query_annotations/test-dataset?include_board_annotations=false"
    ).mock(return_value=Response(200, json=mock_list_response(QueryAnnotationFactory, count=3)))

    async with HoneycombClient(api_key="test-key") as client:
        annotations = await client.query_annotations.list_async(dataset="test-dataset")
        assert len(annotations) == 3


@pytest.mark.asyncio
@respx.mock
async def test_list_query_annotations_with_board_annotations_async():
    """Test listing query annotations including board annotations (async)."""
    respx.get(
        "https://api.honeycomb.io/1/query_annotations/test-dataset?include_board_annotations=true"
    ).mock(return_value=Response(200, json=mock_list_response(QueryAnnotationFactory, count=5)))

    async with HoneycombClient(api_key="test-key") as client:
        annotations = await client.query_annotations.list_async(
            dataset="test-dataset", include_board_annotations=True
        )
        assert len(annotations) == 5


@pytest.mark.asyncio
@respx.mock
async def test_list_query_annotations_empty_async():
    """Test listing query annotations returns empty list (async)."""
    respx.get(
        "https://api.honeycomb.io/1/query_annotations/test-dataset?include_board_annotations=false"
    ).mock(return_value=Response(200, json=[]))

    async with HoneycombClient(api_key="test-key") as client:
        annotations = await client.query_annotations.list_async(dataset="test-dataset")
        assert len(annotations) == 0


@pytest.mark.asyncio
@respx.mock
async def test_get_query_annotation_async():
    """Test getting a specific query annotation (async)."""
    respx.get("https://api.honeycomb.io/1/query_annotations/test-dataset/annot-123").mock(
        return_value=Response(
            200, json=mock_response(QueryAnnotationFactory, id="annot-123", name="Test Query")
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        annotation = await client.query_annotations.get_async(
            dataset="test-dataset", annotation_id="annot-123"
        )
        assert annotation.id == "annot-123"
        assert annotation.name == "Test Query"


@pytest.mark.asyncio
@respx.mock
async def test_create_query_annotation_async():
    """Test creating a query annotation (async)."""
    respx.post("https://api.honeycomb.io/1/query_annotations/test-dataset").mock(
        return_value=Response(
            201,
            json=mock_response(QueryAnnotationFactory, id="new-annot", name="Error Rate Analysis"),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = QueryAnnotationCreateFactory.build(
            name="Error Rate Analysis", description="Tracks errors"
        )
        annotation = await client.query_annotations.create_async(
            dataset="test-dataset", annotation=request
        )
        assert annotation.id == "new-annot"
        assert annotation.name == "Error Rate Analysis"


@pytest.mark.asyncio
@respx.mock
async def test_update_query_annotation_async():
    """Test updating a query annotation (async)."""
    respx.put("https://api.honeycomb.io/1/query_annotations/test-dataset/annot-123").mock(
        return_value=Response(
            200,
            json=mock_response(
                QueryAnnotationFactory,
                id="annot-123",
                name="Updated Analysis",
                description="Updated description",
            ),
        )
    )

    async with HoneycombClient(api_key="test-key") as client:
        request = QueryAnnotationCreateFactory.build(
            name="Updated Analysis", description="Updated description"
        )
        annotation = await client.query_annotations.update_async(
            dataset="test-dataset", annotation_id="annot-123", annotation=request
        )
        assert annotation.id == "annot-123"
        assert annotation.name == "Updated Analysis"
        assert annotation.description == "Updated description"


@pytest.mark.asyncio
@respx.mock
async def test_delete_query_annotation_async():
    """Test deleting a query annotation (async)."""
    respx.delete("https://api.honeycomb.io/1/query_annotations/test-dataset/annot-123").mock(
        return_value=Response(204)
    )

    async with HoneycombClient(api_key="test-key") as client:
        # Should not raise
        await client.query_annotations.delete_async(
            dataset="test-dataset", annotation_id="annot-123"
        )


# -------------------------------------------------------------------------
# Sync resource tests
# -------------------------------------------------------------------------


@respx.mock
def test_list_query_annotations_sync():
    """Test listing query annotations (sync)."""
    respx.get(
        "https://api.honeycomb.io/1/query_annotations/test-dataset?include_board_annotations=false"
    ).mock(return_value=Response(200, json=mock_list_response(QueryAnnotationFactory, count=2)))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        annotations = client.query_annotations.list(dataset="test-dataset")
        assert len(annotations) == 2


@respx.mock
def test_list_query_annotations_with_board_annotations_sync():
    """Test listing query annotations including board annotations (sync)."""
    respx.get(
        "https://api.honeycomb.io/1/query_annotations/test-dataset?include_board_annotations=true"
    ).mock(return_value=Response(200, json=mock_list_response(QueryAnnotationFactory, count=4)))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        annotations = client.query_annotations.list(
            dataset="test-dataset", include_board_annotations=True
        )
        assert len(annotations) == 4


@respx.mock
def test_list_query_annotations_empty_sync():
    """Test listing query annotations returns empty list (sync)."""
    respx.get(
        "https://api.honeycomb.io/1/query_annotations/test-dataset?include_board_annotations=false"
    ).mock(return_value=Response(200, json=[]))

    with HoneycombClient(api_key="test-key", sync=True) as client:
        annotations = client.query_annotations.list(dataset="test-dataset")
        assert len(annotations) == 0


@respx.mock
def test_get_query_annotation_sync():
    """Test getting a specific query annotation (sync)."""
    respx.get("https://api.honeycomb.io/1/query_annotations/test-dataset/annot-123").mock(
        return_value=Response(
            200, json=mock_response(QueryAnnotationFactory, id="annot-123", name="Test Query")
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        annotation = client.query_annotations.get(dataset="test-dataset", annotation_id="annot-123")
        assert annotation.id == "annot-123"
        assert annotation.name == "Test Query"


@respx.mock
def test_create_query_annotation_sync():
    """Test creating a query annotation (sync)."""
    respx.post("https://api.honeycomb.io/1/query_annotations/test-dataset").mock(
        return_value=Response(
            201, json=mock_response(QueryAnnotationFactory, id="new-annot", name="New Analysis")
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = QueryAnnotationCreateFactory.build(name="New Analysis")
        annotation = client.query_annotations.create(dataset="test-dataset", annotation=request)
        assert annotation.id == "new-annot"
        assert annotation.name == "New Analysis"


@respx.mock
def test_update_query_annotation_sync():
    """Test updating a query annotation (sync)."""
    respx.put("https://api.honeycomb.io/1/query_annotations/test-dataset/annot-123").mock(
        return_value=Response(
            200,
            json=mock_response(QueryAnnotationFactory, id="annot-123", name="Updated"),
        )
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        request = QueryAnnotationCreateFactory.build(name="Updated")
        annotation = client.query_annotations.update(
            dataset="test-dataset", annotation_id="annot-123", annotation=request
        )
        assert annotation.id == "annot-123"
        assert annotation.name == "Updated"


@respx.mock
def test_delete_query_annotation_sync():
    """Test deleting a query annotation (sync)."""
    respx.delete("https://api.honeycomb.io/1/query_annotations/test-dataset/annot-123").mock(
        return_value=Response(204)
    )

    with HoneycombClient(api_key="test-key", sync=True) as client:
        # Should not raise
        client.query_annotations.delete(dataset="test-dataset", annotation_id="annot-123")


# -------------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------------


def test_sync_methods_require_sync_mode():
    """Test that sync methods raise error in async mode."""
    client = HoneycombClient(api_key="test-key")  # async mode

    with pytest.raises(RuntimeError, match="Use list_async"):
        client.query_annotations.list(dataset="test-dataset")

    with pytest.raises(RuntimeError, match="Use get_async"):
        client.query_annotations.get(dataset="test-dataset", annotation_id="annot-123")

    with pytest.raises(RuntimeError, match="Use create_async"):
        request = QueryAnnotationCreateFactory.build()
        client.query_annotations.create(dataset="test-dataset", annotation=request)

    with pytest.raises(RuntimeError, match="Use update_async"):
        request = QueryAnnotationCreateFactory.build()
        client.query_annotations.update(
            dataset="test-dataset", annotation_id="annot-123", annotation=request
        )

    with pytest.raises(RuntimeError, match="Use delete_async"):
        client.query_annotations.delete(dataset="test-dataset", annotation_id="annot-123")
