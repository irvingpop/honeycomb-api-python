from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.filter_op import FilterOp
from ..types import UNSET, Unset

T = TypeVar("T", bound="QueryFiltersItem")



@_attrs_define
class QueryFiltersItem:
    """ 
        Attributes:
            op (FilterOp):
            column (Union[None, str]):
            value (Union[None, Unset, bool, float, int, list[str], str]):
     """

    op: FilterOp
    column: Union[None, str]
    value: Union[None, Unset, bool, float, int, list[str], str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        op = self.op.value

        column: Union[None, str]
        column = self.column

        value: Union[None, Unset, bool, float, int, list[str], str]
        if isinstance(self.value, Unset):
            value = UNSET
        elif isinstance(self.value, list):
            value = self.value


        else:
            value = self.value


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "op": op,
            "column": column,
        })
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        op = FilterOp(d.pop("op"))




        def _parse_column(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        column = _parse_column(d.pop("column"))


        def _parse_value(data: object) -> Union[None, Unset, bool, float, int, list[str], str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value_type_5 = cast(list[str], data)

                return value_type_5
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, bool, float, int, list[str], str], data)

        value = _parse_value(d.pop("value", UNSET))


        query_filters_item = cls(
            op=op,
            column=column,
            value=value,
        )


        query_filters_item.additional_properties = d
        return query_filters_item

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
