from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environment_type import EnvironmentType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.environment_attributes import EnvironmentAttributes
  from ..models.environment_links import EnvironmentLinks





T = TypeVar("T", bound="Environment")



@_attrs_define
class Environment:
    """ 
        Attributes:
            id (str):
            type_ (EnvironmentType):
            links (EnvironmentLinks):
            attributes (EnvironmentAttributes):
     """

    id: str
    type_: EnvironmentType
    links: 'EnvironmentLinks'
    attributes: 'EnvironmentAttributes'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.environment_attributes import EnvironmentAttributes
        from ..models.environment_links import EnvironmentLinks
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
        from ..models.environment_attributes import EnvironmentAttributes
        from ..models.environment_links import EnvironmentLinks
        d = src_dict.copy()
        id = d.pop("id")

        type_ = EnvironmentType(d.pop("type"))




        links = EnvironmentLinks.from_dict(d.pop("links"))




        attributes = EnvironmentAttributes.from_dict(d.pop("attributes"))




        environment = cls(
            id=id,
            type_=type_,
            links=links,
            attributes=attributes,
        )


        environment.additional_properties = d
        return environment

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
