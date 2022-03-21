import platform
from enum import Enum
from typing import Tuple, Union

PLATFORM = platform.system()

"""
SEC.MIL or 'SEC.MIL'
(MIN, SEC.MIL) or 'MIN:SEC.MIL'
(HRS, MIN, SEC.MIL) or 'HRS:MIN:SEC.MIL'
"""
TIME_FORMAT = Union[float, Tuple[int, float], Tuple[int, int, float], str]


class Color(str, Enum):
    BLACK = "black"
    WHITE = "white"

    def hex_code(self):
        if self.value == self.BLACK:
            return "#000000"
        elif self.value == self.WHITE:
            return "#ffffff"
        else:
            raise ValueError(f"No Hex code defined for {self}")


class Platform(str, Enum):
    LINUX = "Linux"
    MACOS = "Darwin"
    WINDOWS = "Windows"
