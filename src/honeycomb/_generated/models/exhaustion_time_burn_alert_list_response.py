from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.exhaustion_time_alert_type import ExhaustionTimeAlertType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime

if TYPE_CHECKING:
  from ..models.exhaustion_time_burn_alert_list_response_slo import ExhaustionTimeBurnAlertListResponseSlo





T = TypeVar("T", bound="ExhaustionTimeBurnAlertListResponse")



@_attrs_define
class ExhaustionTimeBurnAlertListResponse:
    """ 
        Attributes:
            exhaustion_minutes (int): Required when `alert_type` is `exhaustion_time`.

                Must not be specified when `alert_type` is `budget_rate`.

                Amount of time (in minutes) left until your projected SLO budget is exhausted.
                The alert will fire when this exhaustion threshold is reached.
                 Example: 120.
            id (Union[Unset, str]): Unique identifier (ID) of a Burn alert. Example: fS7vfB81Wcy.
            description (Union[Unset, str]): A description of the Burn Alert. Example: Use this runbook if this alert
                fires..
            triggered (Union[Unset, bool]): Indicates if the Burn Alert has been triggered. This field is read-only and is
                set to `true` when the alert is triggered.
            created_at (Union[Unset, datetime.datetime]): The ISO8601-formatted time when the Burn Alert was created.
                Example: 2022-09-22T17:32:11Z.
            updated_at (Union[Unset, datetime.datetime]): The ISO8601-formatted time when the Burn Alert was updated.
                Example: 2022-10-31T15:08:11Z.
            alert_type (Union[Unset, ExhaustionTimeAlertType]): One of the supported alert types:
                1. `exhaustion_time`: Notifies when you are about to run out of SLO budget within a specified number of hours.
                1. `budget_rate`: Notifies when budget drops by at least a specified percentage within a defined time window.
                 Default: ExhaustionTimeAlertType.EXHAUSTION_TIME. Example: exhaustion_time.
            slo (Union[Unset, ExhaustionTimeBurnAlertListResponseSlo]): Details about the SLO associated with the burn
                alert. Example: {'id': '2LBq9LckbcA'}.
     """

    exhaustion_minutes: int
    id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    triggered: Union[Unset, bool] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    alert_type: Union[Unset, ExhaustionTimeAlertType] = ExhaustionTimeAlertType.EXHAUSTION_TIME
    slo: Union[Unset, 'ExhaustionTimeBurnAlertListResponseSlo'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.exhaustion_time_burn_alert_list_response_slo import ExhaustionTimeBurnAlertListResponseSlo
        exhaustion_minutes = self.exhaustion_minutes

        id = self.id

        description = self.description

        triggered = self.triggered

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        alert_type: Union[Unset, str] = UNSET
        if not isinstance(self.alert_type, Unset):
            alert_type = self.alert_type.value


        slo: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.slo, Unset):
            slo = self.slo.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "exhaustion_minutes": exhaustion_minutes,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if triggered is not UNSET:
            field_dict["triggered"] = triggered
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if alert_type is not UNSET:
            field_dict["alert_type"] = alert_type
        if slo is not UNSET:
            field_dict["slo"] = slo

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.exhaustion_time_burn_alert_list_response_slo import ExhaustionTimeBurnAlertListResponseSlo
        d = src_dict.copy()
        exhaustion_minutes = d.pop("exhaustion_minutes")

        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        triggered = d.pop("triggered", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at,  Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)




        _alert_type = d.pop("alert_type", UNSET)
        alert_type: Union[Unset, ExhaustionTimeAlertType]
        if isinstance(_alert_type,  Unset):
            alert_type = UNSET
        else:
            alert_type = ExhaustionTimeAlertType(_alert_type)




        _slo = d.pop("slo", UNSET)
        slo: Union[Unset, ExhaustionTimeBurnAlertListResponseSlo]
        if isinstance(_slo,  Unset):
            slo = UNSET
        else:
            slo = ExhaustionTimeBurnAlertListResponseSlo.from_dict(_slo)




        exhaustion_time_burn_alert_list_response = cls(
            exhaustion_minutes=exhaustion_minutes,
            id=id,
            description=description,
            triggered=triggered,
            created_at=created_at,
            updated_at=updated_at,
            alert_type=alert_type,
            slo=slo,
        )


        exhaustion_time_burn_alert_list_response.additional_properties = d
        return exhaustion_time_burn_alert_list_response

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
