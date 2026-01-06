from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ingest_key_type_key_type import IngestKeyTypeKeyType
from ..types import UNSET, Unset

T = TypeVar("T", bound="IngestKeyType")



@_attrs_define
class IngestKeyType:
    """ 
        Attributes:
            key_type (IngestKeyTypeKeyType): The type of API Key Example: ingest.
            time_to_live (Union[Unset, str]): An optional property of an ingest key that determines the time at which the
                key becomes unauthorized.
                When the time_to_live passes, the key will no longer be usable. The time_to_live property can only
                be set when the key is created and cannot be changed.
                Expressed as a RFC3339-formatted time.
                 Example: 2025-11-19T18:01:02+00:00.
     """

    key_type: IngestKeyTypeKeyType
    time_to_live: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        key_type = self.key_type.value

        time_to_live = self.time_to_live


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "key_type": key_type,
        })
        if time_to_live is not UNSET:
            field_dict["time_to_live"] = time_to_live

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        key_type = IngestKeyTypeKeyType(d.pop("key_type"))




        time_to_live = d.pop("time_to_live", UNSET)

        ingest_key_type = cls(
            key_type=key_type,
            time_to_live=time_to_live,
        )


        ingest_key_type.additional_properties = d
        return ingest_key_type

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
