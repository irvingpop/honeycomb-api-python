from enum import Enum


class ValidationErrorTypeDetailItemCode(str, Enum):
    ALREADY_EXISTS = "already_exists"
    INCORRECT_TYPE = "incorrect_type"
    INVALID = "invalid"
    MISSING = "missing"

    def __str__(self) -> str:
        return str(self.value)
