from enum import Enum

class ListApiKeysFiltertype(str, Enum):
    CONFIGURATION = "configuration"
    INGEST = "ingest"

    def __str__(self) -> str:
        return str(self.value)
