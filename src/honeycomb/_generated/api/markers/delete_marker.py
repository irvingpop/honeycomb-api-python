from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.marker import Marker
from typing import cast



def _get_kwargs(
    dataset_slug: str,
    marker_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/1/markers/{dataset_slug}/{marker_id}".format(dataset_slug=dataset_slug,marker_id=marker_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, Marker]]:
    if response.status_code == 200:
        response_200 = Marker.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, Marker]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_slug: str,
    marker_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Error, Marker]]:
    """ Delete a Marker

    Args:
        dataset_slug (str):
        marker_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Marker]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
marker_id=marker_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    marker_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Error, Marker]]:
    """ Delete a Marker

    Args:
        dataset_slug (str):
        marker_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Marker]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
marker_id=marker_id,
client=client,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    marker_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Error, Marker]]:
    """ Delete a Marker

    Args:
        dataset_slug (str):
        marker_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Marker]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
marker_id=marker_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    marker_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Error, Marker]]:
    """ Delete a Marker

    Args:
        dataset_slug (str):
        marker_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Marker]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
marker_id=marker_id,
client=client,

    )).parsed
