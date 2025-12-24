from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.map_node import MapNode





T = TypeVar("T", bound="MapDependency")



@_attrs_define
class MapDependency:
    """ A dependency relationship between two services.

        Attributes:
            parent_node (Union[Unset, MapNode]): A node in the service map (typically a service).
            child_node (Union[Unset, MapNode]): A node in the service map (typically a service).
            call_count (Union[Unset, int]): Number of calls between the parent and child services.
                 Example: 142.
     """

    parent_node: Union[Unset, 'MapNode'] = UNSET
    child_node: Union[Unset, 'MapNode'] = UNSET
    call_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.map_node import MapNode
        parent_node: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.parent_node, Unset):
            parent_node = self.parent_node.to_dict()

        child_node: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.child_node, Unset):
            child_node = self.child_node.to_dict()

        call_count = self.call_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if parent_node is not UNSET:
            field_dict["parent_node"] = parent_node
        if child_node is not UNSET:
            field_dict["child_node"] = child_node
        if call_count is not UNSET:
            field_dict["call_count"] = call_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.map_node import MapNode
        d = src_dict.copy()
        _parent_node = d.pop("parent_node", UNSET)
        parent_node: Union[Unset, MapNode]
        if isinstance(_parent_node,  Unset):
            parent_node = UNSET
        else:
            parent_node = MapNode.from_dict(_parent_node)




        _child_node = d.pop("child_node", UNSET)
        child_node: Union[Unset, MapNode]
        if isinstance(_child_node,  Unset):
            child_node = UNSET
        else:
            child_node = MapNode.from_dict(_child_node)




        call_count = d.pop("call_count", UNSET)

        map_dependency = cls(
            parent_node=parent_node,
            child_node=child_node,
            call_count=call_count,
        )


        map_dependency.additional_properties = d
        return map_dependency

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
