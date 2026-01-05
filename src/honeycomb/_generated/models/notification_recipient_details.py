from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.notification_recipient_details_pagerduty_severity import \
    NotificationRecipientDetailsPagerdutySeverity
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.notification_recipient_details_variables_item import \
      NotificationRecipientDetailsVariablesItem





T = TypeVar("T", bound="NotificationRecipientDetails")



@_attrs_define
class NotificationRecipientDetails:
    """ 
        Attributes:
            pagerduty_severity (Union[Unset, NotificationRecipientDetailsPagerdutySeverity]): When using a Recipient of
                `type = "pagerduty"`, the severity of the alert can be specified.
                 Default: NotificationRecipientDetailsPagerdutySeverity.CRITICAL.
            variables (Union[Unset, list['NotificationRecipientDetailsVariablesItem']]): When using a Recipient of `type =
                "webhook"`, the alert-level variables can be specified.
     """

    pagerduty_severity: Union[Unset, NotificationRecipientDetailsPagerdutySeverity] = NotificationRecipientDetailsPagerdutySeverity.CRITICAL
    variables: Union[Unset, list['NotificationRecipientDetailsVariablesItem']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.notification_recipient_details_variables_item import \
            NotificationRecipientDetailsVariablesItem
        pagerduty_severity: Union[Unset, str] = UNSET
        if not isinstance(self.pagerduty_severity, Unset):
            pagerduty_severity = self.pagerduty_severity.value


        variables: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.variables, Unset):
            variables = []
            for variables_item_data in self.variables:
                variables_item = variables_item_data.to_dict()
                variables.append(variables_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if pagerduty_severity is not UNSET:
            field_dict["pagerduty_severity"] = pagerduty_severity
        if variables is not UNSET:
            field_dict["variables"] = variables

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.notification_recipient_details_variables_item import \
            NotificationRecipientDetailsVariablesItem
        d = src_dict.copy()
        _pagerduty_severity = d.pop("pagerduty_severity", UNSET)
        pagerduty_severity: Union[Unset, NotificationRecipientDetailsPagerdutySeverity]
        if isinstance(_pagerduty_severity,  Unset):
            pagerduty_severity = UNSET
        else:
            pagerduty_severity = NotificationRecipientDetailsPagerdutySeverity(_pagerduty_severity)




        variables = []
        _variables = d.pop("variables", UNSET)
        for variables_item_data in (_variables or []):
            variables_item = NotificationRecipientDetailsVariablesItem.from_dict(variables_item_data)



            variables.append(variables_item)


        notification_recipient_details = cls(
            pagerduty_severity=pagerduty_severity,
            variables=variables,
        )


        notification_recipient_details.additional_properties = d
        return notification_recipient_details

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
