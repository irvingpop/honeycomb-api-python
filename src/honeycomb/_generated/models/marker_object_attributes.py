from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.marker_object_attributes_timestamps import \
      MarkerObjectAttributesTimestamps





T = TypeVar("T", bound="MarkerObjectAttributes")



@_attrs_define
class MarkerObjectAttributes:
    """ 
        Attributes:
            start_time (int): The time the Marker should be placed. Expressed in Unix Time (seconds since epoch). Example:
                1471040808.
            end_time (Union[Unset, int]): Optional end time, allows a Marker to represent a time range. Expressed in Unix
                Time (seconds since epoch). Example: 1471040908.
            message (Union[Unset, str]): A message to describe this specific Marker. Example: backend deploy #123.
            type_ (Union[Unset, str]): Groups similar Markers. All Markers of the same type appear with the same color on
                the graph. Example: deploy.
            url (Union[Unset, str]): A target URL for the marker. Clicking the marker text will navigate to this URL.
                Example: https://github.com/myorg/myrepo/commit/abc123.
            color (Union[Unset, str]): Color assigned to this marker type via Marker Settings. Specified as hexadecimal RGB.
                Example: #F96E11.
            timestamps (Union[Unset, MarkerObjectAttributesTimestamps]):
     """

    start_time: int
    end_time: Union[Unset, int] = UNSET
    message: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    color: Union[Unset, str] = UNSET
    timestamps: Union[Unset, 'MarkerObjectAttributesTimestamps'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.marker_object_attributes_timestamps import \
            MarkerObjectAttributesTimestamps
        start_time = self.start_time

        end_time = self.end_time

        message = self.message

        type_ = self.type_

        url = self.url

        color = self.color

        timestamps: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.timestamps, Unset):
            timestamps = self.timestamps.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "start_time": start_time,
        })
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if message is not UNSET:
            field_dict["message"] = message
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url
        if color is not UNSET:
            field_dict["color"] = color
        if timestamps is not UNSET:
            field_dict["timestamps"] = timestamps

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.marker_object_attributes_timestamps import \
            MarkerObjectAttributesTimestamps
        d = src_dict.copy()
        start_time = d.pop("start_time")

        end_time = d.pop("end_time", UNSET)

        message = d.pop("message", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        color = d.pop("color", UNSET)

        _timestamps = d.pop("timestamps", UNSET)
        timestamps: Union[Unset, MarkerObjectAttributesTimestamps]
        if isinstance(_timestamps,  Unset):
            timestamps = UNSET
        else:
            timestamps = MarkerObjectAttributesTimestamps.from_dict(_timestamps)




        marker_object_attributes = cls(
            start_time=start_time,
            end_time=end_time,
            message=message,
            type_=type_,
            url=url,
            color=color,
            timestamps=timestamps,
        )


        marker_object_attributes.additional_properties = d
        return marker_object_attributes

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
