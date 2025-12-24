from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.query_panel_query_panel_query_style import QueryPanelQueryPanelQueryStyle
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.board_query_visualization_settings import BoardQueryVisualizationSettings





T = TypeVar("T", bound="QueryPanelQueryPanel")



@_attrs_define
class QueryPanelQueryPanel:
    """ 
        Attributes:
            query_id (str): The ID of the Query to display on the board. The Query must be in the same environment as the
                board.
                 Example: abc1234e.
            query_annotation_id (str): The ID of a Query Annotation that provides a name and description for the Query. The
                Query Annotation must apply to the `query_id` or `query` specified.
                 Example: e4c24a35.
            query_style (Union[Unset, QueryPanelQueryPanelQueryStyle]): How the query should be displayed on the board.
                Default: QueryPanelQueryPanelQueryStyle.GRAPH.
            dataset (Union[Unset, str]): The dataset name to which the query is scoped. Empty for environment-wide queries.
                 Example: My Dataset.
            visualization_settings (Union[Unset, BoardQueryVisualizationSettings]): A map of values to control the display
                settings for the Query on the Board. Unspecified boolean values are assumed to be `false`. Unspecified integers
                are assumed to be `0`, unspecified arrays are assumed to be null and unspecified strings are assumed to be
                empty. This is incompatible with the `graph_settings` field.
     """

    query_id: str
    query_annotation_id: str
    query_style: Union[Unset, QueryPanelQueryPanelQueryStyle] = QueryPanelQueryPanelQueryStyle.GRAPH
    dataset: Union[Unset, str] = UNSET
    visualization_settings: Union[Unset, 'BoardQueryVisualizationSettings'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.board_query_visualization_settings import BoardQueryVisualizationSettings
        query_id = self.query_id

        query_annotation_id = self.query_annotation_id

        query_style: Union[Unset, str] = UNSET
        if not isinstance(self.query_style, Unset):
            query_style = self.query_style.value


        dataset = self.dataset

        visualization_settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.visualization_settings, Unset):
            visualization_settings = self.visualization_settings.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "query_id": query_id,
            "query_annotation_id": query_annotation_id,
        })
        if query_style is not UNSET:
            field_dict["query_style"] = query_style
        if dataset is not UNSET:
            field_dict["dataset"] = dataset
        if visualization_settings is not UNSET:
            field_dict["visualization_settings"] = visualization_settings

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.board_query_visualization_settings import BoardQueryVisualizationSettings
        d = src_dict.copy()
        query_id = d.pop("query_id")

        query_annotation_id = d.pop("query_annotation_id")

        _query_style = d.pop("query_style", UNSET)
        query_style: Union[Unset, QueryPanelQueryPanelQueryStyle]
        if isinstance(_query_style,  Unset):
            query_style = UNSET
        else:
            query_style = QueryPanelQueryPanelQueryStyle(_query_style)




        dataset = d.pop("dataset", UNSET)

        _visualization_settings = d.pop("visualization_settings", UNSET)
        visualization_settings: Union[Unset, BoardQueryVisualizationSettings]
        if isinstance(_visualization_settings,  Unset):
            visualization_settings = UNSET
        else:
            visualization_settings = BoardQueryVisualizationSettings.from_dict(_visualization_settings)




        query_panel_query_panel = cls(
            query_id=query_id,
            query_annotation_id=query_annotation_id,
            query_style=query_style,
            dataset=dataset,
            visualization_settings=visualization_settings,
        )


        query_panel_query_panel.additional_properties = d
        return query_panel_query_panel

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
