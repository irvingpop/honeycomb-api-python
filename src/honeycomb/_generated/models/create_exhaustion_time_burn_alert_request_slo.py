from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="CreateExhaustionTimeBurnAlertRequestSlo")



@_attrs_define
class CreateExhaustionTimeBurnAlertRequestSlo:
    """ Details about the SLO associated with the burn alert.

        Example:
            {'id': '2LBq9LckbcA'}

        Attributes:
            id (str): Unique identifier (ID) of a SLO.
     """

    id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        id = self.id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        create_exhaustion_time_burn_alert_request_slo = cls(
            id=id,
        )


        create_exhaustion_time_burn_alert_request_slo.additional_properties = d
        return create_exhaustion_time_burn_alert_request_slo

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
