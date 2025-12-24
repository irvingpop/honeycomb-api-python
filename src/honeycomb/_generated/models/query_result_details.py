from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.query import Query
  from ..models.query_result_details_links import QueryResultDetailsLinks
  from ..models.query_result_details_data import QueryResultDetailsData





T = TypeVar("T", bound="QueryResultDetails")



@_attrs_define
class QueryResultDetails:
    """ Query Results for the Query ID.
    The response body will be a JSON object with "complete": true and the results populated once the query is complete.
    The response body will contain caching headers to indicate that once complete, and the Query Result may be cached,
    as it will not change.

        Attributes:
            query (Union[Unset, Query]):
            id (Union[Unset, str]): The unique identifier (ID) of a Query Result Example: sGUnkBHgRFN.
            complete (Union[Unset, bool]): Indicates if the query results are available yet or not. For example, is the
                query still being processed or complete? Example: True.
            data (Union[Unset, QueryResultDetailsData]): An object containing the query result data
            links (Union[Unset, QueryResultDetailsLinks]): An object containing UI links to the query result and query
                result graph
     """

    query: Union[Unset, 'Query'] = UNSET
    id: Union[Unset, str] = UNSET
    complete: Union[Unset, bool] = UNSET
    data: Union[Unset, 'QueryResultDetailsData'] = UNSET
    links: Union[Unset, 'QueryResultDetailsLinks'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.query import Query
        from ..models.query_result_details_links import QueryResultDetailsLinks
        from ..models.query_result_details_data import QueryResultDetailsData
        query: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.query, Unset):
            query = self.query.to_dict()

        id = self.id

        complete = self.complete

        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

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
        if data is not UNSET:
            field_dict["data"] = data
        if links is not UNSET:
            field_dict["links"] = links

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.query import Query
        from ..models.query_result_details_links import QueryResultDetailsLinks
        from ..models.query_result_details_data import QueryResultDetailsData
        d = src_dict.copy()
        _query = d.pop("query", UNSET)
        query: Union[Unset, Query]
        if isinstance(_query,  Unset):
            query = UNSET
        else:
            query = Query.from_dict(_query)




        id = d.pop("id", UNSET)

        complete = d.pop("complete", UNSET)

        _data = d.pop("data", UNSET)
        data: Union[Unset, QueryResultDetailsData]
        if isinstance(_data,  Unset):
            data = UNSET
        else:
            data = QueryResultDetailsData.from_dict(_data)




        _links = d.pop("links", UNSET)
        links: Union[Unset, QueryResultDetailsLinks]
        if isinstance(_links,  Unset):
            links = UNSET
        else:
            links = QueryResultDetailsLinks.from_dict(_links)




        query_result_details = cls(
            query=query,
            id=id,
            complete=complete,
            data=data,
            links=links,
        )


        query_result_details.additional_properties = d
        return query_result_details

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
