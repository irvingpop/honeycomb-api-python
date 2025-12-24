from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.environment_attributes_color_type_1 import EnvironmentAttributesColorType1
from ..models.environment_color import EnvironmentColor
from typing import cast
from typing import cast, Union

if TYPE_CHECKING:
  from ..models.environment_attributes_settings import EnvironmentAttributesSettings





T = TypeVar("T", bound="EnvironmentAttributes")



@_attrs_define
class EnvironmentAttributes:
    """ 
        Attributes:
            name (str):
            description (str):
            color (Union[EnvironmentAttributesColorType1, EnvironmentColor]): 'classic' color is used only for auto-created
                Classic environments and cannot be set on any other environment. Classic environments cannot be set to any other
                color.
            slug (str):
            settings (EnvironmentAttributesSettings):
     """

    name: str
    description: str
    color: Union[EnvironmentAttributesColorType1, EnvironmentColor]
    slug: str
    settings: 'EnvironmentAttributesSettings'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.environment_attributes_settings import EnvironmentAttributesSettings
        name = self.name

        description = self.description

        color: str
        if isinstance(self.color, EnvironmentColor):
            color = self.color.value
        else:
            color = self.color.value


        slug = self.slug

        settings = self.settings.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "description": description,
            "color": color,
            "slug": slug,
            "settings": settings,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.environment_attributes_settings import EnvironmentAttributesSettings
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        def _parse_color(data: object) -> Union[EnvironmentAttributesColorType1, EnvironmentColor]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                color_type_0 = EnvironmentColor(data)



                return color_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, str):
                raise TypeError()
            color_type_1 = EnvironmentAttributesColorType1(data)



            return color_type_1

        color = _parse_color(d.pop("color"))


        slug = d.pop("slug")

        settings = EnvironmentAttributesSettings.from_dict(d.pop("settings"))




        environment_attributes = cls(
            name=name,
            description=description,
            color=color,
            slug=slug,
            settings=settings,
        )


        environment_attributes.additional_properties = d
        return environment_attributes

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
