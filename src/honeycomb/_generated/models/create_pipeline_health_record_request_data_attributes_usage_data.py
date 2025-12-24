from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItem





T = TypeVar("T", bound="CreatePipelineHealthRecordRequestDataAttributesUsageData")



@_attrs_define
class CreatePipelineHealthRecordRequestDataAttributesUsageData:
    """ 
        Attributes:
            resource_metrics (list['CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItem']):
     """

    resource_metrics: list['CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItem']
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItem
        resource_metrics = []
        for resource_metrics_item_data in self.resource_metrics:
            resource_metrics_item = resource_metrics_item_data.to_dict()
            resource_metrics.append(resource_metrics_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "resourceMetrics": resource_metrics,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItem
        d = src_dict.copy()
        resource_metrics = []
        _resource_metrics = d.pop("resourceMetrics")
        for resource_metrics_item_data in (_resource_metrics):
            resource_metrics_item = CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItem.from_dict(resource_metrics_item_data)



            resource_metrics.append(resource_metrics_item)


        create_pipeline_health_record_request_data_attributes_usage_data = cls(
            resource_metrics=resource_metrics,
        )


        create_pipeline_health_record_request_data_attributes_usage_data.additional_properties = d
        return create_pipeline_health_record_request_data_attributes_usage_data

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
