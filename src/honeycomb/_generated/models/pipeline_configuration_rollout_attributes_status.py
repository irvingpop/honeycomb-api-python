from enum import Enum

class PipelineConfigurationRolloutAttributesStatus(str, Enum):
    ARCHIVED = "archived"
    DEPLOYING = "deploying"
    FAILED = "failed"
    LIVE = "live"
    PENDING = "pending"
    REMOVING = "removing"

    def __str__(self) -> str:
        return str(self.value)
