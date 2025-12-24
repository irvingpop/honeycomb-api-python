from enum import Enum

class IngestKeyAttributesKeyType(str, Enum):
    INGEST = "ingest"

    def __str__(self) -> str:
        return str(self.value)
