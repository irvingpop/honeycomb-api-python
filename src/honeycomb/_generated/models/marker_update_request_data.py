from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.marker_update_request_data_type import MarkerUpdateRequestDataType
from typing import cast

if TYPE_CHECKING:
  from ..models.marker_update_request_data_attributes import MarkerUpdateRequestDataAttributes
  from ..models.marker_update_request_data_relationships import MarkerUpdateRequestDataRelationships





T = TypeVar("T", bound="MarkerUpdateRequestData")



@_attrs_define
class MarkerUpdateRequestData:
    """ 
        Attributes:
            type_ (MarkerUpdateRequestDataType):
            attributes (MarkerUpdateRequestDataAttributes):
            relationships (MarkerUpdateRequestDataRelationships):
     """

    type_: MarkerUpdateRequestDataType
    attributes: 'MarkerUpdateRequestDataAttributes'
    relationships: 'MarkerUpdateRequestDataRelationships'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.marker_update_request_data_attributes import MarkerUpdateRequestDataAttributes
        from ..models.marker_update_request_data_relationships import MarkerUpdateRequestDataRelationships
        type_ = self.type_.value

        attributes = self.attributes.to_dict()

        relationships = self.relationships.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "type": type_,
            "attributes": attributes,
            "relationships": relationships,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.marker_update_request_data_attributes import MarkerUpdateRequestDataAttributes
        from ..models.marker_update_request_data_relationships import MarkerUpdateRequestDataRelationships
        d = src_dict.copy()
        type_ = MarkerUpdateRequestDataType(d.pop("type"))




        attributes = MarkerUpdateRequestDataAttributes.from_dict(d.pop("attributes"))




        relationships = MarkerUpdateRequestDataRelationships.from_dict(d.pop("relationships"))




        marker_update_request_data = cls(
            type_=type_,
            attributes=attributes,
            relationships=relationships,
        )


        marker_update_request_data.additional_properties = d
        return marker_update_request_data

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
