from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...models.marker_create_request import MarkerCreateRequest
from ...models.marker_response import MarkerResponse
from ...models.validation_error import ValidationError
from ...types import UNSET, Response


def _get_kwargs(
    team_slug: str,
    *,
    body: MarkerCreateRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/2/teams/{team_slug}/markers".format(team_slug=team_slug,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[DetailedError, Error, MarkerResponse, ValidationError]]:
    if response.status_code == 201:
        response_201 = MarkerResponse.from_dict(response.json())



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
    if response.status_code == 413:
        response_413 = DetailedError.from_dict(response.json())



        return response_413
    if response.status_code == 422:
        response_422 = ValidationError.from_dict(response.json())



        return response_422
    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())



        return response_429
    if response.status_code == 500:
        response_500 = DetailedError.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[DetailedError, Error, MarkerResponse, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    body: MarkerCreateRequest,

) -> Response[Union[DetailedError, Error, MarkerResponse, ValidationError]]:
    """ Create a Marker

     Creates a Marker in the specified Environment. The Marker can be environment-wide (no dataset
    relationship) or associated with a specific dataset.

    Args:
        team_slug (str):
        body (MarkerCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, MarkerResponse, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    body: MarkerCreateRequest,

) -> Optional[Union[DetailedError, Error, MarkerResponse, ValidationError]]:
    """ Create a Marker

     Creates a Marker in the specified Environment. The Marker can be environment-wide (no dataset
    relationship) or associated with a specific dataset.

    Args:
        team_slug (str):
        body (MarkerCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, MarkerResponse, ValidationError]
     """


    return sync_detailed(
        team_slug=team_slug,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    body: MarkerCreateRequest,

) -> Response[Union[DetailedError, Error, MarkerResponse, ValidationError]]:
    """ Create a Marker

     Creates a Marker in the specified Environment. The Marker can be environment-wide (no dataset
    relationship) or associated with a specific dataset.

    Args:
        team_slug (str):
        body (MarkerCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, MarkerResponse, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    body: MarkerCreateRequest,

) -> Optional[Union[DetailedError, Error, MarkerResponse, ValidationError]]:
    """ Create a Marker

     Creates a Marker in the specified Environment. The Marker can be environment-wide (no dataset
    relationship) or associated with a specific dataset.

    Args:
        team_slug (str):
        body (MarkerCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, MarkerResponse, ValidationError]
     """


    return (await asyncio_detailed(
        team_slug=team_slug,
client=client,
body=body,

    )).parsed
