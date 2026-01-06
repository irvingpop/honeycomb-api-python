from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.auth_type import AuthType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.auth_api_key_access import AuthApiKeyAccess
  from ..models.auth_environment import AuthEnvironment
  from ..models.auth_team import AuthTeam





T = TypeVar("T", bound="Auth")



@_attrs_define
class Auth:
    """ 
        Attributes:
            id (str): Unique identifier (ID) of the API Key.
            type_ (AuthType): The type of API Key.
            api_key_access (AuthApiKeyAccess):
            environment (AuthEnvironment):
            team (AuthTeam):
            time_to_live (Union[Unset, str]): An optional property of an ingest key that determines the time at which the
                key becomes unauthorized.
                When the time_to_live passes, the key will no longer be usable. Expressed as a RFC3339-formatted time.
                 Example: 2025-11-19T18:01:02+00:00.
     """

    id: str
    type_: AuthType
    api_key_access: 'AuthApiKeyAccess'
    environment: 'AuthEnvironment'
    team: 'AuthTeam'
    time_to_live: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.auth_api_key_access import AuthApiKeyAccess
        from ..models.auth_environment import AuthEnvironment
        from ..models.auth_team import AuthTeam
        id = self.id

        type_ = self.type_.value

        api_key_access = self.api_key_access.to_dict()

        environment = self.environment.to_dict()

        team = self.team.to_dict()

        time_to_live = self.time_to_live


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "type": type_,
            "api_key_access": api_key_access,
            "environment": environment,
            "team": team,
        })
        if time_to_live is not UNSET:
            field_dict["time_to_live"] = time_to_live

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.auth_api_key_access import AuthApiKeyAccess
        from ..models.auth_environment import AuthEnvironment
        from ..models.auth_team import AuthTeam
        d = src_dict.copy()
        id = d.pop("id")

        type_ = AuthType(d.pop("type"))




        api_key_access = AuthApiKeyAccess.from_dict(d.pop("api_key_access"))




        environment = AuthEnvironment.from_dict(d.pop("environment"))




        team = AuthTeam.from_dict(d.pop("team"))




        time_to_live = d.pop("time_to_live", UNSET)

        auth = cls(
            id=id,
            type_=type_,
            api_key_access=api_key_access,
            environment=environment,
            team=team,
            time_to_live=time_to_live,
        )


        auth.additional_properties = d
        return auth

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
