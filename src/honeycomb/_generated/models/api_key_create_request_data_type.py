from enum import Enum

class ApiKeyCreateRequestDataType(str, Enum):
    API_KEYS = "api-keys"

    def __str__(self) -> str:
        return str(self.value)
