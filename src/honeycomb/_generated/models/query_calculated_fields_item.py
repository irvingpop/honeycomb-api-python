from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="QueryCalculatedFieldsItem")



@_attrs_define
class QueryCalculatedFieldsItem:
    """ 
        Attributes:
            name (str): The field name
            expression (str): The formula for your Calculated Field. To learn more about syntax and available functions, and
                to explore some example formulas, visit [Calculated Field Formula
                Reference](https://docs.honeycomb.io/reference/derived-column-formula/).
     """

    name: str
    expression: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        name = self.name

        expression = self.expression


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "expression": expression,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        expression = d.pop("expression")

        query_calculated_fields_item = cls(
            name=name,
            expression=expression,
        )


        query_calculated_fields_item.additional_properties = d
        return query_calculated_fields_item

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
