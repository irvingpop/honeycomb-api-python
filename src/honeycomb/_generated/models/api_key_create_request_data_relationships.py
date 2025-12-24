from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.environment_relationship import EnvironmentRelationship





T = TypeVar("T", bound="ApiKeyCreateRequestDataRelationships")



@_attrs_define
class ApiKeyCreateRequestDataRelationships:
    """ 
        Attributes:
            environment (EnvironmentRelationship): The Environment this object is associated with.
     """

    environment: 'EnvironmentRelationship'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.environment_relationship import EnvironmentRelationship
        environment = self.environment.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "environment": environment,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.environment_relationship import EnvironmentRelationship
        d = src_dict.copy()
        environment = EnvironmentRelationship.from_dict(d.pop("environment"))




        api_key_create_request_data_relationships = cls(
            environment=environment,
        )


        api_key_create_request_data_relationships.additional_properties = d
        return api_key_create_request_data_relationships

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
