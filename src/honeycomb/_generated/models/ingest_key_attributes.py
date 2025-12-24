from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.ingest_key_type_key_type import IngestKeyTypeKeyType
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.ingest_key_attributes_permissions import IngestKeyAttributesPermissions
  from ..models.ingest_key_attributes_timestamps import IngestKeyAttributesTimestamps





T = TypeVar("T", bound="IngestKeyAttributes")



@_attrs_define
class IngestKeyAttributes:
    """ 
        Attributes:
            key_type (IngestKeyTypeKeyType): The type of API Key Example: ingest.
            name (str): A human-readable name for the API Key Example: us-west-2 collectors key.
            time_to_live (Union[Unset, str]): An optional property of an ingest key that determines the time at which the
                key becomes unauthorized.
                When the time_to_live passes, the key will no longer be usable. The time_to_live property can only
                be set when the key is created and cannot be changed.
                Expressed as a RFC3339-formatted time.
                 Example: 2025-11-19T18:01:02+00:00.
            disabled (Union[Unset, bool]): Whether the API Key is disabled Default: False.
            permissions (Union[Unset, IngestKeyAttributesPermissions]): The permissions granted to this Ingest API Key
            timestamps (Union[Unset, IngestKeyAttributesTimestamps]):
     """

    key_type: IngestKeyTypeKeyType
    name: str
    time_to_live: Union[Unset, str] = UNSET
    disabled: Union[Unset, bool] = False
    permissions: Union[Unset, 'IngestKeyAttributesPermissions'] = UNSET
    timestamps: Union[Unset, 'IngestKeyAttributesTimestamps'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.ingest_key_attributes_permissions import IngestKeyAttributesPermissions
        from ..models.ingest_key_attributes_timestamps import IngestKeyAttributesTimestamps
        key_type = self.key_type.value

        name = self.name

        time_to_live = self.time_to_live

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
        if time_to_live is not UNSET:
            field_dict["time_to_live"] = time_to_live
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if timestamps is not UNSET:
            field_dict["timestamps"] = timestamps

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ingest_key_attributes_permissions import IngestKeyAttributesPermissions
        from ..models.ingest_key_attributes_timestamps import IngestKeyAttributesTimestamps
        d = src_dict.copy()
        key_type = IngestKeyTypeKeyType(d.pop("key_type"))




        name = d.pop("name")

        time_to_live = d.pop("time_to_live", UNSET)

        disabled = d.pop("disabled", UNSET)

        _permissions = d.pop("permissions", UNSET)
        permissions: Union[Unset, IngestKeyAttributesPermissions]
        if isinstance(_permissions,  Unset):
            permissions = UNSET
        else:
            permissions = IngestKeyAttributesPermissions.from_dict(_permissions)




        _timestamps = d.pop("timestamps", UNSET)
        timestamps: Union[Unset, IngestKeyAttributesTimestamps]
        if isinstance(_timestamps,  Unset):
            timestamps = UNSET
        else:
            timestamps = IngestKeyAttributesTimestamps.from_dict(_timestamps)




        ingest_key_attributes = cls(
            key_type=key_type,
            name=name,
            time_to_live=time_to_live,
            disabled=disabled,
            permissions=permissions,
            timestamps=timestamps,
        )


        ingest_key_attributes.additional_properties = d
        return ingest_key_attributes

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
