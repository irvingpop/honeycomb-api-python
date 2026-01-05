from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigurationKeyRequestAttributesPermissions")



@_attrs_define
class ConfigurationKeyRequestAttributesPermissions:
    """ The permissions granted to this Configuration API Key. Values omitted will not be replaced.

        Attributes:
            create_datasets (Union[Unset, bool]): Whether this API Key can create new Datasets
            send_events (Union[Unset, bool]): Whether this API Key can send Events
            manage_markers (Union[Unset, bool]): Whether this API Key can manage Markers
            manage_triggers (Union[Unset, bool]): Whether this API Key can manage Triggers
            manage_boards (Union[Unset, bool]): Whether this API Key can manage Boards
            run_queries (Union[Unset, bool]): Whether this API Key can run Queries
            manage_columns (Union[Unset, bool]): Whether this API Key can manage Columns and Queries
            manage_slos (Union[Unset, bool]): Whether this API Key can manage SLOs
            manage_recipients (Union[Unset, bool]): Whether this API Key can manage Recipients
            manage_private_boards (Union[Unset, bool]): Whether this API Key can manage Private Boards
            read_service_maps (Union[Unset, bool]): Whether this API Key can read Service Maps
            visible_team_members (Union[Unset, bool]): Whether this API Key can be accessed by members.
                This value is not checked when fetching API keys through the API, there are no permissions check in the
                API.
     """

    create_datasets: Union[Unset, bool] = UNSET
    send_events: Union[Unset, bool] = UNSET
    manage_markers: Union[Unset, bool] = UNSET
    manage_triggers: Union[Unset, bool] = UNSET
    manage_boards: Union[Unset, bool] = UNSET
    run_queries: Union[Unset, bool] = UNSET
    manage_columns: Union[Unset, bool] = UNSET
    manage_slos: Union[Unset, bool] = UNSET
    manage_recipients: Union[Unset, bool] = UNSET
    manage_private_boards: Union[Unset, bool] = UNSET
    read_service_maps: Union[Unset, bool] = UNSET
    visible_team_members: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        create_datasets = self.create_datasets

        send_events = self.send_events

        manage_markers = self.manage_markers

        manage_triggers = self.manage_triggers

        manage_boards = self.manage_boards

        run_queries = self.run_queries

        manage_columns = self.manage_columns

        manage_slos = self.manage_slos

        manage_recipients = self.manage_recipients

        manage_private_boards = self.manage_private_boards

        read_service_maps = self.read_service_maps

        visible_team_members = self.visible_team_members


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if create_datasets is not UNSET:
            field_dict["create_datasets"] = create_datasets
        if send_events is not UNSET:
            field_dict["send_events"] = send_events
        if manage_markers is not UNSET:
            field_dict["manage_markers"] = manage_markers
        if manage_triggers is not UNSET:
            field_dict["manage_triggers"] = manage_triggers
        if manage_boards is not UNSET:
            field_dict["manage_boards"] = manage_boards
        if run_queries is not UNSET:
            field_dict["run_queries"] = run_queries
        if manage_columns is not UNSET:
            field_dict["manage_columns"] = manage_columns
        if manage_slos is not UNSET:
            field_dict["manage_slos"] = manage_slos
        if manage_recipients is not UNSET:
            field_dict["manage_recipients"] = manage_recipients
        if manage_private_boards is not UNSET:
            field_dict["manage_privateBoards"] = manage_private_boards
        if read_service_maps is not UNSET:
            field_dict["read_service_maps"] = read_service_maps
        if visible_team_members is not UNSET:
            field_dict["visible_team_members"] = visible_team_members

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        create_datasets = d.pop("create_datasets", UNSET)

        send_events = d.pop("send_events", UNSET)

        manage_markers = d.pop("manage_markers", UNSET)

        manage_triggers = d.pop("manage_triggers", UNSET)

        manage_boards = d.pop("manage_boards", UNSET)

        run_queries = d.pop("run_queries", UNSET)

        manage_columns = d.pop("manage_columns", UNSET)

        manage_slos = d.pop("manage_slos", UNSET)

        manage_recipients = d.pop("manage_recipients", UNSET)

        manage_private_boards = d.pop("manage_privateBoards", UNSET)

        read_service_maps = d.pop("read_service_maps", UNSET)

        visible_team_members = d.pop("visible_team_members", UNSET)

        configuration_key_request_attributes_permissions = cls(
            create_datasets=create_datasets,
            send_events=send_events,
            manage_markers=manage_markers,
            manage_triggers=manage_triggers,
            manage_boards=manage_boards,
            run_queries=run_queries,
            manage_columns=manage_columns,
            manage_slos=manage_slos,
            manage_recipients=manage_recipients,
            manage_private_boards=manage_private_boards,
            read_service_maps=read_service_maps,
            visible_team_members=visible_team_members,
        )


        configuration_key_request_attributes_permissions.additional_properties = d
        return configuration_key_request_attributes_permissions

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
