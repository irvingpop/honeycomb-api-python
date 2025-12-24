from enum import Enum

class BaseTriggerAlertType(str, Enum):
    ON_CHANGE = "on_change"
    ON_TRUE = "on_true"

    def __str__(self) -> str:
        return str(self.value)
