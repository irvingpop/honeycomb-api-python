from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.having_calculate_op import HavingCalculateOp
from ..models.having_op import HavingOp
from ..types import UNSET, Unset

T = TypeVar("T", bound="QueryHavingsItem")



@_attrs_define
class QueryHavingsItem:
    """ 
        Attributes:
            calculate_op (HavingCalculateOp):
            column (Union[None, Unset, str]): The name of the column to filter against
            op (Union[Unset, HavingOp]):
            value (Union[Unset, float]):  Default: 10.0.
     """

    calculate_op: HavingCalculateOp
    column: Union[None, Unset, str] = UNSET
    op: Union[Unset, HavingOp] = UNSET
    value: Union[Unset, float] = 10.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        calculate_op = self.calculate_op.value

        column: Union[None, Unset, str]
        if isinstance(self.column, Unset):
            column = UNSET
        else:
            column = self.column

        op: Union[Unset, str] = UNSET
        if not isinstance(self.op, Unset):
            op = self.op.value


        value = self.value


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "calculate_op": calculate_op,
        })
        if column is not UNSET:
            field_dict["column"] = column
        if op is not UNSET:
            field_dict["op"] = op
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        calculate_op = HavingCalculateOp(d.pop("calculate_op"))




        def _parse_column(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        column = _parse_column(d.pop("column", UNSET))


        _op = d.pop("op", UNSET)
        op: Union[Unset, HavingOp]
        if isinstance(_op,  Unset):
            op = UNSET
        else:
            op = HavingOp(_op)




        value = d.pop("value", UNSET)

        query_havings_item = cls(
            calculate_op=calculate_op,
            column=column,
            op=op,
            value=value,
        )


        query_havings_item.additional_properties = d
        return query_havings_item

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
