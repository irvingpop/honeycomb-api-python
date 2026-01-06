import datetime
from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.query_annotation_source import QueryAnnotationSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="QueryAnnotation")



@_attrs_define
class QueryAnnotation:
    """ A Query Annotation consists of a name and description associated with a query to add context when collaborating.

        Attributes:
            name (str): A name for the Query. Example: My Named Query.
            query_id (str): The ID of the Query that the annotation describes. **Note**: Once created, it is NOT possible to
                change the query ID associated with an annotation. It is possible to have multiple annotations associated with a
                Query.
                 Example: mabAMpSPDjH.
            description (Union[Unset, str]): A description of the Query. Example: A nice description of My Named Query.
            id (Union[Unset, str]): The unique identifier (ID) of a Query Annotation. Example: sGUnkBHgRFN.
            created_at (Union[Unset, datetime.datetime]): ISO8601 formatted time when the Query Annotation was created.
                Example: 2022-10-26T21:36:04Z.
            updated_at (Union[Unset, datetime.datetime]): ISO8601 formatted time when the Query Annotation was updated.
                Example: 2022-12-04T08:14:26Z.
            source (Union[Unset, QueryAnnotationSource]): The source of the Query Annotation. Example: query.
     """

    name: str
    query_id: str
    description: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    source: Union[Unset, QueryAnnotationSource] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        name = self.name

        query_id = self.query_id

        description = self.description

        id = self.id

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "query_id": query_id,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        query_id = d.pop("query_id")

        description = d.pop("description", UNSET)

        id = d.pop("id", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at,  Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)




        _source = d.pop("source", UNSET)
        source: Union[Unset, QueryAnnotationSource]
        if isinstance(_source,  Unset):
            source = UNSET
        else:
            source = QueryAnnotationSource(_source)




        query_annotation = cls(
            name=name,
            query_id=query_id,
            description=description,
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            source=source,
        )


        query_annotation.additional_properties = d
        return query_annotation

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
