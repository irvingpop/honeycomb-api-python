from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.team_relationship_team_data_type import TeamRelationshipTeamDataType






T = TypeVar("T", bound="TeamRelationshipTeamData")



@_attrs_define
class TeamRelationshipTeamData:
    """ 
        Attributes:
            id (str): The ID of the Team this object is associated with Example: hxctm_12345678901234567890123456.
            type_ (TeamRelationshipTeamDataType):
     """

    id: str
    type_: TeamRelationshipTeamDataType
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

        type_ = TeamRelationshipTeamDataType(d.pop("type"))




        team_relationship_team_data = cls(
            id=id,
            type_=type_,
        )


        team_relationship_team_data.additional_properties = d
        return team_relationship_team_data

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
