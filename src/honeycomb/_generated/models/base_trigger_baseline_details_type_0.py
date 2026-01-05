from typing import TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.base_trigger_baseline_details_type_0_offset_minutes import \
    BaseTriggerBaselineDetailsType0OffsetMinutes
from ..models.base_trigger_baseline_details_type_0_type import \
    BaseTriggerBaselineDetailsType0Type
from ..types import UNSET, Unset

T = TypeVar("T", bound="BaseTriggerBaselineDetailsType0")



@_attrs_define
class BaseTriggerBaselineDetailsType0:
    """ Additional properties needed to configure this trigger with a dynamic baseline threshold.

        Example:
            {'offset_minutes': 60, 'type': 'percentage'}

        Attributes:
            offset_minutes (BaseTriggerBaselineDetailsType0OffsetMinutes): For a given trigger run, how far back we should
                look to compare results. Currently only support comparison 1 hour, 24 hours, 7 days, or 28 days in the past.
            type_ (BaseTriggerBaselineDetailsType0Type): How to compare the change in the two time periods. Currently
                supports the difference in values (b-a) or the percentage difference in values (b-a)/b.
     """

    offset_minutes: BaseTriggerBaselineDetailsType0OffsetMinutes
    type_: BaseTriggerBaselineDetailsType0Type
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        offset_minutes = self.offset_minutes.value

        type_ = self.type_.value


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "offset_minutes": offset_minutes,
            "type": type_,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        offset_minutes = BaseTriggerBaselineDetailsType0OffsetMinutes(d.pop("offset_minutes"))




        type_ = BaseTriggerBaselineDetailsType0Type(d.pop("type"))




        base_trigger_baseline_details_type_0 = cls(
            offset_minutes=offset_minutes,
            type_=type_,
        )


        base_trigger_baseline_details_type_0.additional_properties = d
        return base_trigger_baseline_details_type_0

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
