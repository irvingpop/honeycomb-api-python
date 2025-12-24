from enum import Enum

class CreateEventsContentEncoding(str, Enum):
    GZIP = "gzip"
    ZSTD = "zstd"

    def __str__(self) -> str:
        return str(self.value)
