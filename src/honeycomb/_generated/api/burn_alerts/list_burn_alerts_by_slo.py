from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.validation_error import ValidationError
from typing import cast



def _get_kwargs(
    dataset_slug: str,
    *,
    slo_id: str,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["slo_id"] = slo_id


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/burn_alerts/{dataset_slug}".format(dataset_slug=dataset_slug,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, ValidationError]]:
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
        response_429 = Error.from_dict(response.json())



        return response_429
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, ValidationError]]:
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
    slo_id: str,

) -> Response[Union[Error, ValidationError]]:
    """ List All Burn Alerts for an SLO

     Get all burn alerts associated with the SLO specified in the `slo_id` query param. It is not
    currently possible to retrieve all burn alerts for a dataset, environment, or team.

    Args:
        dataset_slug (str):
        slo_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
slo_id=slo_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    slo_id: str,

) -> Optional[Union[Error, ValidationError]]:
    """ List All Burn Alerts for an SLO

     Get all burn alerts associated with the SLO specified in the `slo_id` query param. It is not
    currently possible to retrieve all burn alerts for a dataset, environment, or team.

    Args:
        dataset_slug (str):
        slo_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, ValidationError]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,
slo_id=slo_id,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    slo_id: str,

) -> Response[Union[Error, ValidationError]]:
    """ List All Burn Alerts for an SLO

     Get all burn alerts associated with the SLO specified in the `slo_id` query param. It is not
    currently possible to retrieve all burn alerts for a dataset, environment, or team.

    Args:
        dataset_slug (str):
        slo_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
slo_id=slo_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    slo_id: str,

) -> Optional[Union[Error, ValidationError]]:
    """ List All Burn Alerts for an SLO

     Get all burn alerts associated with the SLO specified in the `slo_id` query param. It is not
    currently possible to retrieve all burn alerts for a dataset, environment, or team.

    Args:
        dataset_slug (str):
        slo_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, ValidationError]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
slo_id=slo_id,

    )).parsed
