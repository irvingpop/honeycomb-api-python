from enum import Enum

class SlackRecipientType(str, Enum):
    SLACK = "slack"

    def __str__(self) -> str:
        return str(self.value)
