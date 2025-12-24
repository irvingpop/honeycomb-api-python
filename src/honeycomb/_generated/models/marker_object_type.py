from enum import Enum

class MarkerObjectType(str, Enum):
    MARKERS = "markers"

    def __str__(self) -> str:
        return str(self.value)
