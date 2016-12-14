import os
import sys
import json
import shutil
import logging
import Tkinter as tk
import tkFileDialog
from fractions import Fraction
from collections import OrderedDict

# Project modules
import settings as s

### INPUTS ###

def get_music_video_name(output_name, is_regenerated):
    music_video_name = None
    if output_name == None:
        count = 0
        while True:
            music_video_name = 'regenerated_' if is_regenerated else ""
            music_video_name += s.OUTPUT_NAME_DEFAULT + "_%s" % count
            if not os.path.exists(get_output_path(music_video_name)):
                break
            else:
                count += 1
    else:
        music_video_name = output_name

    return music_video_name

# Validates a file path from a given source, or returns a file path after prompting user for selection
def get_file(src, file_type):
    file = None

    # Select via terminal input
    if src:
        src_exists = os.path.exists(src)

        # Check that file exists
        if not src_exists:
            print("{} source path '{}' does not exist.".format(file_type, src))
            sys.exit(1)

        file = src
    # Select via file selection dialog
    else:
        root = tk.Tk()
        root.withdraw()
        src = tkFileDialog.askopenfilename(message="Select {} file".format(file_type))
        root.update()

        if src == "":
            print("No {} file was selected.".format(file_type))
            sys.exit(1)

        # Properly encode file name
        file = src.encode('utf-8')

    logging.debug("{}_file {}".format(file_type, file))
    return file

# Returns list of file paths from a given source, or after prompting user for selection
def get_files(src, file_type):
    files = []

    # Select  via terminal input
    if src:
        src_exists = os.path.exists(src)
        src_is_dir = os.path.isdir(src)

        # Check that file/directory exists
        if not src_exists:
            print("{} source path {} does not exist.".format(file_type, src))
            sys.exit(1)

        # Check if source is file or directory  
        if src_is_dir:
            files = [file for file in listdir_nohidden(src) if os.path.isfile(file)]
        else:
            files = [src]
    # Select files via file selection dialog
    else:
        root = tk.Tk()
        root.withdraw()
        src = tkFileDialog.askopenfilename(message="Select {} file(s)".format(file_type), multiple=True)
        root.update()

        if src == "":
            print("No {} file(s) were selected.".format(file_type, src))
            sys.exit(1)

        # Properly encode file names
        files = [file.encode('utf-8') for file in src]

    logging.debug("{}_src {}".format(file_type, src))
    for file in files:
        logging.debug("{}_file: {}".format(file_type, file))
    return files

def parse_speed_multiplier(speed_multiplier, speed_multiplier_offset):
    if speed_multiplier == 0 or (speed_multiplier.numerator != 1 and speed_multiplier.denominator != 1):
        print("Improper speed multiplier provided." + s.HELP)
        sys.exit(1)

    if speed_multiplier_offset:
        if speed_multiplier >= 1:
            print("Speed multiplier offsets may only be used with slowdown speed multipliers." + s.HELP)
            sys.exit(1)
        elif speed_multiplier_offset > speed_multiplier.denominator - 1:
            print("Speed multiplier offset may not be greater than x - 1 for a slowdown of 1/x." + s.HELP)
            sys.exit(1)

    logging.debug('speed_multiplier: {}'.format(speed_multiplier))

    return speed_multiplier, speed_multiplier_offset

def parse_spec_file(spec_file):
    with open(spec_file) as spec_file:    
        spec = json.load(spec_file, object_pairs_hook=OrderedDict)

    return spec

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

def get_output_path(music_video_name):
    return s.OUTPUT_PATH_BASE + music_video_name + s.OUTPUT_EXTENSION

def get_spec_path(music_video_name):
    return s.OUTPUT_PATH_BASE + music_video_name + '_spec' + s.SPEC_EXTENSION

def get_segments_dir(music_video_name):
    return s.SEGMENTS_PATH_BASE + music_video_name + '/'

def reserve_file(file_name):
    open(file_name, 'a').close()

def sanitize_filename(filename):
    keepcharacters = (' ','.','_','-','(',')','[',']')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip() if filename else None

def listdir_nohidden(path):
    for file in os.listdir(path):
        if not file.startswith('.'):
            yield path + file