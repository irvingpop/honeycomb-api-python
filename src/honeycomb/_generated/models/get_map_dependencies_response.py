from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_map_dependencies_response_status import \
    GetMapDependenciesResponseStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.map_dependency import MapDependency
  from ..models.pagination_links import PaginationLinks





T = TypeVar("T", bound="GetMapDependenciesResponse")



@_attrs_define
class GetMapDependenciesResponse:
    """ Response containing map dependencies data.

        Attributes:
            request_id (Union[Unset, str]): Unique identifier for the Map Dependency Request.
                 Example: abc123.
            status (Union[Unset, GetMapDependenciesResponseStatus]): Status of the Map Dependency Request.
                 Example: ready.
            dependencies (Union[None, Unset, list['MapDependency']]): Array of service dependencies. Null when status is
                "pending" or "error".
            links (Union[Unset, PaginationLinks]): Links to iterate through the pages of results.
     """

    request_id: Union[Unset, str] = UNSET
    status: Union[Unset, GetMapDependenciesResponseStatus] = UNSET
    dependencies: Union[None, Unset, list['MapDependency']] = UNSET
    links: Union[Unset, 'PaginationLinks'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.map_dependency import MapDependency
        from ..models.pagination_links import PaginationLinks
        request_id = self.request_id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        dependencies: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.dependencies, Unset):
            dependencies = UNSET
        elif isinstance(self.dependencies, list):
            dependencies = []
            for dependencies_type_0_item_data in self.dependencies:
                dependencies_type_0_item = dependencies_type_0_item_data.to_dict()
                dependencies.append(dependencies_type_0_item)


        else:
            dependencies = self.dependencies

        links: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.links, Unset):
            links = self.links.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if request_id is not UNSET:
            field_dict["request_id"] = request_id
        if status is not UNSET:
            field_dict["status"] = status
        if dependencies is not UNSET:
            field_dict["dependencies"] = dependencies
        if links is not UNSET:
            field_dict["links"] = links

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.map_dependency import MapDependency
        from ..models.pagination_links import PaginationLinks
        d = src_dict.copy()
        request_id = d.pop("request_id", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, GetMapDependenciesResponseStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = GetMapDependenciesResponseStatus(_status)




        def _parse_dependencies(data: object) -> Union[None, Unset, list['MapDependency']]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                dependencies_type_0 = []
                _dependencies_type_0 = data
                for dependencies_type_0_item_data in (_dependencies_type_0):
                    dependencies_type_0_item = MapDependency.from_dict(dependencies_type_0_item_data)



                    dependencies_type_0.append(dependencies_type_0_item)

                return dependencies_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, list['MapDependency']], data)

        dependencies = _parse_dependencies(d.pop("dependencies", UNSET))


        _links = d.pop("links", UNSET)
        links: Union[Unset, PaginationLinks]
        if isinstance(_links,  Unset):
            links = UNSET
        else:
            links = PaginationLinks.from_dict(_links)




        get_map_dependencies_response = cls(
            request_id=request_id,
            status=status,
            dependencies=dependencies,
            links=links,
        )


        get_map_dependencies_response.additional_properties = d
        return get_map_dependencies_response

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
