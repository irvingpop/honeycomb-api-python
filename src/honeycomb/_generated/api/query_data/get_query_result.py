from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.query_result_details import QueryResultDetails
from ...types import UNSET, Response


def _get_kwargs(
    dataset_slug: str,
    query_result_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/query_results/{dataset_slug}/{query_result_id}".format(dataset_slug=dataset_slug,query_result_id=query_result_id,),
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, QueryResultDetails]]:
    if response.status_code == 200:
        response_200 = QueryResultDetails.from_dict(response.json())



        return response_200
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, QueryResultDetails]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_slug: str,
    query_result_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Error, QueryResultDetails]]:
    """ Get Query Result

     Get the Query Result details for a specific Query Result ID.
    This endpoint is used to fetch the results of a query that had previously been created. It is
    recommended to follow the Location header included in the Create Query Result output, but the URL
    can also be constructed manually with the &lt;query-result-id&gt;.

    Args:
        dataset_slug (str):
        query_result_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, QueryResultDetails]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
query_result_id=query_result_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    query_result_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Error, QueryResultDetails]]:
    """ Get Query Result

     Get the Query Result details for a specific Query Result ID.
    This endpoint is used to fetch the results of a query that had previously been created. It is
    recommended to follow the Location header included in the Create Query Result output, but the URL
    can also be constructed manually with the &lt;query-result-id&gt;.

    Args:
        dataset_slug (str):
        query_result_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, QueryResultDetails]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
query_result_id=query_result_id,
client=client,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    query_result_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Union[Error, QueryResultDetails]]:
    """ Get Query Result

     Get the Query Result details for a specific Query Result ID.
    This endpoint is used to fetch the results of a query that had previously been created. It is
    recommended to follow the Location header included in the Create Query Result output, but the URL
    can also be constructed manually with the &lt;query-result-id&gt;.

    Args:
        dataset_slug (str):
        query_result_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, QueryResultDetails]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
query_result_id=query_result_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    query_result_id: str,
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Error, QueryResultDetails]]:
    """ Get Query Result

     Get the Query Result details for a specific Query Result ID.
    This endpoint is used to fetch the results of a query that had previously been created. It is
    recommended to follow the Location header included in the Create Query Result output, but the URL
    can also be constructed manually with the &lt;query-result-id&gt;.

    Args:
        dataset_slug (str):
        query_result_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, QueryResultDetails]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
query_result_id=query_result_id,
client=client,

    )).parsed
