from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.validation_error_type_detail_item_code import ValidationErrorTypeDetailItemCode
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="ValidationErrorTypeDetailItem")



@_attrs_define
class ValidationErrorTypeDetailItem:
    """ 
        Attributes:
            field (Union[Unset, str]):
            code (Union[Unset, ValidationErrorTypeDetailItemCode]):
            description (Union[Unset, str]):
     """

    field: Union[Unset, str] = UNSET
    code: Union[Unset, ValidationErrorTypeDetailItemCode] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        field = self.field

        code: Union[Unset, str] = UNSET
        if not isinstance(self.code, Unset):
            code = self.code.value


        description = self.description


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if field is not UNSET:
            field_dict["field"] = field
        if code is not UNSET:
            field_dict["code"] = code
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        field = d.pop("field", UNSET)

        _code = d.pop("code", UNSET)
        code: Union[Unset, ValidationErrorTypeDetailItemCode]
        if isinstance(_code,  Unset):
            code = UNSET
        else:
            code = ValidationErrorTypeDetailItemCode(_code)




        description = d.pop("description", UNSET)

        validation_error_type_detail_item = cls(
            field=field,
            code=code,
            description=description,
        )


        validation_error_type_detail_item.additional_properties = d
        return validation_error_type_detail_item

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
