from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.board_query_visualization_settings_charts_item_chart_type import BoardQueryVisualizationSettingsChartsItemChartType
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="BoardQueryVisualizationSettingsChartsItem")



@_attrs_define
class BoardQueryVisualizationSettingsChartsItem:
    """ 
        Attributes:
            chart_index (Union[Unset, int]):  Default: 0.
            chart_type (Union[Unset, BoardQueryVisualizationSettingsChartsItemChartType]):  Default:
                BoardQueryVisualizationSettingsChartsItemChartType.DEFAULT.
            log_scale (Union[Unset, bool]):  Default: False.
            omit_missing_values (Union[Unset, bool]):  Default: False.
     """

    chart_index: Union[Unset, int] = 0
    chart_type: Union[Unset, BoardQueryVisualizationSettingsChartsItemChartType] = BoardQueryVisualizationSettingsChartsItemChartType.DEFAULT
    log_scale: Union[Unset, bool] = False
    omit_missing_values: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        chart_index = self.chart_index

        chart_type: Union[Unset, str] = UNSET
        if not isinstance(self.chart_type, Unset):
            chart_type = self.chart_type.value


        log_scale = self.log_scale

        omit_missing_values = self.omit_missing_values


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if chart_index is not UNSET:
            field_dict["chart_index"] = chart_index
        if chart_type is not UNSET:
            field_dict["chart_type"] = chart_type
        if log_scale is not UNSET:
            field_dict["log_scale"] = log_scale
        if omit_missing_values is not UNSET:
            field_dict["omit_missing_values"] = omit_missing_values

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        chart_index = d.pop("chart_index", UNSET)

        _chart_type = d.pop("chart_type", UNSET)
        chart_type: Union[Unset, BoardQueryVisualizationSettingsChartsItemChartType]
        if isinstance(_chart_type,  Unset):
            chart_type = UNSET
        else:
            chart_type = BoardQueryVisualizationSettingsChartsItemChartType(_chart_type)




        log_scale = d.pop("log_scale", UNSET)

        omit_missing_values = d.pop("omit_missing_values", UNSET)

        board_query_visualization_settings_charts_item = cls(
            chart_index=chart_index,
            chart_type=chart_type,
            log_scale=log_scale,
            omit_missing_values=omit_missing_values,
        )


        board_query_visualization_settings_charts_item.additional_properties = d
        return board_query_visualization_settings_charts_item

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
