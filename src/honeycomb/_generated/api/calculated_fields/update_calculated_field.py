from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.calculated_field import CalculatedField
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...types import UNSET, Response


def _get_kwargs(
    dataset_slug: str,
    derived_column_id: str,
    *,
    body: CalculatedField,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/1/derived_columns/{dataset_slug}/{derived_column_id}".format(dataset_slug=dataset_slug,derived_column_id=derived_column_id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[CalculatedField, DetailedError, Error]]:
    if response.status_code == 200:
        response_200 = CalculatedField.from_dict(response.json())



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
    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())



        return response_409
    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())



        return response_429
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[CalculatedField, DetailedError, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_slug: str,
    derived_column_id: str,
    *,
    client: AuthenticatedClient,
    body: CalculatedField,

) -> Response[Union[CalculatedField, DetailedError, Error]]:
    """ Update a Calculated Field

     Update a Calculated Field (also called a Derived Column).

    Args:
        dataset_slug (str):
        derived_column_id (str):
        body (CalculatedField):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CalculatedField, DetailedError, Error]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
derived_column_id=derived_column_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    derived_column_id: str,
    *,
    client: AuthenticatedClient,
    body: CalculatedField,

) -> Optional[Union[CalculatedField, DetailedError, Error]]:
    """ Update a Calculated Field

     Update a Calculated Field (also called a Derived Column).

    Args:
        dataset_slug (str):
        derived_column_id (str):
        body (CalculatedField):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CalculatedField, DetailedError, Error]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
derived_column_id=derived_column_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    derived_column_id: str,
    *,
    client: AuthenticatedClient,
    body: CalculatedField,

) -> Response[Union[CalculatedField, DetailedError, Error]]:
    """ Update a Calculated Field

     Update a Calculated Field (also called a Derived Column).

    Args:
        dataset_slug (str):
        derived_column_id (str):
        body (CalculatedField):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CalculatedField, DetailedError, Error]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
derived_column_id=derived_column_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    derived_column_id: str,
    *,
    client: AuthenticatedClient,
    body: CalculatedField,

) -> Optional[Union[CalculatedField, DetailedError, Error]]:
    """ Update a Calculated Field

     Update a Calculated Field (also called a Derived Column).

    Args:
        dataset_slug (str):
        derived_column_id (str):
        body (CalculatedField):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CalculatedField, DetailedError, Error]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
derived_column_id=derived_column_id,
client=client,
body=body,

    )).parsed
