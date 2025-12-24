from enum import Enum

class BoardType(str, Enum):
    FLEXIBLE = "flexible"

    def __str__(self) -> str:
        return str(self.value)
