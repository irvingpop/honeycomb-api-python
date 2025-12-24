from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.map_node_type import MapNodeType
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="MapNode")



@_attrs_define
class MapNode:
    """ A node in the service map (typically a service).

        Attributes:
            name (str): Name of the service or node.
                 Example: user-service.
            type_ (Union[Unset, MapNodeType]): Type of the node. Currently only "service" is supported. Defaults to
                "service" if not specified.
                 Example: service.
     """

    name: str
    type_: Union[Unset, MapNodeType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
        })
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, MapNodeType]
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = MapNodeType(_type_)




        map_node = cls(
            name=name,
            type_=type_,
        )


        map_node.additional_properties = d
        return map_node

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
