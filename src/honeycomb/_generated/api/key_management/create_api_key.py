from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.api_key_create_request import ApiKeyCreateRequest
from ...models.detailed_error import DetailedError
from ...models.error import Error
from ...models.validation_error import ValidationError
from typing import cast



def _get_kwargs(
    team_slug: str,
    *,
    body: ApiKeyCreateRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/2/teams/{team_slug}/api-keys".format(team_slug=team_slug,),
    }

    _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/vnd.api+json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[DetailedError, Error, ValidationError]]:
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


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[DetailedError, Error, ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    body: ApiKeyCreateRequest,

) -> Response[Union[DetailedError, Error, ValidationError]]:
    """ Create an API Key

     This creates an API Key, which will return the API Key components in the response. The Key ID will
    be found at `data.id` and
    the Key Secret will be found at `data.attributes.secret`. For security reasons the Key Secret will
    only be available during creation so make sure to save it.

    To use a newly-created Ingest Key it should be passed in the `X-Honeycomb-Team` header with the API
    Key's ID and secret
    concatenated (and with no separator). For example, `X-Honeycomb-Team:
    hcxik_1234567890123456789012345612345678901234567890123456789012`

    Check out our [best practices for API Keys](https://docs.honeycomb.io/get-started/best-
    practices/api-keys/#ingest-keys).

    Args:
        team_slug (str):
        body (ApiKeyCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    body: ApiKeyCreateRequest,

) -> Optional[Union[DetailedError, Error, ValidationError]]:
    """ Create an API Key

     This creates an API Key, which will return the API Key components in the response. The Key ID will
    be found at `data.id` and
    the Key Secret will be found at `data.attributes.secret`. For security reasons the Key Secret will
    only be available during creation so make sure to save it.

    To use a newly-created Ingest Key it should be passed in the `X-Honeycomb-Team` header with the API
    Key's ID and secret
    concatenated (and with no separator). For example, `X-Honeycomb-Team:
    hcxik_1234567890123456789012345612345678901234567890123456789012`

    Check out our [best practices for API Keys](https://docs.honeycomb.io/get-started/best-
    practices/api-keys/#ingest-keys).

    Args:
        team_slug (str):
        body (ApiKeyCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, ValidationError]
     """


    return sync_detailed(
        team_slug=team_slug,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    body: ApiKeyCreateRequest,

) -> Response[Union[DetailedError, Error, ValidationError]]:
    """ Create an API Key

     This creates an API Key, which will return the API Key components in the response. The Key ID will
    be found at `data.id` and
    the Key Secret will be found at `data.attributes.secret`. For security reasons the Key Secret will
    only be available during creation so make sure to save it.

    To use a newly-created Ingest Key it should be passed in the `X-Honeycomb-Team` header with the API
    Key's ID and secret
    concatenated (and with no separator). For example, `X-Honeycomb-Team:
    hcxik_1234567890123456789012345612345678901234567890123456789012`

    Check out our [best practices for API Keys](https://docs.honeycomb.io/get-started/best-
    practices/api-keys/#ingest-keys).

    Args:
        team_slug (str):
        body (ApiKeyCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, ValidationError]]
     """


    kwargs = _get_kwargs(
        team_slug=team_slug,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    team_slug: str,
    *,
    client: AuthenticatedClient,
    body: ApiKeyCreateRequest,

) -> Optional[Union[DetailedError, Error, ValidationError]]:
    """ Create an API Key

     This creates an API Key, which will return the API Key components in the response. The Key ID will
    be found at `data.id` and
    the Key Secret will be found at `data.attributes.secret`. For security reasons the Key Secret will
    only be available during creation so make sure to save it.

    To use a newly-created Ingest Key it should be passed in the `X-Honeycomb-Team` header with the API
    Key's ID and secret
    concatenated (and with no separator). For example, `X-Honeycomb-Team:
    hcxik_1234567890123456789012345612345678901234567890123456789012`

    Check out our [best practices for API Keys](https://docs.honeycomb.io/get-started/best-
    practices/api-keys/#ingest-keys).

    Args:
        team_slug (str):
        body (ApiKeyCreateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, ValidationError]
     """


    return (await asyncio_detailed(
        team_slug=team_slug,
client=client,
body=body,

    )).parsed
