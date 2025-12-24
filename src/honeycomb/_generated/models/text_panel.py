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
  from ..models.text_panel_text_panel import TextPanelTextPanel





T = TypeVar("T", bound="TextPanel")



@_attrs_define
class TextPanel:
    """ 
        Attributes:
            type_ (Literal['text']): The type of the board panel.
            text_panel (TextPanelTextPanel):
            position (Union[Unset, BoardPanelPosition]): The position of the panel within the layout. When X and Y
                coordinates are not specified for any of the panels, the layout will be generated automatically.
     """

    type_: Literal['text']
    text_panel: 'TextPanelTextPanel'
    position: Union[Unset, 'BoardPanelPosition'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.board_panel_position import BoardPanelPosition
        from ..models.text_panel_text_panel import TextPanelTextPanel
        type_ = self.type_

        text_panel = self.text_panel.to_dict()

        position: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.position, Unset):
            position = self.position.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "type": type_,
            "text_panel": text_panel,
        })
        if position is not UNSET:
            field_dict["position"] = position

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.board_panel_position import BoardPanelPosition
        from ..models.text_panel_text_panel import TextPanelTextPanel
        d = src_dict.copy()
        type_ = cast(Literal['text'] , d.pop("type"))
        if type_ != 'text':
            raise ValueError(f"type must match const 'text', got '{type_}'")

        text_panel = TextPanelTextPanel.from_dict(d.pop("text_panel"))




        _position = d.pop("position", UNSET)
        position: Union[Unset, BoardPanelPosition]
        if isinstance(_position,  Unset):
            position = UNSET
        else:
            position = BoardPanelPosition.from_dict(_position)




        text_panel = cls(
            type_=type_,
            text_panel=text_panel,
            position=position,
        )


        text_panel.additional_properties = d
        return text_panel

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
