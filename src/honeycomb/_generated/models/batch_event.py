from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.event import Event





T = TypeVar("T", bound="BatchEvent")



@_attrs_define
class BatchEvent:
    """ 
        Attributes:
            data (Union[Unset, Event]):
            time (Union[Unset, str]): Should be in RFC3339 high precision format (for example, YYYY-MM-DDTHH:MM:SS.mmmZ).
                May be a Unix epoch (seconds since 1970) with second or greater precision (for example, 1452759330927).
                Optional. If not set, defaults to the time that the API receives the event.
            samplerate (Union[Unset, int]): An integer representing the denominator in the fraction 1/n when client-side
                sampling has been applied. Optional. If not set, defaults to `1`, meaning "not sampled". Refer to
                [Sampling](https://docs.honeycomb.io/manage-data-volume/sample/sampled-data-in-honeycomb/) for more detail.
     """

    data: Union[Unset, 'Event'] = UNSET
    time: Union[Unset, str] = UNSET
    samplerate: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.event import Event
        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        time = self.time

        samplerate = self.samplerate


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if data is not UNSET:
            field_dict["data"] = data
        if time is not UNSET:
            field_dict["time"] = time
        if samplerate is not UNSET:
            field_dict["samplerate"] = samplerate

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.event import Event
        d = src_dict.copy()
        _data = d.pop("data", UNSET)
        data: Union[Unset, Event]
        if isinstance(_data,  Unset):
            data = UNSET
        else:
            data = Event.from_dict(_data)




        time = d.pop("time", UNSET)

        samplerate = d.pop("samplerate", UNSET)

        batch_event = cls(
            data=data,
            time=time,
            samplerate=samplerate,
        )


        batch_event.additional_properties = d
        return batch_event

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
