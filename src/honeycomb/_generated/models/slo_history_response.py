from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.slo_history import SLOHistory





T = TypeVar("T", bound="SLOHistoryResponse")



@_attrs_define
class SLOHistoryResponse:
    """ A mapping from SLO IDs (e.g., "2LBq9LckbcA") to their historical data. Each SLO ID maps to an array of compliance
    and budget intervals.

        Example:
            {'2LBq9LckbcA': [{'timestamp': 1744650000, 'compliance': 91.44851657940663, 'budget_remaining':
                14.48516579406632}, {'timestamp': 1744653600, 'compliance': 97.98746514671242, 'budget_remaining':
                88.13453467953423}], 'CzcpPs7cJ4d': [{'timestamp': 1744650000, 'compliance': 93.53414567784128,
                'budget_remaining': -71.02966841186735}]}

     """

    additional_properties: dict[str, list['SLOHistory']] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.slo_history import SLOHistory
        
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = []
            for additional_property_item_data in prop:
                additional_property_item = additional_property_item_data.to_dict()
                field_dict[prop_name].append(additional_property_item)



        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.slo_history import SLOHistory
        d = src_dict.copy()
        slo_history_response = cls(
        )


        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = []
            _additional_property = prop_dict
            for additional_property_item_data in (_additional_property):
                additional_property_item = SLOHistory.from_dict(additional_property_item_data)



                additional_property.append(additional_property_item)

            additional_properties[prop_name] = additional_property

        slo_history_response.additional_properties = additional_properties
        return slo_history_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> list['SLOHistory']:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: list['SLOHistory']) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
