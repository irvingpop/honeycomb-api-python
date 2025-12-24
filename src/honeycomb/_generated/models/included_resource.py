from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.included_resource_attributes import IncludedResourceAttributes





T = TypeVar("T", bound="IncludedResource")



@_attrs_define
class IncludedResource:
    """ 
        Attributes:
            id (Union[Unset, str]): The unique identifier of the resource Example: hcxen_01hznmeqrcq8rz533xrvtc6mk0.
            type_ (Union[Unset, str]):  Example: environments.
            attributes (Union[Unset, IncludedResourceAttributes]):  Example: {'name': 'Production', 'slug': 'production'}.
     """

    id: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    attributes: Union[Unset, 'IncludedResourceAttributes'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.included_resource_attributes import IncludedResourceAttributes
        id = self.id

        type_ = self.type_

        attributes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.included_resource_attributes import IncludedResourceAttributes
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        type_ = d.pop("type", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, IncludedResourceAttributes]
        if isinstance(_attributes,  Unset):
            attributes = UNSET
        else:
            attributes = IncludedResourceAttributes.from_dict(_attributes)




        included_resource = cls(
            id=id,
            type_=type_,
            attributes=attributes,
        )


        included_resource.additional_properties = d
        return included_resource

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
