from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.configuration_key_request_attributes_permissions import \
      ConfigurationKeyRequestAttributesPermissions





T = TypeVar("T", bound="ConfigurationKeyRequestAttributes")



@_attrs_define
class ConfigurationKeyRequestAttributes:
    """ 
        Attributes:
            name (Union[Unset, str]): A human-readable name for the API Key Example: updated key name.
            disabled (Union[Unset, bool]): Whether the API Key is enabled
            permissions (Union[Unset, ConfigurationKeyRequestAttributesPermissions]): The permissions granted to this
                Configuration API Key. Values omitted will not be replaced.
     """

    name: Union[Unset, str] = UNSET
    disabled: Union[Unset, bool] = UNSET
    permissions: Union[Unset, 'ConfigurationKeyRequestAttributesPermissions'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.configuration_key_request_attributes_permissions import \
            ConfigurationKeyRequestAttributesPermissions
        name = self.name

        disabled = self.disabled

        permissions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.configuration_key_request_attributes_permissions import \
            ConfigurationKeyRequestAttributesPermissions
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        disabled = d.pop("disabled", UNSET)

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, ConfigurationKeyRequestAttributesPermissions]
        if isinstance(_permissions,  Unset):
            permissions = UNSET
        else:
            permissions = ConfigurationKeyRequestAttributesPermissions.from_dict(_permissions)




        configuration_key_request_attributes = cls(
            name=name,
            disabled=disabled,
            permissions=permissions,
        )


        configuration_key_request_attributes.additional_properties = d
        return configuration_key_request_attributes

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
