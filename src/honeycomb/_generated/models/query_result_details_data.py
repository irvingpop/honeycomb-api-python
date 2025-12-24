from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.query_results_series import QueryResultsSeries
  from ..models.query_results_data import QueryResultsData





T = TypeVar("T", bound="QueryResultDetailsData")



@_attrs_define
class QueryResultDetailsData:
    """ An object containing the query result data

        Attributes:
            series (Union[Unset, list['QueryResultsSeries']]): Timeseries data from the query result (equivalent to the
                graph data in the Honeycomb UI)
            results (Union[Unset, list['QueryResultsData']]): Query results data (equivalent to the Overview in the
                Honeycomb UI below the graph)
            total_by_aggregate (Union[Unset, QueryResultsData]): Query result details
            total_by_aggregate_series (Union[Unset, list['QueryResultsSeries']]): Timeseries data showing the total value of
                each aggregate returned in `total_by_aggregate` across the time range. Aggregate values returned do not respect
                any Having clauses included in a query. Only available if both `disable_total_by_aggregate` and `disable_series`
                are set to `false`.
            other_by_aggregate (Union[Unset, QueryResultsData]): Query result details
     """

    series: Union[Unset, list['QueryResultsSeries']] = UNSET
    results: Union[Unset, list['QueryResultsData']] = UNSET
    total_by_aggregate: Union[Unset, 'QueryResultsData'] = UNSET
    total_by_aggregate_series: Union[Unset, list['QueryResultsSeries']] = UNSET
    other_by_aggregate: Union[Unset, 'QueryResultsData'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.query_results_series import QueryResultsSeries
        from ..models.query_results_data import QueryResultsData
        series: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.series, Unset):
            series = []
            for series_item_data in self.series:
                series_item = series_item_data.to_dict()
                series.append(series_item)



        results: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)



        total_by_aggregate: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.total_by_aggregate, Unset):
            total_by_aggregate = self.total_by_aggregate.to_dict()

        total_by_aggregate_series: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.total_by_aggregate_series, Unset):
            total_by_aggregate_series = []
            for total_by_aggregate_series_item_data in self.total_by_aggregate_series:
                total_by_aggregate_series_item = total_by_aggregate_series_item_data.to_dict()
                total_by_aggregate_series.append(total_by_aggregate_series_item)



        other_by_aggregate: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.other_by_aggregate, Unset):
            other_by_aggregate = self.other_by_aggregate.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if series is not UNSET:
            field_dict["series"] = series
        if results is not UNSET:
            field_dict["results"] = results
        if total_by_aggregate is not UNSET:
            field_dict["total_by_aggregate"] = total_by_aggregate
        if total_by_aggregate_series is not UNSET:
            field_dict["total_by_aggregate_series"] = total_by_aggregate_series
        if other_by_aggregate is not UNSET:
            field_dict["other_by_aggregate"] = other_by_aggregate

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.query_results_series import QueryResultsSeries
        from ..models.query_results_data import QueryResultsData
        d = src_dict.copy()
        series = []
        _series = d.pop("series", UNSET)
        for series_item_data in (_series or []):
            series_item = QueryResultsSeries.from_dict(series_item_data)



            series.append(series_item)


        results = []
        _results = d.pop("results", UNSET)
        for results_item_data in (_results or []):
            results_item = QueryResultsData.from_dict(results_item_data)



            results.append(results_item)


        _total_by_aggregate = d.pop("total_by_aggregate", UNSET)
        total_by_aggregate: Union[Unset, QueryResultsData]
        if isinstance(_total_by_aggregate,  Unset):
            total_by_aggregate = UNSET
        else:
            total_by_aggregate = QueryResultsData.from_dict(_total_by_aggregate)




        total_by_aggregate_series = []
        _total_by_aggregate_series = d.pop("total_by_aggregate_series", UNSET)
        for total_by_aggregate_series_item_data in (_total_by_aggregate_series or []):
            total_by_aggregate_series_item = QueryResultsSeries.from_dict(total_by_aggregate_series_item_data)



            total_by_aggregate_series.append(total_by_aggregate_series_item)


        _other_by_aggregate = d.pop("other_by_aggregate", UNSET)
        other_by_aggregate: Union[Unset, QueryResultsData]
        if isinstance(_other_by_aggregate,  Unset):
            other_by_aggregate = UNSET
        else:
            other_by_aggregate = QueryResultsData.from_dict(_other_by_aggregate)




        query_result_details_data = cls(
            series=series,
            results=results,
            total_by_aggregate=total_by_aggregate,
            total_by_aggregate_series=total_by_aggregate_series,
            other_by_aggregate=other_by_aggregate,
        )


        query_result_details_data.additional_properties = d
        return query_result_details_data

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
