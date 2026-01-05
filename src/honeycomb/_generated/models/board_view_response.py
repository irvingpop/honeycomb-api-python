from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.board_view_filter import BoardViewFilter





T = TypeVar("T", bound="BoardViewResponse")



@_attrs_define
class BoardViewResponse:
    """ 
        Attributes:
            id (Union[Unset, str]): Unique identifier for the board view. Example: eC_abc123.
            name (Union[Unset, str]): The name of the view. Example: My View.
            filters (Union[Unset, list['BoardViewFilter']]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    filters: Union[Unset, list['BoardViewFilter']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.board_view_filter import BoardViewFilter
        id = self.id

        name = self.name

        filters: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = []
            for filters_item_data in self.filters:
                filters_item = filters_item_data.to_dict()
                filters.append(filters_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.board_view_filter import BoardViewFilter
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        filters = []
        _filters = d.pop("filters", UNSET)
        for filters_item_data in (_filters or []):
            filters_item = BoardViewFilter.from_dict(filters_item_data)



            filters.append(filters_item)


        board_view_response = cls(
            id=id,
            name=name,
            filters=filters,
        )


        board_view_response.additional_properties = d
        return board_view_response

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
