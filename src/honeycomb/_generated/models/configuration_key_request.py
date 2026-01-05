from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.configuration_key_request_type import ConfigurationKeyRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.configuration_key_request_attributes import \
      ConfigurationKeyRequestAttributes





T = TypeVar("T", bound="ConfigurationKeyRequest")



@_attrs_define
class ConfigurationKeyRequest:
    """ 
        Attributes:
            id (str): The unique identifier of the Configuration Key ID with hcxlk_ prefix Example:
                hcxlk_12345678901234567890123456.
            type_ (ConfigurationKeyRequestType):
            attributes (ConfigurationKeyRequestAttributes):
     """

    id: str
    type_: ConfigurationKeyRequestType
    attributes: 'ConfigurationKeyRequestAttributes'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.configuration_key_request_attributes import \
            ConfigurationKeyRequestAttributes
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
        from ..models.configuration_key_request_attributes import \
            ConfigurationKeyRequestAttributes
        d = src_dict.copy()
        id = d.pop("id")

        type_ = ConfigurationKeyRequestType(d.pop("type"))




        attributes = ConfigurationKeyRequestAttributes.from_dict(d.pop("attributes"))




        configuration_key_request = cls(
            id=id,
            type_=type_,
            attributes=attributes,
        )


        configuration_key_request.additional_properties = d
        return configuration_key_request

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
