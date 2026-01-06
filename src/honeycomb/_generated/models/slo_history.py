from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SLOHistory")



@_attrs_define
class SLOHistory:
    """ 
        Attributes:
            timestamp (Union[Unset, int]): The starting Unix timestamp, in seconds since the epoch, for the interval.
                Example: 1744650000.
            compliance (Union[Unset, float]): Historical compliance of the SLO in this interval.
                 Example: 91.44851657940663.
            budget_remaining (Union[Unset, float]): How much error budget remains for the SLO in this interval.
                 Example: 14.48516579406632.
     """

    timestamp: Union[Unset, int] = UNSET
    compliance: Union[Unset, float] = UNSET
    budget_remaining: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        timestamp = self.timestamp

        compliance = self.compliance

        budget_remaining = self.budget_remaining


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if compliance is not UNSET:
            field_dict["compliance"] = compliance
        if budget_remaining is not UNSET:
            field_dict["budget_remaining"] = budget_remaining

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        timestamp = d.pop("timestamp", UNSET)

        compliance = d.pop("compliance", UNSET)

        budget_remaining = d.pop("budget_remaining", UNSET)

        slo_history = cls(
            timestamp=timestamp,
            compliance=compliance,
            budget_remaining=budget_remaining,
        )


        slo_history.additional_properties = d
        return slo_history

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
