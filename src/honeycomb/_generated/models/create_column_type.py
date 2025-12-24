from enum import Enum

class CreateColumnType(str, Enum):
    BOOLEAN = "boolean"
    FLOAT = "float"
    HISTOGRAM = "histogram"
    INTEGER = "integer"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
