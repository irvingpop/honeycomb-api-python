from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast






T = TypeVar("T", bound="SLOHistoryRequest")



@_attrs_define
class SLOHistoryRequest:
    """ 
        Attributes:
            ids (list[str]): A list of SLO IDs to retrieve history for. Cannot be an empty array or more than 24 in length.
                 Example: ['2LBq9LckbcA', 'CzcpPs7cJ4d'].
            start_time (int): The starting Unix timestamp, in seconds since the epoch, to retrieve historical data for.
                Cannot be more than a year in the past. Example: 1742230800.
            end_time (int): The ending Unix timestamp, in seconds since the epoch, to retrieve historical data for. Must be
                greater than `start_time`. Cannot be a future timestamp. Example: 1745254800.
     """

    ids: list[str]
    start_time: int
    end_time: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        ids = self.ids



        start_time = self.start_time

        end_time = self.end_time


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "ids": ids,
            "start_time": start_time,
            "end_time": end_time,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        ids = cast(list[str], d.pop("ids"))


        start_time = d.pop("start_time")

        end_time = d.pop("end_time")

        slo_history_request = cls(
            ids=ids,
            start_time=start_time,
            end_time=end_time,
        )


        slo_history_request.additional_properties = d
        return slo_history_request

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
