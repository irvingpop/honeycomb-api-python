from enum import Enum

class AuthV2ResponseDataAttributesKeyType(str, Enum):
    MANAGEMENT = "management"

    def __str__(self) -> str:
        return str(self.value)
