from enum import Enum


class EnvironmentAttributesColorType1(str, Enum):
    CLASSIC = "classic"

    def __str__(self) -> str:
        return str(self.value)
