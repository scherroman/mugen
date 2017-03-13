import os
import sys
import logging
import Tkinter as tk
import tkFileDialog

# Project modules
import mugen.constants as c

""" COMMAND LINE UTILITY FUNCTIONS """

def get_music_video_name(is_regenerated=False):
    music_video_name = None

    count = 0
    while True:
        music_video_name = 'regenerated_' if is_regenerated else ""
        music_video_name += c.MUSIC_VIDEO_NAME_DEFAULT + "_%s" % count

        if not os.path.exists(paths.music_video_output_path(music_video_name)):
            break

        count += 1

    return music_video_name

def prompt_file_selection(file_type):
    # Select via file selection dialog
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

def prompt_files_selection(file_type):
    files = []

    # Select files via file selection dialog
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

    for file in files:
        logging.debug("{}_file: {}".format(file_type, file))

    return files

def validate_path(*paths):
    for path in paths:
        if path and not os.path.exists(path):
            print("Path {} does not exist.".format(path))
            sys.exit(1)

def validate_replace_segments(replace_segments, video_segments):
    for segment in replace_segments:
        if segment < 0 or segment > (len(video_segments) - 1):
            print("No segment {} exists in spec for music video".format(segment))
            sys.exit(1)

def validate_speed_multiplier(speed_multiplier, speed_multiplier_offset):
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
