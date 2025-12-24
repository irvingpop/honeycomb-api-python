from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.board_query_visualization_settings_charts_item import BoardQueryVisualizationSettingsChartsItem





T = TypeVar("T", bound="BoardQueryVisualizationSettings")



@_attrs_define
class BoardQueryVisualizationSettings:
    """ A map of values to control the display settings for the Query on the Board. Unspecified boolean values are assumed
    to be `false`. Unspecified integers are assumed to be `0`, unspecified arrays are assumed to be null and unspecified
    strings are assumed to be empty. This is incompatible with the `graph_settings` field.

        Attributes:
            hide_compare (Union[Unset, bool]):  Default: False.
            hide_hovers (Union[Unset, bool]):  Default: False.
            hide_markers (Union[Unset, bool]):  Default: False.
            utc_xaxis (Union[Unset, bool]):  Default: False.
            overlaid_charts (Union[Unset, bool]):  Default: False.
            charts (Union[Unset, list['BoardQueryVisualizationSettingsChartsItem']]):
     """

    hide_compare: Union[Unset, bool] = False
    hide_hovers: Union[Unset, bool] = False
    hide_markers: Union[Unset, bool] = False
    utc_xaxis: Union[Unset, bool] = False
    overlaid_charts: Union[Unset, bool] = False
    charts: Union[Unset, list['BoardQueryVisualizationSettingsChartsItem']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.board_query_visualization_settings_charts_item import BoardQueryVisualizationSettingsChartsItem
        hide_compare = self.hide_compare

        hide_hovers = self.hide_hovers

        hide_markers = self.hide_markers

        utc_xaxis = self.utc_xaxis

        overlaid_charts = self.overlaid_charts

        charts: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.charts, Unset):
            charts = []
            for charts_item_data in self.charts:
                charts_item = charts_item_data.to_dict()
                charts.append(charts_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if hide_compare is not UNSET:
            field_dict["hide_compare"] = hide_compare
        if hide_hovers is not UNSET:
            field_dict["hide_hovers"] = hide_hovers
        if hide_markers is not UNSET:
            field_dict["hide_markers"] = hide_markers
        if utc_xaxis is not UNSET:
            field_dict["utc_xaxis"] = utc_xaxis
        if overlaid_charts is not UNSET:
            field_dict["overlaid_charts"] = overlaid_charts
        if charts is not UNSET:
            field_dict["charts"] = charts

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.board_query_visualization_settings_charts_item import BoardQueryVisualizationSettingsChartsItem
        d = src_dict.copy()
        hide_compare = d.pop("hide_compare", UNSET)

        hide_hovers = d.pop("hide_hovers", UNSET)

        hide_markers = d.pop("hide_markers", UNSET)

        utc_xaxis = d.pop("utc_xaxis", UNSET)

        overlaid_charts = d.pop("overlaid_charts", UNSET)

        charts = []
        _charts = d.pop("charts", UNSET)
        for charts_item_data in (_charts or []):
            charts_item = BoardQueryVisualizationSettingsChartsItem.from_dict(charts_item_data)



            charts.append(charts_item)


        board_query_visualization_settings = cls(
            hide_compare=hide_compare,
            hide_hovers=hide_hovers,
            hide_markers=hide_markers,
            utc_xaxis=utc_xaxis,
            overlaid_charts=overlaid_charts,
            charts=charts,
        )


        board_query_visualization_settings.additional_properties = d
        return board_query_visualization_settings

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
