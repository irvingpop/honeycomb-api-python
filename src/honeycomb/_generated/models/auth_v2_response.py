from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.auth_v2_response_data import AuthV2ResponseData
  from ..models.included_resource import IncludedResource





T = TypeVar("T", bound="AuthV2Response")



@_attrs_define
class AuthV2Response:
    """ 
        Attributes:
            data (AuthV2ResponseData):
            included (Union[Unset, list['IncludedResource']]):  Example: [{'id': 'hcxtm_12345678901234567890123456', 'type':
                'teams', 'attributes': {'name': 'My Team', 'slug': 'my-team'}}].
     """

    data: 'AuthV2ResponseData'
    included: Union[Unset, list['IncludedResource']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.auth_v2_response_data import AuthV2ResponseData
        from ..models.included_resource import IncludedResource
        data = self.data.to_dict()

        included: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.included, Unset):
            included = []
            for included_item_data in self.included:
                included_item = included_item_data.to_dict()
                included.append(included_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "data": data,
        })
        if included is not UNSET:
            field_dict["included"] = included

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.auth_v2_response_data import AuthV2ResponseData
        from ..models.included_resource import IncludedResource
        d = src_dict.copy()
        data = AuthV2ResponseData.from_dict(d.pop("data"))




        included = []
        _included = d.pop("included", UNSET)
        for included_item_data in (_included or []):
            included_item = IncludedResource.from_dict(included_item_data)



            included.append(included_item)


        auth_v2_response = cls(
            data=data,
            included=included,
        )


        auth_v2_response.additional_properties = d
        return auth_v2_response

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
