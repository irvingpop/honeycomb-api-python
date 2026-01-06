from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.query import Query
  from ..models.query_result_links import QueryResultLinks





T = TypeVar("T", bound="QueryResult")



@_attrs_define
class QueryResult:
    """ A Query Result is created with the Query ID.

        Attributes:
            query (Union[Unset, Query]):
            id (Union[Unset, str]): The unique identifier (ID) of a Query Result. Example: sGUnkBHgRFN.
            complete (Union[Unset, bool]): Indicates if the query results are available yet or not. For example, is the
                query still being processed or complete?
            links (Union[Unset, QueryResultLinks]): An object containing UI links to the query result and query result graph
     """

    query: Union[Unset, 'Query'] = UNSET
    id: Union[Unset, str] = UNSET
    complete: Union[Unset, bool] = UNSET
    links: Union[Unset, 'QueryResultLinks'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.query import Query
        from ..models.query_result_links import QueryResultLinks
        query: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.query, Unset):
            query = self.query.to_dict()

        id = self.id

        complete = self.complete

        links: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.links, Unset):
            links = self.links.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if query is not UNSET:
            field_dict["query"] = query
        if id is not UNSET:
            field_dict["id"] = id
        if complete is not UNSET:
            field_dict["complete"] = complete
        if links is not UNSET:
            field_dict["links"] = links

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.query import Query
        from ..models.query_result_links import QueryResultLinks
        d = src_dict.copy()
        _query = d.pop("query", UNSET)
        query: Union[Unset, Query]
        if isinstance(_query,  Unset):
            query = UNSET
        else:
            query = Query.from_dict(_query)




        id = d.pop("id", UNSET)

        complete = d.pop("complete", UNSET)

        _links = d.pop("links", UNSET)
        links: Union[Unset, QueryResultLinks]
        if isinstance(_links,  Unset):
            links = UNSET
        else:
            links = QueryResultLinks.from_dict(_links)




        query_result = cls(
            query=query,
            id=id,
            complete=complete,
            links=links,
        )


        query_result.additional_properties = d
        return query_result

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
