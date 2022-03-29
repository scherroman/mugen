import os
import shutil
import subprocess
import tempfile
from subprocess import CalledProcessError, CompletedProcess
from typing import List

from mugen.utilities.general import preprocess_args

TEMP_PATH_BASE = tempfile.TemporaryDirectory().name


def touch(filename):
    """
    Creates an empty file if it does not already exist
    """
    open(filename, "a").close()


def ensure_directory_exists(*directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def recreate_directory(*directories):
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)


def _list_directory(path, include_hidden=False):
    for file in os.listdir(path):
        if not include_hidden and file.startswith("."):
            continue
        yield os.path.join(path, file)


def list_directory_files(directory: str) -> List[str]:
    """
    Returns
    -------
    A list of all files found in the directory
    """
    return [
        item
        for item in _list_directory(directory, include_hidden=False)
        if os.path.isfile(item)
    ]


def run_command(command) -> CompletedProcess:
    """
    Executes a system command
    """
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except CalledProcessError as error:
        print("Error executing command")
        print(error.stdout)
        print(error.stderr)
        raise error

    return result


def _generate_temp_file_path(extension: str) -> str:
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
        return path_variable or _generate_temp_file_path(extension)

    return preprocess_args(_use_temporary_file_path, [path_var])
