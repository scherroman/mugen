import json
import os
import re
import shutil
import subprocess as sp
from collections import OrderedDict
from fractions import Fraction

from typing import List, Callable, Optional as Opt, Union

import numpy as np
import decorator

from mugen.constants import TIME_FORMAT
from mugen.exceptions import ParameterError
import mugen.exceptions as ex
import mugen.paths as paths


""" SYSTEM """

def touch(filename):
    """
    Creates an empty file if it does not already exist
    """
    open(filename, 'a').close()


def which(executable):
    """
    Checks if an executable exists
    (Mimics behavior of UNIX which command)
    """
    envdir_list = [os.curdir] + os.environ["PATH"].split(os.pathsep)

    for envdir in envdir_list:
        executable_path = os.path.join(envdir, executable)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path


def get_ffmpeg_binary():
    """
    Returns appropriate ffmpeg binary for current system
    """
    # Unix
    if which("ffmpeg"):
        return "ffmpeg"
    # Windows
    elif which("ffmpeg.exe"):
        return "ffmpeg.exe"
    else:
        raise IOError("Could not find ffmpeg binary for system.")


def execute_ffmpeg_command(cmd):
    """
    Executes an ffmpeg command
    """
    p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    p_out, p_err = p.communicate()

    if p.returncode != 0:
        raise ex.FFMPEGError(f"Error executing ffmpeg command. Error code: {p.returncode}, Error: {p_err}")


""" FILESYSTEM  """


def ensure_dir(*directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def recreate_dir(*directories):
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)


def delete_dir(*directories):
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)


def listdir_nohidden(path):
    # Make sure path has trailing slash
    path = os.path.join(path, '')
    for file in os.listdir(path):
        if not file.startswith('.'):
            yield path + file


def parse_json_file(json_file: str) -> dict:
    with open(json_file) as json_file:
        json_content = json.load(json_file, object_pairs_hook=OrderedDict)

    return json_content


""" MISC """


def ranges_overlap(a_start, a_end, b_start, b_end) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)


def float_to_fraction(float_var):
    return Fraction(float_var).limit_denominator()


def time_to_seconds(time: TIME_FORMAT) -> float:
    """ 
    Convert any time into seconds.
    """

    if isinstance(time, str):
        expr = r"(?:(?:(\d+):)?(?:(\d+):))?(\d+)?(?:[,|.](\d+))?"
        finds = re.findall(expr, time)[0]
        finds = [find if find else '0' for find in finds]

        seconds = (3600*int(finds[0]) +
                   60*int(finds[1]) +
                   int(finds[2]) +
                   int(finds[3])/(10**len(finds[3])))
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


def time_list_to_seconds(times: List[TIME_FORMAT]) -> List[float]:
    return [time_to_seconds(time) for time in times]


""" DECORATORS """


def preprocess_args(fun: Callable, varnames: List[str]):
    """ 
    Applies fun to variables in varnames before launching the function 
    """
    def wrapper(f, *a, **kw):
        func_code = f.__code__

        names = func_code.co_varnames
        new_a = [fun(arg) if (name in varnames) else arg
                 for (arg, name) in zip(a, names)]
        new_kw = {k: fun(v) if k in varnames else v
                  for (k, v) in kw.items()}
        return f(*new_a, **new_kw)

    return decorator.decorator(wrapper)


def temp_file_enabled(path_var: str, extension: str):
    """
    Decorator to set path_var to a temporary file path if it is None. Does not create the file.

    Args:
        path_var: A variable expecting a file path
        extension: extension for the temporary file
    """
    def _use_temp_file_path(path_variable):
        return path_variable or paths.generate_temp_file_path(extension)

    return preprocess_args(_use_temp_file_path, [path_var])


def ensure_json_serializable(*dicts: dict):
    """
    Decorator ensures dicts are json serializable
    """
    def _ensure_json_serializable(dictionary):
        try:
            json.dumps(dictionary)
        except TypeError as e:
            print(f"{dictionary} is not json serializable. Error: {e}")
            raise

        return dictionary

    return preprocess_args(_ensure_json_serializable, *dicts)


def convert_to_fraction(*varnames: str):
    """
    Decorator to convert varnames from floats to fractions
    """
    return preprocess_args(float_to_fraction, *varnames)


def convert_time_to_seconds(*varnames: str):
    """
    Decorator to convert varnames from TIME_FORMAT to seconds
    """
    return preprocess_args(time_to_seconds, *varnames)


def convert_time_list_to_seconds(*varnames: str):
    """
    Decorator to convert varnames from TIME_FORMAT to seconds
    """
    return preprocess_args(time_list_to_seconds, *varnames)


""" LOCATIONS & INTERVALS """

def offset_locations(locations: List[float], offset: float) -> List[float]:
    return [location + offset for location in locations]


def intervals_from_locations(locations: List[float]) -> List[float]:
    intervals = []

    previous_location = None
    for index, location in enumerate(locations):
        if index == 0:
            intervals.append(location)
        else:
            intervals.append(location - previous_location)
        previous_location = location

    return intervals


def locations_from_intervals(intervals: List[float]) -> List[float]:
    locations = []
    running_duration = 0
    for index, interval in enumerate(intervals):
        if index < len(intervals):
            running_duration += interval
            locations.append(running_duration)

    return locations


def split_locations(locations: List[float], pieces_per_split: int) -> List[float]:
    """
    Splits locations up to form shorter intervals

    Args:
        locations
        pieces_per_split: Number of pieces to split each location into

    Returns: Split locations
    """
    splintered_locations = []

    for index, location in enumerate(locations):
        splintered_locations.append(location)

        if index == len(locations) - 1:
            continue

        next_location = locations[index + 1]
        interval = next_location - location
        interval_piece = interval / pieces_per_split

        for _ in range(pieces_per_split - 1):
            location += interval_piece
            splintered_locations.append(location)

    return splintered_locations


def merge_locations(locations: List[float], pieces_per_merge: int, offset: Opt[int] = None) -> List[float]:
    """
        Merges adjacent locations to form longer intervals
    
        Args:
            locations
            pieces_per_merge: Number of adjacent locations to merge at a time
            offset: Offset for the merging of locations
    
        Returns: Merged locations
    """
    if offset is None:
        offset = 0

    combined_locations = []

    for index, location in enumerate(locations):
        if (index - offset) % pieces_per_merge == 0:
            combined_locations.append(location)

    return combined_locations


@convert_to_fraction('speed_multiplier')
def locations_after_speed_multiplier(locations: Union[List[float], np.ndarray],
                                     speed_multiplier: Union[float, Fraction],
                                     speed_multiplier_offset: Opt[int] = None) -> List[float]:
    if speed_multiplier > 1:
        locations = split_locations(locations, speed_multiplier.numerator)
    elif speed_multiplier < 1:
        locations = merge_locations(locations, speed_multiplier.denominator,
                                    speed_multiplier_offset)

    return locations


def start_end_locations_from_intervals(intervals: List[float]):
    start_locations = []
    end_locations = []

    running_duration = 0
    for index, duration in enumerate(intervals):
        start_time = running_duration
        end_time = start_time + duration

        start_locations.append(start_time)
        end_locations.append(end_time)

        running_duration += duration

    return start_locations, end_locations











