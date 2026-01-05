from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.environment_color import EnvironmentColor
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.update_environment_request_data_attributes_settings import \
      UpdateEnvironmentRequestDataAttributesSettings





T = TypeVar("T", bound="UpdateEnvironmentRequestDataAttributes")



@_attrs_define
class UpdateEnvironmentRequestDataAttributes:
    """ 
        Attributes:
            description (Union[Unset, str]):
            color (Union[Unset, EnvironmentColor]):
            settings (Union[Unset, UpdateEnvironmentRequestDataAttributesSettings]):
     """

    description: Union[Unset, str] = UNSET
    color: Union[Unset, EnvironmentColor] = UNSET
    settings: Union[Unset, 'UpdateEnvironmentRequestDataAttributesSettings'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.update_environment_request_data_attributes_settings import \
            UpdateEnvironmentRequestDataAttributesSettings
        description = self.description

        color: Union[Unset, str] = UNSET
        if not isinstance(self.color, Unset):
            color = self.color.value


        settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if description is not UNSET:
            field_dict["description"] = description
        if color is not UNSET:
            field_dict["color"] = color
        if settings is not UNSET:
            field_dict["settings"] = settings

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.update_environment_request_data_attributes_settings import \
            UpdateEnvironmentRequestDataAttributesSettings
        d = src_dict.copy()
        description = d.pop("description", UNSET)

        _color = d.pop("color", UNSET)
        color: Union[Unset, EnvironmentColor]
        if isinstance(_color,  Unset):
            color = UNSET
        else:
            color = EnvironmentColor(_color)




        _settings = d.pop("settings", UNSET)
        settings: Union[Unset, UpdateEnvironmentRequestDataAttributesSettings]
        if isinstance(_settings,  Unset):
            settings = UNSET
        else:
            settings = UpdateEnvironmentRequestDataAttributesSettings.from_dict(_settings)




        update_environment_request_data_attributes = cls(
            description=description,
            color=color,
            settings=settings,
        )


        update_environment_request_data_attributes.additional_properties = d
        return update_environment_request_data_attributes

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
