from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.board_layout_generation import BoardLayoutGeneration
from ..models.board_type import BoardType
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.board_links import BoardLinks
  from ..models.preset_filter import PresetFilter
  from ..models.query_panel import QueryPanel
  from ..models.slo_panel import SLOPanel
  from ..models.tag import Tag
  from ..models.text_panel import TextPanel





T = TypeVar("T", bound="Board")



@_attrs_define
class Board:
    """ 
        Attributes:
            name (str): The name of the Board. Example: My Board.
            type_ (BoardType): The type of the board. Only flexible boards are supported.
            description (Union[Unset, str]): A description of the Board. Example: A board created via the API.
            links (Union[Unset, BoardLinks]):
            id (Union[Unset, str]): Unique identifier (ID), returned in response bodies. Example: 2NeeaE9bBLd.
            panels (Union[Unset, list[Union['QueryPanel', 'SLOPanel', 'TextPanel']]]):
            layout_generation (Union[Unset, BoardLayoutGeneration]): The layout generation mode for the board. When set to
                "auto", the board will be automatically laid out based on the panels. When set to "manual", the board will be
                laid out manually by the user.
                 Default: BoardLayoutGeneration.MANUAL.
            tags (Union[Unset, list['Tag']]): A list of key-value pairs to help identify the Trigger. Example: [{'key':
                'team', 'value': 'blue'}].
            preset_filters (Union[Unset, list['PresetFilter']]): A list of preset filters to apply to the board. For
                backwards compatibility, if no preset filters are provided, the existing preset filters will be preserved. If an
                empty array is provided, all preset filters will be deleted. Example: [{'column': 'app.Service', 'alias':
                'Service'}].
     """

    name: str
    type_: BoardType
    description: Union[Unset, str] = UNSET
    links: Union[Unset, 'BoardLinks'] = UNSET
    id: Union[Unset, str] = UNSET
    panels: Union[Unset, list[Union['QueryPanel', 'SLOPanel', 'TextPanel']]] = UNSET
    layout_generation: Union[Unset, BoardLayoutGeneration] = BoardLayoutGeneration.MANUAL
    tags: Union[Unset, list['Tag']] = UNSET
    preset_filters: Union[Unset, list['PresetFilter']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.board_links import BoardLinks
        from ..models.preset_filter import PresetFilter
        from ..models.query_panel import QueryPanel
        from ..models.slo_panel import SLOPanel
        from ..models.tag import Tag
        from ..models.text_panel import TextPanel
        name = self.name

        type_ = self.type_.value

        description = self.description

        links: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.links, Unset):
            links = self.links.to_dict()

        id = self.id

        panels: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.panels, Unset):
            panels = []
            for panels_item_data in self.panels:
                panels_item: dict[str, Any]
                if isinstance(panels_item_data, QueryPanel):
                    panels_item = panels_item_data.to_dict()
                elif isinstance(panels_item_data, SLOPanel):
                    panels_item = panels_item_data.to_dict()
                else:
                    panels_item = panels_item_data.to_dict()

                panels.append(panels_item)



        layout_generation: Union[Unset, str] = UNSET
        if not isinstance(self.layout_generation, Unset):
            layout_generation = self.layout_generation.value


        tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)



        preset_filters: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.preset_filters, Unset):
            preset_filters = []
            for preset_filters_item_data in self.preset_filters:
                preset_filters_item = preset_filters_item_data.to_dict()
                preset_filters.append(preset_filters_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "type": type_,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if links is not UNSET:
            field_dict["links"] = links
        if id is not UNSET:
            field_dict["id"] = id
        if panels is not UNSET:
            field_dict["panels"] = panels
        if layout_generation is not UNSET:
            field_dict["layout_generation"] = layout_generation
        if tags is not UNSET:
            field_dict["tags"] = tags
        if preset_filters is not UNSET:
            field_dict["preset_filters"] = preset_filters

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.board_links import BoardLinks
        from ..models.preset_filter import PresetFilter
        from ..models.query_panel import QueryPanel
        from ..models.slo_panel import SLOPanel
        from ..models.tag import Tag
        from ..models.text_panel import TextPanel
        d = src_dict.copy()
        name = d.pop("name")

        type_ = BoardType(d.pop("type"))




        description = d.pop("description", UNSET)

        _links = d.pop("links", UNSET)
        links: Union[Unset, BoardLinks]
        if isinstance(_links,  Unset):
            links = UNSET
        else:
            links = BoardLinks.from_dict(_links)




        id = d.pop("id", UNSET)

        panels = []
        _panels = d.pop("panels", UNSET)
        for panels_item_data in (_panels or []):
            def _parse_panels_item(data: object) -> Union['QueryPanel', 'SLOPanel', 'TextPanel']:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_board_panel_type_0 = QueryPanel.from_dict(data)



                    return componentsschemas_board_panel_type_0
                except: # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_board_panel_type_1 = SLOPanel.from_dict(data)



                    return componentsschemas_board_panel_type_1
                except: # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_board_panel_type_2 = TextPanel.from_dict(data)



                return componentsschemas_board_panel_type_2

            panels_item = _parse_panels_item(panels_item_data)

            panels.append(panels_item)


        _layout_generation = d.pop("layout_generation", UNSET)
        layout_generation: Union[Unset, BoardLayoutGeneration]
        if isinstance(_layout_generation,  Unset):
            layout_generation = UNSET
        else:
            layout_generation = BoardLayoutGeneration(_layout_generation)




        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in (_tags or []):
            tags_item = Tag.from_dict(tags_item_data)



            tags.append(tags_item)


        preset_filters = []
        _preset_filters = d.pop("preset_filters", UNSET)
        for preset_filters_item_data in (_preset_filters or []):
            preset_filters_item = PresetFilter.from_dict(preset_filters_item_data)



            preset_filters.append(preset_filters_item)


        board = cls(
            name=name,
            type_=type_,
            description=description,
            links=links,
            id=id,
            panels=panels,
            layout_generation=layout_generation,
            tags=tags,
            preset_filters=preset_filters,
        )


        board.additional_properties = d
        return board

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
