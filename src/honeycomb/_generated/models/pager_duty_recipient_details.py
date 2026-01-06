from typing import TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PagerDutyRecipientDetails")



@_attrs_define
class PagerDutyRecipientDetails:
    """ Specific schema for the Pagerduty Recipient Type

        Attributes:
            pagerduty_integration_name (str): A name for this Integration. Example: Example PagerDuty Service.
            pagerduty_integration_key (str): Pagerduty Integration Key. Example: 7zOwh1edS8xHGcwfb2bA4sqY8E6PJzSK.
     """

    pagerduty_integration_name: str
    pagerduty_integration_key: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        pagerduty_integration_name = self.pagerduty_integration_name

        pagerduty_integration_key = self.pagerduty_integration_key


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "pagerduty_integration_name": pagerduty_integration_name,
            "pagerduty_integration_key": pagerduty_integration_key,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        pagerduty_integration_name = d.pop("pagerduty_integration_name")

        pagerduty_integration_key = d.pop("pagerduty_integration_key")

        pager_duty_recipient_details = cls(
            pagerduty_integration_name=pagerduty_integration_name,
            pagerduty_integration_key=pagerduty_integration_key,
        )


        pager_duty_recipient_details.additional_properties = d
        return pager_duty_recipient_details

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
