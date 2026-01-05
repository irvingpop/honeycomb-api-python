from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Marker")



@_attrs_define
class Marker:
    """ 
        Attributes:
            start_time (Union[Unset, int]): Indicates the time the Marker should be placed. If missing, defaults to the time
                the request arrives. Expressed in Unix Time. Example: 1471040808.
            end_time (Union[Unset, int]): Specifies end time, and allows a Marker to be recorded as representing a time
                range, such as a 5 minute deploy. Expressed in Unix Time. Example: 1668453920.
            message (Union[Unset, str]): A message to describe this specific Marker. Example: backend deploy #123.
            type_ (Union[Unset, str]): Groups similar Markers. For example, `deploys`. All Markers of the same type appear
                with the same color on the graph. Refer to the [Marker Settings](/api/marker-settings/) API for altering the
                color of each type. Example: deploy.
            url (Union[Unset, str]): A target for the marker. Clicking the marker text will take you to this URL. Example:
                http://link-to-build.here.
            id (Union[Unset, str]): A 6 character hexadecimal string assigned on Marker creation.
            created_at (Union[Unset, str]): The ISO8601-formatted time when the Marker was created.
            updated_at (Union[Unset, str]): The ISO8601-formatted time when the Marker was updated.
            color (Union[Unset, str]): Color can be assigned to Markers using the Marker Settings endpoint. This field will
                be populated when List All Markers is called.
     """

    start_time: Union[Unset, int] = UNSET
    end_time: Union[Unset, int] = UNSET
    message: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    created_at: Union[Unset, str] = UNSET
    updated_at: Union[Unset, str] = UNSET
    color: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        start_time = self.start_time

        end_time = self.end_time

        message = self.message

        type_ = self.type_

        url = self.url

        id = self.id

        created_at = self.created_at

        updated_at = self.updated_at

        color = self.color


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if start_time is not UNSET:
            field_dict["start_time"] = start_time
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if message is not UNSET:
            field_dict["message"] = message
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url
        if id is not UNSET:
            field_dict["id"] = id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if color is not UNSET:
            field_dict["color"] = color

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        start_time = d.pop("start_time", UNSET)

        end_time = d.pop("end_time", UNSET)

        message = d.pop("message", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        id = d.pop("id", UNSET)

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        color = d.pop("color", UNSET)

        marker = cls(
            start_time=start_time,
            end_time=end_time,
            message=message,
            type_=type_,
            url=url,
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            color=color,
        )


        marker.additional_properties = d
        return marker

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
