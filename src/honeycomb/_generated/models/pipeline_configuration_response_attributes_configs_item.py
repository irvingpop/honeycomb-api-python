from typing import TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PipelineConfigurationResponseAttributesConfigsItem")



@_attrs_define
class PipelineConfigurationResponseAttributesConfigsItem:
    """ 
        Attributes:
            kind (str): The configuration kind. Example: refinery_config.
            config_data (str): The pipeline configuration data. Example: refinery_config:
                  GRPCServerParameters:
                    Enabled: true
                    ListenAddr: 0.0.0.0:4317
                  General:
                    ConfigurationVersion: 2
                    MinRefineryVersion: "v2.0"
                .
     """

    kind: str
    config_data: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        config_data = self.config_data


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "kind": kind,
            "configData": config_data,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        kind = d.pop("kind")

        config_data = d.pop("configData")

        pipeline_configuration_response_attributes_configs_item = cls(
            kind=kind,
            config_data=config_data,
        )


        pipeline_configuration_response_attributes_configs_item.additional_properties = d
        return pipeline_configuration_response_attributes_configs_item

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
