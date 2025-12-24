from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Literal, cast
from typing import Union

if TYPE_CHECKING:
  from ..models.board_panel_position import BoardPanelPosition
  from ..models.query_panel_query_panel import QueryPanelQueryPanel





T = TypeVar("T", bound="QueryPanel")



@_attrs_define
class QueryPanel:
    """ 
        Attributes:
            type_ (Literal['query']): The type of the board panel.
            query_panel (QueryPanelQueryPanel):
            position (Union[Unset, BoardPanelPosition]): The position of the panel within the layout. When X and Y
                coordinates are not specified for any of the panels, the layout will be generated automatically.
     """

    type_: Literal['query']
    query_panel: 'QueryPanelQueryPanel'
    position: Union[Unset, 'BoardPanelPosition'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.board_panel_position import BoardPanelPosition
        from ..models.query_panel_query_panel import QueryPanelQueryPanel
        type_ = self.type_

        query_panel = self.query_panel.to_dict()

        position: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.position, Unset):
            position = self.position.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "type": type_,
            "query_panel": query_panel,
        })
        if position is not UNSET:
            field_dict["position"] = position

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.board_panel_position import BoardPanelPosition
        from ..models.query_panel_query_panel import QueryPanelQueryPanel
        d = src_dict.copy()
        type_ = cast(Literal['query'] , d.pop("type"))
        if type_ != 'query':
            raise ValueError(f"type must match const 'query', got '{type_}'")

        query_panel = QueryPanelQueryPanel.from_dict(d.pop("query_panel"))




        _position = d.pop("position", UNSET)
        position: Union[Unset, BoardPanelPosition]
        if isinstance(_position,  Unset):
            position = UNSET
        else:
            position = BoardPanelPosition.from_dict(_position)




        query_panel = cls(
            type_=type_,
            query_panel=query_panel,
            position=position,
        )


        query_panel.additional_properties = d
        return query_panel

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
