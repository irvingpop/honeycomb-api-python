from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.configuration_key_attributes_key_type import ConfigurationKeyAttributesKeyType
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.configuration_key_attributes_timestamps import ConfigurationKeyAttributesTimestamps
  from ..models.configuration_key_attributes_permissions import ConfigurationKeyAttributesPermissions





T = TypeVar("T", bound="ConfigurationKeyAttributes")



@_attrs_define
class ConfigurationKeyAttributes:
    """ 
        Attributes:
            key_type (ConfigurationKeyAttributesKeyType): The type of API Key Example: configuration.
            name (str): A human-readable name for the API Key Example: us-west-2 collectors key.
            disabled (Union[Unset, bool]): Whether the API Key is disabled Default: False.
            permissions (Union[Unset, ConfigurationKeyAttributesPermissions]): The permissions granted to this Configuration
                API Key
            timestamps (Union[Unset, ConfigurationKeyAttributesTimestamps]):
     """

    key_type: ConfigurationKeyAttributesKeyType
    name: str
    disabled: Union[Unset, bool] = False
    permissions: Union[Unset, 'ConfigurationKeyAttributesPermissions'] = UNSET
    timestamps: Union[Unset, 'ConfigurationKeyAttributesTimestamps'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.configuration_key_attributes_timestamps import ConfigurationKeyAttributesTimestamps
        from ..models.configuration_key_attributes_permissions import ConfigurationKeyAttributesPermissions
        key_type = self.key_type.value

        name = self.name

        disabled = self.disabled

        permissions: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions.to_dict()

        timestamps: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.timestamps, Unset):
            timestamps = self.timestamps.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "key_type": key_type,
            "name": name,
        })
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if timestamps is not UNSET:
            field_dict["timestamps"] = timestamps

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.configuration_key_attributes_timestamps import ConfigurationKeyAttributesTimestamps
        from ..models.configuration_key_attributes_permissions import ConfigurationKeyAttributesPermissions
        d = src_dict.copy()
        key_type = ConfigurationKeyAttributesKeyType(d.pop("key_type"))




        name = d.pop("name")

        disabled = d.pop("disabled", UNSET)

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, ConfigurationKeyAttributesPermissions]
        if isinstance(_permissions,  Unset):
            permissions = UNSET
        else:
            permissions = ConfigurationKeyAttributesPermissions.from_dict(_permissions)




        _timestamps = d.pop("timestamps", UNSET)
        timestamps: Union[Unset, ConfigurationKeyAttributesTimestamps]
        if isinstance(_timestamps,  Unset):
            timestamps = UNSET
        else:
            timestamps = ConfigurationKeyAttributesTimestamps.from_dict(_timestamps)




        configuration_key_attributes = cls(
            key_type=key_type,
            name=name,
            disabled=disabled,
            permissions=permissions,
            timestamps=timestamps,
        )


        configuration_key_attributes.additional_properties = d
        return configuration_key_attributes

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
