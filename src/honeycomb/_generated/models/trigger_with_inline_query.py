from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.base_trigger_alert_type import BaseTriggerAlertType
from ..models.base_trigger_evaluation_schedule_type import BaseTriggerEvaluationScheduleType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime

if TYPE_CHECKING:
  from ..models.base_trigger_threshold import BaseTriggerThreshold
  from ..models.tag import Tag
  from ..models.base_trigger_evaluation_schedule import BaseTriggerEvaluationSchedule
  from ..models.trigger_with_inline_query_query import TriggerWithInlineQueryQuery
  from ..models.base_trigger_baseline_details_type_0 import BaseTriggerBaselineDetailsType0
  from ..models.notification_recipient import NotificationRecipient





T = TypeVar("T", bound="TriggerWithInlineQuery")



@_attrs_define
class TriggerWithInlineQuery:
    """ 
        Attributes:
            id (Union[Unset, str]): The unique identifier (ID) for this Trigger.
            dataset_slug (Union[Unset, str]): The slug of the dataset this trigger belongs to. For environment-wide
                triggers, this will be "__all__".
            name (Union[Unset, str]): A short, human-readable name for this Trigger, which will be displayed in the UI and
                when the trigger fires.
            description (Union[Unset, str]): A longer description, displayed on the Trigger's detail page.
            tags (Union[Unset, list['Tag']]): A list of key-value pairs to help identify the Trigger. Example: [{'key':
                'team', 'value': 'blue'}].
            threshold (Union[Unset, BaseTriggerThreshold]): The threshold over which the trigger will fire, specified as
                both an operator and a value.
            frequency (Union[Unset, int]): The interval in seconds in which to check the results of the query’s calculation
                against the threshold. Cannot be more than 4 times the query's duration (i.e. `duration <= frequency*4`). See [A
                Caveat on Time](https://docs.honeycomb.io/investigate/collaborate/share-query/define-query-json/#how-to-specify-
                an-absolute-time-range) for more information on specifying a query's duration. minimum: 60 maximum: 86400
                multipleOf: 60 default: 900
            alert_type (Union[Unset, BaseTriggerAlertType]): How often to fire an alert when a trigger threshold is crossed.
                - `on_change` sends a trigger notification when the result of the specified calculation crosses the threshold.
                  The trigger resolves only when the result of the query no longer satisfies the threshold condition.
                - `on_true` keeps sending a trigger notification at current frequency when and while the threshold is met.
                  (This reflects the same behavior as the "Send an alert every time a threshold is met" checkbox in the
                Honeycomb UI.)
                 Default: BaseTriggerAlertType.ON_CHANGE.
            disabled (Union[Unset, bool]): If true, the trigger will not be evaluated and alerts will not be sent.
                 Default: False.
            triggered (Union[Unset, bool]): If true, the trigger has crossed its specified threshold without resolving.
            recipients (Union[Unset, list['NotificationRecipient']]): A list of [Recipients](/api/recipients/) to notify
                when the Trigger fires. Using `type`+`target` is deprecated. First, create the Recipient via the Recipients API,
                and then specify the ID.
            evaluation_schedule_type (Union[Unset, BaseTriggerEvaluationScheduleType]): The schedule type used by the
                trigger. The default is frequency, where the trigger runs at the
                specified frequency. The window type means that the trigger will run at the specified frequency,
                but only in the time window specified in the evaluation_schedule field.
            evaluation_schedule (Union[Unset, BaseTriggerEvaluationSchedule]): A schedule that determines when the trigger
                is run. When the time is within the scheduled
                window, the trigger will be run at the specified frequency. Outside of the window, the trigger
                will not be run.
            created_at (Union[Unset, datetime.datetime]):
            updated_at (Union[Unset, datetime.datetime]):
            baseline_details (Union['BaseTriggerBaselineDetailsType0', Any, Unset]):
            query (Union[Unset, TriggerWithInlineQueryQuery]): A query ID or an inline query that is a strict subset of a
                Query Specification.
     """

    id: Union[Unset, str] = UNSET
    dataset_slug: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    tags: Union[Unset, list['Tag']] = UNSET
    threshold: Union[Unset, 'BaseTriggerThreshold'] = UNSET
    frequency: Union[Unset, int] = UNSET
    alert_type: Union[Unset, BaseTriggerAlertType] = BaseTriggerAlertType.ON_CHANGE
    disabled: Union[Unset, bool] = False
    triggered: Union[Unset, bool] = UNSET
    recipients: Union[Unset, list['NotificationRecipient']] = UNSET
    evaluation_schedule_type: Union[Unset, BaseTriggerEvaluationScheduleType] = UNSET
    evaluation_schedule: Union[Unset, 'BaseTriggerEvaluationSchedule'] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    baseline_details: Union['BaseTriggerBaselineDetailsType0', Any, Unset] = UNSET
    query: Union[Unset, 'TriggerWithInlineQueryQuery'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.base_trigger_threshold import BaseTriggerThreshold
        from ..models.tag import Tag
        from ..models.base_trigger_evaluation_schedule import BaseTriggerEvaluationSchedule
        from ..models.trigger_with_inline_query_query import TriggerWithInlineQueryQuery
        from ..models.base_trigger_baseline_details_type_0 import BaseTriggerBaselineDetailsType0
        from ..models.notification_recipient import NotificationRecipient
        id = self.id

        dataset_slug = self.dataset_slug

        name = self.name

        description = self.description

        tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)



        threshold: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.threshold, Unset):
            threshold = self.threshold.to_dict()

        frequency = self.frequency

        alert_type: Union[Unset, str] = UNSET
        if not isinstance(self.alert_type, Unset):
            alert_type = self.alert_type.value


        disabled = self.disabled

        triggered = self.triggered

        recipients: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.recipients, Unset):
            recipients = []
            for recipients_item_data in self.recipients:
                recipients_item = recipients_item_data.to_dict()
                recipients.append(recipients_item)



        evaluation_schedule_type: Union[Unset, str] = UNSET
        if not isinstance(self.evaluation_schedule_type, Unset):
            evaluation_schedule_type = self.evaluation_schedule_type.value


        evaluation_schedule: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.evaluation_schedule, Unset):
            evaluation_schedule = self.evaluation_schedule.to_dict()

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        baseline_details: Union[Any, Unset, dict[str, Any]]
        if isinstance(self.baseline_details, Unset):
            baseline_details = UNSET
        elif isinstance(self.baseline_details, BaseTriggerBaselineDetailsType0):
            baseline_details = self.baseline_details.to_dict()
        else:
            baseline_details = self.baseline_details

        query: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.query, Unset):
            query = self.query.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if dataset_slug is not UNSET:
            field_dict["dataset_slug"] = dataset_slug
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if tags is not UNSET:
            field_dict["tags"] = tags
        if threshold is not UNSET:
            field_dict["threshold"] = threshold
        if frequency is not UNSET:
            field_dict["frequency"] = frequency
        if alert_type is not UNSET:
            field_dict["alert_type"] = alert_type
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if triggered is not UNSET:
            field_dict["triggered"] = triggered
        if recipients is not UNSET:
            field_dict["recipients"] = recipients
        if evaluation_schedule_type is not UNSET:
            field_dict["evaluation_schedule_type"] = evaluation_schedule_type
        if evaluation_schedule is not UNSET:
            field_dict["evaluation_schedule"] = evaluation_schedule
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if baseline_details is not UNSET:
            field_dict["baseline_details"] = baseline_details
        if query is not UNSET:
            field_dict["query"] = query

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.base_trigger_threshold import BaseTriggerThreshold
        from ..models.tag import Tag
        from ..models.base_trigger_evaluation_schedule import BaseTriggerEvaluationSchedule
        from ..models.trigger_with_inline_query_query import TriggerWithInlineQueryQuery
        from ..models.base_trigger_baseline_details_type_0 import BaseTriggerBaselineDetailsType0
        from ..models.notification_recipient import NotificationRecipient
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        dataset_slug = d.pop("dataset_slug", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in (_tags or []):
            tags_item = Tag.from_dict(tags_item_data)



            tags.append(tags_item)


        _threshold = d.pop("threshold", UNSET)
        threshold: Union[Unset, BaseTriggerThreshold]
        if isinstance(_threshold,  Unset):
            threshold = UNSET
        else:
            threshold = BaseTriggerThreshold.from_dict(_threshold)




        frequency = d.pop("frequency", UNSET)

        _alert_type = d.pop("alert_type", UNSET)
        alert_type: Union[Unset, BaseTriggerAlertType]
        if isinstance(_alert_type,  Unset):
            alert_type = UNSET
        else:
            alert_type = BaseTriggerAlertType(_alert_type)




        disabled = d.pop("disabled", UNSET)

        triggered = d.pop("triggered", UNSET)

        recipients = []
        _recipients = d.pop("recipients", UNSET)
        for recipients_item_data in (_recipients or []):
            recipients_item = NotificationRecipient.from_dict(recipients_item_data)



            recipients.append(recipients_item)


        _evaluation_schedule_type = d.pop("evaluation_schedule_type", UNSET)
        evaluation_schedule_type: Union[Unset, BaseTriggerEvaluationScheduleType]
        if isinstance(_evaluation_schedule_type,  Unset):
            evaluation_schedule_type = UNSET
        else:
            evaluation_schedule_type = BaseTriggerEvaluationScheduleType(_evaluation_schedule_type)




        _evaluation_schedule = d.pop("evaluation_schedule", UNSET)
        evaluation_schedule: Union[Unset, BaseTriggerEvaluationSchedule]
        if isinstance(_evaluation_schedule,  Unset):
            evaluation_schedule = UNSET
        else:
            evaluation_schedule = BaseTriggerEvaluationSchedule.from_dict(_evaluation_schedule)




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




        def _parse_baseline_details(data: object) -> Union['BaseTriggerBaselineDetailsType0', Any, Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                baseline_details_type_0 = BaseTriggerBaselineDetailsType0.from_dict(data)



                return baseline_details_type_0
            except: # noqa: E722
                pass
            return cast(Union['BaseTriggerBaselineDetailsType0', Any, Unset], data)

        baseline_details = _parse_baseline_details(d.pop("baseline_details", UNSET))


        _query = d.pop("query", UNSET)
        query: Union[Unset, TriggerWithInlineQueryQuery]
        if isinstance(_query,  Unset):
            query = UNSET
        else:
            query = TriggerWithInlineQueryQuery.from_dict(_query)




        trigger_with_inline_query = cls(
            id=id,
            dataset_slug=dataset_slug,
            name=name,
            description=description,
            tags=tags,
            threshold=threshold,
            frequency=frequency,
            alert_type=alert_type,
            disabled=disabled,
            triggered=triggered,
            recipients=recipients,
            evaluation_schedule_type=evaluation_schedule_type,
            evaluation_schedule=evaluation_schedule,
            created_at=created_at,
            updated_at=updated_at,
            baseline_details=baseline_details,
            query=query,
        )


        trigger_with_inline_query.additional_properties = d
        return trigger_with_inline_query

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
