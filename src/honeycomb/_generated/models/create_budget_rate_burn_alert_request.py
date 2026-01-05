import datetime
from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.budget_rate_alert_type import BudgetRateAlertType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.create_budget_rate_burn_alert_request_slo import \
      CreateBudgetRateBurnAlertRequestSlo
  from ..models.notification_recipient import NotificationRecipient





T = TypeVar("T", bound="CreateBudgetRateBurnAlertRequest")



@_attrs_define
class CreateBudgetRateBurnAlertRequest:
    """ 
        Attributes:
            alert_type (BudgetRateAlertType): One of the supported alert types:
                1. `exhaustion_time`: Notifies when you are about to run out of SLO budget within a specified number of hours.
                1. `budget_rate`: Notifies when budget drops by at least a specified percentage within a defined time window.
                 Default: BudgetRateAlertType.EXHAUSTION_TIME. Example: budget_rate.
            budget_rate_window_minutes (int): Required when `alert_type` is `budget_rate`.

                Must not be specified when `alert_type` is `exhaustion_time`.

                Time period (in minutes) over which a budget rate will be calculated.

                Must be no greater than the associated SLO's time period.
                 Example: 120.
            budget_rate_decrease_threshold_per_million (int): Required when `alert_type` is `budget_rate`.

                Must not be specified when `alert_type` is `exhaustion_time`.

                The percent the budget has decreased over the budget rate window, represented as a value out of one million.
                The alert will fire when this budget decrease threshold is reached.

                See the table below for some example conversions from desired budget decrease percent to the representation as a
                value out of one million
                | Desired percent | Value per million |
                |-----------------|-------------------|
                | 0.001%          | 1                 |
                | 1%              | 10,000            |
                | 5%              | 50,000            |
                | 99.99%          | 999,900           |
                 Example: 1000.
            slo (CreateBudgetRateBurnAlertRequestSlo): Details about the SLO associated with the burn alert. Example: {'id':
                '2LBq9LckbcA'}.
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
     """

    budget_rate_window_minutes: int
    budget_rate_decrease_threshold_per_million: int
    slo: 'CreateBudgetRateBurnAlertRequestSlo'
    recipients: list['NotificationRecipient']
    alert_type: BudgetRateAlertType = BudgetRateAlertType.EXHAUSTION_TIME
    id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    triggered: Union[Unset, bool] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_budget_rate_burn_alert_request_slo import \
            CreateBudgetRateBurnAlertRequestSlo
        from ..models.notification_recipient import NotificationRecipient
        alert_type = self.alert_type.value

        budget_rate_window_minutes = self.budget_rate_window_minutes

        budget_rate_decrease_threshold_per_million = self.budget_rate_decrease_threshold_per_million

        slo = self.slo.to_dict()

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


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "alert_type": alert_type,
            "budget_rate_window_minutes": budget_rate_window_minutes,
            "budget_rate_decrease_threshold_per_million": budget_rate_decrease_threshold_per_million,
            "slo": slo,
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

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_budget_rate_burn_alert_request_slo import \
            CreateBudgetRateBurnAlertRequestSlo
        from ..models.notification_recipient import NotificationRecipient
        d = src_dict.copy()
        alert_type = BudgetRateAlertType(d.pop("alert_type"))




        budget_rate_window_minutes = d.pop("budget_rate_window_minutes")

        budget_rate_decrease_threshold_per_million = d.pop("budget_rate_decrease_threshold_per_million")

        slo = CreateBudgetRateBurnAlertRequestSlo.from_dict(d.pop("slo"))




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




        create_budget_rate_burn_alert_request = cls(
            alert_type=alert_type,
            budget_rate_window_minutes=budget_rate_window_minutes,
            budget_rate_decrease_threshold_per_million=budget_rate_decrease_threshold_per_million,
            slo=slo,
            recipients=recipients,
            id=id,
            description=description,
            triggered=triggered,
            created_at=created_at,
            updated_at=updated_at,
        )


        create_budget_rate_burn_alert_request.additional_properties = d
        return create_budget_rate_burn_alert_request

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
