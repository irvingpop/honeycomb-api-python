from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.validation_error_type_detail_item import \
      ValidationErrorTypeDetailItem





T = TypeVar("T", bound="ValidationError")



@_attrs_define
class ValidationError:
    """ 
        Attributes:
            error (str):  Default: 'something went wrong!'.
            status (float): The HTTP status code of the error. Default: 422.0.
            type_ (str): Type is a URI used to uniquely identify the type of error. Default:
                'https://api.honeycomb.io/problems/validation-failed'.
            title (str): Title is a human-readable summary that explains the `type` of the problem. Default: 'The provided
                input is invalid.'.
            detail (Union[Unset, str]): The general, human-readable error message.
            instance (Union[Unset, str]): The unique identifier (ID) for this specific error.
            type_detail (Union[Unset, list['ValidationErrorTypeDetailItem']]):
     """

    error: str = 'something went wrong!'
    status: float = 422.0
    type_: str = 'https://api.honeycomb.io/problems/validation-failed'
    title: str = 'The provided input is invalid.'
    detail: Union[Unset, str] = UNSET
    instance: Union[Unset, str] = UNSET
    type_detail: Union[Unset, list['ValidationErrorTypeDetailItem']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.validation_error_type_detail_item import \
            ValidationErrorTypeDetailItem
        error = self.error

        status = self.status

        type_ = self.type_

        title = self.title

        detail = self.detail

        instance = self.instance

        type_detail: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.type_detail, Unset):
            type_detail = []
            for type_detail_item_data in self.type_detail:
                type_detail_item = type_detail_item_data.to_dict()
                type_detail.append(type_detail_item)




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
        if type_detail is not UNSET:
            field_dict["type_detail"] = type_detail

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.validation_error_type_detail_item import \
            ValidationErrorTypeDetailItem
        d = src_dict.copy()
        error = d.pop("error")

        status = d.pop("status")

        type_ = d.pop("type")

        title = d.pop("title")

        detail = d.pop("detail", UNSET)

        instance = d.pop("instance", UNSET)

        type_detail = []
        _type_detail = d.pop("type_detail", UNSET)
        for type_detail_item_data in (_type_detail or []):
            type_detail_item = ValidationErrorTypeDetailItem.from_dict(type_detail_item_data)



            type_detail.append(type_detail_item)


        validation_error = cls(
            error=error,
            status=status,
            type_=type_,
            title=title,
            detail=detail,
            instance=instance,
            type_detail=type_detail,
        )


        validation_error.additional_properties = d
        return validation_error

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
