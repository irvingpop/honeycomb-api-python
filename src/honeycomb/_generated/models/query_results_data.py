from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.query_results_data_data import QueryResultsDataData





T = TypeVar("T", bound="QueryResultsData")



@_attrs_define
class QueryResultsData:
    """ Query result details

        Attributes:
            data (Union[Unset, QueryResultsDataData]):
     """

    data: Union[Unset, 'QueryResultsDataData'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.query_results_data_data import QueryResultsDataData
        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if data is not UNSET:
            field_dict["data"] = data

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




        query_results_data = cls(
            data=data,
        )


        query_results_data.additional_properties = d
        return query_results_data

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
