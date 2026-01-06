from enum import Enum


class MSTeamsRecipientType(str, Enum):
    MSTEAMS = "msteams"

    def __str__(self) -> str:
        return str(self.value)
