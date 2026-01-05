from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.dataset_definition_type_1_column_type import \
    DatasetDefinitionType1ColumnType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DatasetDefinitionType1")



@_attrs_define
class DatasetDefinitionType1:
    """ 
        Attributes:
            name (str): The name of the Column or of the Calculated Field (also called Derived Column) to map to this
                Dataset Definition Type. An empty string clears the mapping, potentially reverting to a default mapping.
            column_type (Union[Unset, DatasetDefinitionType1ColumnType]): Optional: `column` for regular columns and
                `derived_column` for Calculated Fields (also called Derived Columns) when setting Dataset Definitions. Honeycomb
                does not use this field when updating Dataset definitions.
     """

    name: str
    column_type: Union[Unset, DatasetDefinitionType1ColumnType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        name = self.name

        column_type: Union[Unset, str] = UNSET
        if not isinstance(self.column_type, Unset):
            column_type = self.column_type.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
        })
        if column_type is not UNSET:
            field_dict["column_type"] = column_type

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        _column_type = d.pop("column_type", UNSET)
        column_type: Union[Unset, DatasetDefinitionType1ColumnType]
        if isinstance(_column_type,  Unset):
            column_type = UNSET
        else:
            column_type = DatasetDefinitionType1ColumnType(_column_type)




        dataset_definition_type_1 = cls(
            name=name,
            column_type=column_type,
        )


        dataset_definition_type_1.additional_properties = d
        return dataset_definition_type_1

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
