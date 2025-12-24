from enum import Enum

class PagerDutyRecipientType(str, Enum):
    PAGERDUTY = "pagerduty"

    def __str__(self) -> str:
        return str(self.value)
