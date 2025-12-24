from enum import Enum

class PipelineConfigurationResponseType(str, Enum):
    PIPELINE_CONFIGURATION = "pipeline_configuration"

    def __str__(self) -> str:
        return str(self.value)
