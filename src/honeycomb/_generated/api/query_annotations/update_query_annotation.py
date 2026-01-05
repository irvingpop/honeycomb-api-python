from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.query_annotation import QueryAnnotation
from ...types import UNSET, Response


def _get_kwargs(
    dataset_slug: str,
    query_annotation_id: str,
    *,
    body: QueryAnnotation,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/1/query_annotations/{dataset_slug}/{query_annotation_id}".format(dataset_slug=dataset_slug,query_annotation_id=query_annotation_id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, QueryAnnotation]]:
    if response.status_code == 200:
        response_200 = QueryAnnotation.from_dict(response.json())



        return response_200
    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



        return response_400
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, QueryAnnotation]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_slug: str,
    query_annotation_id: str,
    *,
    client: AuthenticatedClient,
    body: QueryAnnotation,

) -> Response[Union[Error, QueryAnnotation]]:
    """ Update a Query Annotation

     Update a Query Annotation by specifying its ID. The Query ID associated with the Query Annotation
    cannot be updated. Partial updates are not supported.

    Args:
        dataset_slug (str):
        query_annotation_id (str):
        body (QueryAnnotation): A Query Annotation consists of a name and description associated
            with a query to add context when collaborating.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, QueryAnnotation]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
query_annotation_id=query_annotation_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    query_annotation_id: str,
    *,
    client: AuthenticatedClient,
    body: QueryAnnotation,

) -> Optional[Union[Error, QueryAnnotation]]:
    """ Update a Query Annotation

     Update a Query Annotation by specifying its ID. The Query ID associated with the Query Annotation
    cannot be updated. Partial updates are not supported.

    Args:
        dataset_slug (str):
        query_annotation_id (str):
        body (QueryAnnotation): A Query Annotation consists of a name and description associated
            with a query to add context when collaborating.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, QueryAnnotation]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
query_annotation_id=query_annotation_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    query_annotation_id: str,
    *,
    client: AuthenticatedClient,
    body: QueryAnnotation,

) -> Response[Union[Error, QueryAnnotation]]:
    """ Update a Query Annotation

     Update a Query Annotation by specifying its ID. The Query ID associated with the Query Annotation
    cannot be updated. Partial updates are not supported.

    Args:
        dataset_slug (str):
        query_annotation_id (str):
        body (QueryAnnotation): A Query Annotation consists of a name and description associated
            with a query to add context when collaborating.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, QueryAnnotation]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
query_annotation_id=query_annotation_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    query_annotation_id: str,
    *,
    client: AuthenticatedClient,
    body: QueryAnnotation,

) -> Optional[Union[Error, QueryAnnotation]]:
    """ Update a Query Annotation

     Update a Query Annotation by specifying its ID. The Query ID associated with the Query Annotation
    cannot be updated. Partial updates are not supported.

    Args:
        dataset_slug (str):
        query_annotation_id (str):
        body (QueryAnnotation): A Query Annotation consists of a name and description associated
            with a query to add context when collaborating.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, QueryAnnotation]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
query_annotation_id=query_annotation_id,
client=client,
body=body,

    )).parsed
