from enum import IntEnum


class BaseTriggerBaselineDetailsType0OffsetMinutes(IntEnum):
    VALUE_60 = 60
    VALUE_1440 = 1440
    VALUE_10080 = 10080
    VALUE_40320 = 40320

    def __str__(self) -> str:
        return str(self.value)
