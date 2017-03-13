import os
import json
import shutil
import subprocess as sp
from collections import OrderedDict
from moviepy.decorators import preprocess_args

# Project modules
import mugen.constants as c
import mugen.exceptions as ex
import mugen.paths as paths

""" INPUTS """

def get_files(sources):
    """
    Returns list of file paths from a given list of sources,
    """
    files = []

    for source in sources:
        source_is_dir = os.path.isdir(source)

        # Check if source is file or directory
        if source_is_dir:
            files.extend([file for file in listdir_nohidden(source) if os.path.isfile(file)])
        else:
            files.append(source)

    return files

def parse_spec_file(spec_file):
    with open(spec_file) as spec_file:    
        spec = json.load(spec_file, object_pairs_hook=OrderedDict)

    return spec

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

def sanitize_directory_name(*directory_names):
    """
    Decorator ensures directory name parameters end with '/'
    """
    def _sanitize_directory_name(directory_name):
        return directory_name if directory_name.endswith('/') else directory_name + '/'

    return preprocess_args(_sanitize_directory_name, directory_names)

def listdir_nohidden(path):
    # Make sure path has trailing slash
    path = os.path.join(path, '')
    for file in os.listdir(path):
        if not file.startswith('.'):
            yield path + file

""" SYSTEM """

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

def touch(filename):
    """
    Creates an empty file
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
