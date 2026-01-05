from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.kinesis_event_record import KinesisEventRecord





T = TypeVar("T", bound="KinesisEvent")



@_attrs_define
class KinesisEvent:
    """ 
        Attributes:
            request_id (Union[Unset, str]):
            timestamp (Union[Unset, int]):
            records (Union[Unset, list['KinesisEventRecord']]):
     """

    request_id: Union[Unset, str] = UNSET
    timestamp: Union[Unset, int] = UNSET
    records: Union[Unset, list['KinesisEventRecord']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.kinesis_event_record import KinesisEventRecord
        request_id = self.request_id

        timestamp = self.timestamp

        records: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.records, Unset):
            records = []
            for records_item_data in self.records:
                records_item = records_item_data.to_dict()
                records.append(records_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if request_id is not UNSET:
            field_dict["requestId"] = request_id
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if records is not UNSET:
            field_dict["records"] = records

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.kinesis_event_record import KinesisEventRecord
        d = src_dict.copy()
        request_id = d.pop("requestId", UNSET)

        timestamp = d.pop("timestamp", UNSET)

        records = []
        _records = d.pop("records", UNSET)
        for records_item_data in (_records or []):
            records_item = KinesisEventRecord.from_dict(records_item_data)



            records.append(records_item)


        kinesis_event = cls(
            request_id=request_id,
            timestamp=timestamp,
            records=records,
        )


        kinesis_event.additional_properties = d
        return kinesis_event

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
