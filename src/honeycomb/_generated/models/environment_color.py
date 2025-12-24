from enum import Enum

class EnvironmentColor(str, Enum):
    BLUE = "blue"
    GOLD = "gold"
    GREEN = "green"
    LIGHTBLUE = "lightBlue"
    LIGHTGOLD = "lightGold"
    LIGHTGREEN = "lightGreen"
    LIGHTPURPLE = "lightPurple"
    LIGHTRED = "lightRed"
    PURPLE = "purple"
    RED = "red"

    def __str__(self) -> str:
        return str(self.value)
