from enum import Enum

class DatasetRelationshipDataType(str, Enum):
    DATASETS = "datasets"

    def __str__(self) -> str:
        return str(self.value)
