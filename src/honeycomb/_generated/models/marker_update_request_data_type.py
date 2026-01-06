from enum import Enum


class MarkerUpdateRequestDataType(str, Enum):
    MARKERS = "markers"

    def __str__(self) -> str:
        return str(self.value)
