from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.create_pipeline_health_record_request_data_attributes_usage_data import CreatePipelineHealthRecordRequestDataAttributesUsageData





T = TypeVar("T", bound="CreatePipelineHealthRecordRequestDataAttributes")



@_attrs_define
class CreatePipelineHealthRecordRequestDataAttributes:
    """ 
        Attributes:
            usage_data (Union[Unset, CreatePipelineHealthRecordRequestDataAttributesUsageData]):
     """

    usage_data: Union[Unset, 'CreatePipelineHealthRecordRequestDataAttributesUsageData'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data import CreatePipelineHealthRecordRequestDataAttributesUsageData
        usage_data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.usage_data, Unset):
            usage_data = self.usage_data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if usage_data is not UNSET:
            field_dict["usageData"] = usage_data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data import CreatePipelineHealthRecordRequestDataAttributesUsageData
        d = src_dict.copy()
        _usage_data = d.pop("usageData", UNSET)
        usage_data: Union[Unset, CreatePipelineHealthRecordRequestDataAttributesUsageData]
        if isinstance(_usage_data,  Unset):
            usage_data = UNSET
        else:
            usage_data = CreatePipelineHealthRecordRequestDataAttributesUsageData.from_dict(_usage_data)




        create_pipeline_health_record_request_data_attributes = cls(
            usage_data=usage_data,
        )


        create_pipeline_health_record_request_data_attributes.additional_properties = d
        return create_pipeline_health_record_request_data_attributes

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
