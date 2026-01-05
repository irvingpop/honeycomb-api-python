from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.base_trigger_evaluation_schedule_window_days_of_week_item import \
    BaseTriggerEvaluationScheduleWindowDaysOfWeekItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="BaseTriggerEvaluationScheduleWindow")



@_attrs_define
class BaseTriggerEvaluationScheduleWindow:
    """ Window start/end times and days of the week are calculated in UTC. If the end time is the same as or earlier than
    the start time, the end time is treated as being in the following day.

        Attributes:
            days_of_week (list[BaseTriggerEvaluationScheduleWindowDaysOfWeekItem]):
            start_time (str): A UTC time in HH:mm format (13:00) Example: 840.
            end_time (str): A UTC time in HH:mm format (13:00) Example: 1260.
     """

    days_of_week: list[BaseTriggerEvaluationScheduleWindowDaysOfWeekItem]
    start_time: str
    end_time: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        days_of_week = []
        for days_of_week_item_data in self.days_of_week:
            days_of_week_item = days_of_week_item_data.value
            days_of_week.append(days_of_week_item)



        start_time = self.start_time

        end_time = self.end_time


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "days_of_week": days_of_week,
            "start_time": start_time,
            "end_time": end_time,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        days_of_week = []
        _days_of_week = d.pop("days_of_week")
        for days_of_week_item_data in (_days_of_week):
            days_of_week_item = BaseTriggerEvaluationScheduleWindowDaysOfWeekItem(days_of_week_item_data)



            days_of_week.append(days_of_week_item)


        start_time = d.pop("start_time")

        end_time = d.pop("end_time")

        base_trigger_evaluation_schedule_window = cls(
            days_of_week=days_of_week,
            start_time=start_time,
            end_time=end_time,
        )


        base_trigger_evaluation_schedule_window.additional_properties = d
        return base_trigger_evaluation_schedule_window

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
