from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.payload_template import PayloadTemplate





T = TypeVar("T", bound="WebhookRecipientDetailsWebhookPayloadsPayloadTemplates")



@_attrs_define
class WebhookRecipientDetailsWebhookPayloadsPayloadTemplates:
    """ 
        Attributes:
            trigger (Union[Unset, PayloadTemplate]):
            budget_rate (Union[Unset, PayloadTemplate]):
            exhaustion_time (Union[Unset, PayloadTemplate]):
     """

    trigger: Union[Unset, 'PayloadTemplate'] = UNSET
    budget_rate: Union[Unset, 'PayloadTemplate'] = UNSET
    exhaustion_time: Union[Unset, 'PayloadTemplate'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.payload_template import PayloadTemplate
        trigger: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.trigger, Unset):
            trigger = self.trigger.to_dict()

        budget_rate: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.budget_rate, Unset):
            budget_rate = self.budget_rate.to_dict()

        exhaustion_time: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.exhaustion_time, Unset):
            exhaustion_time = self.exhaustion_time.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if trigger is not UNSET:
            field_dict["trigger"] = trigger
        if budget_rate is not UNSET:
            field_dict["budget_rate"] = budget_rate
        if exhaustion_time is not UNSET:
            field_dict["exhaustion_time"] = exhaustion_time

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.payload_template import PayloadTemplate
        d = src_dict.copy()
        _trigger = d.pop("trigger", UNSET)
        trigger: Union[Unset, PayloadTemplate]
        if isinstance(_trigger,  Unset):
            trigger = UNSET
        else:
            trigger = PayloadTemplate.from_dict(_trigger)




        _budget_rate = d.pop("budget_rate", UNSET)
        budget_rate: Union[Unset, PayloadTemplate]
        if isinstance(_budget_rate,  Unset):
            budget_rate = UNSET
        else:
            budget_rate = PayloadTemplate.from_dict(_budget_rate)




        _exhaustion_time = d.pop("exhaustion_time", UNSET)
        exhaustion_time: Union[Unset, PayloadTemplate]
        if isinstance(_exhaustion_time,  Unset):
            exhaustion_time = UNSET
        else:
            exhaustion_time = PayloadTemplate.from_dict(_exhaustion_time)




        webhook_recipient_details_webhook_payloads_payload_templates = cls(
            trigger=trigger,
            budget_rate=budget_rate,
            exhaustion_time=exhaustion_time,
        )


        webhook_recipient_details_webhook_payloads_payload_templates.additional_properties = d
        return webhook_recipient_details_webhook_payloads_payload_templates

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
