from enum import Enum


class QueryPanelQueryPanelQueryStyle(str, Enum):
    COMBO = "combo"
    GRAPH = "graph"
    TABLE = "table"

    def __str__(self) -> str:
        return str(self.value)
