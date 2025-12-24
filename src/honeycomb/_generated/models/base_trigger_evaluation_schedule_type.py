from enum import Enum

class BaseTriggerEvaluationScheduleType(str, Enum):
    FREQUENCY = "frequency"
    WINDOW = "window"

    def __str__(self) -> str:
        return str(self.value)
