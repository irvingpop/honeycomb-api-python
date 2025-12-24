from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.query_compare_time_offset_seconds import QueryCompareTimeOffsetSeconds
from ..models.query_filter_combination import QueryFilterCombination
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.query_calculated_fields_item import QueryCalculatedFieldsItem
  from ..models.query_calculations_item import QueryCalculationsItem
  from ..models.query_orders_item import QueryOrdersItem
  from ..models.query_filters_item import QueryFiltersItem
  from ..models.query_havings_item import QueryHavingsItem





T = TypeVar("T", bound="Query")



@_attrs_define
class Query:
    """ 
        Attributes:
            id (Union[Unset, str]):
            breakdowns (Union[Unset, list[str]]): the columns by which to break events down into groups
            calculations (Union[Unset, list['QueryCalculationsItem']]): the calculations to return as a time series and
                summary table
            filters (Union[Unset, list['QueryFiltersItem']]): the filters with which to restrict the considered events
            filter_combination (Union[Unset, QueryFilterCombination]): set to "OR" to match ANY filter in the filter list
                Default: QueryFilterCombination.AND.
            granularity (Union[Unset, int]): The time resolution of the query's graph, in seconds. Given a query time range
                T, valid values (T/1000...T/1). If left blank, granularity may be set to a sub-second value for queries with
                short time ranges.
            orders (Union[Unset, list['QueryOrdersItem']]): The terms on which to order the query results. Each term must
                appear in either the `breakdowns` field or the `calculations` field.
            limit (Union[Unset, int]): The maximum number of unique groups returned in 'results'. Aggregating many unique
                groups across a large time range is computationally expensive, and too high a limit with too many unique groups
                may cause queries to fail completely. Limiting the results to only the needed values can significantly speed up
                queries.
                The normal allowed maximum value when creating a query is 1_000. When running 'disable_series' queries, this can
                be overridden to be up to 10_000, so the maximum value returned from the API when fetching a query may be up to
                10_000.
                 Default: 100.
            start_time (Union[Unset, int]): Absolute start time of query, in seconds since UNIX epoch. Must be <=
                `end_time`.
                 Default: 1676399428.
            end_time (Union[Unset, int]): Absolute end time of query, in seconds since UNIX epoch. Default: 1676467828.
            time_range (Union[Unset, int]): Time range of query in seconds. Can be used with either `start_time` (seconds
                after `start_time`), `end_time` (seconds before `end_time`), or without either (seconds before now).
                 Default: 7200.
            havings (Union[Unset, list['QueryHavingsItem']]): The Having clause allows you to filter on the results table.
                This operation is distinct from the Where clause, which filters the underlying events. Order By allows you to
                order the results, and Having filters them.
            calculated_fields (Union[Unset, list['QueryCalculatedFieldsItem']]): Computed properties that are calculated by
                a formula.
            compare_time_offset_seconds (Union[Unset, QueryCompareTimeOffsetSeconds]): When set, offsets the query's time
                range by this number of seconds into the past, allowing comparison with historical data from an earlier time
                period. For example, setting this to 86400 (24 hours) will compare current results against data from 24 hours
                ago.
                ##### Note
                  - The offset must be greater than or equal to the query's time range duration.

                ##### Allowed values
                - same time range as query time range
                - `1800` - 30 minutes
                - `3600` - 1 hour
                - `7200` - 2 hours
                - `28800` - 8 hours
                - `86400` - 24 hours
                - `604800` - 7 days
                - `2419200` - 28 days
                - `15724800` - 6 months
     """

    id: Union[Unset, str] = UNSET
    breakdowns: Union[Unset, list[str]] = UNSET
    calculations: Union[Unset, list['QueryCalculationsItem']] = UNSET
    filters: Union[Unset, list['QueryFiltersItem']] = UNSET
    filter_combination: Union[Unset, QueryFilterCombination] = QueryFilterCombination.AND
    granularity: Union[Unset, int] = UNSET
    orders: Union[Unset, list['QueryOrdersItem']] = UNSET
    limit: Union[Unset, int] = 100
    start_time: Union[Unset, int] = 1676399428
    end_time: Union[Unset, int] = 1676467828
    time_range: Union[Unset, int] = 7200
    havings: Union[Unset, list['QueryHavingsItem']] = UNSET
    calculated_fields: Union[Unset, list['QueryCalculatedFieldsItem']] = UNSET
    compare_time_offset_seconds: Union[Unset, QueryCompareTimeOffsetSeconds] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.query_calculated_fields_item import QueryCalculatedFieldsItem
        from ..models.query_calculations_item import QueryCalculationsItem
        from ..models.query_orders_item import QueryOrdersItem
        from ..models.query_filters_item import QueryFiltersItem
        from ..models.query_havings_item import QueryHavingsItem
        id = self.id

        breakdowns: Union[Unset, list[str]] = UNSET
        if not isinstance(self.breakdowns, Unset):
            breakdowns = self.breakdowns



        calculations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.calculations, Unset):
            calculations = []
            for calculations_item_data in self.calculations:
                calculations_item = calculations_item_data.to_dict()
                calculations.append(calculations_item)



        filters: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = []
            for filters_item_data in self.filters:
                filters_item = filters_item_data.to_dict()
                filters.append(filters_item)



        filter_combination: Union[Unset, str] = UNSET
        if not isinstance(self.filter_combination, Unset):
            filter_combination = self.filter_combination.value


        granularity = self.granularity

        orders: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.orders, Unset):
            orders = []
            for orders_item_data in self.orders:
                orders_item = orders_item_data.to_dict()
                orders.append(orders_item)



        limit = self.limit

        start_time = self.start_time

        end_time = self.end_time

        time_range = self.time_range

        havings: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.havings, Unset):
            havings = []
            for havings_item_data in self.havings:
                havings_item = havings_item_data.to_dict()
                havings.append(havings_item)



        calculated_fields: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.calculated_fields, Unset):
            calculated_fields = []
            for calculated_fields_item_data in self.calculated_fields:
                calculated_fields_item = calculated_fields_item_data.to_dict()
                calculated_fields.append(calculated_fields_item)



        compare_time_offset_seconds: Union[Unset, int] = UNSET
        if not isinstance(self.compare_time_offset_seconds, Unset):
            compare_time_offset_seconds = self.compare_time_offset_seconds.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if breakdowns is not UNSET:
            field_dict["breakdowns"] = breakdowns
        if calculations is not UNSET:
            field_dict["calculations"] = calculations
        if filters is not UNSET:
            field_dict["filters"] = filters
        if filter_combination is not UNSET:
            field_dict["filter_combination"] = filter_combination
        if granularity is not UNSET:
            field_dict["granularity"] = granularity
        if orders is not UNSET:
            field_dict["orders"] = orders
        if limit is not UNSET:
            field_dict["limit"] = limit
        if start_time is not UNSET:
            field_dict["start_time"] = start_time
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if time_range is not UNSET:
            field_dict["time_range"] = time_range
        if havings is not UNSET:
            field_dict["havings"] = havings
        if calculated_fields is not UNSET:
            field_dict["calculated_fields"] = calculated_fields
        if compare_time_offset_seconds is not UNSET:
            field_dict["compare_time_offset_seconds"] = compare_time_offset_seconds

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.query_calculated_fields_item import QueryCalculatedFieldsItem
        from ..models.query_calculations_item import QueryCalculationsItem
        from ..models.query_orders_item import QueryOrdersItem
        from ..models.query_filters_item import QueryFiltersItem
        from ..models.query_havings_item import QueryHavingsItem
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        breakdowns = cast(list[str], d.pop("breakdowns", UNSET))


        calculations = []
        _calculations = d.pop("calculations", UNSET)
        for calculations_item_data in (_calculations or []):
            calculations_item = QueryCalculationsItem.from_dict(calculations_item_data)



            calculations.append(calculations_item)


        filters = []
        _filters = d.pop("filters", UNSET)
        for filters_item_data in (_filters or []):
            filters_item = QueryFiltersItem.from_dict(filters_item_data)



            filters.append(filters_item)


        _filter_combination = d.pop("filter_combination", UNSET)
        filter_combination: Union[Unset, QueryFilterCombination]
        if isinstance(_filter_combination,  Unset):
            filter_combination = UNSET
        else:
            filter_combination = QueryFilterCombination(_filter_combination)




        granularity = d.pop("granularity", UNSET)

        orders = []
        _orders = d.pop("orders", UNSET)
        for orders_item_data in (_orders or []):
            orders_item = QueryOrdersItem.from_dict(orders_item_data)



            orders.append(orders_item)


        limit = d.pop("limit", UNSET)

        start_time = d.pop("start_time", UNSET)

        end_time = d.pop("end_time", UNSET)

        time_range = d.pop("time_range", UNSET)

        havings = []
        _havings = d.pop("havings", UNSET)
        for havings_item_data in (_havings or []):
            havings_item = QueryHavingsItem.from_dict(havings_item_data)



            havings.append(havings_item)


        calculated_fields = []
        _calculated_fields = d.pop("calculated_fields", UNSET)
        for calculated_fields_item_data in (_calculated_fields or []):
            calculated_fields_item = QueryCalculatedFieldsItem.from_dict(calculated_fields_item_data)



            calculated_fields.append(calculated_fields_item)


        _compare_time_offset_seconds = d.pop("compare_time_offset_seconds", UNSET)
        compare_time_offset_seconds: Union[Unset, QueryCompareTimeOffsetSeconds]
        if isinstance(_compare_time_offset_seconds,  Unset):
            compare_time_offset_seconds = UNSET
        else:
            compare_time_offset_seconds = QueryCompareTimeOffsetSeconds(_compare_time_offset_seconds)




        query = cls(
            id=id,
            breakdowns=breakdowns,
            calculations=calculations,
            filters=filters,
            filter_combination=filter_combination,
            granularity=granularity,
            orders=orders,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            time_range=time_range,
            havings=havings,
            calculated_fields=calculated_fields,
            compare_time_offset_seconds=compare_time_offset_seconds,
        )


        query.additional_properties = d
        return query

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
