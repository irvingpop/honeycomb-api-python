from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="DatasetCreationPayload")



@_attrs_define
class DatasetCreationPayload:
    """ an object to send to the Dataset API via PUT

        Attributes:
            name (str): The name of the dataset.
            description (Union[Unset, str]): A description for the dataset. Default: ''. Example: A nice description of my
                dataset.
            expand_json_depth (Union[Unset, int]): The maximum unpacking depth of nested JSON fields. Default: 0. Example:
                3.
     """

    name: str
    description: Union[Unset, str] = ''
    expand_json_depth: Union[Unset, int] = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        expand_json_depth = self.expand_json_depth


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if expand_json_depth is not UNSET:
            field_dict["expand_json_depth"] = expand_json_depth

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description", UNSET)

        expand_json_depth = d.pop("expand_json_depth", UNSET)

        dataset_creation_payload = cls(
            name=name,
            description=description,
            expand_json_depth=expand_json_depth,
        )


        dataset_creation_payload.additional_properties = d
        return dataset_creation_payload

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
