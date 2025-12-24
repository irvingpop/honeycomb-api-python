from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...models.pipeline_configuration_response import PipelineConfigurationResponse
from ...models.validation_error import ValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import Union



def _get_kwargs(
    team_slug: str,
    pipeline_id: str,
    configuration_id: str,
    *,
    filterkind: Union[Unset, str] = UNSET,
    generate_ingest_keys: Union[Unset, bool] = UNSET,
    if_none_match: Union[Unset, str] = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(if_none_match, Unset):
        headers["If-None-Match"] = if_none_match



    

    params: dict[str, Any] = {}

    params["filter[kind]"] = filterkind

    params["generate_ingest_keys"] = generate_ingest_keys


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/2/teams/{team_slug}/pipelines/{pipeline_id}/configurations/{configuration_id}".format(team_slug=team_slug,pipeline_id=pipeline_id,configuration_id=configuration_id,),
        "params": params,
    }


    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]]:
    if response.status_code == 200:
        response_200 = PipelineConfigurationResponse.from_dict(response.json())



        return response_200
    if response.status_code == 304:
        response_304 = cast(Any, None)
        return response_304
    if response.status_code == 400:
        response_400 = DetailedError.from_dict(response.json())



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
    if response.status_code == 422:
        response_422 = ValidationError.from_dict(response.json())



        return response_422
    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())



        return response_429
    if response.status_code == 500:
        response_500 = DetailedError.from_dict(response.json())



        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_slug: str,
    pipeline_id: str,
    configuration_id: str,
    *,
    client: AuthenticatedClient,
    filterkind: Union[Unset, str] = UNSET,
    generate_ingest_keys: Union[Unset, bool] = UNSET,
    if_none_match: Union[Unset, str] = UNSET,

) -> Response[Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]]:
    """ Get a Pipeline Configuration.

     Returns all the possible configuration kinds for a given pipeline configuration.

    Args:
        team_slug (str):
        pipeline_id (str):
        configuration_id (str):
        filterkind (Union[Unset, str]):
        generate_ingest_keys (Union[Unset, bool]):
        if_none_match (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
pipeline_id=pipeline_id,
configuration_id=configuration_id,
filterkind=filterkind,
generate_ingest_keys=generate_ingest_keys,
if_none_match=if_none_match,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    team_slug: str,
    pipeline_id: str,
    configuration_id: str,
    *,
    client: AuthenticatedClient,
    filterkind: Union[Unset, str] = UNSET,
    generate_ingest_keys: Union[Unset, bool] = UNSET,
    if_none_match: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]]:
    """ Get a Pipeline Configuration.

     Returns all the possible configuration kinds for a given pipeline configuration.

    Args:
        team_slug (str):
        pipeline_id (str):
        configuration_id (str):
        filterkind (Union[Unset, str]):
        generate_ingest_keys (Union[Unset, bool]):
        if_none_match (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]
     """


    return sync_detailed(
        team_slug=team_slug,
pipeline_id=pipeline_id,
configuration_id=configuration_id,
client=client,
filterkind=filterkind,
generate_ingest_keys=generate_ingest_keys,
if_none_match=if_none_match,

    ).parsed

async def asyncio_detailed(
    team_slug: str,
    pipeline_id: str,
    configuration_id: str,
    *,
    client: AuthenticatedClient,
    filterkind: Union[Unset, str] = UNSET,
    generate_ingest_keys: Union[Unset, bool] = UNSET,
    if_none_match: Union[Unset, str] = UNSET,

) -> Response[Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]]:
    """ Get a Pipeline Configuration.

     Returns all the possible configuration kinds for a given pipeline configuration.

    Args:
        team_slug (str):
        pipeline_id (str):
        configuration_id (str):
        filterkind (Union[Unset, str]):
        generate_ingest_keys (Union[Unset, bool]):
        if_none_match (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
pipeline_id=pipeline_id,
configuration_id=configuration_id,
filterkind=filterkind,
generate_ingest_keys=generate_ingest_keys,
if_none_match=if_none_match,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    team_slug: str,
    pipeline_id: str,
    configuration_id: str,
    *,
    client: AuthenticatedClient,
    filterkind: Union[Unset, str] = UNSET,
    generate_ingest_keys: Union[Unset, bool] = UNSET,
    if_none_match: Union[Unset, str] = UNSET,

) -> Optional[Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]]:
    """ Get a Pipeline Configuration.

     Returns all the possible configuration kinds for a given pipeline configuration.

    Args:
        team_slug (str):
        pipeline_id (str):
        configuration_id (str):
        filterkind (Union[Unset, str]):
        generate_ingest_keys (Union[Unset, bool]):
        if_none_match (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DetailedError, Error, PipelineConfigurationResponse, ValidationError]
     """


    return (await asyncio_detailed(
        team_slug=team_slug,
pipeline_id=pipeline_id,
configuration_id=configuration_id,
client=client,
filterkind=filterkind,
generate_ingest_keys=generate_ingest_keys,
if_none_match=if_none_match,

    )).parsed
