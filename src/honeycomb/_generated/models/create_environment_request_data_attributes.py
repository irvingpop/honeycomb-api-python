from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.environment_color import EnvironmentColor
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="CreateEnvironmentRequestDataAttributes")



@_attrs_define
class CreateEnvironmentRequestDataAttributes:
    """ 
        Attributes:
            name (str):
            description (Union[Unset, str]):
            color (Union[Unset, EnvironmentColor]):
     """

    name: str
    description: Union[Unset, str] = UNSET
    color: Union[Unset, EnvironmentColor] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        color: Union[Unset, str] = UNSET
        if not isinstance(self.color, Unset):
            color = self.color.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if color is not UNSET:
            field_dict["color"] = color

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description", UNSET)

        _color = d.pop("color", UNSET)
        color: Union[Unset, EnvironmentColor]
        if isinstance(_color,  Unset):
            color = UNSET
        else:
            color = EnvironmentColor(_color)




        create_environment_request_data_attributes = cls(
            name=name,
            description=description,
            color=color,
        )


        create_environment_request_data_attributes.additional_properties = d
        return create_environment_request_data_attributes

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
