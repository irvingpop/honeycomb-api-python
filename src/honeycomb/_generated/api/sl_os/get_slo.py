from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.error import Error
from ...models.slo import SLO
from ...models.slo_detailed_response import SLODetailedResponse
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union



def _get_kwargs(
    dataset_slug: str,
    slo_id: str,
    *,
    detailed: Union[Unset, bool] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["detailed"] = detailed


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/slos/{dataset_slug}/{slo_id}".format(dataset_slug=dataset_slug,slo_id=slo_id,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, Union['SLO', 'SLODetailedResponse']]]:
    if response.status_code == 200:
        def _parse_response_200(data: object) -> Union['SLO', 'SLODetailedResponse']:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_type_0 = SLO.from_dict(data)



                return response_200_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_1 = SLODetailedResponse.from_dict(data)



            return response_200_type_1

        response_200 = _parse_response_200(response.json())

        return response_200
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, Union['SLO', 'SLODetailedResponse']]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    dataset_slug: str,
    slo_id: str,
    *,
    client: AuthenticatedClient,
    detailed: Union[Unset, bool] = UNSET,

) -> Response[Union[Error, Union['SLO', 'SLODetailedResponse']]]:
    """ Get an SLO

     Get an SLO by ID.

    Args:
        dataset_slug (str):
        slo_id (str):
        detailed (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Union['SLO', 'SLODetailedResponse']]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
slo_id=slo_id,
detailed=detailed,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    slo_id: str,
    *,
    client: AuthenticatedClient,
    detailed: Union[Unset, bool] = UNSET,

) -> Optional[Union[Error, Union['SLO', 'SLODetailedResponse']]]:
    """ Get an SLO

     Get an SLO by ID.

    Args:
        dataset_slug (str):
        slo_id (str):
        detailed (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Union['SLO', 'SLODetailedResponse']]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
slo_id=slo_id,
client=client,
detailed=detailed,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    slo_id: str,
    *,
    client: AuthenticatedClient,
    detailed: Union[Unset, bool] = UNSET,

) -> Response[Union[Error, Union['SLO', 'SLODetailedResponse']]]:
    """ Get an SLO

     Get an SLO by ID.

    Args:
        dataset_slug (str):
        slo_id (str):
        detailed (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Union['SLO', 'SLODetailedResponse']]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
slo_id=slo_id,
detailed=detailed,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    slo_id: str,
    *,
    client: AuthenticatedClient,
    detailed: Union[Unset, bool] = UNSET,

) -> Optional[Union[Error, Union['SLO', 'SLODetailedResponse']]]:
    """ Get an SLO

     Get an SLO by ID.

    Args:
        dataset_slug (str):
        slo_id (str):
        detailed (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Union['SLO', 'SLODetailedResponse']]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
slo_id=slo_id,
client=client,
detailed=detailed,

    )).parsed
