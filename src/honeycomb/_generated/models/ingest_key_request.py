from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ingest_key_request_type import IngestKeyRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.ingest_key_request_attributes import IngestKeyRequestAttributes





T = TypeVar("T", bound="IngestKeyRequest")



@_attrs_define
class IngestKeyRequest:
    """ 
        Attributes:
            id (str): The unique identifier of the Ingest Key ID with hcxik_ prefix Example:
                hcxik_12345678901234567890123456.
            type_ (IngestKeyRequestType):
            attributes (IngestKeyRequestAttributes):
     """

    id: str
    type_: IngestKeyRequestType
    attributes: 'IngestKeyRequestAttributes'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.ingest_key_request_attributes import \
            IngestKeyRequestAttributes
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
        from ..models.ingest_key_request_attributes import \
            IngestKeyRequestAttributes
        d = src_dict.copy()
        id = d.pop("id")

        type_ = IngestKeyRequestType(d.pop("type"))




        attributes = IngestKeyRequestAttributes.from_dict(d.pop("attributes"))




        ingest_key_request = cls(
            id=id,
            type_=type_,
            attributes=attributes,
        )


        ingest_key_request.additional_properties = d
        return ingest_key_request

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
