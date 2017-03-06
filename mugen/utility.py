import os
import sys
import json
import shutil
import logging
import Tkinter as tk
import tkFileDialog
import subprocess as sp
from collections import OrderedDict

# Project modules
import mugen.exceptions as ex
import mugen.constants as c

### INPUTS ###

def get_music_video_name(output_name, is_regenerated):
    music_video_name = None
    if output_name == None:
        count = 0
        while True:
            music_video_name = 'regenerated_' if is_regenerated else ""
            music_video_name += c.MUSIC_VIDEO_NAME_DEFAULT + "_%s" % count
            if not os.path.exists(get_music_video_output_path(music_video_name)):
                break
            else:
                count += 1
    else:
        music_video_name = output_name

    print("Preparing {}...".format(music_video_name))

    return music_video_name

def get_file(file_type, source):
    """
    Validates a file path from a given source, 
    or returns a file path after prompting user via file selection dialog
    """
    file = None

    # Select via terminal input
    if source:
        source_exists = os.path.exists(source)

        # Check that file exists
        if not source_exists:
            print("{} source path '{}' does not exist.".format(file_type, source))
            sys.exit(1)

        file = source
    # Select via file selection dialog
    else:
        root = tk.Tk()
        root.withdraw()
        source = tkFileDialog.askopenfilename(message="Select {} file".format(file_type))
        root.update()

        if source == "":
            print("No {} file was selected.".format(file_type))
            sys.exit(1)

        # Properly encode file name
        file = source.encode('utf-8')

    logging.debug("{}_file {}".format(file_type, file))
    return file

def get_files(file_type, *sources):
    """
    Returns list of file paths from a given list of sources, 
    or after prompting user for a list of sources via file selection dialog
    """
    files = []

    # Select  via terminal input
    if sources:
        for source in sources:
            source_exists = os.path.exists(source)
            source_is_dir = os.path.isdir(source)

            # Check that file/directory exists
            if not source_exists:
                print("{} source path {} does not exist.".format(file_type, source))
                sys.exit(1)

            # Check if source is file or directory  
            if source_is_dir:
                files.extend([file for file in listdir_nohidden(source) if os.path.isfile(file)])
            else:
                files.append(source)
    # Select files via file selection dialog
    else:
        message = "Select {} files".format(file_type)
        while True:
            root = tk.Tk()
            root.withdraw()
            source = tkFileDialog.askopenfilename(message=message, multiple=True)
            message = "Select more {} files, or press cancel if done".format(file_type)
            root.update()
    
            if not source:
                break

            # Properly encode file names
            files.extend([file.encode('utf-8') for file in source])

        if len(files) == 0:
            print("No {} files were selected.".format(file_type))
            sys.exit(1)

    logging.debug("{}_source {}".format(file_type, sources))
    for file in files:
        logging.debug("{}_file: {}".format(file_type, file))
    return files

def parse_speed_multiplier(speed_multiplier, speed_multiplier_offset):
    if speed_multiplier == 0 or (speed_multiplier.numerator != 1 and speed_multiplier.denominator != 1):
        print("Improper speed multiplier provided." + c.HELP)
        sys.exit(1)

    if speed_multiplier_offset:
        if speed_multiplier >= 1:
            print("Speed multiplier offsets may only be used with slowdown speed multipliers." + c.HELP)
            sys.exit(1)
        elif speed_multiplier_offset > speed_multiplier.denominator - 1:
            print("Speed multiplier offset may not be greater than x - 1 for a slowdown of 1/x." + c.HELP)
            sys.exit(1)

    logging.debug('speed_multiplier: {}'.format(speed_multiplier))

    return speed_multiplier, speed_multiplier_offset

def parse_spec_file(spec_file):
    with open(spec_file) as spec_file:    
        spec = json.load(spec_file, object_pairs_hook=OrderedDict)

    return spec

def validate_replace_segments(replace_segments, video_segments):
    for segment in replace_segments:
        if segment < 0 or segment > (len(video_segments) - 1):
            print("No segment {} exists in spec for music video".format(segment))
            sys.exit(1)

### FILESYSTEM ###

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

def get_segments_dir(music_video_name):
    return c.SEGMENTS_PATH_BASE + music_video_name + '/'

def get_music_video_output_path(music_video_name):
    return c.OUTPUT_PATH_BASE + music_video_name + c.VIDEO_OUTPUT_EXTENSION

def get_spec_path(music_video_name):
    return c.OUTPUT_PATH_BASE + music_video_name + '_spec' + c.SPEC_EXTENSION

def get_audio_preview_path(audio_file):
    return c.OUTPUT_PATH_BASE + filename_from_path(audio_file) + "_marked_audio_preview" + c.ESSENTIA_ONSETS_AUDIO_EXTENSION

def get_temp_music_video_output_path(music_video_name):
    return c.TEMP_PATH_BASE + 'temp_' + music_video_name + c.VIDEO_OUTPUT_EXTENSION

def get_temp_subtitle_path(music_video_name, track_type):
    return c.TEMP_PATH_BASE + music_video_name + '_' + track_type + '_subs' + c.SUBTITLES_EXTENSION

def get_temp_audio_onsets_path(audio_file):
    return c.TEMP_PATH_BASE + filename_from_path(audio_file) + '_marked_audio' + c.ESSENTIA_ONSETS_AUDIO_EXTENSION

def get_temp_audio_offset_path(audio_file):
    return c.TEMP_PATH_BASE + filename_from_path(audio_file) + '_offset_audio' + os.path.splitext(audio_file)[1]

def filename_from_path(path):
    """
    Returns a path's file basename without its extension
    """
    file = os.path.basename(path)
    filename, extension = os.path.splitext(file)

    return filename

def sanitize_filename(filename):
    keepcharacters = (' ','.','_','-','(',')','[',']')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip() if filename else None

def listdir_nohidden(path):
    # Make sure path has trailing slash
    path = os.path.join(path, '')
    for file in os.listdir(path):
        if not file.startswith('.'):
            yield path + file

### SYSTEM ###

def get_ffmpeg_binary():
    """
    Return appropriate ffmpeg binary for system
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
    p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    p_out, p_err = p.communicate()

    if p.returncode != 0:
        raise ex.FFMPEGError("Error executing ffmpeg command.", p.returncode, p_out, p_err)

def touch(filename):
    open(filename, 'a').close()

def which(program):
    """
    Mimics behavior of UNIX which command.
    """
    envdir_list = [os.curdir] + os.environ["PATH"].split(os.pathsep)

    for envdir in envdir_list:
        program_path = os.path.join(envdir, program)
        if os.path.isfile(program_path) and os.access(program_path, os.X_OK):
            return program_path