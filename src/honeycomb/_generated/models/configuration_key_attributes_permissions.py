from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigurationKeyAttributesPermissions")



@_attrs_define
class ConfigurationKeyAttributesPermissions:
    """ The permissions granted to this Configuration API Key

        Attributes:
            create_datasets (Union[Unset, bool]): Whether this API Key can create new Datasets Default: False.
            send_events (Union[Unset, bool]): Whether this API Key can send Events Default: False.
            manage_markers (Union[Unset, bool]): Whether this API Key can manage Markers Default: False.
            manage_triggers (Union[Unset, bool]): Whether this API Key can manage Triggers Default: False.
            manage_boards (Union[Unset, bool]): Whether this API Key can manage Boards Default: False.
            run_queries (Union[Unset, bool]): Whether this API Key can run Queries Default: False.
            manage_columns (Union[Unset, bool]): Whether this API Key can manage Columns and Queries Default: False.
            manage_slos (Union[Unset, bool]): Whether this API Key can manage SLOs Default: False.
            manage_recipients (Union[Unset, bool]): Whether this API Key can manage Recipients Default: False.
            manage_private_boards (Union[Unset, bool]): Whether this API Key can manage Private Boards Default: False.
            read_service_maps (Union[Unset, bool]): Whether this API Key can read Service Maps Default: False.
            visible_team_members (Union[Unset, bool]): Whether this API Key secret can be accessed by members in the
                Honeycomb dashboard. The user will only
                see a redacted key if they aren't an owner when this setting is enabled.

                This parameter has no effect when used through the API since the API never returns the configuration
                key secret except at creation.
                 Default: False.
     """

    create_datasets: Union[Unset, bool] = False
    send_events: Union[Unset, bool] = False
    manage_markers: Union[Unset, bool] = False
    manage_triggers: Union[Unset, bool] = False
    manage_boards: Union[Unset, bool] = False
    run_queries: Union[Unset, bool] = False
    manage_columns: Union[Unset, bool] = False
    manage_slos: Union[Unset, bool] = False
    manage_recipients: Union[Unset, bool] = False
    manage_private_boards: Union[Unset, bool] = False
    read_service_maps: Union[Unset, bool] = False
    visible_team_members: Union[Unset, bool] = False
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

        configuration_key_attributes_permissions = cls(
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


        configuration_key_attributes_permissions.additional_properties = d
        return configuration_key_attributes_permissions

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
