from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.update_pipeline_configuration_rollout_type import UpdatePipelineConfigurationRolloutType
from typing import cast

if TYPE_CHECKING:
  from ..models.update_pipeline_configuration_rollout_attributes import UpdatePipelineConfigurationRolloutAttributes





T = TypeVar("T", bound="UpdatePipelineConfigurationRollout")



@_attrs_define
class UpdatePipelineConfigurationRollout:
    """ 
        Attributes:
            id (str):
            type_ (UpdatePipelineConfigurationRolloutType):
            attributes (UpdatePipelineConfigurationRolloutAttributes):
     """

    id: str
    type_: UpdatePipelineConfigurationRolloutType
    attributes: 'UpdatePipelineConfigurationRolloutAttributes'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.update_pipeline_configuration_rollout_attributes import UpdatePipelineConfigurationRolloutAttributes
        id = self.id

        type_ = self.type_.value

        attributes = self.attributes.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "type": type_,
            "attributes": attributes,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.update_pipeline_configuration_rollout_attributes import UpdatePipelineConfigurationRolloutAttributes
        d = src_dict.copy()
        id = d.pop("id")

        type_ = UpdatePipelineConfigurationRolloutType(d.pop("type"))




        attributes = UpdatePipelineConfigurationRolloutAttributes.from_dict(d.pop("attributes"))




        update_pipeline_configuration_rollout = cls(
            id=id,
            type_=type_,
            attributes=attributes,
        )


        update_pipeline_configuration_rollout.additional_properties = d
        return update_pipeline_configuration_rollout

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
