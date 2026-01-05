from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.webhook_header import WebhookHeader
  from ..models.webhook_recipient_details_webhook_payloads import \
      WebhookRecipientDetailsWebhookPayloads





T = TypeVar("T", bound="WebhookRecipientDetails")



@_attrs_define
class WebhookRecipientDetails:
    """ Specific schema for the Webhook Recipient Type

        Attributes:
            webhook_name (str): A name for this Integration. Example: Example webhook.
            webhook_url (str): Webhook URL. Example: https://webhook.example.com.
            webhook_headers (Union[Unset, list['WebhookHeader']]): Custom headers for this webhook Example: [{'header':
                'Authorization', 'value': 'Bearer xyz123'}].
            webhook_secret (Union[Unset, str]): Webhook secret. Example: secret.
            webhook_payloads (Union[Unset, WebhookRecipientDetailsWebhookPayloads]): Specify a custom webhook payload.
     """

    webhook_name: str
    webhook_url: str
    webhook_headers: Union[Unset, list['WebhookHeader']] = UNSET
    webhook_secret: Union[Unset, str] = UNSET
    webhook_payloads: Union[Unset, 'WebhookRecipientDetailsWebhookPayloads'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.webhook_header import WebhookHeader
        from ..models.webhook_recipient_details_webhook_payloads import \
            WebhookRecipientDetailsWebhookPayloads
        webhook_name = self.webhook_name

        webhook_url = self.webhook_url

        webhook_headers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.webhook_headers, Unset):
            webhook_headers = []
            for webhook_headers_item_data in self.webhook_headers:
                webhook_headers_item = webhook_headers_item_data.to_dict()
                webhook_headers.append(webhook_headers_item)



        webhook_secret = self.webhook_secret

        webhook_payloads: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.webhook_payloads, Unset):
            webhook_payloads = self.webhook_payloads.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "webhook_name": webhook_name,
            "webhook_url": webhook_url,
        })
        if webhook_headers is not UNSET:
            field_dict["webhook_headers"] = webhook_headers
        if webhook_secret is not UNSET:
            field_dict["webhook_secret"] = webhook_secret
        if webhook_payloads is not UNSET:
            field_dict["webhook_payloads"] = webhook_payloads

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.webhook_header import WebhookHeader
        from ..models.webhook_recipient_details_webhook_payloads import \
            WebhookRecipientDetailsWebhookPayloads
        d = src_dict.copy()
        webhook_name = d.pop("webhook_name")

        webhook_url = d.pop("webhook_url")

        webhook_headers = []
        _webhook_headers = d.pop("webhook_headers", UNSET)
        for webhook_headers_item_data in (_webhook_headers or []):
            webhook_headers_item = WebhookHeader.from_dict(webhook_headers_item_data)



            webhook_headers.append(webhook_headers_item)


        webhook_secret = d.pop("webhook_secret", UNSET)

        _webhook_payloads = d.pop("webhook_payloads", UNSET)
        webhook_payloads: Union[Unset, WebhookRecipientDetailsWebhookPayloads]
        if isinstance(_webhook_payloads,  Unset):
            webhook_payloads = UNSET
        else:
            webhook_payloads = WebhookRecipientDetailsWebhookPayloads.from_dict(_webhook_payloads)




        webhook_recipient_details = cls(
            webhook_name=webhook_name,
            webhook_url=webhook_url,
            webhook_headers=webhook_headers,
            webhook_secret=webhook_secret,
            webhook_payloads=webhook_payloads,
        )


        webhook_recipient_details.additional_properties = d
        return webhook_recipient_details

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
