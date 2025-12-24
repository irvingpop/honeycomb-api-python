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
  from ..models.notification_recipient import NotificationRecipient





T = TypeVar("T", bound="UpdateExhaustionTimeBurnAlertRequest")



@_attrs_define
class UpdateExhaustionTimeBurnAlertRequest:
    """ 
        Attributes:
            exhaustion_minutes (int): Required when `alert_type` is `exhaustion_time`.

                Must not be specified when `alert_type` is `budget_rate`.

                Amount of time (in minutes) left until your projected SLO budget is exhausted.
                The alert will fire when this exhaustion threshold is reached.
                 Example: 120.
            recipients (list['NotificationRecipient']): A list of [Recipients](/api/recipients/) to notify when an alert
                fires. Using `type`+`target` is deprecated. First, create the Recipient via the Recipients API, and then specify
                the ID.
                 Example: [{'id': 'abcd123', 'type': 'email', 'target': 'alerts@example.com'}].
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
     """

    exhaustion_minutes: int
    recipients: list['NotificationRecipient']
    id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    triggered: Union[Unset, bool] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    alert_type: Union[Unset, ExhaustionTimeAlertType] = ExhaustionTimeAlertType.EXHAUSTION_TIME
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.notification_recipient import NotificationRecipient
        exhaustion_minutes = self.exhaustion_minutes

        recipients = []
        for recipients_item_data in self.recipients:
            recipients_item = recipients_item_data.to_dict()
            recipients.append(recipients_item)



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



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "exhaustion_minutes": exhaustion_minutes,
            "recipients": recipients,
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

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.notification_recipient import NotificationRecipient
        d = src_dict.copy()
        exhaustion_minutes = d.pop("exhaustion_minutes")

        recipients = []
        _recipients = d.pop("recipients")
        for recipients_item_data in (_recipients):
            recipients_item = NotificationRecipient.from_dict(recipients_item_data)



            recipients.append(recipients_item)


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




        update_exhaustion_time_burn_alert_request = cls(
            exhaustion_minutes=exhaustion_minutes,
            recipients=recipients,
            id=id,
            description=description,
            triggered=triggered,
            created_at=created_at,
            updated_at=updated_at,
            alert_type=alert_type,
        )


        update_exhaustion_time_burn_alert_request.additional_properties = d
        return update_exhaustion_time_burn_alert_request

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
