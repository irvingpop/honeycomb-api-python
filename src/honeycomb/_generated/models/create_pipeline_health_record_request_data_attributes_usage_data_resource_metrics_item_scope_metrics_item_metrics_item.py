from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum import \
      CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum





T = TypeVar("T", bound="CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItem")



@_attrs_define
class CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItem:
    """ 
        Attributes:
            name (str):
            sum_ (Union[Unset,
                CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum]):
     """

    name: str
    sum_: Union[Unset, 'CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum import \
            CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum
        name = self.name

        sum_: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sum_, Unset):
            sum_ = self.sum_.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
        })
        if sum_ is not UNSET:
            field_dict["sum"] = sum_

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum import \
            CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum
        d = src_dict.copy()
        name = d.pop("name")

        _sum_ = d.pop("sum", UNSET)
        sum_: Union[Unset, CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum]
        if isinstance(_sum_,  Unset):
            sum_ = UNSET
        else:
            sum_ = CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSum.from_dict(_sum_)




        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item = cls(
            name=name,
            sum_=sum_,
        )


        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item.additional_properties = d
        return create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item

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
