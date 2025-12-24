from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.pipeline_configuration_response_type import PipelineConfigurationResponseType
from typing import cast

if TYPE_CHECKING:
  from ..models.pipeline_configuration_response_links import PipelineConfigurationResponseLinks
  from ..models.pipeline_configuration_response_attributes import PipelineConfigurationResponseAttributes





T = TypeVar("T", bound="PipelineConfigurationResponse")



@_attrs_define
class PipelineConfigurationResponse:
    """ 
        Attributes:
            id (str):
            type_ (PipelineConfigurationResponseType):
            links (PipelineConfigurationResponseLinks):
            attributes (PipelineConfigurationResponseAttributes):
     """

    id: str
    type_: PipelineConfigurationResponseType
    links: 'PipelineConfigurationResponseLinks'
    attributes: 'PipelineConfigurationResponseAttributes'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.pipeline_configuration_response_links import PipelineConfigurationResponseLinks
        from ..models.pipeline_configuration_response_attributes import PipelineConfigurationResponseAttributes
        id = self.id

        type_ = self.type_.value

        links = self.links.to_dict()

        attributes = self.attributes.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "type": type_,
            "links": links,
            "attributes": attributes,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.pipeline_configuration_response_links import PipelineConfigurationResponseLinks
        from ..models.pipeline_configuration_response_attributes import PipelineConfigurationResponseAttributes
        d = src_dict.copy()
        id = d.pop("id")

        type_ = PipelineConfigurationResponseType(d.pop("type"))




        links = PipelineConfigurationResponseLinks.from_dict(d.pop("links"))




        attributes = PipelineConfigurationResponseAttributes.from_dict(d.pop("attributes"))




        pipeline_configuration_response = cls(
            id=id,
            type_=type_,
            links=links,
            attributes=attributes,
        )


        pipeline_configuration_response.additional_properties = d
        return pipeline_configuration_response

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
