from enum import Enum

class TeamRelationshipTeamDataType(str, Enum):
    TEAMS = "teams"

    def __str__(self) -> str:
        return str(self.value)
