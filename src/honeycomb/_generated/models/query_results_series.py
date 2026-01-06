from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.query_results_data_data import QueryResultsDataData





T = TypeVar("T", bound="QueryResultsSeries")



@_attrs_define
class QueryResultsSeries:
    """ 
        Attributes:
            data (Union[Unset, QueryResultsDataData]):
            time (Union[Unset, str]):  Example: 2021-04-09T14:16:00Z.
     """

    data: Union[Unset, 'QueryResultsDataData'] = UNSET
    time: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.query_results_data_data import QueryResultsDataData
        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        time = self.time


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if data is not UNSET:
            field_dict["data"] = data
        if time is not UNSET:
            field_dict["time"] = time

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.query_results_data_data import QueryResultsDataData
        d = src_dict.copy()
        _data = d.pop("data", UNSET)
        data: Union[Unset, QueryResultsDataData]
        if isinstance(_data,  Unset):
            data = UNSET
        else:
            data = QueryResultsDataData.from_dict(_data)




        time = d.pop("time", UNSET)

        query_results_series = cls(
            data=data,
            time=time,
        )


        query_results_series.additional_properties = d
        return query_results_series

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
