from enum import Enum


class ConfigurationKeyAttributesKeyType(str, Enum):
    CONFIGURATION = "configuration"

    def __str__(self) -> str:
        return str(self.value)
