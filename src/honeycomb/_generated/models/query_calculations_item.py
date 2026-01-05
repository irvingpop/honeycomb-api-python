from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.query_op import QueryOp
from ..types import UNSET, Unset

T = TypeVar("T", bound="QueryCalculationsItem")



@_attrs_define
class QueryCalculationsItem:
    """ 
        Attributes:
            op (QueryOp):
            column (Union[None, Unset, str]): the name of the column
     """

    op: QueryOp
    column: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        op = self.op.value

        column: Union[None, Unset, str]
        if isinstance(self.column, Unset):
            column = UNSET
        else:
            column = self.column


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "op": op,
        })
        if column is not UNSET:
            field_dict["column"] = column

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        op = QueryOp(d.pop("op"))




        def _parse_column(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        column = _parse_column(d.pop("column", UNSET))


        query_calculations_item = cls(
            op=op,
            column=column,
        )


        query_calculations_item.additional_properties = d
        return query_calculations_item

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
