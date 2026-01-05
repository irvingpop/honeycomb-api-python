from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.team_relationship_team import TeamRelationshipTeam





T = TypeVar("T", bound="TeamRelationship")



@_attrs_define
class TeamRelationship:
    """ 
        Attributes:
            team (TeamRelationshipTeam):
     """

    team: 'TeamRelationshipTeam'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.team_relationship_team import TeamRelationshipTeam
        team = self.team.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "team": team,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.team_relationship_team import TeamRelationshipTeam
        d = src_dict.copy()
        team = TeamRelationshipTeam.from_dict(d.pop("team"))




        team_relationship = cls(
            team=team,
        )


        team_relationship.additional_properties = d
        return team_relationship

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
