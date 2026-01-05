from enum import Enum


class NotificationRecipientDetailsPagerdutySeverity(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
