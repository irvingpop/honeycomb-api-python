from enum import Enum


class ApiKeyObjectType(str, Enum):
    API_KEYS = "api-keys"

    def __str__(self) -> str:
        return str(self.value)
