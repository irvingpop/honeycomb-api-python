from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="CalculatedField")



@_attrs_define
class CalculatedField:
    """ 
        Attributes:
            id (str): Unique identifier (ID), returned in response bodies.
            alias (str): The human-readable name of the Calculated Field (also called Derived Column), as it will be
                referenced when building queries.
            expression (str): The expression to evaluate to construct this Calculated Field's value. (Calculated Field is
                also called Derived Column.) Refer to the [Calculated Field
                Reference](https://docs.honeycomb.io/reference/derived-column-formula/).
            created_at (str): ISO8601 formatted time when the field was created.
            updated_at (str): ISO8601 formatted time when the field was updated.
            description (Union[Unset, str]): A human-readable description for the Calculated Field that displays in the UI.
                Default: ''.
     """

    id: str
    alias: str
    expression: str
    created_at: str
    updated_at: str
    description: Union[Unset, str] = ''
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        id = self.id

        alias = self.alias

        expression = self.expression

        created_at = self.created_at

        updated_at = self.updated_at

        description = self.description


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "alias": alias,
            "expression": expression,
            "created_at": created_at,
            "updated_at": updated_at,
        })
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        alias = d.pop("alias")

        expression = d.pop("expression")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        description = d.pop("description", UNSET)

        calculated_field = cls(
            id=id,
            alias=alias,
            expression=expression,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
        )


        calculated_field.additional_properties = d
        return calculated_field

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
