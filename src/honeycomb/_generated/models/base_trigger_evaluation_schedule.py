from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.base_trigger_evaluation_schedule_window import \
      BaseTriggerEvaluationScheduleWindow





T = TypeVar("T", bound="BaseTriggerEvaluationSchedule")



@_attrs_define
class BaseTriggerEvaluationSchedule:
    """ A schedule that determines when the trigger is run. When the time is within the scheduled
    window, the trigger will be run at the specified frequency. Outside of the window, the trigger
    will not be run.

        Attributes:
            window (BaseTriggerEvaluationScheduleWindow): Window start/end times and days of the week are calculated in UTC.
                If the end time is the same as or earlier than the start time, the end time is treated as being in the following
                day.
     """

    window: 'BaseTriggerEvaluationScheduleWindow'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.base_trigger_evaluation_schedule_window import \
            BaseTriggerEvaluationScheduleWindow
        window = self.window.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "window": window,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.base_trigger_evaluation_schedule_window import \
            BaseTriggerEvaluationScheduleWindow
        d = src_dict.copy()
        window = BaseTriggerEvaluationScheduleWindow.from_dict(d.pop("window"))




        base_trigger_evaluation_schedule = cls(
            window=window,
        )


        base_trigger_evaluation_schedule.additional_properties = d
        return base_trigger_evaluation_schedule

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
