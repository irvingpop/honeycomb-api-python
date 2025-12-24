from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.slack_recipient_type import SlackRecipientType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime

if TYPE_CHECKING:
  from ..models.slack_recipient_details import SlackRecipientDetails





T = TypeVar("T", bound="SlackRecipient")



@_attrs_define
class SlackRecipient:
    """ 
        Attributes:
            id (Union[Unset, str]):  Example: yUheCUmgZ8p.
            created_at (Union[Unset, datetime.datetime]): ISO8601 formatted time the Recipient was created. Example:
                2022-07-26T22:38:04Z.
            updated_at (Union[Unset, datetime.datetime]): ISO8601 formatted time the Recipient was updated. Example:
                2022-07-26T22:38:04Z.
            type_ (Union[Unset, SlackRecipientType]): One of the supported Recipient Types
            details (Union[Unset, SlackRecipientDetails]): Specific schema for the Slack Recipient Type.
     """

    id: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    type_: Union[Unset, SlackRecipientType] = UNSET
    details: Union[Unset, 'SlackRecipientDetails'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.slack_recipient_details import SlackRecipientDetails
        id = self.id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value


        details: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if type_ is not UNSET:
            field_dict["type"] = type_
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.slack_recipient_details import SlackRecipientDetails
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at,  Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)




        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, SlackRecipientType]
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = SlackRecipientType(_type_)




        _details = d.pop("details", UNSET)
        details: Union[Unset, SlackRecipientDetails]
        if isinstance(_details,  Unset):
            details = UNSET
        else:
            details = SlackRecipientDetails.from_dict(_details)




        slack_recipient = cls(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            type_=type_,
            details=details,
        )


        slack_recipient.additional_properties = d
        return slack_recipient

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
