from enum import Enum

class MSTeamsWorkflowRecipientType(str, Enum):
    MSTEAMS_WORKFLOW = "msteams_workflow"

    def __str__(self) -> str:
        return str(self.value)
