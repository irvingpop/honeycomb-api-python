from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.marker_object_type import MarkerObjectType
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.marker_object_relationships import MarkerObjectRelationships
  from ..models.marker_object_attributes import MarkerObjectAttributes
  from ..models.marker_object_links import MarkerObjectLinks





T = TypeVar("T", bound="MarkerObject")



@_attrs_define
class MarkerObject:
    """ 
        Attributes:
            id (str): The unique identifier of the Marker Example: d1c84ec0.
            type_ (MarkerObjectType):
            attributes (MarkerObjectAttributes):
            links (MarkerObjectLinks):
            relationships (Union[Unset, MarkerObjectRelationships]):
     """

    id: str
    type_: MarkerObjectType
    attributes: 'MarkerObjectAttributes'
    links: 'MarkerObjectLinks'
    relationships: Union[Unset, 'MarkerObjectRelationships'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.marker_object_relationships import MarkerObjectRelationships
        from ..models.marker_object_attributes import MarkerObjectAttributes
        from ..models.marker_object_links import MarkerObjectLinks
        id = self.id

        type_ = self.type_.value

        attributes = self.attributes.to_dict()

        links = self.links.to_dict()

        relationships: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.relationships, Unset):
            relationships = self.relationships.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "type": type_,
            "attributes": attributes,
            "links": links,
        })
        if relationships is not UNSET:
            field_dict["relationships"] = relationships

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.marker_object_relationships import MarkerObjectRelationships
        from ..models.marker_object_attributes import MarkerObjectAttributes
        from ..models.marker_object_links import MarkerObjectLinks
        d = src_dict.copy()
        id = d.pop("id")

        type_ = MarkerObjectType(d.pop("type"))




        attributes = MarkerObjectAttributes.from_dict(d.pop("attributes"))




        links = MarkerObjectLinks.from_dict(d.pop("links"))




        _relationships = d.pop("relationships", UNSET)
        relationships: Union[Unset, MarkerObjectRelationships]
        if isinstance(_relationships,  Unset):
            relationships = UNSET
        else:
            relationships = MarkerObjectRelationships.from_dict(_relationships)




        marker_object = cls(
            id=id,
            type_=type_,
            attributes=attributes,
            links=links,
            relationships=relationships,
        )


        marker_object.additional_properties = d
        return marker_object

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
