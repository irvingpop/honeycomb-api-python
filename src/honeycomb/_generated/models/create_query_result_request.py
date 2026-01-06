from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateQueryResultRequest")



@_attrs_define
class CreateQueryResultRequest:
    """ A Query Result is created with the Query ID.

        Attributes:
            query_id (str): The ID of a query returned from the [Queries endpoint](/api/queries/).
                 Example: mabAMpSPDjH.
            disable_series (Union[Unset, bool]): If `true`, timeseries data will not be returned in the `series` response
                field, and only summarized data will be returned in the `results` response field.
                 Default: False.
            disable_total_by_aggregate (Union[Unset, bool]): If `true`, data representing each aggregate in the query's
                total value will not be returned. Ensure `disable_series` is false to return the timeseries data.
                 Default: True.
            disable_other_by_aggregate (Union[Unset, bool]): If true, the "other_by_aggregate" data is excluded from the
                query result.
                 Default: True.
            limit (Union[Unset, int]): If `disable_series` is `true`, a limit may be optionally given. The limit will
                override the default limit of 1_000 results with a maximum available limit of 10_000. If `disable_series` is
                `false`, this field will be ignored.
     """

    query_id: str
    disable_series: Union[Unset, bool] = False
    disable_total_by_aggregate: Union[Unset, bool] = True
    disable_other_by_aggregate: Union[Unset, bool] = True
    limit: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        query_id = self.query_id

        disable_series = self.disable_series

        disable_total_by_aggregate = self.disable_total_by_aggregate

        disable_other_by_aggregate = self.disable_other_by_aggregate

        limit = self.limit


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "query_id": query_id,
        })
        if disable_series is not UNSET:
            field_dict["disable_series"] = disable_series
        if disable_total_by_aggregate is not UNSET:
            field_dict["disable_total_by_aggregate"] = disable_total_by_aggregate
        if disable_other_by_aggregate is not UNSET:
            field_dict["disable_other_by_aggregate"] = disable_other_by_aggregate
        if limit is not UNSET:
            field_dict["limit"] = limit

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        query_id = d.pop("query_id")

        disable_series = d.pop("disable_series", UNSET)

        disable_total_by_aggregate = d.pop("disable_total_by_aggregate", UNSET)

        disable_other_by_aggregate = d.pop("disable_other_by_aggregate", UNSET)

        limit = d.pop("limit", UNSET)

        create_query_result_request = cls(
            query_id=query_id,
            disable_series=disable_series,
            disable_total_by_aggregate=disable_total_by_aggregate,
            disable_other_by_aggregate=disable_other_by_aggregate,
            limit=limit,
        )


        create_query_result_request.additional_properties = d
        return create_query_result_request

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
