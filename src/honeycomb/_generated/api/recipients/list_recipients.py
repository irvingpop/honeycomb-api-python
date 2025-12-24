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
from ...models.webhook_recipient import WebhookRecipient
from typing import cast
from typing import cast, Union



def _get_kwargs(
    
) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/1/recipients",
    }


    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            def _parse_response_200_item(data: object) -> Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']:
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

            response_200_item = _parse_response_200_item(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())



        return response_401
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,

) -> Response[Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]]:
    """ List all Recipients

     Retrieve all recipients for a team.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]]
     """


    kwargs = _get_kwargs(
        
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]]:
    """ List all Recipients

     Retrieve all recipients for a team.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]
     """


    return sync_detailed(
        client=client,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,

) -> Response[Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]]:
    """ List all Recipients

     Retrieve all recipients for a team.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]]
     """


    kwargs = _get_kwargs(
        
    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,

) -> Optional[Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]]:
    """ List all Recipients

     Retrieve all recipients for a team.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, list[Union['EmailRecipient', 'MSTeamsRecipient', 'MSTeamsWorkflowRecipient', 'PagerDutyRecipient', 'SlackRecipient', 'WebhookRecipient']]]
     """


    return (await asyncio_detailed(
        client=client,

    )).parsed
