from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.query_annotation import QueryAnnotation
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    dataset_slug: str,
    *,
    include_board_annotations: Union[Unset, bool] = False,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["include_board_annotations"] = include_board_annotations


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/query_annotations/{dataset_slug}".format(dataset_slug=dataset_slug,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, list['QueryAnnotation']]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = QueryAnnotation.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, list['QueryAnnotation']]]:
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
    include_board_annotations: Union[Unset, bool] = False,

) -> Response[Union[Error, list['QueryAnnotation']]]:
    """ List Query Annotations

     List all Query Annotations in the specified dataset.

    Args:
        dataset_slug (str):
        include_board_annotations (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['QueryAnnotation']]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
include_board_annotations=include_board_annotations,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    include_board_annotations: Union[Unset, bool] = False,

) -> Optional[Union[Error, list['QueryAnnotation']]]:
    """ List Query Annotations

     List all Query Annotations in the specified dataset.

    Args:
        dataset_slug (str):
        include_board_annotations (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['QueryAnnotation']]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,
include_board_annotations=include_board_annotations,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    include_board_annotations: Union[Unset, bool] = False,

) -> Response[Union[Error, list['QueryAnnotation']]]:
    """ List Query Annotations

     List all Query Annotations in the specified dataset.

    Args:
        dataset_slug (str):
        include_board_annotations (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['QueryAnnotation']]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
include_board_annotations=include_board_annotations,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    include_board_annotations: Union[Unset, bool] = False,

) -> Optional[Union[Error, list['QueryAnnotation']]]:
    """ List Query Annotations

     List all Query Annotations in the specified dataset.

    Args:
        dataset_slug (str):
        include_board_annotations (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['QueryAnnotation']]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
include_board_annotations=include_board_annotations,

    )).parsed
