from typing import (TYPE_CHECKING, Any, BinaryIO, Optional, TextIO, TypeVar,
                    Union, cast)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
  from ..models.create_enhance_indexer_usage_record_request_data_attributes_usage_data import \
      CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageData





T = TypeVar("T", bound="CreateEnhanceIndexerUsageRecordRequestDataAttributes")



@_attrs_define
class CreateEnhanceIndexerUsageRecordRequestDataAttributes:
    """ 
        Attributes:
            s_3_bucket (str): The S3 bucket name
            usage_data (CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageData):
            s_3_file_prefix (Union[Unset, str]): The S3 file prefix
     """

    s_3_bucket: str
    usage_data: 'CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageData'
    s_3_file_prefix: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> dict[str, Any]:
        from ..models.create_enhance_indexer_usage_record_request_data_attributes_usage_data import \
            CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageData
        s_3_bucket = self.s_3_bucket

        usage_data = self.usage_data.to_dict()

        s_3_file_prefix = self.s_3_file_prefix


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "s3Bucket": s_3_bucket,
            "usageData": usage_data,
        })
        if s_3_file_prefix is not UNSET:
            field_dict["s3FilePrefix"] = s_3_file_prefix

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.create_enhance_indexer_usage_record_request_data_attributes_usage_data import \
            CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageData
        d = src_dict.copy()
        s_3_bucket = d.pop("s3Bucket")

        usage_data = CreateEnhanceIndexerUsageRecordRequestDataAttributesUsageData.from_dict(d.pop("usageData"))




        s_3_file_prefix = d.pop("s3FilePrefix", UNSET)

        create_enhance_indexer_usage_record_request_data_attributes = cls(
            s_3_bucket=s_3_bucket,
            usage_data=usage_data,
            s_3_file_prefix=s_3_file_prefix,
        )


        create_enhance_indexer_usage_record_request_data_attributes.additional_properties = d
        return create_enhance_indexer_usage_record_request_data_attributes

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
