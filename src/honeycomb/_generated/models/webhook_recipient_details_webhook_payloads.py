from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.template_variable_definition import TemplateVariableDefinition
  from ..models.webhook_recipient_details_webhook_payloads_payload_templates import \
      WebhookRecipientDetailsWebhookPayloadsPayloadTemplates





T = TypeVar("T", bound="WebhookRecipientDetailsWebhookPayloads")



@_attrs_define
class WebhookRecipientDetailsWebhookPayloads:
    """ Specify a custom webhook payload.

        Attributes:
            template_variables (Union[Unset, list['TemplateVariableDefinition']]): Custom variable definitions for this
                webhook Example: [{'name': 'severity', 'default_value': 'CRITICAL'}].
            payload_templates (Union[Unset, WebhookRecipientDetailsWebhookPayloadsPayloadTemplates]):
     """

    template_variables: Union[Unset, list['TemplateVariableDefinition']] = UNSET
    payload_templates: Union[Unset, 'WebhookRecipientDetailsWebhookPayloadsPayloadTemplates'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.template_variable_definition import \
            TemplateVariableDefinition
        from ..models.webhook_recipient_details_webhook_payloads_payload_templates import \
            WebhookRecipientDetailsWebhookPayloadsPayloadTemplates
        template_variables: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.template_variables, Unset):
            template_variables = []
            for template_variables_item_data in self.template_variables:
                template_variables_item = template_variables_item_data.to_dict()
                template_variables.append(template_variables_item)



        payload_templates: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.payload_templates, Unset):
            payload_templates = self.payload_templates.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if template_variables is not UNSET:
            field_dict["template_variables"] = template_variables
        if payload_templates is not UNSET:
            field_dict["payload_templates"] = payload_templates

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.template_variable_definition import \
            TemplateVariableDefinition
        from ..models.webhook_recipient_details_webhook_payloads_payload_templates import \
            WebhookRecipientDetailsWebhookPayloadsPayloadTemplates
        d = src_dict.copy()
        template_variables = []
        _template_variables = d.pop("template_variables", UNSET)
        for template_variables_item_data in (_template_variables or []):
            template_variables_item = TemplateVariableDefinition.from_dict(template_variables_item_data)



            template_variables.append(template_variables_item)


        _payload_templates = d.pop("payload_templates", UNSET)
        payload_templates: Union[Unset, WebhookRecipientDetailsWebhookPayloadsPayloadTemplates]
        if isinstance(_payload_templates,  Unset):
            payload_templates = UNSET
        else:
            payload_templates = WebhookRecipientDetailsWebhookPayloadsPayloadTemplates.from_dict(_payload_templates)




        webhook_recipient_details_webhook_payloads = cls(
            template_variables=template_variables,
            payload_templates=payload_templates,
        )


        webhook_recipient_details_webhook_payloads.additional_properties = d
        return webhook_recipient_details_webhook_payloads

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
