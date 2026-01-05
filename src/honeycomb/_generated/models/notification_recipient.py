from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recipient_type import RecipientType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.notification_recipient_details import \
      NotificationRecipientDetails





T = TypeVar("T", bound="NotificationRecipient")



@_attrs_define
class NotificationRecipient:
    """ 
        Attributes:
            id (Union[Unset, str]):
            type_ (Union[Unset, RecipientType]): One of the supported Recipient Types
            target (Union[Unset, str]): The target of the notification. For example, the specific Slack channel or email
                address.
                For Recipients of `type = "webhook"` or `type = "msteams_workflow"`,
                this will be the Name in the UI and `webhook_name` in the Recipients API.
                Deprecated: Use the Recipients API first, then pass the Recipient ID.
            details (Union[Unset, NotificationRecipientDetails]):
     """

    id: Union[Unset, str] = UNSET
    type_: Union[Unset, RecipientType] = UNSET
    target: Union[Unset, str] = UNSET
    details: Union[Unset, 'NotificationRecipientDetails'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.notification_recipient_details import \
            NotificationRecipientDetails
        id = self.id

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value


        target = self.target

        details: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if target is not UNSET:
            field_dict["target"] = target
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.notification_recipient_details import \
            NotificationRecipientDetails
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, RecipientType]
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = RecipientType(_type_)




        target = d.pop("target", UNSET)

        _details = d.pop("details", UNSET)
        details: Union[Unset, NotificationRecipientDetails]
        if isinstance(_details,  Unset):
            details = UNSET
        else:
            details = NotificationRecipientDetails.from_dict(_details)




        notification_recipient = cls(
            id=id,
            type_=type_,
            target=target,
            details=details,
        )


        notification_recipient.additional_properties = d
        return notification_recipient

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
