from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_column import CreateColumn
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    dataset_slug: str,
    *,
    key_name: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["key_name"] = key_name


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/columns/{dataset_slug}".format(dataset_slug=dataset_slug,),
        "params": params,
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]]:
    if response.status_code == 200:
        def _parse_response_200(data: object) -> Union['CreateColumn', list['CreateColumn']]:
            try:
                if not isinstance(data, list):
                    raise TypeError()
                response_200_type_0 = []
                _response_200_type_0 = data
                for componentsschemas_column_list_item_data in (_response_200_type_0):
                    componentsschemas_column_list_item = CreateColumn.from_dict(componentsschemas_column_list_item_data)



                    response_200_type_0.append(componentsschemas_column_list_item)

                return response_200_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_1 = CreateColumn.from_dict(data)



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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]]:
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
    key_name: Union[Unset, str] = UNSET,

) -> Response[Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]]:
    """ List all Columns

     Get all the Columns in a dataset or environment.
    Use `__all__`  as the dataset slug to retrieve all Columns across all datasets in the environment
    (not available for classic environments).

    Args:
        dataset_slug (str):
        key_name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
key_name=key_name,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    key_name: Union[Unset, str] = UNSET,

) -> Optional[Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]]:
    """ List all Columns

     Get all the Columns in a dataset or environment.
    Use `__all__`  as the dataset slug to retrieve all Columns across all datasets in the environment
    (not available for classic environments).

    Args:
        dataset_slug (str):
        key_name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]
     """


    return sync_detailed(
        dataset_slug=dataset_slug,
client=client,
key_name=key_name,

    ).parsed

async def asyncio_detailed(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    key_name: Union[Unset, str] = UNSET,

) -> Response[Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]]:
    """ List all Columns

     Get all the Columns in a dataset or environment.
    Use `__all__`  as the dataset slug to retrieve all Columns across all datasets in the environment
    (not available for classic environments).

    Args:
        dataset_slug (str):
        key_name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]]
     """


    kwargs = _get_kwargs(
        dataset_slug=dataset_slug,
key_name=key_name,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    dataset_slug: str,
    *,
    client: AuthenticatedClient,
    key_name: Union[Unset, str] = UNSET,

) -> Optional[Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]]:
    """ List all Columns

     Get all the Columns in a dataset or environment.
    Use `__all__`  as the dataset slug to retrieve all Columns across all datasets in the environment
    (not available for classic environments).

    Args:
        dataset_slug (str):
        key_name (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, Union['CreateColumn', list['CreateColumn']]]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
key_name=key_name,

    )).parsed
