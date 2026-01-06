from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item_value import \
      CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItemValue





T = TypeVar("T", bound="CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItem")



@_attrs_define
class CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItem:
    """ 
        Attributes:
            key (str):
            value (CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum
                DatapointsItemAttributesItemValue):
     """

    key: str
    value: 'CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItemValue'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item_value import \
            CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItemValue
        key = self.key

        value = self.value.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "key": key,
            "value": value,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item_value import \
            CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItemValue
        d = src_dict.copy()
        key = d.pop("key")

        value = CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItemValue.from_dict(d.pop("value"))




        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item = cls(
            key=key,
            value=value,
        )


        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item.additional_properties = d
        return create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item

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
