from enum import Enum


class QueryOp(str, Enum):
    AVG = "AVG"
    CONCURRENCY = "CONCURRENCY"
    COUNT = "COUNT"
    COUNT_DISTINCT = "COUNT_DISTINCT"
    HEATMAP = "HEATMAP"
    MAX = "MAX"
    MIN = "MIN"
    P001 = "P001"
    P01 = "P01"
    P05 = "P05"
    P10 = "P10"
    P20 = "P20"
    P25 = "P25"
    P50 = "P50"
    P75 = "P75"
    P80 = "P80"
    P90 = "P90"
    P95 = "P95"
    P99 = "P99"
    P999 = "P999"
    RATE_AVG = "RATE_AVG"
    RATE_MAX = "RATE_MAX"
    RATE_SUM = "RATE_SUM"
    SUM = "SUM"

    def __str__(self) -> str:
        return str(self.value)
