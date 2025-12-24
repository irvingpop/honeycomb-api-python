from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.base_trigger_threshold_op import BaseTriggerThresholdOp
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="BaseTriggerThreshold")



@_attrs_define
class BaseTriggerThreshold:
    """ The threshold over which the trigger will fire, specified as both an operator and a value.

        Attributes:
            op (BaseTriggerThresholdOp):
            value (float):
            exceeded_limit (Union[Unset, int]): The number of times the threshold must be met before an alert is sent.
                 Default: 1.
     """

    op: BaseTriggerThresholdOp
    value: float
    exceeded_limit: Union[Unset, int] = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        op = self.op.value

        value = self.value

        exceeded_limit = self.exceeded_limit


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "op": op,
            "value": value,
        })
        if exceeded_limit is not UNSET:
            field_dict["exceeded_limit"] = exceeded_limit

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        op = BaseTriggerThresholdOp(d.pop("op"))




        value = d.pop("value")

        exceeded_limit = d.pop("exceeded_limit", UNSET)

        base_trigger_threshold = cls(
            op=op,
            value=value,
            exceeded_limit=exceeded_limit,
        )


        base_trigger_threshold.additional_properties = d
        return base_trigger_threshold

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
