from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import cast, Union

if TYPE_CHECKING:
  from ..models.ingest_key import IngestKey
  from ..models.configuration_key import ConfigurationKey





T = TypeVar("T", bound="ApiKeyUpdateRequest")



@_attrs_define
class ApiKeyUpdateRequest:
    """ 
        Attributes:
            data (Union['ConfigurationKey', 'IngestKey']):
     """

    data: Union['ConfigurationKey', 'IngestKey']
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.ingest_key import IngestKey
        from ..models.configuration_key import ConfigurationKey
        data: dict[str, Any]
        if isinstance(self.data, IngestKey):
            data = self.data.to_dict()
        else:
            data = self.data.to_dict()



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "data": data,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.ingest_key import IngestKey
        from ..models.configuration_key import ConfigurationKey
        d = src_dict.copy()
        def _parse_data(data: object) -> Union['ConfigurationKey', 'IngestKey']:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = IngestKey.from_dict(data)



                return data_type_0
            except: # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            data_type_1 = ConfigurationKey.from_dict(data)



            return data_type_1

        data = _parse_data(d.pop("data"))


        api_key_update_request = cls(
            data=data,
        )


        api_key_update_request.additional_properties = d
        return api_key_update_request

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
