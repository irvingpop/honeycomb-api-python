from enum import Enum

class IngestKeyTypeKeyType(str, Enum):
    INGEST = "ingest"

    def __str__(self) -> str:
        return str(self.value)
