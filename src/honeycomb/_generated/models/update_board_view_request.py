from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.board_view_filter import BoardViewFilter





T = TypeVar("T", bound="UpdateBoardViewRequest")



@_attrs_define
class UpdateBoardViewRequest:
    """ 
        Attributes:
            name (str): The name of the view. Example: My View.
            filters (list['BoardViewFilter']): The filters to apply to this view.
            id (Union[Unset, str]): Unique identifier for the board view. Example: eC_abc123.
     """

    name: str
    filters: list['BoardViewFilter']
    id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.board_view_filter import BoardViewFilter
        name = self.name

        filters = []
        for filters_item_data in self.filters:
            filters_item = filters_item_data.to_dict()
            filters.append(filters_item)



        id = self.id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "filters": filters,
        })
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.board_view_filter import BoardViewFilter
        d = src_dict.copy()
        name = d.pop("name")

        filters = []
        _filters = d.pop("filters")
        for filters_item_data in (_filters):
            filters_item = BoardViewFilter.from_dict(filters_item_data)



            filters.append(filters_item)


        id = d.pop("id", UNSET)

        update_board_view_request = cls(
            name=name,
            filters=filters,
            id=id,
        )


        update_board_view_request.additional_properties = d
        return update_board_view_request

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
