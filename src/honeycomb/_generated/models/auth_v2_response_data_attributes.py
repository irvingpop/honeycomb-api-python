from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.auth_v2_response_data_attributes_key_type import AuthV2ResponseDataAttributesKeyType
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.auth_v2_response_data_attributes_timestamps import AuthV2ResponseDataAttributesTimestamps





T = TypeVar("T", bound="AuthV2ResponseDataAttributes")



@_attrs_define
class AuthV2ResponseDataAttributes:
    """ 
        Attributes:
            name (Union[Unset, str]): A human-readable name for the API Key Example: mgmt write key.
            key_type (Union[Unset, AuthV2ResponseDataAttributesKeyType]): The type of API Key
            disabled (Union[Unset, bool]): Whether the API Key is disabled Default: False.
            scopes (Union[Unset, list[str]]): The scopes assigned to this API Key Example: ['api-keys:write'].
            timestamps (Union[Unset, AuthV2ResponseDataAttributesTimestamps]):
     """

    name: Union[Unset, str] = UNSET
    key_type: Union[Unset, AuthV2ResponseDataAttributesKeyType] = UNSET
    disabled: Union[Unset, bool] = False
    scopes: Union[Unset, list[str]] = UNSET
    timestamps: Union[Unset, 'AuthV2ResponseDataAttributesTimestamps'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.auth_v2_response_data_attributes_timestamps import AuthV2ResponseDataAttributesTimestamps
        name = self.name

        key_type: Union[Unset, str] = UNSET
        if not isinstance(self.key_type, Unset):
            key_type = self.key_type.value


        disabled = self.disabled

        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        timestamps: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.timestamps, Unset):
            timestamps = self.timestamps.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if key_type is not UNSET:
            field_dict["key_type"] = key_type
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if timestamps is not UNSET:
            field_dict["timestamps"] = timestamps

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.auth_v2_response_data_attributes_timestamps import AuthV2ResponseDataAttributesTimestamps
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        _key_type = d.pop("key_type", UNSET)
        key_type: Union[Unset, AuthV2ResponseDataAttributesKeyType]
        if isinstance(_key_type,  Unset):
            key_type = UNSET
        else:
            key_type = AuthV2ResponseDataAttributesKeyType(_key_type)




        disabled = d.pop("disabled", UNSET)

        scopes = cast(list[str], d.pop("scopes", UNSET))


        _timestamps = d.pop("timestamps", UNSET)
        timestamps: Union[Unset, AuthV2ResponseDataAttributesTimestamps]
        if isinstance(_timestamps,  Unset):
            timestamps = UNSET
        else:
            timestamps = AuthV2ResponseDataAttributesTimestamps.from_dict(_timestamps)




        auth_v2_response_data_attributes = cls(
            name=name,
            key_type=key_type,
            disabled=disabled,
            scopes=scopes,
            timestamps=timestamps,
        )


        auth_v2_response_data_attributes.additional_properties = d
        return auth_v2_response_data_attributes

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
