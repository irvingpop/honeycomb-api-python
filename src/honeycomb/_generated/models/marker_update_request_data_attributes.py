from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MarkerUpdateRequestDataAttributes")



@_attrs_define
class MarkerUpdateRequestDataAttributes:
    """ 
        Attributes:
            start_time (Union[Unset, int]): The time the Marker should be placed. Expressed in Unix Time (seconds since
                epoch). Example: 1471040808.
            end_time (Union[Unset, int]): Optional end time. Must be >= start_time if provided. Expressed in Unix Time
                (seconds since epoch). Example: 1471040908.
            message (Union[Unset, str]): A message to describe this specific Marker. Example: backend deploy #123.
            type_ (Union[Unset, str]): Groups similar Markers. Example: deploy.
            url (Union[Unset, str]): A target URL for the marker. Example: https://github.com/myorg/myrepo/commit/abc123.
     """

    start_time: Union[Unset, int] = UNSET
    end_time: Union[Unset, int] = UNSET
    message: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        start_time = self.start_time

        end_time = self.end_time

        message = self.message

        type_ = self.type_

        url = self.url


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

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        start_time = d.pop("start_time", UNSET)

        end_time = d.pop("end_time", UNSET)

        message = d.pop("message", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        marker_update_request_data_attributes = cls(
            start_time=start_time,
            end_time=end_time,
            message=message,
            type_=type_,
            url=url,
        )


        marker_update_request_data_attributes.additional_properties = d
        return marker_update_request_data_attributes

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
