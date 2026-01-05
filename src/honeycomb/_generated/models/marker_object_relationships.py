from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.environment_relationship import EnvironmentRelationship
  from ..models.marker_object_relationships_dataset import \
      MarkerObjectRelationshipsDataset





T = TypeVar("T", bound="MarkerObjectRelationships")



@_attrs_define
class MarkerObjectRelationships:
    """ 
        Attributes:
            environment (Union[Unset, EnvironmentRelationship]): The Environment this object is associated with.
            dataset (Union[Unset, MarkerObjectRelationshipsDataset]): Optional dataset relationship. If null, this is an
                environment-wide marker.
     """

    environment: Union[Unset, 'EnvironmentRelationship'] = UNSET
    dataset: Union[Unset, 'MarkerObjectRelationshipsDataset'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.environment_relationship import EnvironmentRelationship
        from ..models.marker_object_relationships_dataset import \
            MarkerObjectRelationshipsDataset
        environment: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.environment, Unset):
            environment = self.environment.to_dict()

        dataset: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.dataset, Unset):
            dataset = self.dataset.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if environment is not UNSET:
            field_dict["environment"] = environment
        if dataset is not UNSET:
            field_dict["dataset"] = dataset

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.environment_relationship import EnvironmentRelationship
        from ..models.marker_object_relationships_dataset import \
            MarkerObjectRelationshipsDataset
        d = src_dict.copy()
        _environment = d.pop("environment", UNSET)
        environment: Union[Unset, EnvironmentRelationship]
        if isinstance(_environment,  Unset):
            environment = UNSET
        else:
            environment = EnvironmentRelationship.from_dict(_environment)




        _dataset = d.pop("dataset", UNSET)
        dataset: Union[Unset, MarkerObjectRelationshipsDataset]
        if isinstance(_dataset,  Unset):
            dataset = UNSET
        else:
            dataset = MarkerObjectRelationshipsDataset.from_dict(_dataset)




        marker_object_relationships = cls(
            environment=environment,
            dataset=dataset,
        )


        marker_object_relationships.additional_properties = d
        return marker_object_relationships

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
