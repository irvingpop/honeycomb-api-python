from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_query_result_request import CreateQueryResultRequest
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...models.query_result import QueryResult
from ...models.validation_error import ValidationError
from ...types import UNSET, Response


def _get_kwargs(
    dataset_slug: str,
    *,
    body: CreateQueryResultRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/1/query_results/{dataset_slug}".format(dataset_slug=dataset_slug,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[DetailedError, Error, QueryResult, ValidationError]]:
    if response.status_code == 201:
        response_201 = QueryResult.from_dict(response.json())



        return response_201
    if response.status_code == 400:
        response_400 = DetailedError.from_dict(response.json())



        return response_400
    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())



        return response_403
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404
    if response.status_code == 422:
        response_422 = ValidationError.from_dict(response.json())



        return response_422
    if response.status_code == 429:
        response_429 = DetailedError.from_dict(response.json())



        return response_429
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[DetailedError, Error, QueryResult, ValidationError]]:
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
    body: CreateQueryResultRequest,

) -> Response[Union[DetailedError, Error, QueryResult, ValidationError]]:
    """ Create a Query Result

     Kick off processing of a Query to then get back the Query Results.
    Once the Query Result has been created, the query will be run asynchronously, allowing the result
    data to be fetched from the GET query result endpoint.
    A maximum duration of 7 days of data can be queried. Any queries with a `start_time`, `end_time`, or
    `time_range` resulting in a duration longer than 7 days will result in a `400` error response.

    Args:
        dataset_slug (str):
        body (CreateQueryResultRequest): A Query Result is created with the Query ID.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, QueryResult, ValidationError]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: CreateQueryResultRequest,

) -> Optional[Union[DetailedError, Error, QueryResult, ValidationError]]:
    """ Create a Query Result

     Kick off processing of a Query to then get back the Query Results.
    Once the Query Result has been created, the query will be run asynchronously, allowing the result
    data to be fetched from the GET query result endpoint.
    A maximum duration of 7 days of data can be queried. Any queries with a `start_time`, `end_time`, or
    `time_range` resulting in a duration longer than 7 days will result in a `400` error response.

    Args:
        dataset_slug (str):
        body (CreateQueryResultRequest): A Query Result is created with the Query ID.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, QueryResult, ValidationError]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: CreateQueryResultRequest,

) -> Response[Union[DetailedError, Error, QueryResult, ValidationError]]:
    """ Create a Query Result

     Kick off processing of a Query to then get back the Query Results.
    Once the Query Result has been created, the query will be run asynchronously, allowing the result
    data to be fetched from the GET query result endpoint.
    A maximum duration of 7 days of data can be queried. Any queries with a `start_time`, `end_time`, or
    `time_range` resulting in a duration longer than 7 days will result in a `400` error response.

    Args:
        dataset_slug (str):
        body (CreateQueryResultRequest): A Query Result is created with the Query ID.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, QueryResult, ValidationError]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: CreateQueryResultRequest,

) -> Optional[Union[DetailedError, Error, QueryResult, ValidationError]]:
    """ Create a Query Result

     Kick off processing of a Query to then get back the Query Results.
    Once the Query Result has been created, the query will be run asynchronously, allowing the result
    data to be fetched from the GET query result endpoint.
    A maximum duration of 7 days of data can be queried. Any queries with a `start_time`, `end_time`, or
    `time_range` resulting in a duration longer than 7 days will result in a `400` error response.

    Args:
        dataset_slug (str):
        body (CreateQueryResultRequest): A Query Result is created with the Query ID.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, QueryResult, ValidationError]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,

    )).parsed
