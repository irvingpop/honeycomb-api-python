from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.pipeline_configuration_response_attributes_configs_item import PipelineConfigurationResponseAttributesConfigsItem





T = TypeVar("T", bound="PipelineConfigurationResponseAttributes")



@_attrs_define
class PipelineConfigurationResponseAttributes:
    """ 
        Attributes:
            configs (list['PipelineConfigurationResponseAttributesConfigsItem']): The configurations for different pipeline
                components.
            rollout_id (Union[Unset, str]): The ID of the pipeline configuration rollout. Only returned if 'current' was
                requested.
     """

    configs: list['PipelineConfigurationResponseAttributesConfigsItem']
    rollout_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.pipeline_configuration_response_attributes_configs_item import PipelineConfigurationResponseAttributesConfigsItem
        configs = []
        for configs_item_data in self.configs:
            configs_item = configs_item_data.to_dict()
            configs.append(configs_item)



        rollout_id = self.rollout_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "configs": configs,
        })
        if rollout_id is not UNSET:
            field_dict["rolloutID"] = rollout_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.pipeline_configuration_response_attributes_configs_item import PipelineConfigurationResponseAttributesConfigsItem
        d = src_dict.copy()
        configs = []
        _configs = d.pop("configs")
        for configs_item_data in (_configs):
            configs_item = PipelineConfigurationResponseAttributesConfigsItem.from_dict(configs_item_data)



            configs.append(configs_item)


        rollout_id = d.pop("rolloutID", UNSET)

        pipeline_configuration_response_attributes = cls(
            configs=configs,
            rollout_id=rollout_id,
        )


        pipeline_configuration_response_attributes.additional_properties = d
        return pipeline_configuration_response_attributes

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
