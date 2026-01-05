from enum import Enum


class DatasetDefinitionType1ColumnType(str, Enum):
    COLUMN = "column"
    DERIVED_COLUMN = "derived_column"

    def __str__(self) -> str:
        return str(self.value)
