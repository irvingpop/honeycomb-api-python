from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.create_environment_request_data import \
      CreateEnvironmentRequestData





T = TypeVar("T", bound="CreateEnvironmentRequest")



@_attrs_define
class CreateEnvironmentRequest:
    """ 
        Attributes:
            data (CreateEnvironmentRequestData):
     """

    data: 'CreateEnvironmentRequestData'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_environment_request_data import \
            CreateEnvironmentRequestData
        data = self.data.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "data": data,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_environment_request_data import \
            CreateEnvironmentRequestData
        d = src_dict.copy()
        data = CreateEnvironmentRequestData.from_dict(d.pop("data"))




        create_environment_request = cls(
            data=data,
        )


        create_environment_request.additional_properties = d
        return create_environment_request

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
