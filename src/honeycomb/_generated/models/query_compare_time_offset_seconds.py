from enum import IntEnum


class QueryCompareTimeOffsetSeconds(IntEnum):
    VALUE_1800 = 1800
    VALUE_3600 = 3600
    VALUE_7200 = 7200
    VALUE_28800 = 28800
    VALUE_86400 = 86400
    VALUE_604800 = 604800
    VALUE_2419200 = 2419200
    VALUE_15724800 = 15724800

    def __str__(self) -> str:
        return str(self.value)
