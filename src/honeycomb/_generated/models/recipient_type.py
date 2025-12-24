from enum import Enum

class RecipientType(str, Enum):
    EMAIL = "email"
    MSTEAMS = "msteams"
    MSTEAMS_WORKFLOW = "msteams_workflow"
    PAGERDUTY = "pagerduty"
    SLACK = "slack"
    WEBHOOK = "webhook"

    def __str__(self) -> str:
        return str(self.value)
