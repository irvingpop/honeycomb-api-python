from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.create_enhance_indexer_usage_record_request_data import \
      CreateEnhanceIndexerUsageRecordRequestData





T = TypeVar("T", bound="CreateEnhanceIndexerUsageRecordRequest")



@_attrs_define
class CreateEnhanceIndexerUsageRecordRequest:
    """ 
        Attributes:
            data (CreateEnhanceIndexerUsageRecordRequestData):
     """

    data: 'CreateEnhanceIndexerUsageRecordRequestData'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_enhance_indexer_usage_record_request_data import \
            CreateEnhanceIndexerUsageRecordRequestData
        data = self.data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "data": data,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_enhance_indexer_usage_record_request_data import \
            CreateEnhanceIndexerUsageRecordRequestData
        d = src_dict.copy()
        data = CreateEnhanceIndexerUsageRecordRequestData.from_dict(d.pop("data"))




        create_enhance_indexer_usage_record_request = cls(
            data=data,
        )


        create_enhance_indexer_usage_record_request.additional_properties = d
        return create_enhance_indexer_usage_record_request

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
