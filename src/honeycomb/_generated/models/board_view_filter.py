from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.board_view_filter_operation import BoardViewFilterOperation
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="BoardViewFilter")



@_attrs_define
class BoardViewFilter:
    """ 
        Attributes:
            column (str): The column name to filter on. Example: status.
            operation (BoardViewFilterOperation): The filter operation. Example: =.
            value (Union[Unset, Any]): The value to filter by. Example: error.
     """

    column: str
    operation: BoardViewFilterOperation
    value: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        column = self.column

        operation = self.operation.value

        value = self.value


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "column": column,
            "operation": operation,
        })
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        column = d.pop("column")

        operation = BoardViewFilterOperation(d.pop("operation"))




        value = d.pop("value", UNSET)

        board_view_filter = cls(
            column=column,
            operation=operation,
            value=value,
        )


        board_view_filter.additional_properties = d
        return board_view_filter

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
