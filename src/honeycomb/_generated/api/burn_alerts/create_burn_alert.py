from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.create_budget_rate_burn_alert_request import CreateBudgetRateBurnAlertRequest
from ...models.create_exhaustion_time_burn_alert_request import CreateExhaustionTimeBurnAlertRequest
from ...models.error import Error
from ...models.validation_error import ValidationError
from typing import cast
from typing import cast, Union



def _get_kwargs(
    dataset_slug: str,
    *,
    body: Union['CreateBudgetRateBurnAlertRequest', 'CreateExhaustionTimeBurnAlertRequest'],

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/1/burn_alerts/{dataset_slug}".format(dataset_slug=dataset_slug,),
    }

    _body: dict[str, Any]
    if isinstance(body, CreateExhaustionTimeBurnAlertRequest):
        _body = body.to_dict()
    else:
        _body = body.to_dict()



    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: Union['CreateBudgetRateBurnAlertRequest', 'CreateExhaustionTimeBurnAlertRequest'],

) -> Response[Union[Error, ValidationError]]:
    """ Create a Burn Alert

     Create a Burn Alert against a specified SLO.

    Args:
        dataset_slug (str):
        body (Union['CreateBudgetRateBurnAlertRequest', 'CreateExhaustionTimeBurnAlertRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, ValidationError]]
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
    body: Union['CreateBudgetRateBurnAlertRequest', 'CreateExhaustionTimeBurnAlertRequest'],

) -> Optional[Union[Error, ValidationError]]:
    """ Create a Burn Alert

     Create a Burn Alert against a specified SLO.

    Args:
        dataset_slug (str):
        body (Union['CreateBudgetRateBurnAlertRequest', 'CreateExhaustionTimeBurnAlertRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, ValidationError]
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
    body: Union['CreateBudgetRateBurnAlertRequest', 'CreateExhaustionTimeBurnAlertRequest'],

) -> Response[Union[Error, ValidationError]]:
    """ Create a Burn Alert

     Create a Burn Alert against a specified SLO.

    Args:
        dataset_slug (str):
        body (Union['CreateBudgetRateBurnAlertRequest', 'CreateExhaustionTimeBurnAlertRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, ValidationError]]
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
    body: Union['CreateBudgetRateBurnAlertRequest', 'CreateExhaustionTimeBurnAlertRequest'],

) -> Optional[Union[Error, ValidationError]]:
    """ Create a Burn Alert

     Create a Burn Alert against a specified SLO.

    Args:
        dataset_slug (str):
        body (Union['CreateBudgetRateBurnAlertRequest', 'CreateExhaustionTimeBurnAlertRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, ValidationError]
     """


    return (await asyncio_detailed(
        dataset_slug=dataset_slug,
client=client,
body=body,

    )).parsed
