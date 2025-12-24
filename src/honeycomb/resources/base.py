"""Base resource class for Honeycomb API resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from honeycomb.client import HoneycombClient

T = TypeVar("T", bound=BaseModel)


class BaseResource:
    """Base class for API resource clients.

    Provides common functionality for making API requests and
    parsing responses into Pydantic models.
    """

    def __init__(self, client: HoneycombClient) -> None:
        """Initialize the resource.

        Args:
            client: The HoneycombClient instance.
        """
        self._client = client

    # -------------------------------------------------------------------------
    # Async methods
    # -------------------------------------------------------------------------

    async def _get_async(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Make an async GET request and return JSON response."""
        response = await self._client.get_async(path, params=params)
        return response.json()

    async def _post_async(
        self, path: str, *, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        """Make an async POST request and return JSON response."""
        response = await self._client.post_async(path, json=json, params=params)
        return response.json()

    async def _put_async(
        self, path: str, *, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        """Make an async PUT request and return JSON response."""
        response = await self._client.put_async(path, json=json, params=params)
        return response.json()

    async def _delete_async(self, path: str, *, params: dict[str, Any] | None = None) -> None:
        """Make an async DELETE request."""
        await self._client.delete_async(path, params=params)

    # -------------------------------------------------------------------------
    # Sync methods
    # -------------------------------------------------------------------------

    def _get_sync(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Make a sync GET request and return JSON response."""
        response = self._client.get_sync(path, params=params)
        return response.json()

    def _post_sync(
        self, path: str, *, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        """Make a sync POST request and return JSON response."""
        response = self._client.post_sync(path, json=json, params=params)
        return response.json()

    def _put_sync(
        self, path: str, *, json: dict[str, Any] | None = None, params: dict[str, Any] | None = None
    ) -> Any:
        """Make a sync PUT request and return JSON response."""
        response = self._client.put_sync(path, json=json, params=params)
        return response.json()

    def _delete_sync(self, path: str, *, params: dict[str, Any] | None = None) -> None:
        """Make a sync DELETE request."""
        self._client.delete_sync(path, params=params)

    # -------------------------------------------------------------------------
    # Model parsing helpers
    # -------------------------------------------------------------------------

    def _parse_model(self, model_class: type[T], data: dict[str, Any]) -> T:
        """Parse a dict into a Pydantic model."""
        return model_class.model_validate(data)

    def _parse_model_list(self, model_class: type[T], data: list[dict[str, Any]]) -> list[T]:
        """Parse a list of dicts into Pydantic models."""
        return [model_class.model_validate(item) for item in data]

    def _serialize_model(self, model: BaseModel) -> dict[str, Any]:
        """Serialize a Pydantic model to a dict, excluding None values."""
        return model.model_dump(exclude_none=True, by_alias=True)
