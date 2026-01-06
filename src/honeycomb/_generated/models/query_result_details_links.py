from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="QueryResultDetailsLinks")



@_attrs_define
class QueryResultDetailsLinks:
    """ An object containing UI links to the query result and query result graph

        Attributes:
            query_url (Union[Unset, str]): A link to the query result in the Honeycomb UI Example:
                https://ui.honeycomb.io/myteam/datasets/test-via-curl/result/HprJhV1fYy.
            graph_image_url (Union[Unset, str]): A direct link to the graph image from the query result Example:
                https://ui.honeycomb.io/myteam/datasets/test-via-curl/result/HprJhV1fYy/snapshot.
     """

    query_url: Union[Unset, str] = UNSET
    graph_image_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        query_url = self.query_url

        graph_image_url = self.graph_image_url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if query_url is not UNSET:
            field_dict["query_url"] = query_url
        if graph_image_url is not UNSET:
            field_dict["graph_image_url"] = graph_image_url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        query_url = d.pop("query_url", UNSET)

        graph_image_url = d.pop("graph_image_url", UNSET)

        query_result_details_links = cls(
            query_url=query_url,
            graph_image_url=graph_image_url,
        )


        query_result_details_links.additional_properties = d
        return query_result_details_links

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
