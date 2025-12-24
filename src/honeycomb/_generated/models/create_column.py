from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.create_column_type import CreateColumnType
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="CreateColumn")



@_attrs_define
class CreateColumn:
    """ 
        Attributes:
            key_name (str): Name of the Column. Example: my_column.
            type_ (Union[Unset, CreateColumnType]): Type of data that the Column will contain. Histogram is in beta and only
                works in your Metrics dataset. Default: CreateColumnType.STRING. Example: integer.
            description (Union[Unset, str]): Column description. Example: An integer column.
            hidden (Union[Unset, bool]): If `true`, the column is excluded from autocomplete and raw data field lists.
                Default: False.
            id (Union[Unset, str]): Unique identifier (ID), returned in response bodies.
            last_written (Union[Unset, str]): ISO8601 formatted time the column was last written to (received event data).
            created_at (Union[Unset, str]): ISO8601 formatted time the column was created.
            updated_at (Union[Unset, str]): ISO8601 formatted time the column was updated.
     """

    key_name: str
    type_: Union[Unset, CreateColumnType] = CreateColumnType.STRING
    description: Union[Unset, str] = UNSET
    hidden: Union[Unset, bool] = False
    id: Union[Unset, str] = UNSET
    last_written: Union[Unset, str] = UNSET
    created_at: Union[Unset, str] = UNSET
    updated_at: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        key_name = self.key_name

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value


        description = self.description

        hidden = self.hidden

        id = self.id

        last_written = self.last_written

        created_at = self.created_at

        updated_at = self.updated_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "key_name": key_name,
        })
        if type_ is not UNSET:
            field_dict["type"] = type_
        if description is not UNSET:
            field_dict["description"] = description
        if hidden is not UNSET:
            field_dict["hidden"] = hidden
        if id is not UNSET:
            field_dict["id"] = id
        if last_written is not UNSET:
            field_dict["last_written"] = last_written
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        key_name = d.pop("key_name")

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, CreateColumnType]
        if isinstance(_type_,  Unset):
            type_ = UNSET
        else:
            type_ = CreateColumnType(_type_)




        description = d.pop("description", UNSET)

        hidden = d.pop("hidden", UNSET)

        id = d.pop("id", UNSET)

        last_written = d.pop("last_written", UNSET)

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        create_column = cls(
            key_name=key_name,
            type_=type_,
            description=description,
            hidden=hidden,
            id=id,
            last_written=last_written,
            created_at=created_at,
            updated_at=updated_at,
        )


        create_column.additional_properties = d
        return create_column

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
