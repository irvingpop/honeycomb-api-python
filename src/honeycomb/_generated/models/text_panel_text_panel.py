from typing import TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TextPanelTextPanel")



@_attrs_define
class TextPanelTextPanel:
    """ 
        Attributes:
            content (str): The text content to display on the board panel. This field supports Markdown formatting.
                 Example: # This is a text panel with some content.
     """

    content: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        content = self.content


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "content": content,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        content = d.pop("content")

        text_panel_text_panel = cls(
            content=content,
        )


        text_panel_text_panel.additional_properties = d
        return text_panel_text_panel

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
