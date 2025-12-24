from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.dataset_relationship import DatasetRelationship
  from ..models.environment_relationship import EnvironmentRelationship





T = TypeVar("T", bound="MarkerUpdateRequestDataRelationships")



@_attrs_define
class MarkerUpdateRequestDataRelationships:
    """ 
        Attributes:
            environment (EnvironmentRelationship): The Environment this object is associated with.
            dataset (DatasetRelationship): The Dataset this object is associated with.
     """

    environment: 'EnvironmentRelationship'
    dataset: 'DatasetRelationship'
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_relationship import DatasetRelationship
        from ..models.environment_relationship import EnvironmentRelationship
        environment = self.environment.to_dict()

        dataset = self.dataset.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "environment": environment,
            "dataset": dataset,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.dataset_relationship import DatasetRelationship
        from ..models.environment_relationship import EnvironmentRelationship
        d = src_dict.copy()
        environment = EnvironmentRelationship.from_dict(d.pop("environment"))




        dataset = DatasetRelationship.from_dict(d.pop("dataset"))




        marker_update_request_data_relationships = cls(
            environment=environment,
            dataset=dataset,
        )


        marker_update_request_data_relationships.additional_properties = d
        return marker_update_request_data_relationships

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
