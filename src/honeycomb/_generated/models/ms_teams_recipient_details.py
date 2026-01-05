from typing import TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MSTeamsRecipientDetails")



@_attrs_define
class MSTeamsRecipientDetails:
    """ Specific schema for the MS Teams Recipient Type. Now deprecated, please use the `msteams_workflow` type instead.

        Attributes:
            webhook_name (str): A name for this recipient. Example: My Teams Channel.
            webhook_url (str): Incoming webhook URL of an Teams instance. Example:
                https://yourco.webhook.office.com/webhook/xxxx.
     """

    webhook_name: str
    webhook_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        webhook_name = self.webhook_name

        webhook_url = self.webhook_url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "webhook_name": webhook_name,
            "webhook_url": webhook_url,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        webhook_name = d.pop("webhook_name")

        webhook_url = d.pop("webhook_url")

        ms_teams_recipient_details = cls(
            webhook_name=webhook_name,
            webhook_url=webhook_url,
        )


        ms_teams_recipient_details.additional_properties = d
        return ms_teams_recipient_details

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
