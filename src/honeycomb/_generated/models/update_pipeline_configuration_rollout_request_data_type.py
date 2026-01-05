from enum import Enum


class UpdatePipelineConfigurationRolloutRequestDataType(str, Enum):
    PIPELINE_CONFIGURATION_ROLLOUT = "pipeline_configuration_rollout"

    def __str__(self) -> str:
        return str(self.value)
