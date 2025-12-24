from enum import Enum

class MarkerCreateRequestDataType(str, Enum):
    MARKERS = "markers"

    def __str__(self) -> str:
        return str(self.value)
