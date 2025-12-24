from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.email_recipient import EmailRecipient
from ...models.error import Error
from ...models.ms_teams_recipient import MSTeamsRecipient
from ...models.ms_teams_workflow_recipient import MSTeamsWorkflowRecipient
from ...models.pager_duty_recipient import PagerDutyRecipient
from ...models.slack_recipient import SlackRecipient
from ...models.validation_error import ValidationError
from ...models.webhook_recipient import WebhookRecipient
from typing import cast
from typing import cast, Union



def _get_kwargs(
    recipient_id: str,
    *,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/1/recipients/{recipient_id}".format(recipient_id=recipient_id,),
    }

    _body: dict[str, Any]
    if isinstance(body, PagerDutyRecipient):
        _body = body.to_dict()
    elif isinstance(body, EmailRecipient):
        _body = body.to_dict()
    elif isinstance(body, SlackRecipient):
        _body = body.to_dict()
    elif isinstance(body, WebhookRecipient):
        _body = body.to_dict()
    elif isinstance(body, MSTeamsRecipient):
        _body = body.to_dict()
    else:
        _body = body.to_dict()



    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    if response.status_code == 200:
        def _parse_response_200(data: object) -> Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_recipient_type_0 = PagerDutyRecipient.from_dict(data)



                return componentsschemas_recipient_type_0
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_recipient_type_1 = EmailRecipient.from_dict(data)



                return componentsschemas_recipient_type_1
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_recipient_type_2 = SlackRecipient.from_dict(data)



                return componentsschemas_recipient_type_2
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_recipient_type_3 = WebhookRecipient.from_dict(data)



                return componentsschemas_recipient_type_3
            except: # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_recipient_type_4 = MSTeamsRecipient.from_dict(data)



                return componentsschemas_recipient_type_4
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_recipient_type_5 = MSTeamsWorkflowRecipient.from_dict(data)



            return componentsschemas_recipient_type_5

        response_200 = _parse_response_200(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())



        return response_404
    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())



        return response_409
    if response.status_code == 422:
        response_422 = ValidationError.from_dict(response.json())



        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    recipient_id: str,
    *,
    client: AuthenticatedClient,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> Response[Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    """ Update a Recipient

     Update a Recipient by specifying the recipient ID and full recipient details. (Partial PUT is not
    supported.)
    Updates to the Recipient Type is not supported. For example, changing an existing Recipient from
    PagerDuty to Email is not allowed.
    **Important**: Modifying an existing recipient will change the destination of all triggers/burn
    alerts that use that recipient.

    Args:
        recipient_id (str):
        body (Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient',
            'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]
     """


    kwargs = _get_kwargs(
        recipient_id=recipient_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    recipient_id: str,
    *,
    client: AuthenticatedClient,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> Optional[Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    """ Update a Recipient

     Update a Recipient by specifying the recipient ID and full recipient details. (Partial PUT is not
    supported.)
    Updates to the Recipient Type is not supported. For example, changing an existing Recipient from
    PagerDuty to Email is not allowed.
    **Important**: Modifying an existing recipient will change the destination of all triggers/burn
    alerts that use that recipient.

    Args:
        recipient_id (str):
        body (Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient',
            'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]
     """


    return sync_detailed(
        recipient_id=recipient_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    recipient_id: str,
    *,
    client: AuthenticatedClient,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> Response[Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    """ Update a Recipient

     Update a Recipient by specifying the recipient ID and full recipient details. (Partial PUT is not
    supported.)
    Updates to the Recipient Type is not supported. For example, changing an existing Recipient from
    PagerDuty to Email is not allowed.
    **Important**: Modifying an existing recipient will change the destination of all triggers/burn
    alerts that use that recipient.

    Args:
        recipient_id (str):
        body (Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient',
            'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]
     """


    kwargs = _get_kwargs(
        recipient_id=recipient_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    recipient_id: str,
    *,
    client: AuthenticatedClient,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> Optional[Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    """ Update a Recipient

     Update a Recipient by specifying the recipient ID and full recipient details. (Partial PUT is not
    supported.)
    Updates to the Recipient Type is not supported. For example, changing an existing Recipient from
    PagerDuty to Email is not allowed.
    **Important**: Modifying an existing recipient will change the destination of all triggers/burn
    alerts that use that recipient.

    Args:
        recipient_id (str):
        body (Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient',
            'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]
     """


    return (await asyncio_detailed(
        recipient_id=recipient_id,
client=client,
body=body,

    )).parsed
