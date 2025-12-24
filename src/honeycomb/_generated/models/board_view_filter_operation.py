from enum import Enum

class BoardViewFilterOperation(str, Enum):
    CONTAINS = "contains"
    DOES_NOT_CONTAIN = "does-not-contain"
    DOES_NOT_END_WITH = "does-not-end-with"
    DOES_NOT_EXIST = "does-not-exist"
    DOES_NOT_START_WITH = "does-not-start-with"
    ENDS_WITH = "ends-with"
    EXISTS = "exists"
    IN = "in"
    NOT_IN = "not-in"
    STARTS_WITH = "starts-with"
    VALUE_0 = "="
    VALUE_1 = "!="
    VALUE_2 = ">"
    VALUE_3 = ">="
    VALUE_4 = "<"
    VALUE_5 = "<="

    def __str__(self) -> str:
        return str(self.value)
