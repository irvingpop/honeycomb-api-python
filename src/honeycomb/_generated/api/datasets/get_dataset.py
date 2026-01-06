from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dataset import Dataset
from ...models.error import Error
from ...types import UNSET, Response


def _get_kwargs(
    dataset_slug: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/datasets/{dataset_slug}".format(dataset_slug=dataset_slug,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Dataset, Error]]:
    if response.status_code == 200:
        response_200 = Dataset.from_dict(response.json())



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Dataset, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Dataset, Error]]:
    """ Get a Dataset

     Get a single Dataset by slug.

    Args:
        dataset_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Dataset, Error]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Dataset, Error]]:
    """ Get a Dataset

     Get a single Dataset by slug.

    Args:
        dataset_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Dataset, Error]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Dataset, Error]]:
    """ Get a Dataset

     Get a single Dataset by slug.

    Args:
        dataset_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Dataset, Error]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Dataset, Error]]:
    """ Get a Dataset

     Get a single Dataset by slug.

    Args:
        dataset_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Dataset, Error]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,

    )).parsed
