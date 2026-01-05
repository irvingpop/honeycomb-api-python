from enum import Enum


class CreatePipelineHealthRecordRequestDataType(str, Enum):
    PIPELINE_USAGE = "pipeline_usage"

    def __str__(self) -> str:
        return str(self.value)
