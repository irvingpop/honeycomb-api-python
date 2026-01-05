from enum import Enum


class ConfigurationKeyRequestType(str, Enum):
    API_KEYS = "api-keys"

    def __str__(self) -> str:
        return str(self.value)
