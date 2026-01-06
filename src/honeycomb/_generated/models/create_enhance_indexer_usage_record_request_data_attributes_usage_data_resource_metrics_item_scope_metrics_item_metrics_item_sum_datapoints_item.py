from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.create_enhance_indexer_usage_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item import \
      CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItem





T = TypeVar("T", bound="CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItem")



@_attrs_define
class CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItem:
    """ 
        Attributes:
            time_unix_nano (int):
            as_int (int):
            attributes (list['CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsIt
                emMetricsItemSumDatapointsItemAttributesItem']):
     """

    time_unix_nano: int
    as_int: int
    attributes: list['CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItem']
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_enhance_indexer_usage_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item import \
            CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItem
        time_unix_nano = self.time_unix_nano

        as_int = self.as_int

        attributes = []
        for attributes_item_data in self.attributes:
            attributes_item = attributes_item_data.to_dict()
            attributes.append(attributes_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "timeUnixNano": time_unix_nano,
            "asInt": as_int,
            "attributes": attributes,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_enhance_indexer_usage_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item import \
            CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItem
        d = src_dict.copy()
        time_unix_nano = d.pop("timeUnixNano")

        as_int = d.pop("asInt")

        attributes = []
        _attributes = d.pop("attributes")
        for attributes_item_data in (_attributes):
            attributes_item = CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItem.from_dict(attributes_item_data)



            attributes.append(attributes_item)


        create_enhance_indexer_usage_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item = cls(
            time_unix_nano=time_unix_nano,
            as_int=as_int,
            attributes=attributes,
        )


        create_enhance_indexer_usage_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item.additional_properties = d
        return create_enhance_indexer_usage_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item

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
