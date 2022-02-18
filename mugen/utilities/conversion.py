import re
from fractions import Fraction
from typing import List

from mugen.constants import TIME_FORMAT, Color
from mugen.exceptions import ParameterError
from mugen.utilities.general import preprocess_args


def float_to_fraction(float_var: float) -> Fraction:
    return Fraction(float_var).limit_denominator()


def time_to_seconds(time: TIME_FORMAT) -> float:
    """
    Convert any time into seconds.
    """

    if isinstance(time, str):
        expr = r"(?:(?:(\d+):)?(?:(\d+):))?(\d+)?(?:[,|.](\d+))?"
        finds = re.findall(expr, time)[0]
        finds = [find if find else "0" for find in finds]

        seconds = (
            3600 * int(finds[0])
            + 60 * int(finds[1])
            + int(finds[2])
            + int(finds[3]) / (10 ** len(finds[3]))
        )
    elif isinstance(time, tuple):
        if len(time) == 3:
            hr, mn, sec = time
        elif len(time) == 2:
            hr, mn, sec = 0, time[0], time[1]
        else:
            raise ParameterError(f"Unsupported number of elements in tuple {time}")
        seconds = (3600 * hr) + (60 * mn) + sec
    else:
        seconds = time

    return seconds


def seconds_to_time_code(seconds: float) -> str:
    ms = 1000 * round(seconds - int(seconds), 3)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d.%03d" % (h, m, s, ms)


def hex_to_rgb(hex_value) -> List[int]:
    """Return [red, green, blue] for the color given as #rrggbb."""
    hex_value = hex_value.lstrip("#")
    len_hex_value = len(hex_value)
    return [
        int(hex_value[i : i + len_hex_value // 3], 16)
        for i in range(0, len_hex_value, len_hex_value // 3)
    ]


def color_to_hex_code(color):
    if color.startswith("#"):
        return color
    else:
        return Color(color).hex_code()


def convert_float_to_fraction(*variable_names: str):
    """
    Decorator to convert variables from floats to fractions
    """
    return preprocess_args(float_to_fraction, *variable_names)


def convert_time_to_seconds(*variable_names: str):
    """
    Decorator to convert variables from TIME_FORMAT to seconds
    """
    return preprocess_args(time_to_seconds, *variable_names)


def convert_color_to_hex_code(*variable_names: str):
    """
    Decorator to convert variables to hex color format
    """
    return preprocess_args(color_to_hex_code, *variable_names)
