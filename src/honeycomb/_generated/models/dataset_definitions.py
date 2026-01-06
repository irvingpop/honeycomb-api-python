from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.dataset_definition_type_1 import DatasetDefinitionType1





T = TypeVar("T", bound="DatasetDefinitions")



@_attrs_define
class DatasetDefinitions:
    """ Dataset Definitions describe the fields with special meaning in the Dataset.

        Attributes:
            span_id (Union['DatasetDefinitionType1', None, Unset]):
            trace_id (Union['DatasetDefinitionType1', None, Unset]):
            parent_id (Union['DatasetDefinitionType1', None, Unset]):
            name (Union['DatasetDefinitionType1', None, Unset]):
            service_name (Union['DatasetDefinitionType1', None, Unset]):
            duration_ms (Union['DatasetDefinitionType1', None, Unset]):
            span_kind (Union['DatasetDefinitionType1', None, Unset]):
            annotation_type (Union['DatasetDefinitionType1', None, Unset]):
            link_span_id (Union['DatasetDefinitionType1', None, Unset]):
            link_trace_id (Union['DatasetDefinitionType1', None, Unset]):
            error (Union['DatasetDefinitionType1', None, Unset]):
            status (Union['DatasetDefinitionType1', None, Unset]):
            route (Union['DatasetDefinitionType1', None, Unset]):
            user (Union['DatasetDefinitionType1', None, Unset]):
            log_severity (Union['DatasetDefinitionType1', None, Unset]):
            log_message (Union['DatasetDefinitionType1', None, Unset]):
     """

    span_id: Union['DatasetDefinitionType1', None, Unset] = UNSET
    trace_id: Union['DatasetDefinitionType1', None, Unset] = UNSET
    parent_id: Union['DatasetDefinitionType1', None, Unset] = UNSET
    name: Union['DatasetDefinitionType1', None, Unset] = UNSET
    service_name: Union['DatasetDefinitionType1', None, Unset] = UNSET
    duration_ms: Union['DatasetDefinitionType1', None, Unset] = UNSET
    span_kind: Union['DatasetDefinitionType1', None, Unset] = UNSET
    annotation_type: Union['DatasetDefinitionType1', None, Unset] = UNSET
    link_span_id: Union['DatasetDefinitionType1', None, Unset] = UNSET
    link_trace_id: Union['DatasetDefinitionType1', None, Unset] = UNSET
    error: Union['DatasetDefinitionType1', None, Unset] = UNSET
    status: Union['DatasetDefinitionType1', None, Unset] = UNSET
    route: Union['DatasetDefinitionType1', None, Unset] = UNSET
    user: Union['DatasetDefinitionType1', None, Unset] = UNSET
    log_severity: Union['DatasetDefinitionType1', None, Unset] = UNSET
    log_message: Union['DatasetDefinitionType1', None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_definition_type_1 import DatasetDefinitionType1
        span_id: Union[None, Unset, dict[str, Any]]
        if isinstance(self.span_id, Unset):
            span_id = UNSET
        elif isinstance(self.span_id, DatasetDefinitionType1):
            span_id = self.span_id.to_dict()
        else:
            span_id = self.span_id

        trace_id: Union[None, Unset, dict[str, Any]]
        if isinstance(self.trace_id, Unset):
            trace_id = UNSET
        elif isinstance(self.trace_id, DatasetDefinitionType1):
            trace_id = self.trace_id.to_dict()
        else:
            trace_id = self.trace_id

        parent_id: Union[None, Unset, dict[str, Any]]
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        elif isinstance(self.parent_id, DatasetDefinitionType1):
            parent_id = self.parent_id.to_dict()
        else:
            parent_id = self.parent_id

        name: Union[None, Unset, dict[str, Any]]
        if isinstance(self.name, Unset):
            name = UNSET
        elif isinstance(self.name, DatasetDefinitionType1):
            name = self.name.to_dict()
        else:
            name = self.name

        service_name: Union[None, Unset, dict[str, Any]]
        if isinstance(self.service_name, Unset):
            service_name = UNSET
        elif isinstance(self.service_name, DatasetDefinitionType1):
            service_name = self.service_name.to_dict()
        else:
            service_name = self.service_name

        duration_ms: Union[None, Unset, dict[str, Any]]
        if isinstance(self.duration_ms, Unset):
            duration_ms = UNSET
        elif isinstance(self.duration_ms, DatasetDefinitionType1):
            duration_ms = self.duration_ms.to_dict()
        else:
            duration_ms = self.duration_ms

        span_kind: Union[None, Unset, dict[str, Any]]
        if isinstance(self.span_kind, Unset):
            span_kind = UNSET
        elif isinstance(self.span_kind, DatasetDefinitionType1):
            span_kind = self.span_kind.to_dict()
        else:
            span_kind = self.span_kind

        annotation_type: Union[None, Unset, dict[str, Any]]
        if isinstance(self.annotation_type, Unset):
            annotation_type = UNSET
        elif isinstance(self.annotation_type, DatasetDefinitionType1):
            annotation_type = self.annotation_type.to_dict()
        else:
            annotation_type = self.annotation_type

        link_span_id: Union[None, Unset, dict[str, Any]]
        if isinstance(self.link_span_id, Unset):
            link_span_id = UNSET
        elif isinstance(self.link_span_id, DatasetDefinitionType1):
            link_span_id = self.link_span_id.to_dict()
        else:
            link_span_id = self.link_span_id

        link_trace_id: Union[None, Unset, dict[str, Any]]
        if isinstance(self.link_trace_id, Unset):
            link_trace_id = UNSET
        elif isinstance(self.link_trace_id, DatasetDefinitionType1):
            link_trace_id = self.link_trace_id.to_dict()
        else:
            link_trace_id = self.link_trace_id

        error: Union[None, Unset, dict[str, Any]]
        if isinstance(self.error, Unset):
            error = UNSET
        elif isinstance(self.error, DatasetDefinitionType1):
            error = self.error.to_dict()
        else:
            error = self.error

        status: Union[None, Unset, dict[str, Any]]
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, DatasetDefinitionType1):
            status = self.status.to_dict()
        else:
            status = self.status

        route: Union[None, Unset, dict[str, Any]]
        if isinstance(self.route, Unset):
            route = UNSET
        elif isinstance(self.route, DatasetDefinitionType1):
            route = self.route.to_dict()
        else:
            route = self.route

        user: Union[None, Unset, dict[str, Any]]
        if isinstance(self.user, Unset):
            user = UNSET
        elif isinstance(self.user, DatasetDefinitionType1):
            user = self.user.to_dict()
        else:
            user = self.user

        log_severity: Union[None, Unset, dict[str, Any]]
        if isinstance(self.log_severity, Unset):
            log_severity = UNSET
        elif isinstance(self.log_severity, DatasetDefinitionType1):
            log_severity = self.log_severity.to_dict()
        else:
            log_severity = self.log_severity

        log_message: Union[None, Unset, dict[str, Any]]
        if isinstance(self.log_message, Unset):
            log_message = UNSET
        elif isinstance(self.log_message, DatasetDefinitionType1):
            log_message = self.log_message.to_dict()
        else:
            log_message = self.log_message


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if span_id is not UNSET:
            field_dict["span_id"] = span_id
        if trace_id is not UNSET:
            field_dict["trace_id"] = trace_id
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if name is not UNSET:
            field_dict["name"] = name
        if service_name is not UNSET:
            field_dict["service_name"] = service_name
        if duration_ms is not UNSET:
            field_dict["duration_ms"] = duration_ms
        if span_kind is not UNSET:
            field_dict["span_kind"] = span_kind
        if annotation_type is not UNSET:
            field_dict["annotation_type"] = annotation_type
        if link_span_id is not UNSET:
            field_dict["link_span_id"] = link_span_id
        if link_trace_id is not UNSET:
            field_dict["link_trace_id"] = link_trace_id
        if error is not UNSET:
            field_dict["error"] = error
        if status is not UNSET:
            field_dict["status"] = status
        if route is not UNSET:
            field_dict["route"] = route
        if user is not UNSET:
            field_dict["user"] = user
        if log_severity is not UNSET:
            field_dict["log_severity"] = log_severity
        if log_message is not UNSET:
            field_dict["log_message"] = log_message

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.dataset_definition_type_1 import DatasetDefinitionType1
        d = src_dict.copy()
        def _parse_span_id(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        span_id = _parse_span_id(d.pop("span_id", UNSET))


        def _parse_trace_id(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        trace_id = _parse_trace_id(d.pop("trace_id", UNSET))


        def _parse_parent_id(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        parent_id = _parse_parent_id(d.pop("parent_id", UNSET))


        def _parse_name(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        name = _parse_name(d.pop("name", UNSET))


        def _parse_service_name(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        service_name = _parse_service_name(d.pop("service_name", UNSET))


        def _parse_duration_ms(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        duration_ms = _parse_duration_ms(d.pop("duration_ms", UNSET))


        def _parse_span_kind(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        span_kind = _parse_span_kind(d.pop("span_kind", UNSET))


        def _parse_annotation_type(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        annotation_type = _parse_annotation_type(d.pop("annotation_type", UNSET))


        def _parse_link_span_id(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        link_span_id = _parse_link_span_id(d.pop("link_span_id", UNSET))


        def _parse_link_trace_id(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        link_trace_id = _parse_link_trace_id(d.pop("link_trace_id", UNSET))


        def _parse_error(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        error = _parse_error(d.pop("error", UNSET))


        def _parse_status(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        status = _parse_status(d.pop("status", UNSET))


        def _parse_route(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        route = _parse_route(d.pop("route", UNSET))


        def _parse_user(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        user = _parse_user(d.pop("user", UNSET))


        def _parse_log_severity(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        log_severity = _parse_log_severity(d.pop("log_severity", UNSET))


        def _parse_log_message(data: object) -> Union['DatasetDefinitionType1', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_dataset_definition_type_1 = DatasetDefinitionType1.from_dict(data)



                return componentsschemas_dataset_definition_type_1
            except: # noqa: E722
                pass
            return cast(Union['DatasetDefinitionType1', None, Unset], data)

        log_message = _parse_log_message(d.pop("log_message", UNSET))


        dataset_definitions = cls(
            span_id=span_id,
            trace_id=trace_id,
            parent_id=parent_id,
            name=name,
            service_name=service_name,
            duration_ms=duration_ms,
            span_kind=span_kind,
            annotation_type=annotation_type,
            link_span_id=link_span_id,
            link_trace_id=link_trace_id,
            error=error,
            status=status,
            route=route,
            user=user,
            log_severity=log_severity,
            log_message=log_message,
        )


        dataset_definitions.additional_properties = d
        return dataset_definitions

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
