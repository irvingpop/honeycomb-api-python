from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_map_dependencies_request import \
    CreateMapDependenciesRequest
from ...models.create_map_dependencies_response import \
    CreateMapDependenciesResponse
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...models.validation_error import ValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: CreateMapDependenciesRequest,
    limit: Union[Unset, int] = 10000,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    params: dict[str, Any] = {}

    params["limit"] = limit


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/1/maps/dependencies/requests",
        "params": params,
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]]:
    if response.status_code == 200:
        response_200 = CreateMapDependenciesResponse.from_dict(response.json())



        return response_200
    if response.status_code == 201:
        response_201 = CreateMapDependenciesResponse.from_dict(response.json())



        return response_201
    if response.status_code == 400:
        response_400 = DetailedError.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateMapDependenciesRequest,
    limit: Union[Unset, int] = 10000,

) -> Response[Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]]:
    """ Create a Map Dependency Request

     Create a Map Dependency Request.

    Args:
        limit (Union[Unset, int]):  Default: 10000.
        body (CreateMapDependenciesRequest): Create a Map Dependency Request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        body=body,
limit=limit,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    body: CreateMapDependenciesRequest,
    limit: Union[Unset, int] = 10000,

) -> Optional[Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]]:
    """ Create a Map Dependency Request

     Create a Map Dependency Request.

    Args:
        limit (Union[Unset, int]):  Default: 10000.
        body (CreateMapDependenciesRequest): Create a Map Dependency Request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]
     """


    return sync_detailed(
        client=client,
body=body,
limit=limit,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateMapDependenciesRequest,
    limit: Union[Unset, int] = 10000,

) -> Response[Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]]:
    """ Create a Map Dependency Request

     Create a Map Dependency Request.

    Args:
        limit (Union[Unset, int]):  Default: 10000.
        body (CreateMapDependenciesRequest): Create a Map Dependency Request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        body=body,
limit=limit,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CreateMapDependenciesRequest,
    limit: Union[Unset, int] = 10000,

) -> Optional[Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]]:
    """ Create a Map Dependency Request

     Create a Map Dependency Request.

    Args:
        limit (Union[Unset, int]):  Default: 10000.
        body (CreateMapDependenciesRequest): Create a Map Dependency Request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CreateMapDependenciesResponse, DetailedError, Error, ValidationError]
     """


    return (await asyncio_detailed(
        client=client,
body=body,
limit=limit,

    )).parsed
