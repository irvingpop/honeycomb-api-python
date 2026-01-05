from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.map_node import MapNode





T = TypeVar("T", bound="CreateMapDependenciesRequest")



@_attrs_define
class CreateMapDependenciesRequest:
    """ Create a Map Dependency Request.

        Attributes:
            start_time (Union[Unset, int]): Absolute start time to evaluate dependencies, in seconds since UNIX epoch. Must
                be <= `end_time` (when `time_range` is not provided).
                 Example: 1622548800.
            end_time (Union[Unset, int]): Absolute end time to evaluate dependencies, in seconds since UNIX epoch. Must be
                >= `start_time` (when `time_range` is not provided).
                 Example: 1622635200.
            time_range (Union[Unset, int]): Time range in seconds (minimum 1). Can be used with either `start_time` (seconds
                after `start_time`), `end_time` (seconds before `end_time`), or without either (seconds before now).
                 Default: 7200. Example: 7200.
            filters (Union[Unset, list['MapNode']]): Optional list of service nodes to filter dependencies by. Only
                dependencies involving these nodes will be returned.
     """

    start_time: Union[Unset, int] = UNSET
    end_time: Union[Unset, int] = UNSET
    time_range: Union[Unset, int] = 7200
    filters: Union[Unset, list['MapNode']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.map_node import MapNode
        start_time = self.start_time

        end_time = self.end_time

        time_range = self.time_range

        filters: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = []
            for filters_item_data in self.filters:
                filters_item = filters_item_data.to_dict()
                filters.append(filters_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if start_time is not UNSET:
            field_dict["start_time"] = start_time
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if time_range is not UNSET:
            field_dict["time_range"] = time_range
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.map_node import MapNode
        d = src_dict.copy()
        start_time = d.pop("start_time", UNSET)

        end_time = d.pop("end_time", UNSET)

        time_range = d.pop("time_range", UNSET)

        filters = []
        _filters = d.pop("filters", UNSET)
        for filters_item_data in (_filters or []):
            filters_item = MapNode.from_dict(filters_item_data)



            filters.append(filters_item)


        create_map_dependencies_request = cls(
            start_time=start_time,
            end_time=end_time,
            time_range=time_range,
            filters=filters,
        )


        create_map_dependencies_request.additional_properties = d
        return create_map_dependencies_request

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
