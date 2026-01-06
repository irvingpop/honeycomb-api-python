from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.api_key_object_type import ApiKeyObjectType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.api_key_object_links import ApiKeyObjectLinks
  from ..models.api_key_object_relationships import ApiKeyObjectRelationships
  from ..models.configuration_key_attributes import ConfigurationKeyAttributes
  from ..models.ingest_key_attributes import IngestKeyAttributes





T = TypeVar("T", bound="ApiKeyObject")



@_attrs_define
class ApiKeyObject:
    """ 
        Attributes:
            id (Union[Unset, str]): The unique identifier of the API Key.

                The last two characters of the prefix define the type of key. `ik` for Ingest Keys and `lk` for
                Configuration Keys.
                 Example: hcxik_12345678901234567890123456.
            type_ (Union[Unset, ApiKeyObjectType]):
            attributes (Union['ConfigurationKeyAttributes', 'IngestKeyAttributes', Unset]):
            relationships (Union[Unset, ApiKeyObjectRelationships]):
            links (Union[Unset, ApiKeyObjectLinks]):
     """

    id: Union[Unset, str] = UNSET
    type_: Union[Unset, ApiKeyObjectType] = UNSET
    attributes: Union['ConfigurationKeyAttributes', 'IngestKeyAttributes', Unset] = UNSET
    relationships: Union[Unset, 'ApiKeyObjectRelationships'] = UNSET
    links: Union[Unset, 'ApiKeyObjectLinks'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.api_key_object_links import ApiKeyObjectLinks
        from ..models.api_key_object_relationships import \
            ApiKeyObjectRelationships
        from ..models.configuration_key_attributes import \
            ConfigurationKeyAttributes
        from ..models.ingest_key_attributes import IngestKeyAttributes
        id = self.id

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value


        attributes: Union[Unset, dict[str, Any]]
        if isinstance(self.attributes, Unset):
            attributes = UNSET
        elif isinstance(self.attributes, IngestKeyAttributes):
            attributes = self.attributes.to_dict()
        else:
            attributes = self.attributes.to_dict()


        relationships: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.relationships, Unset):
            relationships = self.relationships.to_dict()

        links: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.links, Unset):
            links = self.links.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if relationships is not UNSET:
            field_dict["relationships"] = relationships
        if links is not UNSET:
            field_dict["links"] = links

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.api_key_object_links import ApiKeyObjectLinks
        from ..models.api_key_object_relationships import \
            ApiKeyObjectRelationships
        from ..models.configuration_key_attributes import \
            ConfigurationKeyAttributes
        from ..models.ingest_key_attributes import IngestKeyAttributes
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, ApiKeyObjectType]
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = ApiKeyObjectType(_type_)




        def _parse_attributes(data: object) -> Union['ConfigurationKeyAttributes', 'IngestKeyAttributes', Unset]:
            if isinstance(data, Unset):
                return data
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

        attributes = _parse_attributes(d.pop("attributes", UNSET))


        _relationships = d.pop("relationships", UNSET)
        relationships: Union[Unset, ApiKeyObjectRelationships]
        if isinstance(_relationships,  Unset):
            relationships = UNSET
        else:
            relationships = ApiKeyObjectRelationships.from_dict(_relationships)




        _links = d.pop("links", UNSET)
        links: Union[Unset, ApiKeyObjectLinks]
        if isinstance(_links,  Unset):
            links = UNSET
        else:
            links = ApiKeyObjectLinks.from_dict(_links)




        api_key_object = cls(
            id=id,
            type_=type_,
            attributes=attributes,
            relationships=relationships,
            links=links,
        )


        api_key_object.additional_properties = d
        return api_key_object

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
