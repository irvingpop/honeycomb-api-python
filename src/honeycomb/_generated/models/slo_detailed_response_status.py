from enum import Enum


class SLODetailedResponseStatus(str, Enum):
    NORMAL = "normal"
    NO_ALERTS = "no_alerts"
    NO_EVENTS = "no_events"
    TRIGGERED = "triggered"

    def __str__(self) -> str:
        return str(self.value)
