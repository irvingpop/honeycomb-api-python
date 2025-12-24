from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="AuthApiKeyAccess")



@_attrs_define
class AuthApiKeyAccess:
    """ 
        Attributes:
            events (Union[Unset, bool]):  Default: False.
            markers (Union[Unset, bool]):  Default: False.
            triggers (Union[Unset, bool]):  Default: False.
            boards (Union[Unset, bool]):  Default: False.
            queries (Union[Unset, bool]):  Default: False.
            columns (Union[Unset, bool]):  Default: False.
            create_datasets (Union[Unset, bool]):  Default: False.
            slos (Union[Unset, bool]):  Default: False.
            recipients (Union[Unset, bool]):  Default: False.
            private_boards (Union[Unset, bool]):  Default: False.
     """

    events: Union[Unset, bool] = False
    markers: Union[Unset, bool] = False
    triggers: Union[Unset, bool] = False
    boards: Union[Unset, bool] = False
    queries: Union[Unset, bool] = False
    columns: Union[Unset, bool] = False
    create_datasets: Union[Unset, bool] = False
    slos: Union[Unset, bool] = False
    recipients: Union[Unset, bool] = False
    private_boards: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        events = self.events

        markers = self.markers

        triggers = self.triggers

        boards = self.boards

        queries = self.queries

        columns = self.columns

        create_datasets = self.create_datasets

        slos = self.slos

        recipients = self.recipients

        private_boards = self.private_boards


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if events is not UNSET:
            field_dict["events"] = events
        if markers is not UNSET:
            field_dict["markers"] = markers
        if triggers is not UNSET:
            field_dict["triggers"] = triggers
        if boards is not UNSET:
            field_dict["boards"] = boards
        if queries is not UNSET:
            field_dict["queries"] = queries
        if columns is not UNSET:
            field_dict["columns"] = columns
        if create_datasets is not UNSET:
            field_dict["createDatasets"] = create_datasets
        if slos is not UNSET:
            field_dict["slos"] = slos
        if recipients is not UNSET:
            field_dict["recipients"] = recipients
        if private_boards is not UNSET:
            field_dict["privateBoards"] = private_boards

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        events = d.pop("events", UNSET)

        markers = d.pop("markers", UNSET)

        triggers = d.pop("triggers", UNSET)

        boards = d.pop("boards", UNSET)

        queries = d.pop("queries", UNSET)

        columns = d.pop("columns", UNSET)

        create_datasets = d.pop("createDatasets", UNSET)

        slos = d.pop("slos", UNSET)

        recipients = d.pop("recipients", UNSET)

        private_boards = d.pop("privateBoards", UNSET)

        auth_api_key_access = cls(
            events=events,
            markers=markers,
            triggers=triggers,
            boards=boards,
            queries=queries,
            columns=columns,
            create_datasets=create_datasets,
            slos=slos,
            recipients=recipients,
            private_boards=private_boards,
        )


        auth_api_key_access.additional_properties = d
        return auth_api_key_access

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
