from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItemValue")



@_attrs_define
class CreatePipelineHealthRecordRequestDataAttributesUsageDataResourceMetricsItemScopeMetricsItemMetricsItemSumDatapointsItemAttributesItemValue:
    """ 
        Attributes:
            string_value (Union[Unset, str]):
     """

    string_value: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        string_value = self.string_value


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if string_value is not UNSET:
            field_dict["stringValue"] = string_value

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        string_value = d.pop("stringValue", UNSET)

        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item_value = cls(
            string_value=string_value,
        )


        create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item_value.additional_properties = d
        return create_pipeline_health_record_request_data_attributes_usage_data_resource_metrics_item_scope_metrics_item_metrics_item_sum_datapoints_item_attributes_item_value

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
