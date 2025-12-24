from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.dataset_definitions import DatasetDefinitions
from ...models.detailed_error import DetailedError
from ...models.error import Error
from typing import cast



def _get_kwargs(
    dataset_slug: str,
    *,
    body: DatasetDefinitions,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/1/dataset_definitions/{dataset_slug}".format(dataset_slug=dataset_slug,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[DatasetDefinitions, DetailedError, Error]]:
    if response.status_code == 200:
        response_200 = DatasetDefinitions.from_dict(response.json())



        return response_200
    if response.status_code == 400:
        response_400 = DetailedError.from_dict(response.json())



        return response_400
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404
    if response.status_code == 422:
        response_422 = Error.from_dict(response.json())



        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[DatasetDefinitions, DetailedError, Error]]:
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
    body: DatasetDefinitions,

) -> Response[Union[DatasetDefinitions, DetailedError, Error]]:
    """ Set or Update Dataset Definitions

     Set or update one or more definitions for a Dataset.
    **Note**: While the PATCH payload can include the `column_type`, Honeycomb does not use this field
    when updating Dataset Definitions.

    Args:
        dataset_slug (str):
        body (DatasetDefinitions): Dataset Definitions describe the fields with special meaning in
            the Dataset.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DatasetDefinitions, DetailedError, Error]]
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
    body: DatasetDefinitions,

) -> Optional[Union[DatasetDefinitions, DetailedError, Error]]:
    """ Set or Update Dataset Definitions

     Set or update one or more definitions for a Dataset.
    **Note**: While the PATCH payload can include the `column_type`, Honeycomb does not use this field
    when updating Dataset Definitions.

    Args:
        dataset_slug (str):
        body (DatasetDefinitions): Dataset Definitions describe the fields with special meaning in
            the Dataset.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DatasetDefinitions, DetailedError, Error]
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
    body: DatasetDefinitions,

) -> Response[Union[DatasetDefinitions, DetailedError, Error]]:
    """ Set or Update Dataset Definitions

     Set or update one or more definitions for a Dataset.
    **Note**: While the PATCH payload can include the `column_type`, Honeycomb does not use this field
    when updating Dataset Definitions.

    Args:
        dataset_slug (str):
        body (DatasetDefinitions): Dataset Definitions describe the fields with special meaning in
            the Dataset.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DatasetDefinitions, DetailedError, Error]]
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
    body: DatasetDefinitions,

) -> Optional[Union[DatasetDefinitions, DetailedError, Error]]:
    """ Set or Update Dataset Definitions

     Set or update one or more definitions for a Dataset.
    **Note**: While the PATCH payload can include the `column_type`, Honeycomb does not use this field
    when updating Dataset Definitions.

    Args:
        dataset_slug (str):
        body (DatasetDefinitions): Dataset Definitions describe the fields with special meaning in
            the Dataset.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DatasetDefinitions, DetailedError, Error]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,

    )).parsed
