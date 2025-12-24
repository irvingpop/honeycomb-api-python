from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_aggregation_temporality import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumAggregationTemporality
from typing import cast

if TYPE_CHECKING:
  from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItem





T = TypeVar("T", bound="CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum")



@_attrs_define
class CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum:
    """ 
        Attributes:
            aggregation_temporality (CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetrics
                ItemMetricsItemSumAggregationTemporality):
            datapoints (list['CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMet
                ricsItemSumDatapointsItem']):
     """

    aggregation_temporality: CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumAggregationTemporality
    datapoints: list['CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItem']
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItem
        aggregation_temporality = self.aggregation_temporality.value

        datapoints = []
        for datapoints_item_data in self.datapoints:
            datapoints_item = datapoints_item_data.to_dict()
            datapoints.append(datapoints_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "aggregationTemporality": aggregation_temporality,
            "datapoints": datapoints,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item import CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItem
        d = src_dict.copy()
        aggregation_temporality = CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumAggregationTemporality(d.pop("aggregationTemporality"))




        datapoints = []
        _datapoints = d.pop("datapoints")
        for datapoints_item_data in (_datapoints):
            datapoints_item = CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItem.from_dict(datapoints_item_data)



            datapoints.append(datapoints_item)


        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum = cls(
            aggregation_temporality=aggregation_temporality,
            datapoints=datapoints,
        )


        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum.additional_properties = d
        return create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum

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
