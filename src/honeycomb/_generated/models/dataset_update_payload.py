from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.dataset_update_payload_settings import DatasetUpdatePayloadSettings





T = TypeVar("T", bound="DatasetUpdatePayload")



@_attrs_define
class DatasetUpdatePayload:
    """ an object to send to the Dataset API via PUT

        Attributes:
            description (str): A description for the dataset. Default: ''. Example: A nice description of my dataset.
            expand_json_depth (int): The maximum unpacking depth of nested JSON fields. Default: 0. Example: 3.
            settings (Union[Unset, DatasetUpdatePayloadSettings]):
     """

    description: str = ''
    expand_json_depth: int = 0
    settings: Union[Unset, 'DatasetUpdatePayloadSettings'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_update_payload_settings import DatasetUpdatePayloadSettings
        description = self.description

        expand_json_depth = self.expand_json_depth

        settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "description": description,
            "expand_json_depth": expand_json_depth,
        })
        if settings is not UNSET:
            field_dict["settings"] = settings

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.dataset_update_payload_settings import DatasetUpdatePayloadSettings
        d = src_dict.copy()
        description = d.pop("description")

        expand_json_depth = d.pop("expand_json_depth")

        _settings = d.pop("settings", UNSET)
        settings: Union[Unset, DatasetUpdatePayloadSettings]
        if isinstance(_settings,  Unset):
            settings = UNSET
        else:
            settings = DatasetUpdatePayloadSettings.from_dict(_settings)




        dataset_update_payload = cls(
            description=description,
            expand_json_depth=expand_json_depth,
            settings=settings,
        )


        dataset_update_payload.additional_properties = d
        return dataset_update_payload

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
