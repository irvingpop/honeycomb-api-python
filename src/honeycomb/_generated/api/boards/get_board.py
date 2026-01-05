from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.board import Board
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...types import UNSET, Response


def _get_kwargs(
    board_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/boards/{board_id}".format(board_id=board_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Board, DetailedError, Error]]:
    if response.status_code == 200:
        response_200 = Board.from_dict(response.json())



        return response_200
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
    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())



        return response_429
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Board, DetailedError, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    board_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Board, DetailedError, Error]]:
    """ Get a Board

     Get a single Board by ID.

    Args:
        board_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Board, DetailedError, Error]]
     """


    kwargs = _get_kwargs(
        board_id=board_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    board_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Board, DetailedError, Error]]:
    """ Get a Board

     Get a single Board by ID.

    Args:
        board_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Board, DetailedError, Error]
     """


    return sync_detailed(
        board_id=board_id,
client=client,

    ).parsed

async def asyncio_detailed(
    board_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Board, DetailedError, Error]]:
    """ Get a Board

     Get a single Board by ID.

    Args:
        board_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Board, DetailedError, Error]]
     """


    kwargs = _get_kwargs(
        board_id=board_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    board_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Board, DetailedError, Error]]:
    """ Get a Board

     Get a single Board by ID.

    Args:
        board_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Board, DetailedError, Error]
     """


    return (await asyncio_detailed(
        board_id=board_id,
client=client,

    )).parsed
