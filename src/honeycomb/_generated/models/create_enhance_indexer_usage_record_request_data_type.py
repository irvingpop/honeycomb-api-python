from enum import Enum

class CreateEnhanceIndexerUsageRecordRequestDataType(str, Enum):
    ENHANCE_INDEXER_USAGE = "enhance_indexer_usage"

    def __str__(self) -> str:
        return str(self.value)
