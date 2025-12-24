from enum import Enum

class QueryAnnotationSource(str, Enum):
    BOARD = "board"
    QUERY = "query"

    def __str__(self) -> str:
        return str(self.value)
