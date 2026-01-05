from typing import TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environment_relationship_data_type import \
    EnvironmentRelationshipDataType
from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentRelationshipData")



@_attrs_define
class EnvironmentRelationshipData:
    """ 
        Attributes:
            id (str): The ID of the Environment this object is associated with. Example: hxenv_12345678901234567890123456.
            type_ (EnvironmentRelationshipDataType):
     """

    id: str
    type_: EnvironmentRelationshipDataType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_.value


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "type": type_,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        type_ = EnvironmentRelationshipDataType(d.pop("type"))




        environment_relationship_data = cls(
            id=id,
            type_=type_,
        )


        environment_relationship_data.additional_properties = d
        return environment_relationship_data

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
