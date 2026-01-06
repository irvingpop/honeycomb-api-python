from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.user_relationship_data import UserRelationshipData





T = TypeVar("T", bound="UserRelationship")



@_attrs_define
class UserRelationship:
    """ 
        Attributes:
            data (UserRelationshipData):
     """

    data: 'UserRelationshipData'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.user_relationship_data import UserRelationshipData
        data = self.data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "data": data,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.user_relationship_data import UserRelationshipData
        d = src_dict.copy()
        data = UserRelationshipData.from_dict(d.pop("data"))




        user_relationship = cls(
            data=data,
        )


        user_relationship.additional_properties = d
        return user_relationship

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
