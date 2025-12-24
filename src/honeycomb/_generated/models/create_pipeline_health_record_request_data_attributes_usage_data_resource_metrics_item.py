from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItem





T = TypeVar("T", bound="CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItem")



@_attrs_define
class CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItem:
    """ 
        Attributes:
            scope_metrics
                (list['CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItem']):
     """

    scope_metrics: list['CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItem']
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItem
        scope_metrics = []
        for scope_metrics_item_data in self.scope_metrics:
            scope_metrics_item = scope_metrics_item_data.to_dict()
            scope_metrics.append(scope_metrics_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "scopeMetrics": scope_metrics,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItem
        d = src_dict.copy()
        scope_metrics = []
        _scope_metrics = d.pop("scopeMetrics")
        for scope_metrics_item_data in (_scope_metrics):
            scope_metrics_item = CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItem.from_dict(scope_metrics_item_data)



            scope_metrics.append(scope_metrics_item)


        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item = cls(
            scope_metrics=scope_metrics,
        )


        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item.additional_properties = d
        return create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item

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
