from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.trigger_response import TriggerResponse
from ...types import UNSET, Response


def _get_kwargs(
    recipient_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/recipients/{recipient_id}/triggers".format(recipient_id=recipient_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, list['TriggerResponse']]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = TriggerResponse.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, list['TriggerResponse']]]:
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

) -> Response[Union[Error, list['TriggerResponse']]]:
    """ Get Triggers Associated with a Recipient

     List all triggers that will alert a given Recipient. **Important:** This request will return all
    Triggers associated with the specific Recipient across your entire Honeycomb team rather than being
    scoped to a dataset or environment.

    Args:
        recipient_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['TriggerResponse']]]
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

) -> Optional[Union[Error, list['TriggerResponse']]]:
    """ Get Triggers Associated with a Recipient

     List all triggers that will alert a given Recipient. **Important:** This request will return all
    Triggers associated with the specific Recipient across your entire Honeycomb team rather than being
    scoped to a dataset or environment.

    Args:
        recipient_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['TriggerResponse']]
     """


    return sync_detailed(
        recipient_id=recipient_id,
client=client,

    ).parsed

async def asyncio_detailed(
    recipient_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Error, list['TriggerResponse']]]:
    """ Get Triggers Associated with a Recipient

     List all triggers that will alert a given Recipient. **Important:** This request will return all
    Triggers associated with the specific Recipient across your entire Honeycomb team rather than being
    scoped to a dataset or environment.

    Args:
        recipient_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['TriggerResponse']]]
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

) -> Optional[Union[Error, list['TriggerResponse']]]:
    """ Get Triggers Associated with a Recipient

     List all triggers that will alert a given Recipient. **Important:** This request will return all
    Triggers associated with the specific Recipient across your entire Honeycomb team rather than being
    scoped to a dataset or environment.

    Args:
        recipient_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['TriggerResponse']]
     """


    return (await asyncio_detailed(
        recipient_id=recipient_id,
client=client,

    )).parsed
