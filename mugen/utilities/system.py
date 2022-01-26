import os
import os
import shutil
import subprocess
from typing import List

import tempfile

from mugen.exceptions import FFMPEGError
from mugen.utilities.general import preprocess_args

TEMP_PATH_BASE = tempfile.TemporaryDirectory().name


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


def ensure_directory_exists(*directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def recreate_directory(*directories):
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)


def list_directory(path, include_hidden = False):
    for file in os.listdir(path):
        if not include_hidden and file.startswith('.'):
            continue
        yield os.path.join(path, file)


def list_directory_files(directory: str, include_hidden = False) -> List[str]:
    """
    Returns
    -------
    A list of all files found in the directory
    """
    return [item for item in list_directory(directory, include_hidden=include_hidden) if os.path.isfile(item)]


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
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_output, process_error = process.communicate()

    if process.returncode != 0:
        raise FFMPEGError(f"Error executing ffmpeg command. Error code: {process.returncode}, Error: {process_error}",
                             process.returncode, process_output, process_error)


def generate_temp_file_path(extension: str) -> str:
    return TEMP_PATH_BASE + next(tempfile._RandomNameSequence()) + extension


def use_temporary_file_fallback(path_var: str, extension: str):
    """
    Decorator to set path_var to a temporary file path if it is None. Does not create the file.
    
    Parameters
    ----------
    path_var
        A variable expecting a file path
        
    extension
        extension for the temporary file
    """
    def _use_temporary_file_path(path_variable):
        return path_variable or generate_temp_file_path(extension)

    return preprocess_args(_use_temporary_file_path, [path_var])