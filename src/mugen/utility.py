import json
import os
import re
import shutil
import subprocess as sp
from collections import OrderedDict
from fractions import Fraction
from functools import wraps

from typing import List, Callable, Any, Union

import collections
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
    for file in os.listdir(path):
        if not file.startswith('.'):
            yield os.path.join(path, file)


def parse_json_file(json_file: str) -> dict:
    with open(json_file) as json_file:
        json_content = json.load(json_file, object_pairs_hook=OrderedDict)

    return json_content


""" MISC """


def flatten(l: List[Union[Any, List[Any]]]) -> List[Any]:
    """
    Flattens an arbitrarily nested irregular list of objects
    """
    l_flattened = []

    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            l_flattened.extend(flatten(el))
        else:
            l_flattened.append(el)

    return l_flattened


def ranges_overlap(a_start, a_end, b_start, b_end) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)


def float_to_fraction(float_var) -> Fraction:
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


def temp_file_enabled(path_var: str, extension: str):
    """
    Decorator to set path_var to a temporary file path if it is None. Does not create the file.
    
    Parameters
    ----------
    path_var
        A variable expecting a file path
        
    extension
        extension for the temporary file
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


def validate_speed_multiplier(func):
    """
    Decorator validates speed multiplier and speed_multiplier_offset values
    """

    @wraps(func)
    def _validate_speed_multiplier(*args, **kwargs):
        speed_multiplier = kwargs.get('speed_multiplier')
        speed_multiplier_offset = kwargs.get('speed_multiplier_offset')

        if speed_multiplier:
            speed_multiplier = Fraction(speed_multiplier).limit_denominator()
            if speed_multiplier == 0 or (speed_multiplier.numerator != 1 and speed_multiplier.denominator != 1):
                raise ValueError(f"""Improper speed multiplier {speed_multiplier}. 
                                     Speed multipliers must be of the form x or 1/x, where x is a natural number.""")

        if speed_multiplier_offset:
            if speed_multiplier >= 1:
                raise ValueError(f"""Improper speed multiplier offset {speed_multiplier_offset} for speed multiplier
                                     {speed_multiplier}. Speed multiplier offsets may only be used with slowdown speed
                                     multipliers.""")
            elif speed_multiplier_offset > speed_multiplier.denominator - 1:
                raise ValueError(f"""Improper speed multiplier offset {speed_multiplier_offset} for speed multiplier
                                     {speed_multiplier}. Speed multiplier offset may not be greater than x - 1 for a 
                                     slowdown of 1/x.""")

        return func(*args, **kwargs)

    return _validate_speed_multiplier
