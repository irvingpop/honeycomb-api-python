from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.detailed_error import DetailedError
from ...models.environment_list_response import EnvironmentListResponse
from ...models.error import Error
from ...models.validation_error import ValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    team_slug: str,
    *,
    pageafter: Union[Unset, str] = UNSET,
    pagesize: Union[Unset, float] = 20.0,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["page[after]"] = pageafter

    params["page[size]"] = pagesize


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/2/teams/{team_slug}/environments".format(team_slug=team_slug,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[DetailedError, EnvironmentListResponse, Error, ValidationError]]:
    if response.status_code == 200:
        response_200 = EnvironmentListResponse.from_dict(response.json())



        return response_200
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
    if response.status_code == 500:
        response_500 = DetailedError.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[DetailedError, EnvironmentListResponse, Error, ValidationError]]:
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
    pageafter: Union[Unset, str] = UNSET,
    pagesize: Union[Unset, float] = 20.0,

) -> Response[Union[DetailedError, EnvironmentListResponse, Error, ValidationError]]:
    """ List all Environments

    Args:
        team_slug (str):
        pageafter (Union[Unset, str]):
        pagesize (Union[Unset, float]):  Default: 20.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, EnvironmentListResponse, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
pageafter=pageafter,
pagesize=pagesize,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    pageafter: Union[Unset, str] = UNSET,
    pagesize: Union[Unset, float] = 20.0,

) -> Optional[Union[DetailedError, EnvironmentListResponse, Error, ValidationError]]:
    """ List all Environments

    Args:
        team_slug (str):
        pageafter (Union[Unset, str]):
        pagesize (Union[Unset, float]):  Default: 20.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, EnvironmentListResponse, Error, ValidationError]
     """


    return sync_detailed(
        team_slug=team_slug,
client=client,
pageafter=pageafter,
pagesize=pagesize,

    ).parsed

async def asyncio_detailed(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    pageafter: Union[Unset, str] = UNSET,
    pagesize: Union[Unset, float] = 20.0,

) -> Response[Union[DetailedError, EnvironmentListResponse, Error, ValidationError]]:
    """ List all Environments

    Args:
        team_slug (str):
        pageafter (Union[Unset, str]):
        pagesize (Union[Unset, float]):  Default: 20.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, EnvironmentListResponse, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
pageafter=pageafter,
pagesize=pagesize,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    pageafter: Union[Unset, str] = UNSET,
    pagesize: Union[Unset, float] = 20.0,

) -> Optional[Union[DetailedError, EnvironmentListResponse, Error, ValidationError]]:
    """ List all Environments

    Args:
        team_slug (str):
        pageafter (Union[Unset, str]):
        pagesize (Union[Unset, float]):  Default: 20.0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, EnvironmentListResponse, Error, ValidationError]
     """


    return (await asyncio_detailed(
        team_slug=team_slug,
client=client,
pageafter=pageafter,
pagesize=pagesize,

    )).parsed
