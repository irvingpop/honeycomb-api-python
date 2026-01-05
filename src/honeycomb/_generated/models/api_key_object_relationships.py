from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.environment_relationship import EnvironmentRelationship
  from ..models.user_relationship import UserRelationship





T = TypeVar("T", bound="ApiKeyObjectRelationships")



@_attrs_define
class ApiKeyObjectRelationships:
    """ 
        Attributes:
            environment (EnvironmentRelationship): The Environment this object is associated with.
            creator (Union['UserRelationship', None, Unset]): The User who initially created this resource.
            editor (Union['UserRelationship', None, Unset]): The User who last edited this resource.
     """

    environment: 'EnvironmentRelationship'
    creator: Union['UserRelationship', None, Unset] = UNSET
    editor: Union['UserRelationship', None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.environment_relationship import EnvironmentRelationship
        from ..models.user_relationship import UserRelationship
        environment = self.environment.to_dict()

        creator: Union[None, Unset, dict[str, Any]]
        if isinstance(self.creator, Unset):
            creator = UNSET
        elif isinstance(self.creator, UserRelationship):
            creator = self.creator.to_dict()
        else:
            creator = self.creator

        editor: Union[None, Unset, dict[str, Any]]
        if isinstance(self.editor, Unset):
            editor = UNSET
        elif isinstance(self.editor, UserRelationship):
            editor = self.editor.to_dict()
        else:
            editor = self.editor


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "environment": environment,
        })
        if creator is not UNSET:
            field_dict["creator"] = creator
        if editor is not UNSET:
            field_dict["editor"] = editor

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.environment_relationship import EnvironmentRelationship
        from ..models.user_relationship import UserRelationship
        d = src_dict.copy()
        environment = EnvironmentRelationship.from_dict(d.pop("environment"))




        def _parse_creator(data: object) -> Union['UserRelationship', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_creator_relationship_type_0 = UserRelationship.from_dict(data)



                return componentsschemas_creator_relationship_type_0
            except: # noqa: E722
                pass
            return cast(Union['UserRelationship', None, Unset], data)

        creator = _parse_creator(d.pop("creator", UNSET))


        def _parse_editor(data: object) -> Union['UserRelationship', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_editor_relationship_type_0 = UserRelationship.from_dict(data)



                return componentsschemas_editor_relationship_type_0
            except: # noqa: E722
                pass
            return cast(Union['UserRelationship', None, Unset], data)

        editor = _parse_editor(d.pop("editor", UNSET))


        api_key_object_relationships = cls(
            environment=environment,
            creator=creator,
            editor=editor,
        )


        api_key_object_relationships.additional_properties = d
        return api_key_object_relationships

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
