from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.event import Event
from ...types import UNSET, Response, Unset


def _get_kwargs(
    dataset_slug: str,
    *,
    body: Event,
    x_honeycomb_event_time: Union[Unset, int] = UNSET,
    x_honeycomb_samplerate: Union[Unset, int] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_honeycomb_event_time, Unset):
        headers["X-Honeycomb-Event-Time"] = str(x_honeycomb_event_time)


    if not isinstance(x_honeycomb_samplerate, Unset):
        headers["X-Honeycomb-Samplerate"] = str(x_honeycomb_samplerate)




    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/1/events/{dataset_slug}".format(dataset_slug=dataset_slug,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, Error]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
        return response_200
    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())



        return response_400
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())



        return response_403
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, Error]]:
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
    body: Event,
    x_honeycomb_event_time: Union[Unset, int] = UNSET,
    x_honeycomb_samplerate: Union[Unset, int] = UNSET,

) -> Response[Union[Any, Error]]:
    """ Create an Event

     Using this endpoint for anything more than testing is highly discouraged.

    Sending events in batches will be much more efficient and should be preferred if at all possible.

    Args:
        dataset_slug (str):
        x_honeycomb_event_time (Union[Unset, int]):
        x_honeycomb_samplerate (Union[Unset, int]):
        body (Event):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,
x_honeycomb_event_time=x_honeycomb_event_time,
x_honeycomb_samplerate=x_honeycomb_samplerate,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: Event,
    x_honeycomb_event_time: Union[Unset, int] = UNSET,
    x_honeycomb_samplerate: Union[Unset, int] = UNSET,

) -> Optional[Union[Any, Error]]:
    """ Create an Event

     Using this endpoint for anything more than testing is highly discouraged.

    Sending events in batches will be much more efficient and should be preferred if at all possible.

    Args:
        dataset_slug (str):
        x_honeycomb_event_time (Union[Unset, int]):
        x_honeycomb_samplerate (Union[Unset, int]):
        body (Event):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,
x_honeycomb_event_time=x_honeycomb_event_time,
x_honeycomb_samplerate=x_honeycomb_samplerate,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: Event,
    x_honeycomb_event_time: Union[Unset, int] = UNSET,
    x_honeycomb_samplerate: Union[Unset, int] = UNSET,

) -> Response[Union[Any, Error]]:
    """ Create an Event

     Using this endpoint for anything more than testing is highly discouraged.

    Sending events in batches will be much more efficient and should be preferred if at all possible.

    Args:
        dataset_slug (str):
        x_honeycomb_event_time (Union[Unset, int]):
        x_honeycomb_samplerate (Union[Unset, int]):
        body (Event):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,
x_honeycomb_event_time=x_honeycomb_event_time,
x_honeycomb_samplerate=x_honeycomb_samplerate,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: Event,
    x_honeycomb_event_time: Union[Unset, int] = UNSET,
    x_honeycomb_samplerate: Union[Unset, int] = UNSET,

) -> Optional[Union[Any, Error]]:
    """ Create an Event

     Using this endpoint for anything more than testing is highly discouraged.

    Sending events in batches will be much more efficient and should be preferred if at all possible.

    Args:
        dataset_slug (str):
        x_honeycomb_event_time (Union[Unset, int]):
        x_honeycomb_samplerate (Union[Unset, int]):
        body (Event):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,
x_honeycomb_event_time=x_honeycomb_event_time,
x_honeycomb_samplerate=x_honeycomb_samplerate,

    )).parsed
