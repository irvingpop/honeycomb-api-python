from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.dataset_settings import DatasetSettings





T = TypeVar("T", bound="Dataset")



@_attrs_define
class Dataset:
    """ Datasets are a collection of events from a specific source or related source.

        Attributes:
            name (str): The name of the dataset. Example: My Dataset!.
            description (Union[Unset, str]): A description for the dataset. Default: ''. Example: A nice description of my
                dataset.
            settings (Union[Unset, DatasetSettings]):
            expand_json_depth (Union[Unset, int]): The maximum unpacking depth of nested JSON fields. Default: 0. Example:
                3.
            slug (Union[Unset, str]): The 'slug' of the dataset to be used in URLs. Example: my-dataset-.
            regular_columns_count (Union[None, Unset, int]): The total number of unique fields for this Dataset. The value
                will be null if the dataset does not contain any fields yet.
                 Example: 100.
            last_written_at (Union[None, Unset, str]): The ISO8601-formatted time when the dataset last received event data.
                The value will be null if no data has been received yet.
                 Example: 2022-07-21T18:39:23Z.
            created_at (Union[Unset, str]): The ISO8601-formatted time when the dataset was created. Example:
                2022-09-22T17:32:11Z.
     """

    name: str
    description: Union[Unset, str] = ''
    settings: Union[Unset, 'DatasetSettings'] = UNSET
    expand_json_depth: Union[Unset, int] = 0
    slug: Union[Unset, str] = UNSET
    regular_columns_count: Union[None, Unset, int] = UNSET
    last_written_at: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_settings import DatasetSettings
        name = self.name

        description = self.description

        settings: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()

        expand_json_depth = self.expand_json_depth

        slug = self.slug

        regular_columns_count: Union[None, Unset, int]
        if isinstance(self.regular_columns_count, Unset):
            regular_columns_count = UNSET
        else:
            regular_columns_count = self.regular_columns_count

        last_written_at: Union[None, Unset, str]
        if isinstance(self.last_written_at, Unset):
            last_written_at = UNSET
        else:
            last_written_at = self.last_written_at

        created_at = self.created_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if settings is not UNSET:
            field_dict["settings"] = settings
        if expand_json_depth is not UNSET:
            field_dict["expand_json_depth"] = expand_json_depth
        if slug is not UNSET:
            field_dict["slug"] = slug
        if regular_columns_count is not UNSET:
            field_dict["regular_columns_count"] = regular_columns_count
        if last_written_at is not UNSET:
            field_dict["last_written_at"] = last_written_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.dataset_settings import DatasetSettings
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description", UNSET)

        _settings = d.pop("settings", UNSET)
        settings: Union[Unset, DatasetSettings]
        if isinstance(_settings,  Unset):
            settings = UNSET
        else:
            settings = DatasetSettings.from_dict(_settings)




        expand_json_depth = d.pop("expand_json_depth", UNSET)

        slug = d.pop("slug", UNSET)

        def _parse_regular_columns_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        regular_columns_count = _parse_regular_columns_count(d.pop("regular_columns_count", UNSET))


        def _parse_last_written_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        last_written_at = _parse_last_written_at(d.pop("last_written_at", UNSET))


        created_at = d.pop("created_at", UNSET)

        dataset = cls(
            name=name,
            description=description,
            settings=settings,
            expand_json_depth=expand_json_depth,
            slug=slug,
            regular_columns_count=regular_columns_count,
            last_written_at=last_written_at,
            created_at=created_at,
        )


        dataset.additional_properties = d
        return dataset

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
