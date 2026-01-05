from enum import Enum


class BaseTriggerBaselineDetailsType0Type(str, Enum):
    PERCENTAGE = "percentage"
    VALUE = "value"

    def __str__(self) -> str:
        return str(self.value)
