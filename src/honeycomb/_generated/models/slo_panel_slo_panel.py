from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="SLOPanelSloPanel")



@_attrs_define
class SLOPanelSloPanel:
    """ 
        Attributes:
            slo_id (Union[Unset, str]): The ID of the SLO to display on the board. The SLO must be in the same environment
                as the board.
                 Example: BGfyxhFto.
     """

    slo_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        slo_id = self.slo_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if slo_id is not UNSET:
            field_dict["slo_id"] = slo_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        slo_id = d.pop("slo_id", UNSET)

        slo_panel_slo_panel = cls(
            slo_id=slo_id,
        )


        slo_panel_slo_panel.additional_properties = d
        return slo_panel_slo_panel

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
