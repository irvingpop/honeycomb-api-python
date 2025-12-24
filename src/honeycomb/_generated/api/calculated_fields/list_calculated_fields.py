from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.calculated_field import CalculatedField
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union



def _get_kwargs(
    dataset_slug: str,
    *,
    alias: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["alias"] = alias


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/derived_columns/{dataset_slug}".format(dataset_slug=dataset_slug,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]]:
    if response.status_code == 200:
        def _parse_response_200(data: object) -> Union['CalculatedField', list['CalculatedField']]:
            try:
                if not isinstance(data, list):
                    raise TypeError()
                response_200_type_0 = []
                _response_200_type_0 = data
                for componentsschemas_calculated_field_list_item_data in (_response_200_type_0):
                    componentsschemas_calculated_field_list_item = CalculatedField.from_dict(componentsschemas_calculated_field_list_item_data)



                    response_200_type_0.append(componentsschemas_calculated_field_list_item)

                return response_200_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_1 = CalculatedField.from_dict(data)



            return response_200_type_1

        response_200 = _parse_response_200(response.json())

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
    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())



        return response_429
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]]:
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
    alias: Union[Unset, str] = UNSET,

) -> Response[Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]]:
    """ List all Calculated Fields

     Get all the Calculated Fields (also called Derived Columns) in a dataset or environment. With the
    `?alias=X` query parameter, can return a single Calculated Field by its `alias`.

    Args:
        dataset_slug (str):
        alias (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
alias=alias,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    alias: Union[Unset, str] = UNSET,

) -> Optional[Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]]:
    """ List all Calculated Fields

     Get all the Calculated Fields (also called Derived Columns) in a dataset or environment. With the
    `?alias=X` query parameter, can return a single Calculated Field by its `alias`.

    Args:
        dataset_slug (str):
        alias (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,
alias=alias,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    alias: Union[Unset, str] = UNSET,

) -> Response[Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]]:
    """ List all Calculated Fields

     Get all the Calculated Fields (also called Derived Columns) in a dataset or environment. With the
    `?alias=X` query parameter, can return a single Calculated Field by its `alias`.

    Args:
        dataset_slug (str):
        alias (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
alias=alias,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    alias: Union[Unset, str] = UNSET,

) -> Optional[Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]]:
    """ List all Calculated Fields

     Get all the Calculated Fields (also called Derived Columns) in a dataset or environment. With the
    `?alias=X` query parameter, can return a single Calculated Field by its `alias`.

    Args:
        dataset_slug (str):
        alias (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, Union['CalculatedField', list['CalculatedField']]]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
alias=alias,

    )).parsed
