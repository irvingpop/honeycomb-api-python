from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.board_view_response import BoardViewResponse
from ...models.error import Error
from typing import cast



def _get_kwargs(
    board_id: str,
    view_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/boards/{board_id}/views/{view_id}".format(board_id=board_id,view_id=view_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[BoardViewResponse, Error]]:
    if response.status_code == 200:
        response_200 = BoardViewResponse.from_dict(response.json())



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
    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())



        return response_429
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[BoardViewResponse, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    board_id: str,
    view_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[BoardViewResponse, Error]]:
    """ Get a Board View

     Retrieve a single Board View by ID.

    Args:
        board_id (str):
        view_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BoardViewResponse, Error]]
     """


    kwargs = _get_kwargs(
        board_id=board_id,
view_id=view_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    board_id: str,
    view_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[BoardViewResponse, Error]]:
    """ Get a Board View

     Retrieve a single Board View by ID.

    Args:
        board_id (str):
        view_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BoardViewResponse, Error]
     """


    return sync_detailed(
        board_id=board_id,
view_id=view_id,
client=client,

    ).parsed

async def asyncio_detailed(
    board_id: str,
    view_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[BoardViewResponse, Error]]:
    """ Get a Board View

     Retrieve a single Board View by ID.

    Args:
        board_id (str):
        view_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BoardViewResponse, Error]]
     """


    kwargs = _get_kwargs(
        board_id=board_id,
view_id=view_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    board_id: str,
    view_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[BoardViewResponse, Error]]:
    """ Get a Board View

     Retrieve a single Board View by ID.

    Args:
        board_id (str):
        view_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BoardViewResponse, Error]
     """


    return (await asyncio_detailed(
        board_id=board_id,
view_id=view_id,
client=client,

    )).parsed
