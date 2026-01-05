from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="KinesisResponse")



@_attrs_define
class KinesisResponse:
    """ 
        Attributes:
            request_id (Union[Unset, str]):
            timestamp (Union[Unset, int]):
            error_message (Union[Unset, str]):
     """

    request_id: Union[Unset, str] = UNSET
    timestamp: Union[Unset, int] = UNSET
    error_message: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        timestamp = self.timestamp

        error_message = self.error_message


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if request_id is not UNSET:
            field_dict["requestId"] = request_id
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        request_id = d.pop("requestId", UNSET)

        timestamp = d.pop("timestamp", UNSET)

        error_message = d.pop("errorMessage", UNSET)

        kinesis_response = cls(
            request_id=request_id,
            timestamp=timestamp,
            error_message=error_message,
        )


        kinesis_response.additional_properties = d
        return kinesis_response

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
