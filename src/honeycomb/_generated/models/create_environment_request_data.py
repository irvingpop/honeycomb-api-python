from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_environment_request_data_type import \
    CreateEnvironmentRequestDataType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.create_environment_request_data_attributes import \
      CreateEnvironmentRequestDataAttributes





T = TypeVar("T", bound="CreateEnvironmentRequestData")



@_attrs_define
class CreateEnvironmentRequestData:
    """ 
        Attributes:
            type_ (CreateEnvironmentRequestDataType):
            attributes (CreateEnvironmentRequestDataAttributes):
     """

    type_: CreateEnvironmentRequestDataType
    attributes: 'CreateEnvironmentRequestDataAttributes'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_environment_request_data_attributes import \
            CreateEnvironmentRequestDataAttributes
        type_ = self.type_.value

        attributes = self.attributes.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "type": type_,
            "attributes": attributes,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_environment_request_data_attributes import \
            CreateEnvironmentRequestDataAttributes
        d = src_dict.copy()
        type_ = CreateEnvironmentRequestDataType(d.pop("type"))




        attributes = CreateEnvironmentRequestDataAttributes.from_dict(d.pop("attributes"))




        create_environment_request_data = cls(
            type_=type_,
            attributes=attributes,
        )


        create_environment_request_data.additional_properties = d
        return create_environment_request_data

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
