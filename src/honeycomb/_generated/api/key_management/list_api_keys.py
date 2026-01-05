from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_key_list_response import ApiKeyListResponse
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...models.list_api_keys_filtertype import ListApiKeysFiltertype
from ...models.validation_error import ValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    team_slug: str,
    *,
    pageafter: Union[Unset, str] = UNSET,
    pagesize: Union[Unset, float] = 20.0,
    filtertype: Union[Unset, ListApiKeysFiltertype] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["page[after]"] = pageafter

    params["page[size]"] = pagesize

    json_filtertype: Union[Unset, str] = UNSET
    if not isinstance(filtertype, Unset):
        json_filtertype = filtertype.value

    params["filter[type]"] = json_filtertype


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/2/teams/{team_slug}/api-keys".format(team_slug=team_slug,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ApiKeyListResponse, DetailedError, Error, ValidationError]]:
    if response.status_code == 200:
        response_200 = ApiKeyListResponse.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ApiKeyListResponse, DetailedError, Error, ValidationError]]:
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
    filtertype: Union[Unset, ListApiKeysFiltertype] = UNSET,

) -> Response[Union[ApiKeyListResponse, DetailedError, Error, ValidationError]]:
    """ List all API Keys

     List all API Keys for a Team.

    **Note**: currently only keys of type `ingest` will be returned.

    Args:
        team_slug (str):
        pageafter (Union[Unset, str]):
        pagesize (Union[Unset, float]):  Default: 20.0.
        filtertype (Union[Unset, ListApiKeysFiltertype]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiKeyListResponse, DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
pageafter=pageafter,
pagesize=pagesize,
filtertype=filtertype,

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
    filtertype: Union[Unset, ListApiKeysFiltertype] = UNSET,

) -> Optional[Union[ApiKeyListResponse, DetailedError, Error, ValidationError]]:
    """ List all API Keys

     List all API Keys for a Team.

    **Note**: currently only keys of type `ingest` will be returned.

    Args:
        team_slug (str):
        pageafter (Union[Unset, str]):
        pagesize (Union[Unset, float]):  Default: 20.0.
        filtertype (Union[Unset, ListApiKeysFiltertype]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiKeyListResponse, DetailedError, Error, ValidationError]
     """


    return sync_detailed(
        team_slug=team_slug,
client=client,
pageafter=pageafter,
pagesize=pagesize,
filtertype=filtertype,

    ).parsed

async def asyncio_detailed(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    pageafter: Union[Unset, str] = UNSET,
    pagesize: Union[Unset, float] = 20.0,
    filtertype: Union[Unset, ListApiKeysFiltertype] = UNSET,

) -> Response[Union[ApiKeyListResponse, DetailedError, Error, ValidationError]]:
    """ List all API Keys

     List all API Keys for a Team.

    **Note**: currently only keys of type `ingest` will be returned.

    Args:
        team_slug (str):
        pageafter (Union[Unset, str]):
        pagesize (Union[Unset, float]):  Default: 20.0.
        filtertype (Union[Unset, ListApiKeysFiltertype]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiKeyListResponse, DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
pageafter=pageafter,
pagesize=pagesize,
filtertype=filtertype,

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
    filtertype: Union[Unset, ListApiKeysFiltertype] = UNSET,

) -> Optional[Union[ApiKeyListResponse, DetailedError, Error, ValidationError]]:
    """ List all API Keys

     List all API Keys for a Team.

    **Note**: currently only keys of type `ingest` will be returned.

    Args:
        team_slug (str):
        pageafter (Union[Unset, str]):
        pagesize (Union[Unset, float]):  Default: 20.0.
        filtertype (Union[Unset, ListApiKeysFiltertype]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiKeyListResponse, DetailedError, Error, ValidationError]
     """


    return (await asyncio_detailed(
        team_slug=team_slug,
client=client,
pageafter=pageafter,
pagesize=pagesize,
filtertype=filtertype,

    )).parsed
