import datetime
from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.slo_sli import SLOSli
  from ..models.tag import Tag





T = TypeVar("T", bound="SLO")



@_attrs_define
class SLO:
    """ 
        Attributes:
            name (str): The name of the SLO. Example: My SLO.
            sli (SLOSli): Reference to the [Calculated Field](/api/calculated-fields/) used as the indicator of event
                success. Example: {'alias': 'error_sli'}.
            time_period_days (int): The time period, in days, over which the SLO will be evaluated. Example: 30.
            target_per_million (int): The number of events out of one million (1,000,000) that you expected qualified events
                to succeed. Example: 990000.
            id (Union[Unset, str]):
            description (Union[Unset, str]): A nice description of the SLO's intent and context. Example: SLO to ensure
                requests succeed and are fast.
            tags (Union[Unset, list['Tag']]): A list of key-value pairs to help identify the SLO. Example: [{'key': 'team',
                'value': 'blue'}].
            reset_at (Union[None, Unset, datetime.datetime]): The ISO8601-formatted time the SLO was last reset. The value
                will be `null` if the SLO has not yet been reset. Example: 2022-011-11T09:53:04Z.
            created_at (Union[Unset, datetime.datetime]): The ISO8601-formatted time when the SLO was created. Example:
                2022-09-22T17:32:11Z.
            updated_at (Union[Unset, datetime.datetime]): The ISO8601-formatted time when the SLO was updated. Example:
                2022-10-31T15:08:11Z.
            dataset_slugs (Union[Unset, list[str]]): The dataset(s) the SLO will be evaluated against. Required if using
                `__all__` in the path. Example: ['mydataset1', 'mydataset2'].
     """

    name: str
    sli: 'SLOSli'
    time_period_days: int
    target_per_million: int
    id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    tags: Union[Unset, list['Tag']] = UNSET
    reset_at: Union[None, Unset, datetime.datetime] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    dataset_slugs: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.slo_sli import SLOSli
        from ..models.tag import Tag
        name = self.name

        sli = self.sli.to_dict()

        time_period_days = self.time_period_days

        target_per_million = self.target_per_million

        id = self.id

        description = self.description

        tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)



        reset_at: Union[None, Unset, str]
        if isinstance(self.reset_at, Unset):
            reset_at = UNSET
        elif isinstance(self.reset_at, datetime.datetime):
            reset_at = self.reset_at.isoformat()
        else:
            reset_at = self.reset_at

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        dataset_slugs: Union[Unset, list[str]] = UNSET
        if not isinstance(self.dataset_slugs, Unset):
            dataset_slugs = self.dataset_slugs




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "sli": sli,
            "time_period_days": time_period_days,
            "target_per_million": target_per_million,
        })
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if tags is not UNSET:
            field_dict["tags"] = tags
        if reset_at is not UNSET:
            field_dict["reset_at"] = reset_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if dataset_slugs is not UNSET:
            field_dict["dataset_slugs"] = dataset_slugs

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.slo_sli import SLOSli
        from ..models.tag import Tag
        d = src_dict.copy()
        name = d.pop("name")

        sli = SLOSli.from_dict(d.pop("sli"))




        time_period_days = d.pop("time_period_days")

        target_per_million = d.pop("target_per_million")

        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in (_tags or []):
            tags_item = Tag.from_dict(tags_item_data)



            tags.append(tags_item)


        def _parse_reset_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reset_at_type_1 = isoparse(data)



                return reset_at_type_1
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        reset_at = _parse_reset_at(d.pop("reset_at", UNSET))


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




        dataset_slugs = cast(list[str], d.pop("dataset_slugs", UNSET))


        slo = cls(
            name=name,
            sli=sli,
            time_period_days=time_period_days,
            target_per_million=target_per_million,
            id=id,
            description=description,
            tags=tags,
            reset_at=reset_at,
            created_at=created_at,
            updated_at=updated_at,
            dataset_slugs=dataset_slugs,
        )


        slo.additional_properties = d
        return slo

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
