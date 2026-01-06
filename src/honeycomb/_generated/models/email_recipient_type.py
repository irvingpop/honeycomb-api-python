from enum import Enum


class EmailRecipientType(str, Enum):
    EMAIL = "email"

    def __str__(self) -> str:
        return str(self.value)
