from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dataset import Dataset
from ...models.dataset_creation_payload import DatasetCreationPayload
from ...models.error import Error
from ...models.validation_error import ValidationError
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: DatasetCreationPayload,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/1/datasets",
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Dataset, Error, ValidationError]]:
    if response.status_code == 200:
        response_200 = Dataset.from_dict(response.json())



        return response_200
    if response.status_code == 201:
        response_201 = Dataset.from_dict(response.json())



        return response_201
    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())



        return response_409
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())



        return response_403
    if response.status_code == 422:
        response_422 = ValidationError.from_dict(response.json())



        return response_422
    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())



        return response_429
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Dataset, Error, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: DatasetCreationPayload,

) -> Response[Union[Dataset, Error, ValidationError]]:
    """ Create a Dataset

     Create a Dataset in the environment associated with your API key.
    If a Dataset already exists by that name (or slug), then the existing dataset will be returned.

    Args:
        body (DatasetCreationPayload): an object to send to the Dataset API via PUT

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Dataset, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    body: DatasetCreationPayload,

) -> Optional[Union[Dataset, Error, ValidationError]]:
    """ Create a Dataset

     Create a Dataset in the environment associated with your API key.
    If a Dataset already exists by that name (or slug), then the existing dataset will be returned.

    Args:
        body (DatasetCreationPayload): an object to send to the Dataset API via PUT

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Dataset, Error, ValidationError]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: DatasetCreationPayload,

) -> Response[Union[Dataset, Error, ValidationError]]:
    """ Create a Dataset

     Create a Dataset in the environment associated with your API key.
    If a Dataset already exists by that name (or slug), then the existing dataset will be returned.

    Args:
        body (DatasetCreationPayload): an object to send to the Dataset API via PUT

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Dataset, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: DatasetCreationPayload,

) -> Optional[Union[Dataset, Error, ValidationError]]:
    """ Create a Dataset

     Create a Dataset in the environment associated with your API key.
    If a Dataset already exists by that name (or slug), then the existing dataset will be returned.

    Args:
        body (DatasetCreationPayload): an object to send to the Dataset API via PUT

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Dataset, Error, ValidationError]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
