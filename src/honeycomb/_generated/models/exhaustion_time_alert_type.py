from enum import Enum


class ExhaustionTimeAlertType(str, Enum):
    BUDGET_RATE = "budget_rate"
    EXHAUSTION_TIME = "exhaustion_time"

    def __str__(self) -> str:
        return str(self.value)
