from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.marker_object_relationships_dataset_data_type_0_type import MarkerObjectRelationshipsDatasetDataType0Type
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="MarkerObjectRelationshipsDatasetDataType0")



@_attrs_define
class MarkerObjectRelationshipsDatasetDataType0:
    """ 
        Attributes:
            type_ (Union[Unset, MarkerObjectRelationshipsDatasetDataType0Type]):
            id (Union[Unset, str]): The dataset ID Example: hcxds_12345678901234567890123456.
     """

    type_: Union[Unset, MarkerObjectRelationshipsDatasetDataType0Type] = UNSET
    id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value


        id = self.id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if type_ is not UNSET:
            field_dict["type"] = type_
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, MarkerObjectRelationshipsDatasetDataType0Type]
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = MarkerObjectRelationshipsDatasetDataType0Type(_type_)




        id = d.pop("id", UNSET)

        marker_object_relationships_dataset_data_type_0 = cls(
            type_=type_,
            id=id,
        )


        marker_object_relationships_dataset_data_type_0.additional_properties = d
        return marker_object_relationships_dataset_data_type_0

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
