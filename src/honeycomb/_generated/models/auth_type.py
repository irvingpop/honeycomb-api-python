from enum import Enum

class AuthType(str, Enum):
    CONFIGURATION = "configuration"
    INGEST = "ingest"

    def __str__(self) -> str:
        return str(self.value)
