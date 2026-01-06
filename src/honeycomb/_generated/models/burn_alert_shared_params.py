import datetime
from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="BurnAlertSharedParams")



@_attrs_define
class BurnAlertSharedParams:
    """ 
        Attributes:
            id (Union[Unset, str]): Unique identifier (ID) of a Burn alert. Example: fS7vfB81Wcy.
            description (Union[Unset, str]): A description of the Burn Alert. Example: Use this runbook if this alert
                fires..
            triggered (Union[Unset, bool]): Indicates if the Burn Alert has been triggered. This field is read-only and is
                set to `true` when the alert is triggered.
            created_at (Union[Unset, datetime.datetime]): The ISO8601-formatted time when the Burn Alert was created.
                Example: 2022-09-22T17:32:11Z.
            updated_at (Union[Unset, datetime.datetime]): The ISO8601-formatted time when the Burn Alert was updated.
                Example: 2022-10-31T15:08:11Z.
     """

    id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    triggered: Union[Unset, bool] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        id = self.id

        description = self.description

        triggered = self.triggered

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if triggered is not UNSET:
            field_dict["triggered"] = triggered
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        triggered = d.pop("triggered", UNSET)

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




        burn_alert_shared_params = cls(
            id=id,
            description=description,
            triggered=triggered,
            created_at=created_at,
            updated_at=updated_at,
        )


        burn_alert_shared_params.additional_properties = d
        return burn_alert_shared_params

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
