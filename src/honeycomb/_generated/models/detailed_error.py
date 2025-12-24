from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="DetailedError")



@_attrs_define
class DetailedError:
    """ An RFC7807 'Problem Detail' formatted error message.

        Attributes:
            error (str):  Default: 'something went wrong!'.
            status (float): The HTTP status code of the error.
            type_ (str): Type is a URI used to uniquely identify the type of error.
            title (str): Title is a human-readable summary that explains the `type` of the problem.
            detail (Union[Unset, str]): The general, human-readable error message.
            instance (Union[Unset, str]): The unique identifier (ID) for this specific error.
     """

    status: float
    type_: str
    title: str
    error: str = 'something went wrong!'
    detail: Union[Unset, str] = UNSET
    instance: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        error = self.error

        status = self.status

        type_ = self.type_

        title = self.title

        detail = self.detail

        instance = self.instance


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "error": error,
            "status": status,
            "type": type_,
            "title": title,
        })
        if detail is not UNSET:
            field_dict["detail"] = detail
        if instance is not UNSET:
            field_dict["instance"] = instance

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        error = d.pop("error")

        status = d.pop("status")

        type_ = d.pop("type")

        title = d.pop("title")

        detail = d.pop("detail", UNSET)

        instance = d.pop("instance", UNSET)

        detailed_error = cls(
            error=error,
            status=status,
            type_=type_,
            title=title,
            detail=detail,
            instance=instance,
        )


        detailed_error.additional_properties = d
        return detailed_error

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
