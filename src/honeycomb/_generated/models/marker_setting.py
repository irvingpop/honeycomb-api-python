from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MarkerSetting")



@_attrs_define
class MarkerSetting:
    """ 
        Attributes:
            type_ (str): Groups similar Markers. For example, 'deploys'. All Markers of the same type appears with the same
                color on the graph.
                 Example: deploy.
            color (str): Color to use for display of this marker type. Specified as hexadecimal RGB. For example, "#F96E11".
                 Example: #7b1fa2.
            id (Union[Unset, str]): The unique identifier (ID) for the Marker Setting. Example: gwAHiE5TS4j.
            created_at (Union[Unset, str]): The ISO8601-formatted time when the Marker Setting was created. Example:
                2022-09-15T05:39:42Z.
            updated_at (Union[None, Unset, str]): The ISO8601-formatted time when the Marker Setting was updated. Example:
                2022-12-15T04:25:14Z.
     """

    type_: str
    color: str
    id: Union[Unset, str] = UNSET
    created_at: Union[Unset, str] = UNSET
    updated_at: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        color = self.color

        id = self.id

        created_at = self.created_at

        updated_at: Union[None, Unset, str]
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "type": type_,
            "color": color,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        type_ = d.pop("type")

        color = d.pop("color")

        id = d.pop("id", UNSET)

        created_at = d.pop("created_at", UNSET)

        def _parse_updated_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))


        marker_setting = cls(
            type_=type_,
            color=color,
            id=id,
            created_at=created_at,
            updated_at=updated_at,
        )


        marker_setting.additional_properties = d
        return marker_setting

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
