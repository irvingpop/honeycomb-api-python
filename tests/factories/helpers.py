"""Helper utilities for using factories with respx mocks.

These functions convert Pydantic model instances to JSON-serializable dictionaries
suitable for use in respx mock responses.
"""

from typing import Any, TypeVar

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def mock_response(factory_class: type[ModelFactory[T]], **overrides: Any) -> dict[str, Any]:
    """Generate a JSON dict for a respx mock response.

    Builds a model instance using the factory and converts it to a JSON-serializable
    dictionary. Only specify fields you need for assertions; the factory fills in
    the rest with valid random values.

    Args:
        factory_class: The factory class to use for generating the model.
        **overrides: Field values to override in the generated model.

    Returns:
        A JSON-serializable dictionary representing the model.

    Example:
        respx_mock.get("https://api.honeycomb.io/1/slos/dataset/slo-1").mock(
            return_value=Response(200, json=mock_response(SLOFactory, id="slo-1"))
        )
    """
    instance = factory_class.build(**overrides)
    return instance.model_dump(mode="json", by_alias=True, exclude_none=True)


def mock_list_response(
    factory_class: type[ModelFactory[T]],
    count: int = 3,
    **overrides: Any,
) -> list[dict[str, Any]]:
    """Generate a list of JSON dicts for list endpoint responses.

    Creates multiple model instances and converts them to JSON-serializable
    dictionaries. Each instance gets unique random values.

    Args:
        factory_class: The factory class to use for generating models.
        count: Number of items to generate (default: 3).
        **overrides: Field values to apply to ALL generated models.

    Returns:
        A list of JSON-serializable dictionaries.

    Example:
        respx_mock.get("https://api.honeycomb.io/1/slos/dataset").mock(
            return_value=Response(200, json=mock_list_response(SLOFactory, count=5))
        )
    """
    return [mock_response(factory_class, **overrides) for _ in range(count)]


def mock_paginated_response(
    factory_class: type[ModelFactory[T]],
    count: int = 3,
    has_next: bool = False,
    **overrides: Any,
) -> dict[str, Any]:
    """Generate a paginated response with data and links.

    Creates a response structure with a data array and optional pagination links.

    Args:
        factory_class: The factory class to use for generating models.
        count: Number of items to generate (default: 3).
        has_next: Whether to include a 'next' link (default: False).
        **overrides: Field values to apply to ALL generated models.

    Returns:
        A dictionary with 'data' list and optional 'links' for pagination.

    Example:
        respx_mock.get("https://api.honeycomb.io/1/api_keys").mock(
            return_value=Response(200, json=mock_paginated_response(
                ApiKeyFactory, count=10, has_next=True
            ))
        )
    """
    data = mock_list_response(factory_class, count=count, **overrides)
    result: dict[str, Any] = {"data": data}
    if has_next:
        result["links"] = {"next": "https://api.honeycomb.io/1/next-page"}
    return result
