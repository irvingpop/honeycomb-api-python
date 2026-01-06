from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.api_key_create_request_data_type import \
    ApiKeyCreateRequestDataType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.api_key_create_request_data_relationships import \
      ApiKeyCreateRequestDataRelationships
  from ..models.configuration_key_attributes import ConfigurationKeyAttributes
  from ..models.ingest_key_attributes import IngestKeyAttributes





T = TypeVar("T", bound="ApiKeyCreateRequestData")



@_attrs_define
class ApiKeyCreateRequestData:
    """ 
        Attributes:
            type_ (ApiKeyCreateRequestDataType):
            attributes (Union['ConfigurationKeyAttributes', 'IngestKeyAttributes']):
            relationships (ApiKeyCreateRequestDataRelationships):
     """

    type_: ApiKeyCreateRequestDataType
    attributes: Union['ConfigurationKeyAttributes', 'IngestKeyAttributes']
    relationships: 'ApiKeyCreateRequestDataRelationships'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.api_key_create_request_data_relationships import \
            ApiKeyCreateRequestDataRelationships
        from ..models.configuration_key_attributes import \
            ConfigurationKeyAttributes
        from ..models.ingest_key_attributes import IngestKeyAttributes
        type_ = self.type_.value

        attributes: dict[str, Any]
        if isinstance(self.attributes, IngestKeyAttributes):
            attributes = self.attributes.to_dict()
        else:
            attributes = self.attributes.to_dict()


        relationships = self.relationships.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "type": type_,
            "attributes": attributes,
            "relationships": relationships,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.api_key_create_request_data_relationships import \
            ApiKeyCreateRequestDataRelationships
        from ..models.configuration_key_attributes import \
            ConfigurationKeyAttributes
        from ..models.ingest_key_attributes import IngestKeyAttributes
        d = src_dict.copy()
        type_ = ApiKeyCreateRequestDataType(d.pop("type"))




        def _parse_attributes(data: object) -> Union['ConfigurationKeyAttributes', 'IngestKeyAttributes']:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_api_key_attributes_type_0 = IngestKeyAttributes.from_dict(data)



                return componentsschemas_api_key_attributes_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_api_key_attributes_type_1 = ConfigurationKeyAttributes.from_dict(data)



            return componentsschemas_api_key_attributes_type_1

        attributes = _parse_attributes(d.pop("attributes"))


        relationships = ApiKeyCreateRequestDataRelationships.from_dict(d.pop("relationships"))




        api_key_create_request_data = cls(
            type_=type_,
            attributes=attributes,
            relationships=relationships,
        )


        api_key_create_request_data.additional_properties = d
        return api_key_create_request_data

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
