from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from typing import cast



def _get_kwargs(
    recipient_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/1/recipients/{recipient_id}".format(recipient_id=recipient_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404
    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())



        return response_409
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    recipient_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, Error]]:
    """ Delete a Recipient

     Delete a recipient by specifying the recipient ID.
    A Recipient can only be deleted if it is NOT in use by any Triggers or Burn Alerts associated to the
    team.

    Args:
        recipient_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error]]
     """


    kwargs = _get_kwargs(
        recipient_id=recipient_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    recipient_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, Error]]:
    """ Delete a Recipient

     Delete a recipient by specifying the recipient ID.
    A Recipient can only be deleted if it is NOT in use by any Triggers or Burn Alerts associated to the
    team.

    Args:
        recipient_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error]
     """


    return sync_detailed(
        recipient_id=recipient_id,
client=client,

    ).parsed

async def asyncio_detailed(
    recipient_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Any, Error]]:
    """ Delete a Recipient

     Delete a recipient by specifying the recipient ID.
    A Recipient can only be deleted if it is NOT in use by any Triggers or Burn Alerts associated to the
    team.

    Args:
        recipient_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error]]
     """


    kwargs = _get_kwargs(
        recipient_id=recipient_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    recipient_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Any, Error]]:
    """ Delete a Recipient

     Delete a recipient by specifying the recipient ID.
    A Recipient can only be deleted if it is NOT in use by any Triggers or Burn Alerts associated to the
    team.

    Args:
        recipient_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error]
     """


    return (await asyncio_detailed(
        recipient_id=recipient_id,
client=client,

    )).parsed
