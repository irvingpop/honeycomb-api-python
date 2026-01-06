from enum import Enum


class IngestKeyRequestType(str, Enum):
    API_KEYS = "api-keys"

    def __str__(self) -> str:
        return str(self.value)
