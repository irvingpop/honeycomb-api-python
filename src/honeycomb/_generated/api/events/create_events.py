from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.batch_event import BatchEvent
from ...models.create_events_content_encoding import CreateEventsContentEncoding
from ...models.create_events_response_200_item import CreateEventsResponse200Item
from ...models.error import Error
from ...types import File, FileJsonType
from ...types import UNSET, Unset
from io import BytesIO
from typing import cast
from typing import Union



def _get_kwargs(
    dataset_slug: str,
    *,
    body: Union[
        list['BatchEvent'],
        File,
    ],
    content_encoding: Union[Unset, CreateEventsContentEncoding] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(content_encoding, Unset):
        headers["Content-Encoding"] = str(content_encoding)




    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/1/batch/{dataset_slug}".format(dataset_slug=dataset_slug,),
    }

    if isinstance(body, list['BatchEvent']):
        _json_body = []
        for body_item_data in body:
            body_item = body_item_data.to_dict()
            _json_body.append(body_item)




        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, File):
        _content_body = body.payload

        _kwargs["content"] = _content_body
        headers["Content-Type"] = "application/octet-stream"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, list['CreateEventsResponse200Item']]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = CreateEventsResponse200Item.from_dict(response_200_item_data)



            response_200.append(response_200_item)

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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, list['CreateEventsResponse200Item']]]:
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
    body: Union[
        list['BatchEvent'],
        File,
    ],
    content_encoding: Union[Unset, CreateEventsContentEncoding] = UNSET,

) -> Response[Union[Error, list['CreateEventsResponse200Item']]]:
    r""" Create Events

     Supports batch creation of events.

    Dataset names are case insensitive. `POST` requests to \"MyDatasET\" will land in the same dataset
    as \"mydataset\". Names may contain URL-encoded spaces or other special characters, but not URL-
    encoded slashes. For example, \"My%20Dataset\" will show up in the UI as \"My Dataset\".

    The first event received for a dataset determines the casing of the displayed name. All subsequent
    variations in casing will use the originally specified case.

    Args:
        dataset_slug (str):
        content_encoding (Union[Unset, CreateEventsContentEncoding]):
        body (list['BatchEvent']):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['CreateEventsResponse200Item']]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,
content_encoding=content_encoding,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        list['BatchEvent'],
        File,
    ],
    content_encoding: Union[Unset, CreateEventsContentEncoding] = UNSET,

) -> Optional[Union[Error, list['CreateEventsResponse200Item']]]:
    r""" Create Events

     Supports batch creation of events.

    Dataset names are case insensitive. `POST` requests to \"MyDatasET\" will land in the same dataset
    as \"mydataset\". Names may contain URL-encoded spaces or other special characters, but not URL-
    encoded slashes. For example, \"My%20Dataset\" will show up in the UI as \"My Dataset\".

    The first event received for a dataset determines the casing of the displayed name. All subsequent
    variations in casing will use the originally specified case.

    Args:
        dataset_slug (str):
        content_encoding (Union[Unset, CreateEventsContentEncoding]):
        body (list['BatchEvent']):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['CreateEventsResponse200Item']]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,
content_encoding=content_encoding,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        list['BatchEvent'],
        File,
    ],
    content_encoding: Union[Unset, CreateEventsContentEncoding] = UNSET,

) -> Response[Union[Error, list['CreateEventsResponse200Item']]]:
    r""" Create Events

     Supports batch creation of events.

    Dataset names are case insensitive. `POST` requests to \"MyDatasET\" will land in the same dataset
    as \"mydataset\". Names may contain URL-encoded spaces or other special characters, but not URL-
    encoded slashes. For example, \"My%20Dataset\" will show up in the UI as \"My Dataset\".

    The first event received for a dataset determines the casing of the displayed name. All subsequent
    variations in casing will use the originally specified case.

    Args:
        dataset_slug (str):
        content_encoding (Union[Unset, CreateEventsContentEncoding]):
        body (list['BatchEvent']):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list['CreateEventsResponse200Item']]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
body=body,
content_encoding=content_encoding,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        list['BatchEvent'],
        File,
    ],
    content_encoding: Union[Unset, CreateEventsContentEncoding] = UNSET,

) -> Optional[Union[Error, list['CreateEventsResponse200Item']]]:
    r""" Create Events

     Supports batch creation of events.

    Dataset names are case insensitive. `POST` requests to \"MyDatasET\" will land in the same dataset
    as \"mydataset\". Names may contain URL-encoded spaces or other special characters, but not URL-
    encoded slashes. For example, \"My%20Dataset\" will show up in the UI as \"My Dataset\".

    The first event received for a dataset determines the casing of the displayed name. All subsequent
    variations in casing will use the originally specified case.

    Args:
        dataset_slug (str):
        content_encoding (Union[Unset, CreateEventsContentEncoding]):
        body (list['BatchEvent']):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list['CreateEventsResponse200Item']]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,
content_encoding=content_encoding,

    )).parsed
