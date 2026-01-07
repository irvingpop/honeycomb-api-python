from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.board import Board
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...models.validation_error import ValidationError
from ...types import UNSET, Response


def _get_kwargs(
    board_id: str,
    *,
    body: Board,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/1/boards/{board_id}".format(board_id=board_id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Board, DetailedError, Error, ValidationError]]:
    if response.status_code == 200:
        response_200 = Board.from_dict(response.json())



        return response_200
    if response.status_code == 400:
        response_400 = DetailedError.from_dict(response.json())



        return response_400
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Board, DetailedError, Error, ValidationError]]:
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
    body: Board,

) -> Response[Union[Board, DetailedError, Error, ValidationError]]:
    """ Update a Board

     Update a Board by specifying its ID and full details.
    **Note**: Queries can be added to, removed from, and re-ordered by updating the board itself. It is
    not possible to reference individual queries via the API.
    **Note**: Each board is limited to a maximum of 5 preset filters. Attempting to update a board with
    more than 5 preset filters will result in an error.

    Args:
        board_id (str):
        body (Board):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Board, DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        board_id=board_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    board_id: str,
    *,
    client: AuthenticatedClient,
    body: Board,

) -> Optional[Union[Board, DetailedError, Error, ValidationError]]:
    """ Update a Board

     Update a Board by specifying its ID and full details.
    **Note**: Queries can be added to, removed from, and re-ordered by updating the board itself. It is
    not possible to reference individual queries via the API.
    **Note**: Each board is limited to a maximum of 5 preset filters. Attempting to update a board with
    more than 5 preset filters will result in an error.

    Args:
        board_id (str):
        body (Board):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Board, DetailedError, Error, ValidationError]
     """


    return sync_detailed(
        board_id=board_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    board_id: str,
    *,
    client: AuthenticatedClient,
    body: Board,

) -> Response[Union[Board, DetailedError, Error, ValidationError]]:
    """ Update a Board

     Update a Board by specifying its ID and full details.
    **Note**: Queries can be added to, removed from, and re-ordered by updating the board itself. It is
    not possible to reference individual queries via the API.
    **Note**: Each board is limited to a maximum of 5 preset filters. Attempting to update a board with
    more than 5 preset filters will result in an error.

    Args:
        board_id (str):
        body (Board):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Board, DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        board_id=board_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    board_id: str,
    *,
    client: AuthenticatedClient,
    body: Board,

) -> Optional[Union[Board, DetailedError, Error, ValidationError]]:
    """ Update a Board

     Update a Board by specifying its ID and full details.
    **Note**: Queries can be added to, removed from, and re-ordered by updating the board itself. It is
    not possible to reference individual queries via the API.
    **Note**: Each board is limited to a maximum of 5 preset filters. Attempting to update a board with
    more than 5 preset filters will result in an error.

    Args:
        board_id (str):
        body (Board):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Board, DetailedError, Error, ValidationError]
     """


    return (await asyncio_detailed(
        board_id=board_id,
client=client,
body=body,

    )).parsed
