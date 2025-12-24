from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.api_key_response import ApiKeyResponse
from ...models.api_key_update_request import ApiKeyUpdateRequest
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...models.validation_error import ValidationError
from typing import cast



def _get_kwargs(
    team_slug: str,
    id: str,
    *,
    body: ApiKeyUpdateRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/2/teams/{team_slug}/api-keys/{id}".format(team_slug=team_slug,id=id,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[ApiKeyResponse, DetailedError, Error, ValidationError]]:
    if response.status_code == 200:
        response_200 = ApiKeyResponse.from_dict(response.json())



        return response_200
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
    if response.status_code == 413:
        response_413 = DetailedError.from_dict(response.json())



        return response_413
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[ApiKeyResponse, DetailedError, Error, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_slug: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: ApiKeyUpdateRequest,

) -> Response[Union[ApiKeyResponse, DetailedError, Error, ValidationError]]:
    """ Update an API Key

     Updates an API Key. The expected attributes depend on the key type:
    - **Ingest Keys** (prefix `hcxik_`): Support `name` and `enabled` attributes
    - **Configuration Keys** (prefix `hcxlk_`): Support `name`, `enabled`, and `permissions` attributes

    Args:
        team_slug (str):
        id (str):
        body (ApiKeyUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiKeyResponse, DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
id=id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    team_slug: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: ApiKeyUpdateRequest,

) -> Optional[Union[ApiKeyResponse, DetailedError, Error, ValidationError]]:
    """ Update an API Key

     Updates an API Key. The expected attributes depend on the key type:
    - **Ingest Keys** (prefix `hcxik_`): Support `name` and `enabled` attributes
    - **Configuration Keys** (prefix `hcxlk_`): Support `name`, `enabled`, and `permissions` attributes

    Args:
        team_slug (str):
        id (str):
        body (ApiKeyUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiKeyResponse, DetailedError, Error, ValidationError]
     """


    return sync_detailed(
        team_slug=team_slug,
id=id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    team_slug: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: ApiKeyUpdateRequest,

) -> Response[Union[ApiKeyResponse, DetailedError, Error, ValidationError]]:
    """ Update an API Key

     Updates an API Key. The expected attributes depend on the key type:
    - **Ingest Keys** (prefix `hcxik_`): Support `name` and `enabled` attributes
    - **Configuration Keys** (prefix `hcxlk_`): Support `name`, `enabled`, and `permissions` attributes

    Args:
        team_slug (str):
        id (str):
        body (ApiKeyUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiKeyResponse, DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
id=id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    team_slug: str,
    id: str,
    *,
    client: AuthenticatedClient,
    body: ApiKeyUpdateRequest,

) -> Optional[Union[ApiKeyResponse, DetailedError, Error, ValidationError]]:
    """ Update an API Key

     Updates an API Key. The expected attributes depend on the key type:
    - **Ingest Keys** (prefix `hcxik_`): Support `name` and `enabled` attributes
    - **Configuration Keys** (prefix `hcxlk_`): Support `name`, `enabled`, and `permissions` attributes

    Args:
        team_slug (str):
        id (str):
        body (ApiKeyUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiKeyResponse, DetailedError, Error, ValidationError]
     """


    return (await asyncio_detailed(
        team_slug=team_slug,
id=id,
client=client,
body=body,

    )).parsed
