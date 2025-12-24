from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.query_op import QueryOp
from ..models.query_orders_item_order import QueryOrdersItemOrder
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="QueryOrdersItem")



@_attrs_define
class QueryOrdersItem:
    """ 
        Attributes:
            column (Union[Unset, str]):
            op (Union[Unset, QueryOp]):
            order (Union[Unset, QueryOrdersItemOrder]):  Default: QueryOrdersItemOrder.ASCENDING.
     """

    column: Union[Unset, str] = UNSET
    op: Union[Unset, QueryOp] = UNSET
    order: Union[Unset, QueryOrdersItemOrder] = QueryOrdersItemOrder.ASCENDING
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        column = self.column

        op: Union[Unset, str] = UNSET
        if not isinstance(self.op, Unset):
            op = self.op.value


        order: Union[Unset, str] = UNSET
        if not isinstance(self.order, Unset):
            order = self.order.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if column is not UNSET:
            field_dict["column"] = column
        if op is not UNSET:
            field_dict["op"] = op
        if order is not UNSET:
            field_dict["order"] = order

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        column = d.pop("column", UNSET)

        _op = d.pop("op", UNSET)
        op: Union[Unset, QueryOp]
        if isinstance(_op,  Unset):
            op = UNSET
        else:
            op = QueryOp(_op)




        _order = d.pop("order", UNSET)
        order: Union[Unset, QueryOrdersItemOrder]
        if isinstance(_order,  Unset):
            order = UNSET
        else:
            order = QueryOrdersItemOrder(_order)




        query_orders_item = cls(
            column=column,
            op=op,
            order=order,
        )


        query_orders_item.additional_properties = d
        return query_orders_item

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
