from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.auth_v2_response_data_type import AuthV2ResponseDataType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.auth_v2_response_data_attributes import \
      AuthV2ResponseDataAttributes
  from ..models.auth_v2_response_data_relationships import \
      AuthV2ResponseDataRelationships





T = TypeVar("T", bound="AuthV2ResponseData")



@_attrs_define
class AuthV2ResponseData:
    """ 
        Attributes:
            id (str): The unique identifier of the API Key making the request Example: hcxik_12345678901234567890123456.
            type_ (AuthV2ResponseDataType):
            attributes (AuthV2ResponseDataAttributes):
            relationships (Union[Unset, AuthV2ResponseDataRelationships]):
     """

    id: str
    type_: AuthV2ResponseDataType
    attributes: 'AuthV2ResponseDataAttributes'
    relationships: Union[Unset, 'AuthV2ResponseDataRelationships'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.auth_v2_response_data_attributes import \
            AuthV2ResponseDataAttributes
        from ..models.auth_v2_response_data_relationships import \
            AuthV2ResponseDataRelationships
        id = self.id

        type_ = self.type_.value

        attributes = self.attributes.to_dict()

        relationships: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.relationships, Unset):
            relationships = self.relationships.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "type": type_,
            "attributes": attributes,
        })
        if relationships is not UNSET:
            field_dict["relationships"] = relationships

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.auth_v2_response_data_attributes import \
            AuthV2ResponseDataAttributes
        from ..models.auth_v2_response_data_relationships import \
            AuthV2ResponseDataRelationships
        d = src_dict.copy()
        id = d.pop("id")

        type_ = AuthV2ResponseDataType(d.pop("type"))




        attributes = AuthV2ResponseDataAttributes.from_dict(d.pop("attributes"))




        _relationships = d.pop("relationships", UNSET)
        relationships: Union[Unset, AuthV2ResponseDataRelationships]
        if isinstance(_relationships,  Unset):
            relationships = UNSET
        else:
            relationships = AuthV2ResponseDataRelationships.from_dict(_relationships)




        auth_v2_response_data = cls(
            id=id,
            type_=type_,
            attributes=attributes,
            relationships=relationships,
        )


        auth_v2_response_data.additional_properties = d
        return auth_v2_response_data

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
