from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_column import CreateColumn
from ...models.error import Error
from ...models.validation_error import ValidationError
from ...types import UNSET, Response


def _get_kwargs(
    dataset_slug: str,
    *,
    body: CreateColumn,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/1/columns/{dataset_slug}".format(dataset_slug=dataset_slug,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[CreateColumn, Error, ValidationError]]:
    if response.status_code == 201:
        response_201 = CreateColumn.from_dict(response.json())



        return response_201
    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



        return response_400
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())



        return response_403
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404
    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())



        return response_409
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[CreateColumn, Error, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: CreateColumn,

) -> Response[Union[CreateColumn, Error, ValidationError]]:
    """ Create a Column

     Create a column by providing corresponding details for that type.

    Args:
        dataset_slug (str):
        body (CreateColumn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreateColumn, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: CreateColumn,

) -> Optional[Union[CreateColumn, Error, ValidationError]]:
    """ Create a Column

     Create a column by providing corresponding details for that type.

    Args:
        dataset_slug (str):
        body (CreateColumn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreateColumn, Error, ValidationError]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: CreateColumn,

) -> Response[Union[CreateColumn, Error, ValidationError]]:
    """ Create a Column

     Create a column by providing corresponding details for that type.

    Args:
        dataset_slug (str):
        body (CreateColumn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreateColumn, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: CreateColumn,

) -> Optional[Union[CreateColumn, Error, ValidationError]]:
    """ Create a Column

     Create a column by providing corresponding details for that type.

    Args:
        dataset_slug (str):
        body (CreateColumn):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreateColumn, Error, ValidationError]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,

    )).parsed
