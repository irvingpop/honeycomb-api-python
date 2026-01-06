from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.kinesis_event import KinesisEvent
from ...models.kinesis_response import KinesisResponse
from ...types import UNSET, Response


def _get_kwargs(
    dataset_slug: str,
    *,
    body: KinesisEvent,
    x_amz_firehose_request_id: str,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["X-Amz-Firehose-Request-Id"] = x_amz_firehose_request_id



    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/1/kinesis_events/{dataset_slug}".format(dataset_slug=dataset_slug,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, KinesisResponse]]:
    if response.status_code == 200:
        response_200 = KinesisResponse.from_dict(response.json())



        return response_200
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, KinesisResponse]]:
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
    body: KinesisEvent,
    x_amz_firehose_request_id: str,

) -> Response[Union[Error, KinesisResponse]]:
    """ Create Kinesis Events

     This endpoint processes events and metrics coming from AWS through Kinesis Firehose.

    Args:
        dataset_slug (str):
        x_amz_firehose_request_id (str):
        body (KinesisEvent):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, KinesisResponse]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,
x_amz_firehose_request_id=x_amz_firehose_request_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: KinesisEvent,
    x_amz_firehose_request_id: str,

) -> Optional[Union[Error, KinesisResponse]]:
    """ Create Kinesis Events

     This endpoint processes events and metrics coming from AWS through Kinesis Firehose.

    Args:
        dataset_slug (str):
        x_amz_firehose_request_id (str):
        body (KinesisEvent):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, KinesisResponse]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,
x_amz_firehose_request_id=x_amz_firehose_request_id,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: KinesisEvent,
    x_amz_firehose_request_id: str,

) -> Response[Union[Error, KinesisResponse]]:
    """ Create Kinesis Events

     This endpoint processes events and metrics coming from AWS through Kinesis Firehose.

    Args:
        dataset_slug (str):
        x_amz_firehose_request_id (str):
        body (KinesisEvent):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, KinesisResponse]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,
x_amz_firehose_request_id=x_amz_firehose_request_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: KinesisEvent,
    x_amz_firehose_request_id: str,

) -> Optional[Union[Error, KinesisResponse]]:
    """ Create Kinesis Events

     This endpoint processes events and metrics coming from AWS through Kinesis Firehose.

    Args:
        dataset_slug (str):
        x_amz_firehose_request_id (str):
        body (KinesisEvent):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, KinesisResponse]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,
x_amz_firehose_request_id=x_amz_firehose_request_id,

    )).parsed
