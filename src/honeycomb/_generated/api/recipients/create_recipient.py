from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.detailed_error import DetailedError
from ...models.email_recipient import EmailRecipient
from ...models.error import Error
from ...models.ms_teams_recipient import MSTeamsRecipient
from ...models.ms_teams_workflow_recipient import MSTeamsWorkflowRecipient
from ...models.pager_duty_recipient import PagerDutyRecipient
from ...models.slack_recipient import SlackRecipient
from ...models.validation_error import ValidationError
from ...models.webhook_recipient import WebhookRecipient
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/1/recipients",
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


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    if response.status_code == 201:
        def _parse_response_201(data: object) -> Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']:
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

        response_201 = _parse_response_201(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = DetailedError.from_dict(response.json())



        return response_400
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())



        return response_403
    if response.status_code == 422:
        response_422 = ValidationError.from_dict(response.json())



        return response_422
    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())



        return response_409
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> Response[Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    """ Create a Recipient

     Unlike many resources, Recipients are not linked to a specific Environment or Dataset. The Recipient
    will be created for the Team associated with your API key.
    The `details` fields will vary depending on the `type` of Recipient. Use the drop-down to view the
    specific fields for each `type` value.
    Before Slack Recipients can be created, the Slack OAuth flow in the Integration Center must be
    completed.

    Args:
        body (Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient',
            'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> Optional[Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    """ Create a Recipient

     Unlike many resources, Recipients are not linked to a specific Environment or Dataset. The Recipient
    will be created for the Team associated with your API key.
    The `details` fields will vary depending on the `type` of Recipient. Use the drop-down to view the
    specific fields for each `type` value.
    Before Slack Recipients can be created, the Slack OAuth flow in the Integration Center must be
    completed.

    Args:
        body (Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient',
            'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> Response[Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    """ Create a Recipient

     Unlike many resources, Recipients are not linked to a specific Environment or Dataset. The Recipient
    will be created for the Team associated with your API key.
    The `details` fields will vary depending on the `type` of Recipient. Use the drop-down to view the
    specific fields for each `type` value.
    Before Slack Recipients can be created, the Slack OAuth flow in the Integration Center must be
    completed.

    Args:
        body (Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient',
            'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'],

) -> Optional[Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]]:
    """ Create a Recipient

     Unlike many resources, Recipients are not linked to a specific Environment or Dataset. The Recipient
    will be created for the Team associated with your API key.
    The `details` fields will vary depending on the `type` of Recipient. Use the drop-down to view the
    specific fields for each `type` value.
    Before Slack Recipients can be created, the Slack OAuth flow in the Integration Center must be
    completed.

    Args:
        body (Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient',
            'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DetailedError, Error, Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient'], ValidationError]
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
