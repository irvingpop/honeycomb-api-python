from enum import Enum

class BoardQueryVisualizationSettingsChartsItemChartType(str, Enum):
    CBAR = "cbar"
    CPIE = "cpie"
    DEFAULT = "default"
    LINE = "line"
    STACKED = "stacked"
    STAT = "stat"
    TSBAR = "tsbar"

    def __str__(self) -> str:
        return str(self.value)
