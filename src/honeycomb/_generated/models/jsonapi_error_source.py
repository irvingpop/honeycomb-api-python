from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JSONAPIErrorSource")



@_attrs_define
class JSONAPIErrorSource:
    """ Source of a JSON:API error

        Attributes:
            pointer (Union[Unset, str]):
            header (Union[Unset, str]):
            parameter (Union[Unset, str]):
     """

    pointer: Union[Unset, str] = UNSET
    header: Union[Unset, str] = UNSET
    parameter: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        pointer = self.pointer

        header = self.header

        parameter = self.parameter


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if pointer is not UNSET:
            field_dict["pointer"] = pointer
        if header is not UNSET:
            field_dict["header"] = header
        if parameter is not UNSET:
            field_dict["parameter"] = parameter

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        pointer = d.pop("pointer", UNSET)

        header = d.pop("header", UNSET)

        parameter = d.pop("parameter", UNSET)

        jsonapi_error_source = cls(
            pointer=pointer,
            header=header,
            parameter=parameter,
        )


        jsonapi_error_source.additional_properties = d
        return jsonapi_error_source

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
